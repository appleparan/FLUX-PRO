# -*- coding: utf-8 -*-
from math import *

from numpy import zeros, ones, array, sign, nonzero, median
from numpy import sort, argsort
from numpy import std

from scipy import matrix as spmatrix
from scipy.optimize import fmin as spfmin
from scipy.special 	import 	btdtri as spbtdtri, \
							betainc as spbetainc, \
							betaln as spbetaln
def Reco(beta, TC, PV):
	"""
	Reco Function\n
	Returns SSE
	"""
	A=beta[0]
	B=beta[1]
	Err = zeros(len(TC))
	PVPred = zeros(len(TC))
	if(len(TC) == len(PV)):
		for i in range(len(TC)):

			PVPred[i] = A * exp( B * (1 / (10 + 46.02)-1 / (TC[i] + 46.02)))
			Err[i] = PVPred[i] - PV[i]

		SSE=Err*spmatrix(Err).conj().transpose()
		return SSE
	else:
		print ' length Errorlength(A), length(B)'
		print len(TC),len(PV)

def Reco2(beta,TC,PV,E0):
	"""
	Reco2 Function\n
	Returns SSE
	"""
	A=beta[0]
	Err = zeros(len(TC))
	PVPred = zeros(len(TC))
	if(len(TC) == len(PV)):
		for i in range(len(TC)):
			PVPred[i] = A * exp(E0 * ( 1 / (10 + 46.02) - 1 / (TC[i] + 46.02)))
			Err[i] = PVPred[i]-PV[i]
		SSE=Err * spmatrix(Err).conj().transpose()
		return SSE
	else:
		print ' length Errorlength(A), length(E0)'
		print len(TC),len(PV)

def tq(p, v):
	"""
	Student's T distribution Quantiles\n
	Returns q
	"""
	if(v <= 0):
		print ('L2:tq fucntionDegrees of freedom must be positive.')
		return -1
		
	q = float(sign(p-0.5)) * sqrt(fq(2 * fabs(p -0.5), 1, v))
	return q

def fq(p, v1, v2):
	"""
	Fisher's F distribution Quantiles\n
	Returns q
	"""
	#q = special.spbtdtri(v1/2.0, v2/2.0, p)
	#q = betaq(p,v1/2,v2/2)
	q = spbtdtri(v1/2.0,v2/2.0,p)
	#if(isarray(q) == False):
	#	print 'array'
	#	for i in range(len(q)):
	#		q[i] = v2/v1 * q[i]/(1-q[i])
	#else:
	#	print 'not array'
	q = float(v2)/float(v1) * float(q / (1-q))
	
	#http://docs.scipy.org/doc/scipy/reference/generated/scipy.special.spbtdtri.html
	#pth quantile of the beta distribution
	#q = v2/v1 * q/1-q
	return q

def matlab_sort(data):
	"""
	Sort function with descend order and index sorting\n
	Returns sorted data and sorted index
	"""
	#return sorted(data, reverse=True), sorted(range(len(data)), key = data.__getitem__, reverse = True)
	reversed_data = sort(data)
	reversed_data = reversed_data[::-1]
	data = array(data)
	#reversed_data = array(sorted(data.tolist(), reverse=True))
	reversed_idx = argsort(data)
	reversed_idx = reversed_idx[::-1]
	

	return reversed_data, reversed_idx
	
def matlab_median(data):
	"""
	Median function\n
	If 'nan' value founded, returns 'nan'\n
	Returns medain
	"""
	for i in data:
		if(isnan(i) == True):
			return float('nan')
	
	return median(data)

def stdn1(*args, **kwargs):
	"""
	Standard deviation function which is divdided by n-1 not n \n
	Returns standard deviation
	"""
	return std(*args, **kwargs)/sqrt(float(len(args[0]) - 1) / len(args[0]))	
	
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
	sortedone, key = matlab_sort(a)
	print a, sortedone, key
	return 0

def unit_test_matlab_median():
	a = [0.1, 0.2, 0.3, 0.4, float('nan')]
	print matlab_median(a)

def unit_test_RECO():
	beta_0 = [2, 200]
	TC = [1, 2, 3, 4, 5]
	PV = [5, 4, 3, 2, 1]
	print Reco(beta_0, TC, PV)

def unit_test_RECO2():
	beta_0 = [2, 200]
	TC = [1, 2, 3, 4, 5]
	PV = [5, 4, 3, 2, 1]
	E0 = [2, 4, 6, 8, 10]
	print Reco2(beta_0, TC, PV, E0)


def unit_test_fmin():
	beta0 = [2.0, 200.0]
	TC = array([1.0, 2.0, 3.0, 4.0, 5.0])
	PV = array([5.0, 4.0, 3.0, 2.0, 1.0])
	print TC.shape
	A = TC.shape
	print A[:]
	betafit = spfmin(Reco, beta0, (TC, PV))
	print betafit

def unit_test_erfc():
	print erfc(1)

	
def unit_test_basic():
	print spbetaln(10, 20)
	print spbetainc(0.5, 10, 3)
	print spbetainc(0.5, 10, 3)
	print spbetainc(10, 3, 0.5)
	print spbtdtri(2,3,0.3)
	print fq(0.3, 2, 3)
	print tq(0.3, 10)
	
#unit_test_matlab_sort()
#unit_test_matlab_median()
#unit_test_RECO()
#unit_test_RECO2()
#unit_test_fmin()
#unit_test_erfc()
#unit_test_basic()
