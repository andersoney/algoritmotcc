#include "PCCEEV2.h"
#include <iostream>

using namespace std;
using namespace Stg;

Pool_t pool;

// Pointer to a new robot.
// Every call of this library will create a new robot
// using this pointer.
PCCEEV2 *robot;

int PositionUpdate(Model *pos, PCCEEV2 *robot)
{
    robot->walk();
    return 0;
}

// Function used on Stage simulation. It specifies
// what the robot will do while walking
// See PCCEEV2.h for signature

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

extern "C" int Init(Model *mod, CtrlArgs *args)
{
    robot = new PCCEEV2(&pool);
    vector<string> tokens;
    Tokenize(args->worldfile, tokens);
    robot->pos = (ModelPosition *)mod;
    robot->pos->AddCallback(Model::CB_UPDATE, (model_callback_t)PositionUpdate, robot);
    robot->laser = (ModelRanger *)mod->GetChild("ranger:1");
    robot->theWorld = mod->GetWorld();
    robot->laser->Subscribe(); // starts the laser updates
    robot->pos->Subscribe();   // starts the position updates

    robot->init(atoi(tokens[1].c_str()), atoi(tokens[2].c_str()), atoi(tokens[3].c_str()), atof(tokens[4].c_str()), tokens[5]);
#ifdef DEBUG_FORCES
    robot->pos->AddVisualizer(&robot->fv, true);
#endif
    return 0;
}