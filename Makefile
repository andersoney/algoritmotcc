CXX = g++
CXXFLAGS = -g -Wall `pkg-config --cflags stage`  -fPIC
LINKFLAGS = `pkg-config --libs stage` 

COMMON_DIR = ../common

run: all

all: coordination.so createScenario

createScenario: createScenario.cpp
	$(CXX) createScenario.cpp -o createScenario

coordination.so: connectionlocal.o wiseRobot.o FinalLog.o
	$(CXX) $(CXXFLAGS) $(LINKFLAGS) FinalLog.o connectionlocal.o wiseRobot.o -o coordination.so -shared

wiseRobot.o: wiseRobot.cpp wiseRobot.h ./commonConfig.h \
./commonMethods.cpp ./commonDefs.h \
./FinalLog.h ./FinalLog.cpp \
./connectionlocal.h ./connectionlocal.cpp
	$(CXX) $(CXXFLAGS) $(LINKFLAGS) -c wiseRobot.cpp

connectionlocal.o: ./connectionlocal.h ./connectionlocal.cpp
	$(CXX) -c -fPIC ./connectionlocal.cpp

FinalLog.o: ./FinalLog.h ./FinalLog.cpp 
	$(CXX) -c -fPIC ./FinalLog.cpp

clean:
	@rm -f *.o *.so  server createScenario 
	
reset:
	rm -rf nRobos*

