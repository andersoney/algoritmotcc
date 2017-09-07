#define congestionDangerDist  3.5 //distance between goal and robots for obey protocol
//#define congestionDangerDist  2.5 //distance between goal and robots for obey protocol
#define congestionOkDist  1.5 //minor distance to goal
#define DISTANT_RADIUS 10.0 //maximum radius after that robot reaches goal
#define PROB_CYCLES 40 //number of cycles test changing state probability 
#define MAX_MISSES 30 //number of checks (or cycles) that there is not any robot in front
//Waypoints chosen randomly
const int waypoints[5][2] = { {100,100}, {-999999, 100}, {999999,100}/*, {0,-999999}, {0,999999}*/ };
//const int waypoints[5][2] = { {0,0}, {-999999, 0}, {999999,0}/*, {0,-999999}, {0,999999}*/ };
#define NUMBER_OF_WAYPOINTS 2 //number of waypoints used in all tests
#define Y_MAIS_PROXIMO 0 //Esta variável define se o robô irá para o y da reta mais próximo de sua posição
#define DEAD_ITERATIONS 100000 //Maximum iterations for a experiment
#define CHECK_DEAD_ROBOTS //if enable, consider the above maximum number of iteration
#define MSG_CYCLES 25 //number of cycles to wait until send next message
//#define Ke 0.5   //constant for repulsion forces of WAIT and LOCKED robots
//#define Ki 0.5  //constant for repulsion forces of IMPATIENT and GOING robots
#define Ke 0.5   //constant for repulsion forces of WAIT and LOCKED robots
#define Ki 0.5  //constant for repulsion forces of IMPATIENT and GOING robots
//#define SERVER_FINISH_OUTPUT //if defined, server outputs messages about finished robots
// #define GENERAL_LOG  //if defined, robots output log messages to stout
//#define DEBUG_FORCES //If defined, it allow compilation of force visualization codes

const double Ka = 2.5; //constant for robot controller
const double Kr = 3; //constant for robot controller
const double Kl = 1; //constant for robot controller
const double Kdp = 10; // Weight of the damping force
const double waypointDist = 0.8; //minimum distance to consider that a robot arrive to goal
const double maxForce = 5; //Maximum modulo for resultant force, used on robot controller
const double limit = 0.1; // To avoid a division per zero, the minimum ammount that will be allowed
const double sameWaypointOffset = 0.5; //maximum distance to consider that robots have common goal

//#define MESSAGESLOG //If defined, logs are generated

