#ifndef FLASHGGFINALFIT_BACKGROUND_ROODYCORE_H
#define FLASHGGFINALFIT_BACKGROUND_ROODYCORE_H

#include "RooAbsReal.h"
#include "RooRealProxy.h"

/**
 * RooDYCore
 * ----------
 * Core LO Drell¨CYan lineshape:
 *   DY(m) = sum_q L_{q qbar}(m) * sigma_{q qbar}(m)
 *
 * Resolution convolution is handled externally (placeholder = 1).
 */
class RooDYCore : public RooAbsReal {
public:
  RooDYCore() {}

  RooDYCore(const char* name, const char* title,
            RooAbsReal& _m);

  RooDYCore(const RooDYCore& other, const char* name = 0);

  virtual TObject* clone(const char* newname) const override {
    return new RooDYCore(*this, newname);
  }

  inline virtual ~RooDYCore() {}

protected:
  // Observable
  RooRealProxy m;   // m_ll (GeV)

  // Core evaluation
  Double_t evaluate() const override;

private:
  ClassDef(RooDYCore, 1)
};

#endif // FLASHGGFINALFIT_BACKGROUND_ROODYCORE_H
