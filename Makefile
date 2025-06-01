CXX = g++
CXXFLAGS = -g -Wall `pkg-config --cflags stage`  -fPIC
LINKFLAGS = `pkg-config --libs stage` 

COMMON_DIR = ../common

run: all
	@mkdir -p saida saidas worlds

all: coordination.so createScenario

ConfigFile.o: ConfigFile.cpp ConfigFile.h
	$(CXX) -c ConfigFile.cpp -o ConfigFile.o

createScenario: createScenario.cpp ConfigFile.h ConfigFile.o
	$(CXX) ConfigFile.o createScenario.cpp -o createScenario

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
clean-all: clean
	@rm -rf saida saidas worlds
reset:
	rm -rf nRobos*

