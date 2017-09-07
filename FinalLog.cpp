#include "FinalLog.h"
#include <stdlib.h>
#include <sstream>

//alocating  statics members
unsigned int FinalLog::num_robots, FinalLog::numFinished;
bool FinalLog::initiated;
ofstream FinalLog::logFile;
unsigned int FinalLog::numTotalIterationsReachGoal; // Total number of iterations
unsigned int FinalLog::numTotalIterationsExitGoal;  // Total number of iterations
unsigned int FinalLog::numMaxIterationsReachGoal;   //Maximum number of iterations to reach the goal
unsigned int FinalLog::numMaxIterationsExitGoal;    //Maximum number of iterations to exit from goal
unsigned int FinalLog::numTotalStalls;              //number of times that the robots stalled
unsigned int FinalLog::numMsgs;                     //number of messages
string FinalLog::path;
double FinalLog::prob;

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
        //prob = p;
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
        //path = p;
    }
    num_robots++;
}

void FinalLog::refresh(unsigned int numIterationsReachGoal,
                       unsigned int numIterationsExitGoal,
                       unsigned int messages,
                       unsigned int numStalls)
{
    numMsgs += messages;
    numTotalStalls += numStalls;
    numTotalIterationsReachGoal += numIterationsReachGoal;
    numTotalIterationsExitGoal += numIterationsExitGoal;
    if (numIterationsReachGoal > numMaxIterationsReachGoal)
        numMaxIterationsReachGoal = numIterationsReachGoal;
    if (numIterationsExitGoal > numMaxIterationsExitGoal)
        numMaxIterationsExitGoal = numIterationsExitGoal;
}

void FinalLog::saveLog()
{
    //std::ostringstream strs;
    //strs << prob;
    //std::string probStr = strs.str();
    //std::string probStr = std::to_string(prob);

    //logFile.open((path.c_str()));
    logFile.open("./logs");
    logFile << numTotalIterationsReachGoal + numTotalIterationsExitGoal << endl;
    logFile << numMaxIterationsReachGoal + numMaxIterationsExitGoal << endl;
    logFile << numMsgs << endl;
    logFile << numTotalIterationsReachGoal << endl
            << numTotalIterationsExitGoal << endl;
    logFile << numMaxIterationsReachGoal << endl
            << numMaxIterationsExitGoal << endl;
    logFile << numTotalStalls << endl;

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

        //kill STAGE pid in file pid.txt
        /*string line,line2;
    bool OK = false;
    ifstream pid((std::string("pid")+probStr+std::string(".txt")).c_str());
    if (pid.is_open())
    {
      if (pid.good()) {
        char line_c[256];
        pid.getline (line_c,256);
        line = line_c;
        //also kill SLEEP pid
        if (pid.good()){
          pid.getline (line_c,256);
          line2 = line_c;
          OK = true;
        }
      }
    }
    pid.close();
    if (OK) {
      string command;
      command = "kill -s TERM ";
      command += line;
      command += ' ';
      command += line2;
      system(command.c_str());
      }*/
    }
}
