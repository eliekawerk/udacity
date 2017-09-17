#include <fstream>
#include <math.h>
#include <uWS/uWS.h>
#include <chrono>
#include <iostream>
#include <thread>
#include <vector>
#include "Eigen-3.3/Eigen/Core"
#include "Eigen-3.3/Eigen/QR"
#include "json.hpp"
#include "spline.h"

using namespace std;

// for convenience
using json = nlohmann::json;

// For converting back and forth between radians and degrees.
constexpr double pi() {
	return M_PI;
}
double deg2rad(double x) {
	return x * pi() / 180;
}
double rad2deg(double x) {
	return x * 180 / pi();
}

// Checks if the SocketIO event has JSON data.
// If there is data the JSON object in string format will be returned,
// else the empty string "" will be returned.
string hasData(string s) {
	auto found_null = s.find("null");
	auto b1 = s.find_first_of("[");
	auto b2 = s.find_first_of("}");
	if (found_null != string::npos) {
		return "";
	} else if (b1 != string::npos && b2 != string::npos) {
		return s.substr(b1, b2 - b1 + 2);
	}
	return "";
}

double distance(double x1, double y1, double x2, double y2) {
	return sqrt((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1));
}
int ClosestWaypoint(double x, double y, vector<double> maps_x, vector<double> maps_y) {

	double closestLen = 100000; //large number
	int closestWaypoint = 0;

	for (int i = 0; i < maps_x.size(); i++) {
		double map_x = maps_x[i];
		double map_y = maps_y[i];
		double dist = distance(x, y, map_x, map_y);
		if (dist < closestLen) {
			closestLen = dist;
			closestWaypoint = i;
		}

	}

	return closestWaypoint;

}

int NextWaypoint(double x, double y, double theta, vector<double> maps_x, vector<double> maps_y) {

	int closestWaypoint = ClosestWaypoint(x, y, maps_x, maps_y);

	double map_x = maps_x[closestWaypoint];
	double map_y = maps_y[closestWaypoint];

	double heading = atan2((map_y - y), (map_x - x));

	double angle = abs(theta - heading);

	if (angle > pi() / 4) {
		closestWaypoint++;
	}

	return closestWaypoint;

}

// Transform from Cartesian x,y coordinates to Frenet s,d coordinates
vector<double> getFrenet(double x, double y, double theta, vector<double> maps_x, vector<double> maps_y) {
	int next_wp = NextWaypoint(x, y, theta, maps_x, maps_y);

	int prev_wp;
	prev_wp = next_wp - 1;
	if (next_wp == 0) {
		prev_wp = maps_x.size() - 1;
	}

	double n_x = maps_x[next_wp] - maps_x[prev_wp];
	double n_y = maps_y[next_wp] - maps_y[prev_wp];
	double x_x = x - maps_x[prev_wp];
	double x_y = y - maps_y[prev_wp];

	// find the projection of x onto n
	double proj_norm = (x_x * n_x + x_y * n_y) / (n_x * n_x + n_y * n_y);
	double proj_x = proj_norm * n_x;
	double proj_y = proj_norm * n_y;

	double frenet_d = distance(x_x, x_y, proj_x, proj_y);

	//see if d value is positive or negative by comparing it to a center point

	double center_x = 1000 - maps_x[prev_wp];
	double center_y = 2000 - maps_y[prev_wp];
	double centerToPos = distance(center_x, center_y, x_x, x_y);
	double centerToRef = distance(center_x, center_y, proj_x, proj_y);

	if (centerToPos <= centerToRef) {
		frenet_d *= -1;
	}

	// calculate s value
	double frenet_s = 0;
	for (int i = 0; i < prev_wp; i++) {
		frenet_s += distance(maps_x[i], maps_y[i], maps_x[i + 1], maps_y[i + 1]);
	}

	frenet_s += distance(0, 0, proj_x, proj_y);

	return {frenet_s,frenet_d};

}

// Transform from Frenet s,d coordinates to Cartesian x,y
vector<double> getXY(double s, double d, vector<double> maps_s, vector<double> maps_x, vector<double> maps_y) {
	int prev_wp = -1;

	while (s > maps_s[prev_wp + 1] && (prev_wp < (int) (maps_s.size() - 1))) {
		prev_wp++;
	}

	int wp2 = (prev_wp + 1) % maps_x.size();

	double heading = atan2((maps_y[wp2] - maps_y[prev_wp]), (maps_x[wp2] - maps_x[prev_wp]));
	// the x,y,s along the segment
	double seg_s = (s - maps_s[prev_wp]);

	double seg_x = maps_x[prev_wp] + seg_s * cos(heading);
	double seg_y = maps_y[prev_wp] + seg_s * sin(heading);

	double perp_heading = heading - pi() / 2;

	double x = seg_x + d * cos(perp_heading);
	double y = seg_y + d * sin(perp_heading);

	return {x,y};

}

vector<double> getCarAheadInLane(vector<vector<double>> sensor_fusion, int check_lane, int ego_car_s) {
	vector<double> result_car;
	for (int i = 0; i < sensor_fusion.size(); i++) {
		//car is in the check_lane
		float d = sensor_fusion[i][6]; // [ id, x, y, vx, vy, s, d]
		if (d < (2 + 4 * check_lane + 2) && d > (2 + 4 * check_lane - 2)) {
			vector<double> check_car = sensor_fusion[i];
			double check_car_s = check_car[5];

			if (check_car_s > ego_car_s) {
				if (result_car.size() == 0) { // init condition
					result_car = check_car;
				} else {
					double result_car_s = result_car[5];
					if (result_car_s > check_car_s) {
						result_car = check_car;
					}
				}
			}
		}
	}

	if(result_car.size() > 0)
		cout << "ahead: (" << check_lane << ") " << result_car[0] << endl;
	return result_car;
}

vector<double> getCarBehindInLane(vector<vector<double>>& sensor_fusion, int check_lane, int ego_car_s) {
	vector<double> result_car;

	for (int i = 0; i < sensor_fusion.size(); i++) {
		//car is in the check_lane
		float d = sensor_fusion[i][6]; // [ id, x, y, vx, vy, s, d]
		if (d < (2 + 4 * check_lane + 2) && d > (2 + 4 * check_lane - 2)) {
			vector<double> check_car = sensor_fusion[i];
			double check_car_s = check_car[5];

			if (check_car_s < ego_car_s) {
				if (result_car.size() == 0) { // init condition
					result_car = check_car;
				} else {
					double result_car_s = result_car[5];
					if (check_car_s < result_car_s) {
						result_car = check_car;
					}
				}
			}
		}
	}

	if(result_car.size() > 0)
		cout << "behind: (" << check_lane << ") " << result_car[0] << endl;
	return result_car;
}

double speedBehindCost(vector<double> car_behind) {

	double max_speed = 49.5 * 0.44704; // 0.44704=MPH2MPS conversion

	double car_behind_vx = car_behind[3]; // [ id, x, y, vx, vy, s, d]
	double car_behind_vy = car_behind[4]; // [ id, x, y, vx, vy, s, d]

	double car_behind_speed = std::sqrt(std::pow(car_behind_vx, 2.0) + std::pow(car_behind_vy, 2.0));
	double cost = (car_behind_speed) / max_speed;

	if (cost >= 0)
		return cost;
	else
		return 0.0;
}

double speedAheadCost(vector<double> car_ahead) {

	double max_speed = 49.5 * 0.44704;

	double car_ahead_vx = car_ahead[3]; // [ id, x, y, vx, vy, s, d]
	double car_ahead_vy = car_ahead[4]; // [ id, x, y, vx, vy, s, d]

	double car_ahead_speed = std::sqrt(std::pow(car_ahead_vx, 2.0) + std::pow(car_ahead_vy, 2.0));

	double cost = (max_speed - car_ahead_speed) / max_speed;

	if (cost >= 0)
		return cost;
	else
		return 0.0;
}

double distanceBehindCost(vector<double> car_behind, double max_dist_behind, int ego_car_s) {

	double car_behind_s = car_behind[5]; // [ id, x, y, vx, vy, s, d]

	if (max_dist_behind > 0)
		return (1.0 - (ego_car_s - car_behind_s) / max_dist_behind);
	else
		return 0.0;
}

double distanceAheadCost(vector<double> car_ahead, double max_dist_ahead, int ego_car_s) {

	double car_ahead_s = car_ahead[5]; // [ id, x, y, vx, vy, s, d]

	if (max_dist_ahead > 0)
		return (1.0 - (car_ahead_s - ego_car_s) / max_dist_ahead);
	else
		return 0.0;
}

double getCostForLane(vector<double> car_ahead, vector<double> car_behind, int lane, double max_dist_ahead,
		double max_dist_behind, int ego_car_s, int ego_car_lane) {

	double cost = 0;

	if (ego_car_lane != lane)
		cost = cost + 0.1; // lane change cost

	if (lane != 1) // lane=1 is middle lane
		cost = cost + 0.05; // prefer middle lane

	cost += 3 * distanceAheadCost(car_ahead, max_dist_ahead, ego_car_s);
	cost += 0.5 * distanceBehindCost(car_behind, max_dist_behind, ego_car_s);
	cost += 2 * speedAheadCost(car_ahead);
	cost += 0.5 * speedBehindCost(car_behind);

	return cost;
}

bool checkLaneFeasibility(vector<vector<double>> sensor_fusion, double ego_car_s, double ego_car_lane, int target_lane,
		int prev_size) {

	double horizont_time = 0.02;
	double min_distance_behind = 10.0;
	double min_distance_ahead = 25.0;

	double car_ahead_s = 0.0;
	double car_behind_s = 0.0;

	vector<double> car_ahead = getCarAheadInLane(sensor_fusion, target_lane, ego_car_s);
	vector<double> car_behind = getCarBehindInLane(sensor_fusion, target_lane, ego_car_s);

	cout << " checkLaneFeasibility for lane: " << target_lane << endl;

	if (!(car_ahead.size() == 0)) { // Another car is ahead
		car_ahead_s = car_ahead[5]; // [ id, x, y, vx, vy, s, d]
		double car_ahead_vx = car_ahead[3];
		double car_ahead_vy = car_ahead[4];
		double car_ahead_speed = std::sqrt(std::pow(car_ahead_vx, 2.0) + std::pow(car_ahead_vy, 2.0));
		car_ahead_s = car_ahead_s + prev_size * horizont_time * car_ahead_speed;
	}

	if (!(car_behind.size() == 0)) { // Another car is behind
		car_behind_s = car_behind[5]; // [ id, x, y, vx, vy, s, d]
		double car_behind_vx = car_behind[3];
		double car_behind_vy = car_behind[4];
		double car_behind_speed = std::sqrt(std::pow(car_behind_vx, 2.0) + std::pow(car_behind_vy, 2.0));
		car_behind_s = car_behind_s + prev_size * horizont_time * car_behind_speed;
	}

	cout << "ego_car_s: " << ego_car_s << ", car_ahead_s: " << car_ahead_s << ", car_behind_s: " << car_behind_s << endl;

	if (car_ahead.size() == 0 && car_behind.size() == 0) { //No car ahead and behind
		cout << "NN " << endl;
		return true;
	}


	if (car_ahead.size() == 0 && !(car_behind.size() == 0)) { //No car ahead. Another car is behind
		cout << "NY " << (ego_car_s - car_behind_s) << " ( >= " << min_distance_behind << " ) " << endl;
		bool decision = (ego_car_s - car_behind_s >= min_distance_behind) ? true : false;
		cout << "decision: " << decision << endl;
		return decision;
	}

	if (!(car_ahead.size() == 0) && car_behind.size() == 0) { //Another car is ahead. No car behind
		cout << "YN " << (car_ahead_s - ego_car_s) << " ( >= " << min_distance_ahead << " ) " << endl;
		bool decision = (car_ahead_s - ego_car_s >= min_distance_ahead) ? true : false;
		cout << "decision: " << decision << endl;
		return decision;
	}

	if (!(car_ahead.size() == 0) && !(car_behind.size() == 0)) { //Another car ahead. Another car behind
		cout << "YY " << (car_ahead_s - ego_car_s) << "  ---  " << (ego_car_s - car_behind_s) << endl;
		bool decision = (car_ahead_s - ego_car_s >= min_distance_ahead && ego_car_s - car_behind_s >= min_distance_behind) ?
				true : false;
		cout << "decision: " << decision << endl;
		return decision;
	}

	cout << "XXXXXXXXXXXXXXXXXXXXXXXXXXXX" << endl;

	return false;
}

int getLane(vector<vector<double>> sensor_fusion, double ego_car_s, double ego_car_lane, int prev_size) {

	//prev_size = 1;

	cout << endl << endl;
	cout << "current lane: " << ego_car_lane << endl;
	cout << "prev_size: " << prev_size << endl;

	int result_lane = ego_car_lane;

	if (ego_car_lane == 0 || ego_car_lane == 2) {
		if (checkLaneFeasibility(sensor_fusion, ego_car_s, ego_car_lane, 1, prev_size)) {
			result_lane = 1;
		}
	} else {
		if (checkLaneFeasibility(sensor_fusion, ego_car_s, ego_car_lane, 0, prev_size)) {
			result_lane = 0;
		} else if (checkLaneFeasibility(sensor_fusion, ego_car_s, ego_car_lane, 2, prev_size)) {
			result_lane = 2;
		}
	}

	time_t now = time(0);
	cout << "result_lane:" << result_lane << ", now: " << now << endl;

	return result_lane;
}

int getOptimalLane(vector<vector<double>> sensor_fusion, double ego_car_s, double ego_car_lane, int prev_size) {

	size_t resultLane = ego_car_lane;

	double max_dist_ahead = 0;
	double max_dist_behind = 0;

	vector<vector<double>> cars_ahead;
	vector<vector<double>> cars_behind;

	for (int lane = 0; lane < 3; ++lane) {
		vector<double> car_ahead = getCarAheadInLane(sensor_fusion, lane, ego_car_s);
		vector<double> car_behind = getCarBehindInLane(sensor_fusion, lane, ego_car_s);

		cars_ahead.push_back(car_ahead);
		cars_behind.push_back(car_behind);

		double distance = car_ahead[5] - ego_car_s; // [ id, x, y, vx, vy, s, d]
		if (max_dist_ahead < distance)
			max_dist_ahead = distance;

		distance = car_behind[5] - ego_car_s; // [ id, x, y, vx, vy, s, d]
		if (max_dist_behind < distance)
			max_dist_behind = distance;
	}

	vector<double> costs;
	for (int lane = 0; lane < 3; ++lane) {
		vector<double> car_ahead = cars_ahead[lane];
		vector<double> car_behind = cars_behind[lane];
		double cost = getCostForLane(car_ahead, car_behind, lane, max_dist_ahead, max_dist_behind, ego_car_s,
				ego_car_lane);
		costs.push_back(cost);
	}

	int optimalLane = std::distance(costs.begin(), std::min_element(costs.begin(), costs.end()));

	// return optimalLane;

	if (optimalLane != ego_car_lane) {
		size_t target_lane = ego_car_lane;

		if (optimalLane > ego_car_lane)
			++target_lane;
		else
			--target_lane;

		vector<double> car_ahead = getCarAheadInLane(sensor_fusion, target_lane, ego_car_s);
		vector<double> car_behind = getCarBehindInLane(sensor_fusion, target_lane, ego_car_s);

		double horizont_time = 0.02;
		double min_distance_behind = 10.0;
		double min_distance_ahead = 25.0;

		// car behind
//		double car_behind_s = car_behind[5]; // [ id, x, y, vx, vy, s, d]
//		double car_behind_vx = car_behind[3];
//		double car_behind_vy = car_behind[4];
//		double car_behind_speed = std::sqrt(std::pow(car_behind_vx, 2.0) + std::pow(car_behind_vy, 2.0));
//
//		double check_car_s_behind = car_behind_s + horizont_time * car_behind_speed;
//		if (ego_car_s - check_car_s_behind >= min_distance_behind)
//			resultLane = target_lane;
//
//		// car ahead
//		double car_ahead_s = car_ahead[5]; // [ id, x, y, vx, vy, s, d]
//		double car_ahead_vx = car_ahead[3];
//		double car_ahead_vy = car_ahead[4];
//		double car_ahead_speed = std::sqrt(std::pow(car_ahead_vx, 2.0) + std::pow(car_ahead_vy, 2.0));
//
//		double check_car_s_ahead = car_ahead_s + horizont_time * car_ahead_speed;

		if (car_ahead.size() == 0) //No car ahead
				{
			if (car_behind.size() == 0) //No car behind
					{
				resultLane = target_lane;
			} else //A car behind
			{
				double car_behind_s = car_behind[5]; // [ id, x, y, vx, vy, s, d]
				double car_behind_vx = car_behind[3];
				double car_behind_vy = car_behind[4];
				double car_behind_speed = std::sqrt(std::pow(car_behind_vx, 2.0) + std::pow(car_behind_vy, 2.0));

				double check_car_s_behind = car_behind_s + prev_size * horizont_time * car_behind_speed;
				if (ego_car_s - check_car_s_behind >= min_distance_behind)
					resultLane = target_lane;

				////
				// double check_car_s_behind = car_behind.f_pos.s + horizont_time * car_behind.avgSpeed();

				// if (car_state.f_pos.s - check_car_s_behind >= Configuration::MIN_DIST_BEHIND)
				//	resultLane = target_lane;
			}
		} else // A car ahead
		{
			double car_ahead_s = car_ahead[5]; // [ id, x, y, vx, vy, s, d]
			double car_ahead_vx = car_ahead[3];
			double car_ahead_vy = car_ahead[4];
			double car_ahead_speed = std::sqrt(std::pow(car_ahead_vx, 2.0) + std::pow(car_ahead_vy, 2.0));

			double check_car_s_ahead = car_ahead_s + prev_size * horizont_time * car_ahead_speed;

			// double check_car_s_ahead = car_ahead.f_pos.s + horizont_time * car_ahead.avgSpeed();

			if (car_behind.size() == 0) //No car behind
					{
				if (check_car_s_ahead - ego_car_s >= min_distance_ahead)
					resultLane = target_lane;
				//if (check_car_s_ahead - car_state.f_pos.s >= Configuration::MIN_DIST_AHEAD)
				//	resultLane = target_lane;
			} else //A car behind
			{
				double car_behind_s = car_behind[5]; // [ id, x, y, vx, vy, s, d]
				double car_behind_vx = car_behind[3];
				double car_behind_vy = car_behind[4];
				double car_behind_speed = std::sqrt(std::pow(car_behind_vx, 2.0) + std::pow(car_behind_vy, 2.0));

				double check_car_s_behind = car_behind_s + prev_size * horizont_time * car_behind_speed;

				if (check_car_s_ahead - ego_car_s >= min_distance_ahead
						&& ego_car_s - check_car_s_behind >= min_distance_behind)
					resultLane = target_lane;

				//double check_car_s_behind = car_behind.f_pos.s + horizont_time * car_behind.avgSpeed();

				//if (check_car_s_ahead - car_state.f_pos.s >= Configuration::MIN_DIST_AHEAD
				//		&& car_state.f_pos.s - check_car_s_behind >= Configuration::MIN_DIST_BEHIND)
				//	resultLane = target_lane;
			}
		}
	}

	cout << "resultlane: " << resultLane << endl;

	return resultLane;
}

int main() {
	uWS::Hub h;

// Load up map values for waypoint's x,y,s and d normalized normal vectors
	vector<double> map_waypoints_x;
	vector<double> map_waypoints_y;
	vector<double> map_waypoints_s;
	vector<double> map_waypoints_dx;
	vector<double> map_waypoints_dy;

// Waypoint map to read from
	string map_file_ = "../data/highway_map.csv";
// The max s value before wrapping around the track back to 0
	double max_s = 6945.554;

	ifstream in_map_(map_file_.c_str(), ifstream::in);

	string line;
	while (getline(in_map_, line)) {
		istringstream iss(line);
		double x;
		double y;
		float s;
		float d_x;
		float d_y;
		iss >> x;
		iss >> y;
		iss >> s;
		iss >> d_x;
		iss >> d_y;
		map_waypoints_x.push_back(x);
		map_waypoints_y.push_back(y);
		map_waypoints_s.push_back(s);
		map_waypoints_dx.push_back(d_x);
		map_waypoints_dy.push_back(d_y);
	}

// start in lane 1;
	int lane = 1;

// Have a reference velocity to target
	double ref_vel = 0.0; //mph

	h.onMessage(
			[&ref_vel, &lane, &map_waypoints_x,&map_waypoints_y,&map_waypoints_s,&map_waypoints_dx,&map_waypoints_dy](uWS::WebSocket<uWS::SERVER> ws, char *data, size_t length,
					uWS::OpCode opCode) {
				// "42" at the start of the message means there's a websocket message event.
				// The 4 signifies a websocket message
				// The 2 signifies a websocket event
				//auto sdata = string(data).substr(0, length);
				//cout << sdata << endl;
				if (length && length > 2 && data[0] == '4' && data[1] == '2') {

					auto s = hasData(data);

					if (s != "") {
						auto j = json::parse(s);

						string event = j[0].get<string>();

						if (event == "telemetry") {

							// j[1] is the data JSON object

							// Main car's localization Data
							double car_x = j[1]["x"];
							double car_y = j[1]["y"];
							double car_s = j[1]["s"];
							double car_d = j[1]["d"];
							double car_yaw = j[1]["yaw"];
							double car_speed = j[1]["speed"];

							// Previous path data given to the Planner
							auto previous_path_x = j[1]["previous_path_x"];
							auto previous_path_y = j[1]["previous_path_y"];
							// Previous path's end s and d values
							double end_path_s = j[1]["end_path_s"];
							double end_path_d = j[1]["end_path_d"];

							// Sensor Fusion Data, a list of all other cars on the same side of the road.
							auto sensor_fusion = j[1]["sensor_fusion"];

							int prev_size = previous_path_x.size();

							if (prev_size > 0)
							{
								car_s = end_path_s;
							}

							bool too_close = false;
							bool emergency_brake = false;

							// find ref_v to use
							for(int i=0;i<sensor_fusion.size();i++)
							{
								//car is in my lane
								float d = sensor_fusion[i][6];// [ id, x, y, vx, vy, s, d]
								if(d < (2+4*lane+2) && d > (2+4*lane-2))
								{
									double vx = sensor_fusion[i][3];
									double vy = sensor_fusion[i][4];

									double check_speed = sqrt(vx*vx+vy*vy);
									double check_car_s = sensor_fusion[i][5];

									check_car_s += ((double) prev_size*0.02*check_speed); // if using previous points can project s value out
									// check s values greater than mine and s gap
									if ((check_car_s > car_s) && ((check_car_s - car_s) < 30))
									{
										// do some logic here, lower reference velocity so we don't crash into the car infront of us, could
										// also flag to try to change lane.
										// ref_vel = 29.5; //mph
										too_close = true;
//										if(lane > 0)
//										{
//											// lane = 0; // blindly change lane to left lane :) (for now)
//											double ego_car_s = car_s;
//											double ego_car_lane = lane;
//											lane = getOptimalLane(sensor_fusion, ego_car_s, ego_car_lane, prev_size);
//											cout << lane << endl;
//										}
//
										double ego_car_s = car_s;
										double ego_car_lane = lane;
										lane = getLane(sensor_fusion, ego_car_s, ego_car_lane, prev_size);
										cout << lane << endl;
										break;
									}
								}
							}



							if (too_close)
							{
								ref_vel -= .224; // 5m/second square (which is under 10m/sec-sq requirement)
							}
							else if(ref_vel < 49.5)
							{
								ref_vel += .224;
							}

							// create a list of widely spaced (x,y) waypoints, evenly spaced at 30m
							// later we will interpolate these waypoints with a spline and fill it in with more points that control speed
							vector<double> ptsx;
							vector<double> ptsy;

							// reference x,y,yaw states
							// either we will reference the starting point as where the car is or the previous paths end point
							double ref_x = car_x;
							double ref_y = car_y;
							double ref_yaw = deg2rad(car_yaw);

							// if previous size is almost empty, use the car as starting reference
							if(prev_size < 2)
							{
								// use two points that make the path tangent to the car
								double prev_car_x = car_x - cos(car_yaw);
								double prev_car_y = car_y - sin(car_yaw);

								ptsx.push_back(prev_car_x);
								ptsx.push_back(car_x);

								ptsy.push_back(prev_car_y);
								ptsy.push_back(car_y);
							}
							// use the previous path's endpoint as starting reference
							else
							{
								// redefine reference state as previous path endpoint
								ref_x = previous_path_x[prev_size-1];
								ref_y = previous_path_y[prev_size-1];

								double ref_x_prev = previous_path_x[prev_size-2];
								double ref_y_prev = previous_path_y[prev_size-2];

								ref_yaw = atan2(ref_y-ref_y_prev, ref_x-ref_x_prev);

								// use two points that make the path tangent to the previous path's endpoint
								ptsx.push_back(ref_x_prev);
								ptsx.push_back(ref_x);

								ptsy.push_back(ref_y_prev);
								ptsy.push_back(ref_y);
							}

							// In fernet add evenly 30m spaced points ahead of the starting reference
							vector<double> next_wp0 = getXY(car_s+30, (2+4*lane), map_waypoints_s, map_waypoints_x, map_waypoints_y);
							vector<double> next_wp1 = getXY(car_s+60, (2+4*lane), map_waypoints_s, map_waypoints_x, map_waypoints_y);
							vector<double> next_wp2 = getXY(car_s+90, (2+4*lane), map_waypoints_s, map_waypoints_x, map_waypoints_y);

							ptsx.push_back(next_wp0[0]);
							ptsx.push_back(next_wp1[0]);
							ptsx.push_back(next_wp2[0]);

							ptsy.push_back(next_wp0[1]);
							ptsy.push_back(next_wp1[1]);
							ptsy.push_back(next_wp2[1]);

							for(int i=0; i<ptsx.size(); i++)
							{
								//shift car reference angle to 0 degrees
								double shift_x = ptsx[i] - ref_x;
								double shift_y = ptsy[i] - ref_y;

								ptsx[i] = (shift_x * cos(0-ref_yaw) - shift_y*sin(0-ref_yaw));
								ptsy[i] = (shift_x * sin(0-ref_yaw) + shift_y*cos(0-ref_yaw));
							}

							// create a spline
							tk::spline s;

							// set (x,y) points to the spline
							s.set_points(ptsx, ptsy);

							// define the actual (x,y) points we will use for the planner
							vector<double> next_x_vals;
							vector<double> next_y_vals;

							// start with all of the previous path points from last time
							for(int i=0;i<previous_path_x.size();i++)
							{
								next_x_vals.push_back(previous_path_x[i]);
								next_y_vals.push_back(previous_path_y[i]);
							}

							// calculate how to break up spline points so that we travel at our desired reference velocity
							double target_x = 30.0;//meters
							double target_y = s(target_x);
							double target_dist = sqrt((target_x)*(target_x) + (target_y)*(target_y));

							double x_add_on = 0;

							// fill up the rest of our path planner after filling it with previous points, here we will always output 50 points
							for(int i=0;i<=50-previous_path_x.size();i++)
							{
								double N = (target_dist/(0.02*ref_vel/2.24));
								double x_point = x_add_on+(target_x)/N;
								double y_point = s(x_point);

								x_add_on = x_point;

								double x_ref = x_point;
								double y_ref = y_point;

								// rotate back to normal after rotating it earlier
								x_point = (x_ref*cos(ref_yaw) - y_ref*sin(ref_yaw));
								y_point = (x_ref*sin(ref_yaw) + y_ref*cos(ref_yaw));

								x_point += ref_x;
								y_point += ref_y;

								next_x_vals.push_back(x_point);
								next_y_vals.push_back(y_point);
							}

							json msgJson;

							// TODO: define a path made up of (x,y) points that the car will visit sequentially every .02 seconds
							msgJson["next_x"] = next_x_vals;
							msgJson["next_y"] = next_y_vals;

							auto msg = "42[\"control\","+ msgJson.dump()+"]";

							//this_thread::sleep_for(chrono::milliseconds(1000));
							ws.send(msg.data(), msg.length(), uWS::OpCode::TEXT);

						}
					} else {
						// Manual driving
						std::string msg = "42[\"manual\",{}]";
						ws.send(msg.data(), msg.length(), uWS::OpCode::TEXT);
					}
				}
			});

// We don't need this since we're not using HTTP but if it's removed the
// program
// doesn't compile :-(
	h.onHttpRequest([](uWS::HttpResponse *res, uWS::HttpRequest req, char *data,
			size_t, size_t) {
		const std::string s = "<h1>Hello world!</h1>";
		if (req.getUrl().valueLength == 1) {
			res->end(s.data(), s.length());
		} else {
			// i guess this should be done more gracefully?
			res->end(nullptr, 0);
		}
	});

	h.onConnection([&h](uWS::WebSocket<uWS::SERVER> ws, uWS::HttpRequest req) {
		std::cout << "Connected!!!" << std::endl;
	});

	h.onDisconnection([&h](uWS::WebSocket<uWS::SERVER> ws, int code,
			char *message, size_t length) {
		ws.close();
		std::cout << "Disconnected" << std::endl;
	});

	int port = 4567;
	if (h.listen(port)) {
		std::cout << "Listening to port " << port << std::endl;
	} else {
		std::cerr << "Failed to listen to port" << std::endl;
		return -1;
	}
	h.run();
}

