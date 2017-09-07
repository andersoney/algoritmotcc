/*
Commom methods to the class WiseRobots
Normally, these methods are the same in every test.
If happens that some of these methods are changed to
a specific test, it must to be eliminated from here and put on
specific test.

This file matchs with commomMember.cpp

Note: I think that using some type of override, or abstract class can 
solve this. But I don't think that this project will grow so much.
*/

#include "option.hh"

//Initializes values for sensing with laser, depending on the world file used.
void WiseRobot::init_laser()
{
    //init laser configuration for use in getBearing()
    ModelRanger::Sensor sensor = laser->GetSensors()[0];
    LASER_FOV = rtod(sensor.fov);
    LASER_SAMPLES = sensor.sample_count;
    laser->vis.showArea.set(0);
}

//Used for get the angle of some laser beam on respect to the orientation of robot
inline double WiseRobot::getBearing(int i)
{
    return dtor(-LASER_FOV / 2 + (LASER_FOV / (LASER_SAMPLES - 1)) * i);
}

//Compute euclidian distance between two 2D points coordinates
#define distance(x1, y1, x2, y2) hypot((x1) - (x2), (y1) - (y2))

//Initialize robot position data, i.e. angular and linear velocities,
//initial waypoint to search and seed to random number generator
void WiseRobot::init_position_data()
{
    currentWaypoint = 0;
    linSpeed = 0;
    rotSpeed = 0;
    srand(m_id * time(NULL));
}

//Convert a integer to string
string WiseRobot::intToStr(int integer)
{
    ostringstream stringNumero;

    stringNumero << integer;

    return stringNumero.str();
}

//Saturate  a vector to a limit modulo, keeping scale.
void WiseRobot::saturation(double &x, double &y, double limit)
{
    double factor;

    //Saturation (keeping scale between x and y)
    if ((x > limit) || (y > limit))
    {
        if (x > y)
        {
            factor = x / limit;
            x = x / factor;
            y = y / factor;
        }
        else
        {
            factor = y / limit;
            y = y / factor;
            x = x / factor;
        }
    }
    if ((x < -limit) || (y < -limit))
    {
        if (x < y)
        {
            factor = x / -limit;
            x = x / factor;
            y = y / factor;
        }
        else
        {
            factor = y / -limit;
            y = y / factor;
            x = x / factor;
        }
    }
}

//Substract two angle values (in radians). The result value lies between
//-2 PI and 2 PI.
double WiseRobot::angDiff(double end, double begin)
{
    double returnMe = end - begin;

    if (returnMe > PI)
        returnMe = -(2 * PI - returnMe);
    else if (returnMe < -PI)
        returnMe = 2 * PI + returnMe;

    return returnMe;
}

//Function used on Stage simulation. It specifies
//what the robot will do while walking
//See wiseRobot.h for signature
int PositionUpdate(Model *pos, WiseRobot *robot)
{
    robot->walk();
    return 0;
}

//returns the distance between a robot and your goal
double WiseRobot::pho()
{
    return hypot(m_x - destineX, m_y - destineY);
}

// String tokenizer. From http://oopweb.com/CPP/Documents/CPPHOWTO/Volume/C++Programming-HOWTO-7.html
void Tokenize(const string &str,
              vector<string> &tokens,
              const string &delimiters = " ")
{
    // Skip delimiters at beginning.
    string::size_type lastPos = str.find_first_not_of(delimiters, 0);
    // Find first "non-delimiter".
    string::size_type pos = str.find_first_of(delimiters, lastPos);

    while (string::npos != pos || string::npos != lastPos)
    {
        // Found a token, add it to the vector.
        tokens.push_back(str.substr(lastPos, pos - lastPos));
        // Skip delimiters.  Note the "not_of"
        lastPos = str.find_first_not_of(delimiters, pos);
        // Find next "non-delimiter"
        pos = str.find_first_of(delimiters, lastPos);
    }
}
