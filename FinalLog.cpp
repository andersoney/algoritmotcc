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

void FinalLog::init(string _patch)
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
        path = _patch;
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
int FinalLog::countLines(const std::string &filename)
{
    std::ifstream file(filename);
    if (!file.is_open())
    {
        std::cerr << "Erro ao abrir o arquivo\n";
        return -1;
    }

    int count = 0;
    std::string line;
    while (std::getline(file, line))
    {
        ++count;
    }
    file.close();
    return count;
}
void FinalLog::saveLog()
{
    // std::ostringstream strs;
    // strs << prob;
    // std::string probStr = strs.str();
    // std::string probStr = std::to_string(prob);
#ifdef USAR_PASTAS
    cout << path << endl;
    logFile.open((path.c_str()));
    logFile << num_robots << endl;
    logFile << numTotalIterationsReachGoal + numTotalIterationsExitGoal << endl;
    logFile << numMaxIterationsReachGoal + numMaxIterationsExitGoal << endl;
    logFile
        << numMsgs << endl;
    logFile << numTotalIterationsReachGoal << endl
            << numTotalIterationsExitGoal << endl;
    logFile << numMaxIterationsReachGoal << endl
            << numMaxIterationsExitGoal << endl;
    logFile << numTotalStalls << endl;
    logFile << reachingTargetTime << endl;
#else
    cout << path << endl;
    if (countLines(path) == 0)
    {
        logFile << "num_robots" << ",";
        logFile << "numTotalIterations" << ",";
        logFile << "numMaxIterationsReachGoal + numMaxIterationsExitGoal" << ",";
        logFile << "numMsgs" << ",";
        logFile << "numTotalIterationsReachGoal" << ","
                << "numTotalIterationsExitGoal" << ",";
        logFile << "numMaxIterationsReachGoal" << ","
                << "numMaxIterationsExitGoal" << ",";
        logFile << "numTotalStalls" << ",";
        logFile << "reachingTargetTime";
    }
    cout << countLines(path) << endl;
    logFile << endl;
    logFile << num_robots << ",";
    logFile << numTotalIterationsReachGoal + numTotalIterationsExitGoal << ",";
    logFile << numMaxIterationsReachGoal + numMaxIterationsExitGoal << ",";
    logFile << numMsgs << ",";
    logFile << numTotalIterationsReachGoal << ","
            << numTotalIterationsExitGoal << ",";
    logFile << numMaxIterationsReachGoal << ","
            << numMaxIterationsExitGoal << ",";
    logFile << numTotalStalls << ",";
    logFile << reachingTargetTime;

#endif
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
