#include <fstream>
#include <string>

using namespace std;

class FinalLog{
  private:
    static unsigned int num_robots,numFinished;
    static bool initiated;
    static ofstream logFile;
    static unsigned int numTotalIterationsReachGoal; // Total number of iterations
    static unsigned int numTotalIterationsExitGoal; // Total number of iterations
    static unsigned int numMaxIterationsReachGoal; //Maximum number of iterations to reach the goal
    static unsigned int numMaxIterationsExitGoal; //Maximum number of iterations to exit from goal
    static unsigned int numTotalStalls; //number of times that the robots stalled
    static unsigned int numMsgs; //number of messages

    static void saveLog();    

    static double prob;

    static string path;

  public:
    static void init(string path);

    static void init(double prob);
    
    static void refresh(unsigned int numIterationsReachGoal,
                        unsigned int numIterationsExitGoal,
                        unsigned int messages,
                        unsigned int numStalls);
    
    static void finish();
};
