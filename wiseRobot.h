/*
  This file implements a robot without coordination.
  The robot moves to the target using potential field and repels from another robot
  using this method.
*/

#include <stage.hh>
#include <iostream>
#include <fstream>
#include <sstream>
#include "connectionlocal.h"
#include "commonDefs.h"
#include "commonConfig.h"

using namespace std;
using namespace Stg;

#define PI 3.1416
#define TIME_STEP 0.01 // "Speed" of execution

//#define GENERAL_LOG

/*Implements a robot without coordination*/
class WiseRobot
{
  public:
	//Initialize all robot data (pose, connection, velocity, etc.)
	void init(int id);

	//Finish robot, freeing some variables and closing files
	void finish();

	//Implements the main loop of robot.
	//Also contain robot controller and
	//probabilistic finite state machine codes
	//Constructor. pool is the message pool to send and receive msgs
	WiseRobot(Pool_t *pool);

	void walk();

	//Pointers to classes used in Stage
	ModelPosition *pos;
	ModelRanger *laser;
//This member allows visualize forces for debug
#ifdef DEBUG_FORCES
	ForceVisualizer fv;
#endif
  private:
	//Variavel para o gerenciamento dos estados que serão 2, entrando e saindo.
	int estado;

	//Initialize robot position data, i.e. angular and linear velocities,
	//initial waypoint to search and seed to random number generator
	void init_position_data();

	//Convert a integer to string
	string intToStr(int integer);

	//Saturate a vector to a limit modulo, keeping scale.
	void saturation(double &x, double &y, double limit);

	//Substract two angle values (in radians). The result value lies between
	//-2 PI and 2 PI.
	double angDiff(double end, double begin);

	//returns the distance between a robot and your goal
	double pho();
	//Initializes values for sensing with laser, depending on the world file used.
	void init_laser();
	//Used for get the angle of some laser beam on respect to the orientation of robot
	double getBearing(int i);

	//The name of a robot, used in some functions of Player/Stage
	string m_name;

	//Actual x coordinate of robot position
	double m_x;

	//Actual y coordinate of robot position
	double m_y;

	//Actual theta orientation of robot
	double m_th;

	//Identifier of the robot. Used in communication and for generate the name of robot
	int m_id;

	//Class that encapsulates informations about message sending and other stuffs to send and receive messages
	ConnectionLocal connection;

	//Actual number of iterations.
	int numIterations;

	//number of iterations until reach the goal. The number of iterations from
	//reach the goal until exit a specified area from goal will be the difference
	//between this value and numIterations
	int numIterationsReachGoal;

	//x coordinate to the goal position
	double destineX;

	//y coordinate to the goal position
	double destineY;

	//Indicates if the robot finishes your execution
	bool finished;

	/***** a partir daqui, estas variáveis foram adicionadas para simulacao no Stage ******/

	//index of the current waypoint that this robot search
	//See commomConfigs.h for know these values
	int currentWaypoint;

	//linear velocity of the robot
	double linSpeed;

	//rotation velocity of the robot
	double rotSpeed;

	//FOV and SAMPLES for laser. These values are token from Stage world file, and computed in init_laser()
	double LASER_FOV, LASER_SAMPLES;

	//Boolean for check is robot is already stalled (duh!)
	bool alreadyStalled;

	//Number of times that robot became stalled
	int stalls;

	//Alter the values of fx and fy, adding repulsion force.
	void obstaclesRepulsionForces(double &fx, double &fy);

#ifdef GENERAL_LOG
	ofstream log;
#endif
};

//Function used on Stage simulation. It specifies
//what the robot will do while walking
//See commonMethods.cpp for implementation in the folder common
int PositionUpdate(Model *pos, WiseRobot *robot);
