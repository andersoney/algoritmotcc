#ifndef COMMON_DEF
#define COMMON_DEF

#define PI 3.1416
#define TIME_STEP 0.01 // "Speed" of execution

//Define the codes to each state of prob. finite state machine
//States
//#define GOING       0
#define ENTRANDO        0
#define SAINDO          1
//define the colors used in simulation
//Colors                        R G B
#define GOING_COLOR       Color(1,0,0)
#define WAIT_COLOR        Color(0,1,0)
#define I_DONT_CARE_COLOR Color(0,0,1)
#define WAIT_A_LOT_COLOR  Color(0,1,1)
#define GOING_OUT_COLOR   Color(1,0.7,0)
#define ID_1_COLOR        Color(0,255,0)
#define END_COLOR         Color(0,0,0)

//Msg types
#define WATCH_OUT 0.0
#define STOP 1.0
#define I_DONT_CARE_MSG 2.0

//Size of the msg sended among robots
#define SIZE_MSG 6
#define mudancas
#define INFLUENCE 15 // Normal radius of influence of the obstacles
#define CONSTANTE 11
#define CONSTANTE_R 1
//#define m2

// #define SECURITY_DIST_ENTRANDO 1.8
// #define SECURITY_DIST_SAINDO 1.2
//Compute euclidian distance between two 2D points coordinates
#define distance(x1, y1, x2, y2) hypot((x1) - (x2), (y1) - (y2))

//#define congestionDangerDist  2.5 //distance between goal and robots for obey protocol
#define congestionOkDist  1.5 //minor distance to goal
#define DISTANT_RADIUS 10.0 //maximum radius after that robot reaches goal
#define PROB_CYCLES 40 //number of cycles test changing state probability 
#define MAX_MISSES 30 //number of checks (or cycles) that there is not any robot in front
//Waypoints chosen randomly
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
#define DEBUG_FORCES //If defined, it allow compilation of force visualization codes
// #define SHOW_REPULSIVE 
// #define SHOW_TARGET_REPULSIVE 
#define SHOW_NORMAL_OUTPUT_FORCE 
// #define SHOW_ATTRACTIVE
// #define SHOW_RESULTANT
// #define SHOW_LINE_REPULSIVE

//#define MESSAGESLOG //If defined, logs are generated

#endif