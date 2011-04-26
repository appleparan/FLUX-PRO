# -*- coding: utf-8 -*-
import numpy as np
from scipy.optimize import fmin as spfmin
from scipy.special  import betainc as spbetainc, \
                           betaln as spbetaln

import FLUXPRO_Common as Common



def unit_test_matlab_sort():
    a = [0.0362222222222215, \
        float('NaN'), \
        float('NaN'), \
        0.0844222222222219, \
        0.238877777777778, \
        -0.0548555555555557, \
        float('NaN'), \
        float('NaN'), \
        float('NaN'), \
        float('NaN')
        ]
    sortedone, key = Common.matlab_sort(a)
    print a, sortedone, key
    return 0


def unit_test_matlab_median():
    a = [0.1, 0.2, 0.3, 0.4, float('nan')]
    print Common.matlab_median(a)


def unit_test_RECO():
    beta_0 = [2, 200]
    TC = [1, 2, 3, 4, 5]
    PV = [5, 4, 3, 2, 1]
    print Common.reco_without_E0(beta_0, TC, PV)


def unit_test_reco_const_E0():
    beta_0 = [2, 200]
    TC = [1, 2, 3, 4, 5]
    PV = [5, 4, 3, 2, 1]
    E0 = 10
    print Common.reco_const_E0(beta_0, TC, PV, E0)


def unit_test_reco_array_E0():
    beta_0 = [2, 200]
    TC = [1, 2, 3, 4, 5]
    PV = [5, 4, 3, 2, 1]
    E0 = [1, 2, 3, 4, 5]
    print Common.reco_array_E0(beta_0, TC, PV, E0)


def unit_test_fmin():
    beta0 = [2.0, 200.0]
    TC = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    PV = np.array([5.0, 4.0, 3.0, 2.0, 1.0])
    print TC.shape
    A = TC.shape
    print A[:]
    betafit = spfmin(Common.reco_without_E0, beta0, (TC, PV))
    print betafit

#def unit_test_erfc():
#   print erfc(1)

    
def unit_test_basic():
    print spbetaln(10, 20)
    print spbetainc(0.5, 10, 3)
    print spbetainc(0.5, 10, 3)
    print spbetainc(10, 3, 0.5)
    print Common.spbtdtri(2,3,0.3)
    print Common.fq(0.3, 2, 3)
    print Common.tq(0.3, 10)

    
unit_test_matlab_sort()
unit_test_matlab_median()
unit_test_RECO()
unit_test_reco_const_E0()
unit_test_reco_array_E0()
unit_test_fmin()
#unit_test_erfc()
unit_test_basic()
