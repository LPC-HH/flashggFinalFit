#include "../interface/RooDYSplineCore.h"
#include "TFile.h"
#include <iostream>
#include <cstdlib>
#include <stdexcept>
#include <string>
#include "TSystem.h"

// ===== ���캯�������ٶ��ļ���=====
RooDYSplineCore::RooDYSplineCore(const char* name,
                                 const char* title,
                                 RooAbsReal& _m) :
  RooAbsPdf(name,title),
  m("m","m",this,_m)
{}

// ===== copy ctor =====
RooDYSplineCore::RooDYSplineCore(const RooDYSplineCore& other,
                                 const char* name) :
  RooAbsPdf(other,name),
  m("m",this,other.m)
{}

// ===== evaluate��lazy load spline��=====
Double_t RooDYSplineCore::evaluate() const {

  // ---- ��̬���棨��������ֻ����һ�Σ�----
  static TSpline3* cached = nullptr;

  if (!cached) {

    const char* cmssw_base = std::getenv("CMSSW_BASE");
    if (!cmssw_base) {
      throw std::runtime_error("CMSSW_BASE is not set.");
    }

    std::string filename = std::string(cmssw_base) + "/src/flashggFinalFit/Background/DYshapes/fewz_spline.root";

    // �����þ���·��������Ҫ��
    //const char* filename =c"/uscms/home/esledge/nobackup/fits-hmm/CMSSW_14_1_0_pre4/src/flashggFinalFit/Background/DYshapes/fewz_spline.root";

    const char* splinename = "fewz_spline_smear";

    TFile *f = TFile::Open(filename.c_str());

    if (!f || f->IsZombie()) {
      std::cerr << "[ERROR] Cannot open spline file: " << filename << std::endl;
      return 1e-12;
    }

    TSpline3* tmp = (TSpline3*)f->Get(splinename);

    if (!tmp) {
      std::cerr << "[ERROR] Cannot find spline: " << splinename << std::endl;
      f->Close();
      return 1e-12;
    }

    cached = (TSpline3*)tmp->Clone();
    cached->SetName("cached_fewz_spline");

    f->Close();

    std::cout << "[INFO] FEWZ spline loaded (lazy)" << std::endl;
  }

  // ---- ���� evaluate ----
  double mass = m;

  double xmin = cached->GetXmin();
  double xmax = cached->GetXmax();

  if (mass < xmin || mass > xmax)
    return 1e-12;

  double val = cached->Eval(mass);

  return val > 0 ? val : 1e-12;
}

#include "TClass.h"
ClassImp(RooDYSplineCore)