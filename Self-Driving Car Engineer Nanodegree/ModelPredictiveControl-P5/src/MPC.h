#ifndef MPC_H
#define MPC_H

#include <vector>
#include "Eigen-3.3/Eigen/Core"

using namespace std;

// struct to store results of Solve()
struct Output {
	vector<double> x;
	vector<double> y;
	vector<double> delta;
	vector<double> a;
};

class MPC {
public:
	MPC();

	virtual ~MPC();

	// Solve the model given an initial state and polynomial coefficients.
	// Return the first actuatotions.
	Output Solve(Eigen::VectorXd state, Eigen::VectorXd coeffs);
};

#endif /* MPC_H */
