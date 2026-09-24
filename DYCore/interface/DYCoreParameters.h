#ifndef FLASHGGFINALFIT_DYCORE_PARAMETERS_H
#define FLASHGGFINALFIT_DYCORE_PARAMETERS_H

#include <string>
#include <vector>

struct DYExpParameters {
    double theta;
    double a1;
    double b1;
    double c1;
    double a2;
};

struct DYPowParameters {
    double frac;
    double a1;
    double b1;
    double c1;
    double a2;
};

DYExpParameters loadDYExpParameters(const std::string& cat);
DYPowParameters loadDYPowParameters(const std::string& cat);

#endif
