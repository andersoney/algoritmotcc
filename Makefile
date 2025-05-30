CXX = g++
CXXFLAGS = -g -Wall `pkg-config --cflags stage`  -fPIC
LINKFLAGS = `pkg-config --libs stage -lyaml-cpp` 

COMMON_DIR = ../common

run: all

all: coordination.so createScenario

createScenario: createScenario.cpp
	$(CXX) createScenario.cpp -o createScenario

coordination.so: connectionlocal.o wiseRobot.o FinalLog.o forcevisualizer.o
	$(CXX) $(CXXFLAGS) $(LINKFLAGS) FinalLog.o connectionlocal.o wiseRobot.o forcevisualizer.o -o coordination.so -shared

wiseRobot.o: wiseRobot.cpp wiseRobot.h ./commonConfig.h \
./commonMethods.cpp ./commonDefs.h \
./FinalLog.h ./FinalLog.cpp \
./connectionlocal.h ./connectionlocal.cpp
	$(CXX) $(CXXFLAGS) $(LINKFLAGS) -c wiseRobot.cpp

forcevisualizer.o: forcevisualizer.cpp forcevisualizer.h ./commonConfig.h \
./commonMethods.cpp ./commonDefs.h 
	$(CXX) $(CXXFLAGS) $(LINKFLAGS) -c forcevisualizer.cpp

connectionlocal.o: ./connectionlocal.h ./connectionlocal.cpp
	$(CXX) -c -fPIC ./connectionlocal.cpp

FinalLog.o: ./FinalLog.h ./FinalLog.cpp 
	$(CXX) -c -fPIC ./FinalLog.cpp

clean:
	@rm -f *.o *.so  server createScenario  *.world
	
reset:
	rm -rf nRobos*

