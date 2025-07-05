#include "FinalLog.h"
#include <stdlib.h>
#include <sstream>

// alocating  statics members
unsigned int FinalLog::num_robots, FinalLog::numFinished;
bool FinalLog::initiated;
ofstream FinalLog::logFile;
unsigned int FinalLog::numTotalIterationsReachGoal; // Total number of iterations
unsigned int FinalLog::numTotalIterationsExitGoal;  // Total number of iterations
unsigned int FinalLog::numMaxIterationsReachGoal;   // Maximum number of iterations to reach the goal
unsigned int FinalLog::numMaxIterationsExitGoal;    // Maximum number of iterations to exit from goal
unsigned int FinalLog::numTotalStalls;              // number of times that the robots stalled
FinalLog *FinalLog::INSTANCE;                       // number of messages
unsigned int FinalLog::numMsgs;                     // number of messages
unsigned long int FinalLog::reachingTargetTime;     // number of messages
string FinalLog::path;
double FinalLog::prob;

using namespace std;

void FinalLog::init(string p)
{
    if (!initiated)
    {
        numTotalIterationsReachGoal = 0;
        numTotalIterationsExitGoal = 0;
        numMaxIterationsReachGoal = 0;
        numMaxIterationsExitGoal = 0;
        numMsgs = 0;
        numTotalStalls = 0;
        initiated = true;
        numFinished = 0;
        num_robots = 0;
        // prob = p;
        // reachingTargetTime=15;
        path = p;
    }
    num_robots++;
}

void FinalLog::init(double p)
{
    if (!initiated)
    {
        numTotalIterationsReachGoal = 0;
        numTotalIterationsExitGoal = 0;
        numMaxIterationsReachGoal = 0;
        numMaxIterationsExitGoal = 0;
        numMsgs = 0;
        numTotalStalls = 0;
        initiated = true;
        numFinished = 0;
        num_robots = 0;
        prob = p;
        // path = p;
    }
    num_robots++;
}

void FinalLog::refresh(unsigned int numIterationsReachGoal,
                       unsigned int numIterationsExitGoal,
                       unsigned int messages,
                       unsigned int numStalls,
                       unsigned long reachingTargetTime2)
{
    numMsgs += messages;
    numTotalStalls += numStalls;
    numTotalIterationsReachGoal += numIterationsReachGoal;
    numTotalIterationsExitGoal += numIterationsExitGoal;
    reachingTargetTime = reachingTargetTime2;

    if (numIterationsReachGoal > numMaxIterationsReachGoal)
        numMaxIterationsReachGoal = numIterationsReachGoal;
    if (numIterationsExitGoal > numMaxIterationsExitGoal)
        numMaxIterationsExitGoal = numIterationsExitGoal;
}

void FinalLog::saveLog()
{
    // std::ostringstream strs;
    // strs << prob;
    // std::string probStr = strs.str();
    // std::string probStr = std::to_string(prob);
    cout << path << endl;
    logFile.open((path.c_str()));
    // logFile.open(path);
    logFile << numTotalIterationsReachGoal + numTotalIterationsExitGoal << endl;
    logFile << numMaxIterationsReachGoal + numMaxIterationsExitGoal << endl;
    logFile << numMsgs << endl;
    logFile << numTotalIterationsReachGoal << endl
            << numTotalIterationsExitGoal << endl;
    logFile << numMaxIterationsReachGoal << endl
            << numMaxIterationsExitGoal << endl;
    logFile << numTotalStalls << endl;
    logFile << "simTime" << reachingTargetTime << endl;

    logFile.close();
}

void FinalLog::finish()
{
    numFinished++;
    if (numFinished == num_robots)
    {
        std::ostringstream strs;
        strs << prob;
        std::string probStr = strs.str();

        saveLog();

        exit(0);
    }
}
