#ifndef COMMON_CONFIG
#define COMMON_CONFIG

#define congestionDangerDist  3.5 //distance between goal and robots for obey protocol


const double Ka = 2.5; //constant for robot controller
const double Kr = 3; //constant for robot controller
const double Kl = 1; //constant for robot controller
const double Kdp = 10; // Weight of the damping force
const double waypointDist = 3; //minimum distance to consider that a robot arrive to goal
const double maxForce = 5; //Maximum modulo for resultant force, used on robot controller
const double limit = 0.1; // To avoid a division per zero, the minimum ammount that will be allowed
const double sameWaypointOffset = 0.5; //maximum distance to consider that robots have common goal

const int waypoints[5][2] = { {100,100}, {-999999, 100}, {999999,100}/*, {0,-999999}, {0,999999}*/ };

#endif