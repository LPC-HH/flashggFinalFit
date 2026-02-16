LIBNAME = DYCore

CXX = g++
LD  = g++

UNAME := $(shell uname)
BASEDIR = $(shell pwd)

# include path
USERINCLUDES += -I$(ROOTSYS)/include
USERINCLUDES += -I$(CMSSW_BASE)/src
USERINCLUDES += -I$(CMSSW_RELEASE_BASE)/src

# libraries
USERLIBS += $(shell root-config --glibs)
USERLIBS += -lRooFit -lRooFitCore -lRooStats

CXXFLAGS = -Wall -g -fPIC -std=c++17 $(USERINCLUDES)
LDFLAGS  = -shared

SRCS = $(wildcard src/*.cc)
OBJS = $(patsubst src/%.cc,obj/%.o,$(SRCS))

ROOT_DICT = RootDict.cxx
ROOT_OBJ  = obj/RootDict.o
HEADERS   = $(wildcard interface/*.h)

all: lib/lib$(LIBNAME).so

obj/%.o: src/%.cc
	mkdir -p obj
	$(CXX) $(CXXFLAGS) -c $< -o $@

$(ROOT_DICT): $(HEADERS)
	rootcling -f $@ -c $(HEADERS)

$(ROOT_OBJ): $(ROOT_DICT)
	$(CXX) $(CXXFLAGS) -c $< -o $@

lib/lib$(LIBNAME).so: $(OBJS) $(ROOT_OBJ)
	mkdir -p lib
	$(LD) $(LDFLAGS) -o $@ $^ $(USERLIBS)

clean:
	rm -rf obj lib RootDict.cxx
