/*
 * particle_filter.cpp
 *
 *  Created on: Dec 12, 2016
 *      Author: Tiffany Huang
 */

#include "particle_filter.h"

#include <math.h>
#include <algorithm>
#include <iostream>
#include <iterator>
#include <numeric>
#include <random>
#include <sstream>
#include <string>

using namespace std;

void ParticleFilter::init(double x, double y, double theta, double std[]) {
	// TODO: Set the number of particles. Initialize all particles to first position (based on estimates of
	//   x, y, theta and their uncertainties from GPS) and all weights to 1.
	// Add random Gaussian noise to each particle.
	// NOTE: Consult particle_filter.h for more information about this method (and others in this file).

	// random number engine class that generates pseudo-random numbers.
	default_random_engine random_num_engine;

	num_particles = 50;

	// Initialize normal distributions for sensor noise
	normal_distribution<double> normal_dist_x_init(x, std[0]);
	normal_distribution<double> normal_dist_y_init(y, std[1]);
	normal_distribution<double> normal_dist_theta_init(theta, std[2]);

	// Initialize particles with random normal dist
	for (int i = 0; i < num_particles; ++i) {
		Particle p = { i, normal_dist_x_init(random_num_engine), normal_dist_y_init(random_num_engine),
				normal_dist_theta_init(random_num_engine), 1.0 };
		particles.push_back(p);
	}

	// resize weights vector
	weights.resize(num_particles);
	is_initialized = true;
}

void ParticleFilter::prediction(double delta_t, double std_pos[], double velocity, double yaw_rate) {
	// TODO: Add measurements to each particle and add random Gaussian noise.
	// NOTE: When adding noise you may find std::normal_distribution and std::default_random_engine useful.
	//  http://en.cppreference.com/w/cpp/numeric/random/normal_distribution
	//  http://www.cplusplus.com/reference/random/default_random_engine/

	// random number engine class that generates pseudo-random numbers.
	default_random_engine random_num_engine;

	// for every particle
	for (int i = 0; i < num_particles; ++i) {

		Particle &particle = particles[i];

		// make predictions of x,y,theta

		// avoid division by 0
		if (fabs(yaw_rate) > 0.001) {
			particle.x = particle.x
					+ (velocity / yaw_rate) * (sin(particle.theta + yaw_rate * delta_t) - sin(particle.theta));
			particle.y = particle.y
					+ (velocity / yaw_rate) * (cos(particle.theta) - cos(particle.theta + yaw_rate * delta_t));
			particle.theta = particle.theta + delta_t * yaw_rate;

		} else {
			particle.x = particle.x + velocity * delta_t * cos(particle.theta);
			particle.y = particle.y + velocity * delta_t * sin(particle.theta);
		}

		normal_distribution<double> normal_dist_x(particle.x, std_pos[0]);
		normal_distribution<double> normal_dist_y(particle.y, std_pos[1]);
		normal_distribution<double> normal_dist_theta(particle.theta, std_pos[2]);

		// update predicted x,y,theta
		particle.x = normal_dist_x(random_num_engine);
		particle.y = normal_dist_y(random_num_engine);
		particle.theta = normal_dist_theta(random_num_engine);
	}
}

void ParticleFilter::dataAssociation(std::vector<LandmarkObs> predicted, std::vector<LandmarkObs>& observations) {
	// TODO: Find the predicted measurement that is closest to each observed measurement and assign the
	//   observed measurement to this particular landmark.
	// NOTE: this method will NOT be called by the grading code. But you will probably find it useful to
	//   implement this method and use it as a helper during the updateWeights phase.

	double distThreshold = 999999;

	// for every observation
	for (int i = 0; i < observations.size(); i++) {

		// for every prediciton
		for (int j = 0; j < predicted.size(); j++) {

			LandmarkObs obs = observations[i];
			LandmarkObs pred = predicted[j];

			// calc distance
			double distance = dist(obs.x, obs.y, pred.x, pred.y);
			if (distance < distThreshold) {
				distThreshold = distance;
				observations[i].id = j;
			}
		}
	}
}

void ParticleFilter::updateWeights(double sensor_range, double std_landmark[], std::vector<LandmarkObs> observations,
		Map map_landmarks) {
	// TODO: Update the weights of each particle using a mult-variate Gaussian distribution. You can read
	//   more about this distribution here: https://en.wikipedia.org/wiki/Multivariate_normal_distribution
	// NOTE: The observations are given in the VEHICLE'S coordinate system. Your particles are located
	//   according to the MAP'S coordinate system. You will need to transform between the two systems.
	//   Keep in mind that this transformation requires both rotation AND translation (but no scaling).
	//   The following is a good resource for the theory:
	//   https://www.willamette.edu/~gorr/classes/GeneralGraphics/Transforms/transforms2d.htm
	//   and the following is a good resource for the actual equation to implement (look at equation
	//   3.33
	//   http://planning.cs.uiuc.edu/node99.html

	// for every particle
	for (int i = 0; i < num_particles; ++i) {

		Particle particle = particles[i];
		double weight = 1.0;

		// for every observation
		for (int j = 0; j < observations.size(); j++) {
			double obs_x = particle.x + observations[j].x * cos(particle.theta)
					- observations[j].y * sin(particle.theta);
			double obs_y = particle.y + observations[j].x * sin(particle.theta)
					+ observations[j].y * cos(particle.theta);

			Map::single_landmark_s nearest_lm = { 0, 0.0, 0.0 };
			double mindist_obs2lm = sensor_range;

			// consider every landmark
			for (int k = 0; k < map_landmarks.landmark_list.size(); k++) {
				double dist_part2lm = dist(particle.x, particle.y, map_landmarks.landmark_list[k].x_f,
						map_landmarks.landmark_list[k].y_f);
				if (dist_part2lm <= sensor_range) {
					double dist_obs2lm = dist(obs_x, obs_y, map_landmarks.landmark_list[k].x_f,
							map_landmarks.landmark_list[k].y_f);
					if (dist_obs2lm < mindist_obs2lm) {
						mindist_obs2lm = dist_obs2lm;
						nearest_lm = map_landmarks.landmark_list[k];
					}
				}
			}

			double std_lm_x = std_landmark[0];
			double std_lm_y = std_landmark[1];
			double delta_x = nearest_lm.x_f - obs_x;
			double delta_y = nearest_lm.y_f - obs_y;

			// calc wt for this obs using multivariate Gaussian
			double obs_w = exp(-0.5 * ((pow(delta_x, 2) / pow(std_lm_x, 2)) + (pow(delta_y, 2) / pow(std_lm_y, 2))))
					/ (2 * M_PI * std_lm_x * std_lm_y);

			weight = weight * obs_w;
		}

		particles[i].weight = weight;
		weights[i] = weight;
	}

	// update weights
	double accu_wts = accumulate(weights.begin(), weights.end(), 0.0);
	for (int i = 0; i < num_particles; ++i) {
		particles[i].weight = particles[i].weight / accu_wts;
		weights[i] = particles[i].weight;
	}
}

void ParticleFilter::resample() {
	// TODO: Resample particles with replacement with probability proportional to their weight.
	// NOTE: You may find std::discrete_distribution helpful here.
	//   http://en.cppreference.com/w/cpp/numeric/random/discrete_distribution

	// resampled particles
	vector<Particle> new_particles;

	// random number engine class that generates pseudo-random numbers.
	default_random_engine random_num_engine;

	// std::discrete_distribution produces random integers on the interval [0, n),
	// where the probability of each individual integer i is defined as wi/S, that is
	// the weight of the ith integer divided by the sum of all n weights.
	discrete_distribution<> discrete_dist(weights.begin(), weights.end());

	for (int i = 0; i < num_particles; ++i) {
		int new_particle_index = discrete_dist(random_num_engine);
		Particle new_particle = particles[new_particle_index];
		new_particles.push_back(new_particle);
	}

	particles = new_particles;
}

Particle ParticleFilter::SetAssociations(Particle particle, std::vector<int> associations, std::vector<double> sense_x,
		std::vector<double> sense_y) {
	//particle: the particle to assign each listed association, and association's (x,y) world coordinates mapping to
	// associations: The landmark id that goes along with each listed association
	// sense_x: the associations x mapping already converted to world coordinates
	// sense_y: the associations y mapping already converted to world coordinates

	//Clear the previous associations
	particle.associations.clear();
	particle.sense_x.clear();
	particle.sense_y.clear();

	particle.associations = associations;
	particle.sense_x = sense_x;
	particle.sense_y = sense_y;

	return particle;
}

string ParticleFilter::getAssociations(Particle best) {
	vector<int> v = best.associations;
	stringstream ss;
	copy(v.begin(), v.end(), ostream_iterator<int>(ss, " "));
	string s = ss.str();
	s = s.substr(0, s.length() - 1);  // get rid of the trailing space
	return s;
}
string ParticleFilter::getSenseX(Particle best) {
	vector<double> v = best.sense_x;
	stringstream ss;
	copy(v.begin(), v.end(), ostream_iterator<float>(ss, " "));
	string s = ss.str();
	s = s.substr(0, s.length() - 1);  // get rid of the trailing space
	return s;
}
string ParticleFilter::getSenseY(Particle best) {
	vector<double> v = best.sense_y;
	stringstream ss;
	copy(v.begin(), v.end(), ostream_iterator<float>(ss, " "));
	string s = ss.str();
	s = s.substr(0, s.length() - 1);  // get rid of the trailing space
	return s;
}
