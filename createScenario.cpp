/*
  Creates automatically scenarios for stage.
  This program generates random positions near the goal (X=0,Y=0)
  for a specified number of robots.

  Also it allows specifies the probability to a robot change from WAIT state to IMPATIENT state.
*/

#include <iostream>
#include <fstream>
#include <vector>
#include <cstdlib>
#include <math.h>
#include <string.h>
#include "commonConfig.h"
#include <iostream>
#include <sys/stat.h>
#include <sys/types.h>
#include <errno.h>
#include <stdio.h>
#include "ConfigFile.h"

using namespace std;

#define PI M_PI

typedef struct coord
{
   double x;
   double y;
   double theta;
} coord;

bool intersect(coord newCoord, vector<coord> &history, double mindist)
{
   for (unsigned int i = 0; i < history.size(); i++)
   {
      if (sqrt(pow(newCoord.x - history.at(i).x, 2) + pow(newCoord.y - history.at(i).y, 2)) < mindist)
         return true;
   }
   return false;
}

void rand(coord &newCoord, vector<coord> &history, double minRadius, double maxRadius, double mindist)
{
   double r;
   double pho;
   double theta;

   while (true)
   {
      r = ((double)rand() / ((double)(RAND_MAX) + (double)(1)));
      pho = minRadius + r * (maxRadius - minRadius);
      r = ((double)rand() / ((double)(RAND_MAX) + (double)(1)));
      theta = 0 + r * 2 * PI;

      newCoord.x = pho * cos(theta);
      newCoord.y = pho * sin(theta);
      newCoord.theta = atan2(0 - newCoord.y, 0 - newCoord.x);

      newCoord.x = waypoints[0][0] + newCoord.x;
      newCoord.y = waypoints[0][1] + newCoord.y;

      if (!intersect(newCoord, history, mindist))
         break;
   }
}
void outPutDefine(std::ofstream &out, int numRobots, int numExp)
{
   std::string s = "saidas/nRobots";
   s += std::to_string(numRobots);
   int status = mkdir(s.c_str(), 0755);
   if (status == 0)
   {
      printf("Pasta criada: %s\n", "saidas");
   }
   else if (errno == EEXIST)
   {
      printf("Pasta já existe: %s\n", "saidas");
   }
   else
   {
      perror("Erro ao criar pasta");
   }
   out.open("saidas/saida_" + std::to_string(numRobots) + "_" + std::to_string(numExp) + ".log");
   if (!out.is_open())
   {
      exit(15);
   }
   else
   {
   }
   cout << "Finalizando outputDefine" << endl;
   cout.rdbuf(out.rdbuf());
   cout << "Finalizando outputDefine" << endl;
}

double calcularRaio(int N, double d)
{
   const double densidade = 1.5; // Constante de empacotamento hexagonal aproximada
   return d * std::sqrt(N / densidade);
}

int main(int argc, char **argv)
{
   cout << "Criando cenário" << endl;
   std::ofstream out;
   double D;
   vector<coord> history;
   coord tmp;

   cout << "argumentos: " << argc << endl;
   if (argc < 3)
   {
      cerr << "Invalid parameters" << endl;
      cerr << "Use: " << endl;
      cerr << "createScenario <file> <numRobots> <num_exp> [video] <aditional_params>" << endl;
      exit(1);
   }
   ConfigFile cf("config.ini");
   try
   {
      D = atof(cf.valueOf("D").c_str());
   }
   catch (string str)
   {
      cerr << endl
           << "Configuration file is incorret: " << str << endl;
      exit(1);
   }

   int numExp = atoi(argv[3]);

   cout << "Startando definicoes basicas." << endl;

   int numRobots = atoi(argv[2]);
   double raio = calcularRaio(numRobots, 1.5);
   cout <<"Raio: " <<raio << endl;
   // outPutDefine(out, numRobots, numExp);
   cout << "Number exp: " << numExp << endl;
   cout << "Number Robot: " << numRobots << endl;
   int numRobot = 0;

   srand(time(NULL));
   ofstream output((string(argv[1]) + ".world").c_str());

   output << "# defines 'map' object used for floorplans" << endl
          << "include \"map.inc\"" << endl
          << endl

          << "# defines sick laser" << endl
          << "include \"sick.inc\"" << endl
          << endl
          << "# defines Pioneer-like robots" << endl
          << "include \"pioneer.inc\"" << endl
          << endl
          << "# set the resolution of the underlying raytrace model in meters" << endl
          << "resolution 0.1" << endl
          << "" << endl
          << "speedup -1" << endl
          << "" << endl
          << "# configure the GUI window" << endl
          << "window" << endl
          << "( " << endl
          << "  size [ 591.000 638.000 ] " << endl
          << "  center [ " << waypoints[0][0] << " " << waypoints[0][1] << " ] " << endl
          << "  show_data 1" << endl;

   if (argc >= 5)
   {
      if (strcmp(argv[4], "video") == 0)
      {
         output << "  screenshots 1" << endl;
      }
   }

   output << ")" << endl
          << "define robot pioneer2dx" << endl
          << "(" << endl
          << "sicklaser ()" << endl
          << "size [0.44 0.44 0.44]" << endl
          << "localization \"gps\"" << endl
          << "localization_origin [ 0 0 0 0 ]" << endl
          << ")" << endl
          << endl;

   for (int i = 0; i < numRobots; i++)
   {
      // cout << "Criando robô: " << i << endl;
      rand(tmp, history, D, D + 8., 1);

      history.push_back(tmp);

      output << "robot" << endl
             << "(" << endl
             << "  name \"robot" << numRobot << "\"" << endl
             << "  color \"red\"" << endl
             << "  pose [" << tmp.x << " " << tmp.y << " 0 " << (180 / 3.1416) * tmp.theta << "]" << endl
             << "  ctrl \"coordination.so " << i << " " << numRobots << " " << numExp << " " << raio << "\"" << endl
             << ")" << endl
             << endl;

      numRobot++;
   }

   output.close();
}
