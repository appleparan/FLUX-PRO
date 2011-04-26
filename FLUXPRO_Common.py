# -*- coding: utf-8 -*-
from math import exp, fabs, sqrt, isnan

from numpy import zeros, array, sign, median
from numpy import sort, argsort
from numpy import std

from scipy import matrix as spmatrix
#from scipy.optimize import fmin as spfmin
from scipy.special 	import 	btdtri as spbtdtri
#							betainc as spbetainc, \
#							betaln as spbetaln


def reco_without_E0(beta, TC, PV):

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

			PVPred[i] = A * exp(B * (1 / (10 + 46.02)-1 / (TC[i] + 46.02)))
			Err[i] = PVPred[i] - PV[i]

		SSE=Err*spmatrix(Err).conj().transpose()
		return SSE
	else:
		print ' length Error:length(A), length(B)'
		print len(TC),len(PV)


def reco_const_E0(beta,TC,PV,E0):
	
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
		print ' length Error:length(A), length(E0)'
		print len(TC),len(PV)


def reco_array_E0(beta,TC,PV,E0):
	
	"""
	
	Reco2 Function\n
	Returns SSE
	
	"""
	
	A=beta[0]
	Err = zeros(len(TC))
	PVPred = zeros(len(TC))
	if(len(TC) == len(PV)):
		for i in range(len(TC)):
			PVPred[i] = A * exp(E0[i] * ( 1 / (10 + 46.02) - 1 / (TC[i] + 46.02)))
			Err[i] = PVPred[i]-PV[i]
		SSE=Err * spmatrix(Err).conj().transpose()
		return SSE
	else:
		print ' length Error:length(A), length(E0)'
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

