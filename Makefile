CXX = g++
CXXFLAGS = -g -Wall `pkg-config --cflags stage`  -fPIC
LINKFLAGS = `pkg-config --libs stage` 

COMMON_DIR = ../common

run: all
	@mkdir -p saida saidas worlds
testar-holo: run
	nohup taskset -c 3-15 bash analise.sh 30 saida_v2_holo holo &

all: coordination.so createScenario

ConfigFile.o: ConfigFile.cpp ConfigFile.h
	$(CXX) -c ConfigFile.cpp -o ConfigFile.o

createScenario: createScenario.cpp ConfigFile.h ConfigFile.o
	$(CXX) ConfigFile.o createScenario.cpp -o createScenario

coordination.so: connectionlocal.o PCCEEV2.o FinalLog.o forcevisualizer.o init.o
	$(CXX) $(CXXFLAGS) $(LINKFLAGS) FinalLog.o connectionlocal.o PCCEEV2.o forcevisualizer.o init.o -o coordination.so -shared

PCCEEV2.o: PCCEEV2.cpp PCCEEV2.h ./commonConfig.h ./commonDefs.h \
./FinalLog.h ./FinalLog.cpp \
./connectionlocal.h ./connectionlocal.cpp
	$(CXX) $(CXXFLAGS) $(LINKFLAGS) -c PCCEEV2.cpp

init.o: init.cpp PCCEEV2.cpp
	$(CXX) $(CXXFLAGS) $(LINKFLAGS) -c init.cpp

forcevisualizer.o: forcevisualizer.cpp forcevisualizer.h ./commonConfig.h \
./commonDefs.h 
	$(CXX) $(CXXFLAGS) $(LINKFLAGS) -c forcevisualizer.cpp

connectionlocal.o: ./connectionlocal.h ./connectionlocal.cpp
	$(CXX) -c -fPIC ./connectionlocal.cpp

FinalLog.o: ./FinalLog.h ./FinalLog.cpp 
	$(CXX) -c -fPIC ./FinalLog.cpp

clean:
	@rm -f *.o *.so  server createScenario  *.world
clean-all: clean
	@rm -rf saida* saidas* worlds nohup 
reset:
	rm -rf nRobos*

kill:
	pkill -f analis
	pkill -f test
	pkill -f stage
