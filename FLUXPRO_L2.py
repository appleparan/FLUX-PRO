# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------
#                    Program for processing flux data
#
# Record of revision
#        Date         Programmer         Description of change
#    -----------     ------------      -------------------------
#    Dec/26/2008     Jinkyu Hong         Original code
#    Jan/13/2009     Jinkyu Hong        CO2 flux gap filling using MLTM
#    Feb/10/2009     Jinkyu Hong        LE gap filling using MLTM
#    Nov/23/2009     Jinkyu Hong        Revision of the codes for E0_const
#                                        algorithm
#	 Oct/31/2010	 Jong su, Kim	 	Porting MATLAB program to Python
#   

import os, csv, copy, datetime
from numpy 	import 	zeros 	as npzeros, \
					array 	as nparray, \
					mean 	as npmean, \
					median	as npmedian
from scipy.optimize import fmin as spfmin
from math import *
import FLUXPRO_Common  as Common
from cStringIO import StringIO
import re

def L2(input_path_L1, input_path_Compensate, output_path, E0_const):

	try:
		input_fp_Compensate = open(input_path_Compensate, 'r')
	except IOError:
		print "IO error;Check the input File: ", input_path_Compensate
	except:
		print "Unexpected Open Error: ", input_path_Compensate
		input_fp_Compensate.close()
		
	
	try:
		input_fp_L1 = open(input_path_L1, 'r')
	except IOError:
		print "IO error;Check the input File: ", input_path_L1
	except Error:
		print "Unexpected Open Error: ", input_path_L1
		input_fp_L1.close()
	
	#output file path
	output_file_path = os.path.join(output_path, 'ResultL2.csv')
	try:
		output_fp = open(output_file_path, 'w+')
	except IOError:
		print "IO error;Check the output File: ", output_file_path
		return 'L2 failed'

	#output_plot_1Àº Reynold-Taylor Equation¿¡¼­
	
	output_plot_2_file_path = os.path.join(output_path, 'Plot_L2_2.csv')
	try:
		output_plot_2_fp = open(output_plot_2_file_path, 'w+')
	except IOError:
		print "IO error;Check the output File: ", output_plot_2_file_path
		return 'L2 failed'	
	
	
	try:
		Compensate_csv = csv.reader(input_fp_Compensate, delimiter = ',')
	except csv.Error:    
		print "Parse ErrorCheck the input File: ", input_path_Compensate
	except StandardError:
		print "Unexpected Read Error: ", input_path_Compensate
	
	try:
		L1_csv = csv.reader(input_fp_L1, delimiter = ',')
	except csv.Error:    
		print "Parse ErrorCheck the input File: ", input_path_L1
	except StandardError:
		print "Unexpected Read Error: ", input_path_L1
	n_Compensate = 0
	n_L1 = 0
	
	data_Compensate = []
	data_L1 = []
	
	for row in Compensate_csv:
		data_Compensate.append(row)
		n_Compensate = n_Compensate + 1
	for row in L1_csv:
		data_L1.append(row)
		n_L1 = n_L1 + 1
		
	#Data count check
	if(n_Compensate != n_L1):
		print 'Count Error;Process count dismatch between Compensate and L1'
		return 'L2 failed'

	#initialize
	date = []
	rsdn = npzeros(n_Compensate)
	Ta = npzeros(n_Compensate)
	h2o = npzeros(n_Compensate)
	#press = npzeros(n_Compensate)
	
	#Read Input Data
	i = 0
	for row in data_Compensate:
		rsdn[i] = float(row[0])
		Ta[i] = float(row[1])
		h2o[i] = float(row[2])
		
		i = i + 1

	press = 998.0	
	#initialize    
	Fs = npzeros(n_L1)
	Fc = npzeros(n_L1)
	Fsc = npzeros(n_L1)
	
	Hs = npzeros(n_L1)
	Hc = npzeros(n_L1)
	Hsc = npzeros(n_L1)
	
	LEs = npzeros(n_L1)
	LEc = npzeros(n_L1)
	LEsc = npzeros(n_L1)
	
	co2 = npzeros(n_L1)
	ustar = npzeros(n_L1)
	itime = npzeros(n_L1)
	iustar = npzeros(n_L1)
	date = []
	
	i = 0
	for row in data_L1:
		date.append(row[0])
		Fs[i] = float(row[1])
		Fc[i] = float(row[2])
		Fsc[i] = float(row[3])
		
		Hs[i] = float(row[4])
		Hc[i] = float(row[5])
		Hsc[i] = float(row[6])
		
		LEs[i] = float(row[7])
		LEc[i] = float(row[8])
		LEsc[i] = float(row[9])
		
		co2[i] = float(row[10])
		ustar[i] = float(row[14])
		itime[i] = float(row[15])
		iustar[i] = float(row[16])
		i = i + 1
	# Define constants and parameters for gap filling
	#--------------------------------------------------------------------------
	num_day = 28
	#num_point_per_day = 24          # number of data points per day (48 -> 30 min avg time)
	#avgtime = 30
	#determine num_point_per_day automatically . using datetime module
	date_1st = datetime.datetime.strptime(date[0], "%Y-%m-%d %H:%M")
	date_2nd = datetime.datetime.strptime(date[1], "%Y-%m-%d %H:%M")
	date_diff = date_2nd - date_1st
	avgtime = int(date_diff.seconds / 60) # averaging time (minutes)
	num_point_per_day = 1440 / avgtime # number of data points per day (1440 : minutes of a day)
	num_segment = num_point_per_day * num_day
	num_avg = int(n_L1 / num_segment)
	num_day_2 = 7
	# nday_re = 20
	# noverlap = 5
	num_day_re = 20
	noverlap = 5
	

	#--------------------------------------------------------------------------
	#E0_const = True # Do you want to use constant E0 for one year? Y/N

	ni = 36
	nd = 10
	n1 = 2         # how many the largest points are considered for respiration
					# DO NOT Modify!
	beta0 = nparray([2, 200])
	Tref = 10.0
	T0 = -46.02
	gap_limit = 0.025
	ustar_limit = 0.5
	upper_Fc = 0.35   # upper limit of nighttime CO2 flux (mg/m2/s)
	Fc_limit = 0.005
	
	## Information for MLT
	drsdn = 50.0   # W/m2
	dta = 2.5      # oC
	dvpd = 5.0     # 5 hPa
	rv = 461.51
	#--------------------------------------------------------------------------
	
	upper_co2 = 1000.0 # upper limit of CO2 concent.(mg/m3)
	upper_h2o = 60.0  # upper limit of H2O concent. (g/m3)
	upper_Ta = 60.0   # upper limit of air temperature (oC)
	lower_Fc = -3.0   # lower limit of daytime CO2 flux (mg/m2/s)
	lower_LE = -200    # lower limit of LE (W/m2)
	lower_H = -300     # lower limit of H (W/m2)
	upper_Fc = 3   # upper limit of nighttime CO2 flux (mg/m2/s)
	upper_LE = 800    # upper limit of LE (W/m2)
	upper_H = 800     # upper limit of H (W/m2)
	upper_agc = 95.0  # upper limit of AGC value
	ustar_limit = 0.03 # minimum ustar for filtering out nighttime fluxes
	Fc_limit = 0.005  # lower limit of Re (ecosystem respiration) (mg/m2/s)
	gap_limit = 0.025 # 0.025 --> 95# confidence interval

	Tak = npzeros(len(Ta))
	tr = npzeros(len(Ta))
	ea = npzeros(len(Ta))
	es = npzeros(len(Ta))
	vpd = npzeros(len(Ta))
	#--------------------------------------------------------------------------
	# calculation of vapor pressure deficit
	a = [13.3185, 1.9760, 0.6445, 0.1299]
	
	for i in range(n_Compensate):
		Tak[i] = Ta[i] + 273.15
		tr[i] = 1.0-(373.15/Tak[i])
		es[i] = 1013.25*exp(a[0]*tr[i]-a[1]*(tr[i]**2)-(a[2]*(tr[i]**3))-a[3]*(tr[i]**4)) # hPa
	
	for i in range(n_L1):
		ea[i] = h2o[i]
		vpd[i]= float(es[i]) - float(ea[i])  #unit is hPa
	
		
	Fc_filled = copy.deepcopy(Fsc)
	
	print 'Gap Filling Process'
	print 'Before running this program, '
	print '   please make sure that you correctly set all parameters'
	#print 'E0_const'. E0_const
	#print 'nn', nn
	#print 'num_point_per_day', num_point_per_day
	#print 'num_day_2', num_day_2
	#print 'num_day_re', num_day_re
	#print 'noverlap', noverlap
	#print 'drsdn', drsdn
	#print 'dta', dta
	#print 'dvpd', dvpd
	#print '-------------------------------------------------------------------'
	index = []

	for main_j in range(num_avg):       # loop for gap-filling of CO2 fluxes           
		
		seg_start_i = main_j * num_segment
		seg_fin_i = seg_start_i + num_segment
		
		if((seg_start_i + 2 * num_segment) > n_L1):
			seg_fin_i = n_L1
		x2 = []
		x3 = []
	#--------------------------------------------------------------------------
		if(main_j == 0):
			print 'Application of modified lookup table method'
	#--------------------------------------------------------------------------
		for i in range(seg_start_i, seg_fin_i):
			if(itime[i] == 1):
				ii = 0                
				if(isnan(Fsc[i]) == True):
					jj = 0
					while ((ii < 1) and (jj <= 4)):
						ta_f = Ta[i]
						rsdn_f = rsdn[i]
						vpd_f = vpd[i]

						i0 = i - jj * num_day_2 * num_point_per_day
						i1 = i + jj * num_day_2 * num_point_per_day+1
						
						if(i0 < 1): 
							i0 = 0
							i1 = 2 * jj * num_day_2 * num_point_per_day+1
						if(i1 >= n_L1):
							i0 = n_L1 - 2 * jj * num_day_2 * num_point_per_day
							i1 = n_L1
							if(i0 < 1):
								i0 = 0	
						ks = 0
						for j in range(i0, i1):
							if((fabs(vpd_f - vpd[j]) 	< dvpd) and \
								(fabs(rsdn_f - rsdn[j]) < drsdn) and \
								(fabs(ta_f - Ta[j]) 	< dta) and \
								(isnan(Fsc[j]) 			== False)):
								ks = ks + 1
								x3_temp = []
								
								x2.append(Fsc[j])
								x3_temp.append(j)
								x3_temp.append(vpd[j])
								x3_temp.append(rsdn[j])
								x3_temp.append(Ta[j])
								x3_temp.append(ks)
								x3.append(x3_temp)
								
						ii = ks
						
						#index_temp = []
						#index_temp.append(i)
						#index_temp.append(i0)
						#index_temp.append(i1)
						#index_temp.append(ks)
						#index_temp.append(main_j)
						#index.append(index_temp)
						
						if(ks >= 1):
							Fc_filled[i] = npmedian(nparray(x2))

						jj = jj + 1
						x2 = []
						x3 = []

					if(ii < 1):
						jj = 0
						while(ii < 1):
							rsdn_f = rsdn[i]

							i0 = i - jj * num_day_2 * num_point_per_day
							i1 = i + jj * num_day_2 * num_point_per_day+1
							if(i0 < 1): 
								i0 = 0
								i1 = 2 * jj * num_day_2 * num_point_per_day+1
							
							if(i1 >= n_L1):
								i0 = n_L1 - 2 * jj * num_day_2 * num_point_per_day
								i1 = n_L1
								if(i0 < 0):
									i0 = 0

							ks = 0
							for j in range(i0, i1):
								if((fabs(rsdn_f - rsdn[j]) 	< drsdn) and \
								(isnan(Fsc[j]) 				== False)):
									ks = ks + 1                      
									x3_temp = []
								
									x2.append(Fsc[j])
									x3_temp.append(j)
									x3_temp.append(vpd[j])
									x3_temp.append(rsdn[j])
									x3_temp.append(Ta[j])
									x3_temp.append(ks)
									x3.append(x3_temp)

							ii = ks
							
							#index_temp = []
							#index_temp.append(i)
							#index_temp.append(i0)
							#index_temp.append(i1)
							#index_temp.append(ks)
							#index_temp.append(main_j)
							#index.append(index_temp)
							
							if(ks >= 1):
								Fc_filled[i] = npmedian(nparray(x2))
								
							jj = jj + 1
							x2 = []
							x3 = []
							
		x2 = []
		x3 = []

		ks = 0
		
	d = npzeros((n_L1, 5))
	d2 = npzeros((n_L1, 5))
	dd = npzeros((n_L1, 5))
	x4 = []
	#Regression to Lloyd-Taylor equation
	print 'Regression to Lloyd-Taylor equation'
	if(E0_const == True):
		for i in range(ni-1, n_Compensate, num_point_per_day):
			t1 = npzeros(nd)
			
			for j in range(nd):
				t1[j] = Fsc[i + j]
			
			#Set to 'descend'
			t2, IX = Common.matlab_sort(t1)

			k2 = 0
			for k in range(nd-1):
				if((isnan(t2[k]) 	== False) and \
						(t2[k] 		< upper_Fc) and \
						(t2[k+1] 	> Fc_limit)):
					k2 = k2 + 1
			
			if(k2 >= 2):
				for j in range(nd-1):
					
					if((itime[i+1 + IX[j]]      == 0) and \
					(isnan(t2[j])           	== False) and \
					(isnan(Ta[i+1 + IX[j]])  	== False) and \
					(t2[j]                  	< upper_Fc) and \
					(t2[j + 1]					> Fc_limit) and \
					(iustar[i + IX[j]]      	== 0) and \
					(iustar[i + IX[j+1]]    	== 0)):
						x3.append(t2[j])
						x3.append(t2[j+1])
						x2.append(Ta[i + IX[j]])
						x2.append(Ta[i + IX[j+1]])
						x4.append(date[i + IX[j]])
						x4.append(date[i + IX[j+1]])
			
						ks = ks + n1
						break	
		TC = copy.deepcopy(nparray(x2))
		PV = copy.deepcopy(nparray(x3))
	
		
		betafit = spfmin(Common.Reco, beta0, args = (TC, PV), disp=False)
		A = betafit[0]
		B = betafit[1]
		yfit = npzeros(len(TC))
		for i in range(len(TC)):
			yfit[i] = A * exp(B * (1 / (10 + 46.02) - 1 / (TC[i] + 46.02)))
		E0 = betafit[1]
		E0l = copy.deepcopy(E0)
		

		
		#    figure(1)
		#   plot(TC][PV,'ko',TC][yfit,'or')
		#    grid
		#    xlabel('air temperature (^oC)')
		#    ylabel('Ecosystem respiration(mgm^{-2}s^{-1})')

		#     TC = x2'
		#     PV = x3'
		#     
		#     [beta][resnorm] = lsqcurvefit(@myfun][beta0][TC][PV)
		#     
		#     A=beta(1)
		#     B=beta(2)
		#     yfit=A.*exp(B.*(1./(10.+46.02)-1./(TC+46.02)))
		#     E0 = betafit(2)
		#     E0l = E0
		# 
		# 
		#     figure(5)
		#     plot(TC][PV,'ko',TC][yfit,'or')
		#     grid
		#     xlabel('air temperature (^oC)')
		#     ylabel('Ecosystem respiration(mgm^{-2}s^{-1})')
		x2 = []
		x3 = []
		t1 = []
		t2 = []
		TC = []
		PV = []
		yfit = npzeros(len(TC))

	#num_day_re = 20
	#noverlap = 5
	#avgtime = 30
	delta = (60 / avgtime) * 24 * num_day_re
	dnoverlap = (60 / avgtime) * 24 * noverlap
	jj = 0
	sday = []
	Rref = []
	RE_limit = []
	stdev_E0 = []
	E0v = []
	REs = []
	Taylor_date = []
	yfit_array = []
	for i in range(0, n_L1, dnoverlap):
		i0 = int(i - delta / 2)
		i1 = int(i + delta / 2)
		
		if(i0 < 1):
			i0 = 0
			i1 = int(i0 + delta)
		if(i1 >= n_L1):
			i0 = int(n_L1 - delta) - 1
			i1 = n_L1
		
		ks = 1
		for j in range(i0+ni-1, i1, num_point_per_day):
			t1 = npzeros(nd)
			for k in range(nd):
				t1[k] = Fsc[j + k]
			#Set to 'descend'
			t2, IX = Common.matlab_sort(t1)
			
			k2 = 1
			for k in range(nd-1):
				if((isnan(t2[k])    ==  False) and \
					(t2[k]          <   upper_Fc) and \
					(t2[k+1]        >   Fc_limit)):
					k2 = k2 + 1
			
			if(k2 >= n1):
				for k in range(nd-1):
					if((itime[j+1 +IX[k]]  	== 0) and \
					(isnan(t2[k])           == False) and \
					(isnan(Ta[j + IX[k]])	== False) and \
					(t2[k]                  < upper_Fc) and \
					(t2[k+1]                > Fc_limit) and \
					(iustar[j +IX[k]]      == 0) and \
					(iustar[j +IX[k+1]]    == 0)):
						x3.append(t2[k])
						x3.append(t2[k+1])
						x2.append(Ta[j + IX[k]])
						x2.append(Ta[j + IX[k+1]])
						Taylor_date.append(str(date[j + IX[k]]))
						Taylor_date.append(str(date[j + IX[k+1]]))
					
						ks = ks + n1
						break
			
		ks = ks - 1
		
		if(ks < 6):
			if(E0_const == True):
				Rref.append(float('NaN'))
				RE_limit.append(float('NaN'))
				jj = jj + 1
			else:
				Rref.append(float('NaN'))
				E0v.append(float('NaN'))
				stdev_E0.append(float('NaN'))
				RE_limit.append(float('NaN'))
				jj = jj + 1
		else:
			TC = copy.deepcopy(nparray(x2))
			PV = copy.deepcopy(nparray(x3))
			
			if(E0_const == True):
				betafit = spfmin(Common.Reco2, beta0, args = (TC, PV, E0l), disp=False)
				A = betafit[0]
				Rref.append(A)
				
				for j in range(len(TC)):
					yfit = A * exp(E0 * (1.0/(10.0+46.02) - 1.0/(TC[j] + 46.02)))
					yfit_array.append(yfit)
					REs.append(PV[j] - yfit)
				
				sz = nparray(REs).shape
				upper = fabs(Common.tq(gap_limit, sz[0]-1 ) )
				RE_limit.append(upper*Common.stdn1(nparray(REs))/sqrt(sz[0]))
				
				jj = jj + 1
			else:
				betafit=spfmin(Common.Reco2, beta0, args = (TC, PV, E0))
				
				A=betafit[0]
				B=betafit[1]
				Rref.append(A)
				E0v.append(B)
				
				if((B < 0) or (B > 450)):
					E0v.append(float('NaN'))
				
				for j in range(len(TC)):
					yfit = A * exp(E0v[jj] * (1.0 / (10.0 + 46.02) - 1.0 / (TC[j] + 46.02)))
					yfit_array.append(yfit)
					REs.append(PV[j] - yfit)
				
				sz = nparray(REs).shape
				upper = abs(Common.tq(gap_limit, sz[0]-1))
				stdev_E0.append(Common.stdn1(REs) / sqrt(sz[0]))
				RE_limit.append(upper * Common.stdn1(nparray(REs)) / sqrt(sz[0]))
				
				jj = jj + 1
			#Regression to Lloyd-Taylor equation with 28-day segmentation
			date_extracted = re.search('^(\d{4}[-]\d{2}[-]\d{2})',str(Taylor_date[0]))
			#print date_extracted.group(0)
			if(date_extracted != None):
				fname = 'Plot_L2_1_'+str(date_extracted.group(0))+'.csv'
				output_plot_1_file_path = os.path.join(output_path, fname)	
				
				try:
					output_plot_1_fp = open(output_plot_1_file_path, 'w+')
				except IOError:
					print "IO error;Check the output File: ", output_plot_1_file_path
					return 'L2 failed'	
				
				for i in range(len(TC)):
					file_plot_str = StringIO()
					file_plot_str.write(Taylor_date[i]		+ ',')		#1	
					file_plot_str.write(str(A)	 			+ ',') 		#2
					file_plot_str.write(str(B)	 			+ ',') 		#3
					file_plot_str.write(str(TC[i]) 			+ ',') 		#4
					file_plot_str.write(str(PV[i]) 			+ ',' )		#5
					file_plot_str.write(str(yfit_array[i])	+ '\n' )	#6
					
					output_plot_string = file_plot_str.getvalue()
					
					output_plot_1_fp.write(output_plot_string)
				output_plot_1_fp.close()
			
				
		sday_temp = []
		sday_temp.append(i)
		sday_temp.append(i0)
		sday_temp.append(i1)
		sday.append(sday_temp)
		
		
		
		x2 = []
		x3 = []
		t1 = []
		t2 = []
		TC = []
		PV = []
		Taylor_date = []
		REs = []
		yfit = []

	sday = nparray(sday)
	if(E0_const == True):
		print 'Long-term E0 '
		E0s = copy.deepcopy(E0l)
	else:
		E0v_s = []
		stdev_E0_s = []
		for k in range(len(E0v)):
			E0v_s.append(E0v[k]/stdev_E0[k])
			stdev_E0_s.append(1/stdev_E0[k])
		print 'Short-term E0 '
		E0s = npnansum(E0v_s)/npnansum(stdev_E0_s)
	Rref = []
	#REs = []
	#RE_limit = []
	
	
	jj = 0
	for i in range(0, n_L1, dnoverlap):

		i0 = i - delta / 2
		i1 = i + delta / 2
	
		if(i0 < 1):
			i0 = 0
			i1 = i0 + delta
		if(i1 >= n_L1):
			i0 = n_L1 - delta - 1
			i1 = n_L1
		ks = 1
		for j in range(i0+ni-1,  i1,  num_point_per_day):
			t1 = npzeros(nd)
			for k in range(nd):
				t1[k] = Fsc[j + k]
			#Set to 'descend'
			t2, IX = Common.matlab_sort(t1)

			k2 = 1
			
			for k in range(nd-1):
				if((isnan(t2[k])	== 	False) and \
					(t2[k]			< 	upper_Fc) and \
					(t2[k+1]		> 	Fc_limit)):
					
					k2 = k2 + 1
				
			if(k2 >= n1):
				for k in range(nd-1):
					if((itime[j+1 + IX[k]]		== 0) and \
					(isnan(t2[k])               == False) and \
					(isnan(Ta[j + IX[k]])    	== False) and \
					(t2[k]                    	< upper_Fc) and \
					(t2[k+1]                   	> Fc_limit) and \
					(iustar[j + IX[k]]        	==  0) and \
					(iustar[j + IX[k+1]]        ==  0)):
						x3.append(t2[k])
						x3.append(t2[k + 1])
						x2.append(Ta[j + IX[k]])
						x2.append(Ta[j + IX[k+1]])
						
						ks = ks + n1
						break
					
		ks = ks - 1

		if(ks < 6):
			
#			Rref.append(Rref[jj])
#			RE_limit.append(RE_limit[jj])
			
			Rref.append(Rref[-1])
			RE_limit.append(RE_limit[-1])
			
			if(E0_const != True):
				stdev_E0.append(stdev_E0[jj])
				
			jj = jj + 1
            
			
		else:

			TC = nparray(x2)
			PV = nparray(x3)
			
			betafit = spfmin(Common.Reco2, beta0, args = (TC, PV, E0s), disp=False)
			
			A=betafit[0]
			Rref.append(A)
			
			for j in range(len(TC)):
				yfit = Rref[jj] * exp(E0s * (1 / (10 + 46.02) - 1 / (TC[j] + 46.02)))
				REs.append(PV[j]-yfit)
				
			sz = nparray(REs).shape
			upper = abs(Common.tq(gap_limit, sz[0]-1))
			RE_limit.append(upper*Common.stdn1(REs)/sqrt(sz[0]))
            
			jj = jj + 1
	
		x2 = []
		x3 = []
		t1 = []
		t2 = []
		TC = []
		PV = []
		
		#for k in REs:
		#	print k
		REs = []
	#for k in Rref:
	#	print k
	##    
	
	ks = 0
	nsp2 = npzeros((n_L1 / num_point_per_day))
	RE = npzeros(n_L1) 
	GPP = npzeros(n_L1)
	for i in range(n_L1):
		RE[i] = float('NaN')
		GPP[i] = float('NaN')
	
	for i in range(0, n_L1, num_point_per_day):
		i0 = i
		i1 = i + num_point_per_day
		if(i0 >=sday[ks][1]):
			ks = ks + 1
			if(i0 >= sday[len(sday)-1][1]):
				ks = len(sday)-1
		
		for j in range(i0, i1):
			if(E0_const == True):
				yfit=Rref[ks-1] * exp(E0l * (1.0 / (10 + 46.02) - 1.0 / (Ta[j] + 46.02)))
			else:
				yfit=Rref[ks-1] * exp(E0s * (1.0 / (10 + 46.02) - 1.0 / (Ta[j] + 46.02)))
			
			RE[j] = yfit
			if(itime[j]==0):                 # nighttime condition
				RE[j] = Fc_filled[j]
				
				if((isnan(Fsc[j])    	==  True) or \
					((Fsc[j]-yfit)		<   RE_limit[ks-1]) or \
					((Fsc[j]-yfit)  	>   1.0 * RE_limit[ks-1]) or \
					(iustar[j]      	==  1)):
					nsp2[ks-1] = nsp2[ks-1] + 1
					Fc_filled[j] = yfit
					RE[j] = Fc_filled[j]
			
			GPP[j] = RE[j]- Fc_filled[j]
			
	
	#figure(2)
	#plot(time][Fsc][time][Fc_filled[:],'or')
	#set(gca,'XTick',[year0:1/12:year0+0.9999999])
	#set(gca,'xticklabel',xticks)            
	#ylim = [-1.5][1.5]
	#set(gca,'xLim',xlim(:))
	#ylabel('F_c (mgm^{-2}s^{-1})')
	#--------------------------------------------------------------------------


	#--------------------------------------------------------------------------
	print 'Gap-filling of LE'
	#--------------------------------------------------------------------------
	x2 = []
	x3 = []
	index = []
	LE_filled = copy.deepcopy(LEsc)
	for main_j in range(num_avg):       # loop for gap-filling of H2O fluxes           
		
		
		seg_start_i = main_j * num_segment
		seg_fin_i = seg_start_i + num_segment
		
		if((seg_start_i + 2 * num_segment) > n_L1):
			seg_fin_i = n_L1
			
		x2 = []
		x3 = []

		for i in range(seg_start_i, seg_fin_i):
			
			ii = 0               
			
			if(isnan(LEsc[i]) == True):
				jj = 0
				while((ii < 1) and (jj <= 4)):
					ta_f = Ta[i]
					rsdn_f = rsdn[i]
					vpd_f = vpd[i]

					i0 = i - jj * num_day_2 * num_point_per_day
					i1 = i + jj * num_day_2 * num_point_per_day+1
					if(i0 < 1):
						i0 = 0
						i1 = 2 * jj * num_day_2 * num_point_per_day+1
					if(i1 >= n_L1):
						i0 = n_L1 - 2 * jj * num_day_2 * num_point_per_day - 1
						i1 = n_L1
						if(i0 < 1):
							i0 = 0
					ks = 0
					for j in range(i0, i1):
						if((fabs(vpd_f-vpd[j])	< dvpd) and \
						(fabs(rsdn_f-rsdn[j])	< drsdn)  and \
						(fabs(ta_f-Ta[j])   	< dta) and \
						(isnan(LEsc[j])    		== False)):
							x3_temp = []
							x2.append(LEsc[j])
							x3_temp.append(j)
							x3_temp.append(vpd[j])
							x3_temp.append(rsdn[j])
							x3_temp.append(Ta[j])
							x3_temp.append(ks)
							x3.append(x3_temp)                                
							ks = ks + 1
							
					ii = ks
					#index_temp = []
					#index_temp.append(i)
					#index_temp.append(i0)
					#index_temp.append(i1)
					#index_temp.append(ks)
					#index_temp.append(main_j)
					#index.append(index_temp)

					if(ks >= 1):
						LE_filled[i] = npmedian(nparray(x2))
					jj = jj + 1
					x2 = [] 
					x3 = [] 
					
				if(ii < 1):
					jj = 0
					while(ii < 1):
						rsdn_f = rsdn[i]

						i0 = i - jj * num_day_2 * num_point_per_day 
						i1 = i + jj * num_day_2 * num_point_per_day + 1
						if(i0 < 1):
							i0 = 0
							i1 = 2 * jj * num_day_2 * num_point_per_day + 1
						if(i1 >= n_L1):
							i0 = n_L1 - 2 * jj * num_day_2 * num_point_per_day - 1
							i1 = n_L1
							if(i0 < 1):
								i0 = 0
								
						ks = 0
						for j in range(i0, i1):
							if((fabs(rsdn_f-rsdn[j]) 	< drsdn)  and \
								(isnan(LEsc[j])       		== False)):
								
								x3_temp = []
								x2.append(LEsc[j])
								x3_temp.append(j)
								x3_temp.append(vpd[j])
								x3_temp.append(rsdn[j])
								x3_temp.append(Ta[j])
								x3_temp.append(ks)
								x3.append(x3_temp)
								ks = ks + 1
							
						ii = ks
						#index_temp = []
						#index_temp.append(i)
						#index_temp.append(i0)
						#index_temp.append(i1)
						#index_temp.append(ks)
						#index_temp.append(main_j)
						#index.append(index_temp)

						if(ks >= 1):
							LE_filled[i] = npmedian(nparray(x2))
						jj = jj + 1
						x2 = []
						x3 = []
		
		x2 = []
		x3 = []
		ks = 0

	#figure(3)
	#plot(time][LEsc][time][LE_filled[:],'or')
	#set(gca,'XTick',[year0:1/12:year0+0.9999999])
	#set(gca,'xticklabel',xticks)            
	#ylim = [-100][600]
	#set(gca,'xLim',xlim(:))
	#ylabel('LE (Wm^{-2})')

	##
	#--------------------------------------------------------------------------
	
	print 'Gap-filling of H (sensible heat flux)'
	
	#--------------------------------------------------------------------------
	x2 = []
	x3 = []
	index = []
	H_filled = copy.deepcopy(Hsc)

	for main_j in range(num_avg):       # loop for gap-filling of H2O fluxes           
		seg_start_i = main_j * num_segment
		seg_fin_i = seg_start_i + num_segment
		
		if((seg_start_i + 2 * num_segment) >= n_L1):
			seg_fin_i = n_L1
		
		x2 = []
		x3 = []

		for i in range(seg_start_i, seg_fin_i):
			ii = 0                
			if(isnan(Hsc[i])	== True):
				jj = 0
				while ((ii < 1) and (jj <= 4)):
					ta_f = Ta[i]
					rsdn_f = rsdn[i]
					vpd_f = vpd[i]

					i0 = i - jj * num_day_2 * num_point_per_day
					i1 = i + jj * num_day_2 * num_point_per_day+1
					if(i0 < 1):
						i0 = 0
						i1 = 2 * jj * num_day_2 * num_point_per_day+1
					if(i1 >= n_L1):
						i0 = n_L1 - 2 * jj * num_day_2 * num_point_per_day - 1
						i1 = n_L1
						if(i0 < 1):
							i0 = 0
						
					ks = 0
					for j in range(i0, i1):
						if((fabs(vpd_f-vpd[j])	< dvpd) and \
						(fabs(rsdn_f-rsdn[j])  	< drsdn)  and \
						(fabs(ta_f-Ta[j])      	< dta) and \
						(isnan(Hsc[j])        	== False)):
							                   
							x3_temp = []
							x2.append(Hsc[j])
							x3_temp.append(j)
							x3_temp.append(vpd[j])
							x3_temp.append(rsdn[j])
							x3_temp.append(Ta[j])
							x3_temp.append(ks)
							ks = ks + 1   
							x3.append(x3_temp)    
					ii = ks
					#index_temp = []
					#index_temp.append(i)
					#index_temp.append(i0)
					#index_temp.append(i1)
					#index_temp.append(ks)
					#index_temp.append(main_j)
					#index.append(index_temp)

					if(ks >= 1):
						H_filled[i] = npmedian(nparray(x2))
					jj = jj + 1
					x2 = [] 
					x3 = []

				if(ii < 1):
					jj = 0
					while(ii < 1):
						rsdn_f = rsdn[i]

						i0 = i - jj * num_day_2 * num_point_per_day
						i1 = i + jj * num_day_2 * num_point_per_day+1
						if(i0 < 1):
							i0 = 0
							i1 = 2 * jj * num_day_2 * num_point_per_day+1
						if(i1 >= n_L1):
							i0 = n_L1 - 2 * jj * num_day_2 * num_point_per_day - 1
							i1 = n_L1
							if(i0 < 1):
								i0 = 0
							
						ks = 0
						for j in range(i0, i1): 
							if((fabs(rsdn_f-rsdn[j])    <  drsdn)  and \
							(isnan(Hsc[j])            	== False)):
								ks = ks + 1                      
								x3_temp = []
								x2.append(Hsc[j])
								x3_temp.append(j)
								x3_temp.append(vpd[j])
								x3_temp.append(rsdn[j])
								x3_temp.append(Ta[j])
								x3_temp.append(ks)
								x3.append(x3_temp)    
						
						ii = ks
						#index_temp = []
						#index_temp.append(i)
						#index_temp.append(i0)
						#index_temp.append(i1)
						#index_temp.append(ks)
						#index_temp.append(main_j)
						#index.append(index_temp)
						

						if(ks >= 1):
							H_filled[i] = npmedian(nparray(x2))

						jj = jj + 1
						x2 = []
						x3 = []
					
		x2 = []
		x3 = []
		ks = 0

	#figure(4)
	#plot(time,Hsc,time,H_filled[:],'or')
	#set(gca,'XTick',[year0:1/12:year0+0.9999999])
	#set(gca,'xticklabel',xticks)            
	#ylim = [-100,600]
	#set(gca,'xLim',xlim(:))
	#ylabel('H (Wm^{-2})')
	
	##
	print '-------------------------------------------------------------------'
	print 'Calculating daily mean values'
	print '-------------------------------------------------------------------'
	# disp('Press any key to calculate daily mean values')
	# pause
	print '-------------------------------------------------------------------'
	print 'calculation of daily mean. Unit seg_start_i [C g/m2/day].'
	print '-------------------------------------------------------------------'

	Fsc_daily = npzeros(n_L1/num_point_per_day)
	GPP_daily = npzeros(n_L1/num_point_per_day)
	RE_daily = npzeros(n_L1/num_point_per_day)
	ET_daily = npzeros(n_L1/num_point_per_day)
	H_daily = npzeros(n_L1/num_point_per_day)
	LE_daily = npzeros(n_L1/num_point_per_day)
	H_daily = npzeros(n_L1/num_point_per_day)
	
	k = 0
	for i in range(0, n_L1, num_point_per_day):
		for j in range(i,i + num_point_per_day):
			Fsc_daily[k] = Fsc_daily[k] + Fc_filled[j]
			GPP_daily[k] = GPP_daily[k] + GPP[j]
			RE_daily[k] = RE_daily[k] + RE[j]
			ET_daily[k] = ET_daily[k] + LE_filled[j]
		Fsc_daily[k] = Fsc_daily[k]	*	(60*float(avgtime)/1000*12/44)
		GPP_daily[k] = GPP_daily[k]	*	(60*float(avgtime)/1000*12/44)    
		RE_daily[k] = RE_daily[k]	*	(60*float(avgtime)/1000*12/44)        
		ET_daily[k] = ET_daily[k]	*	(60*float(avgtime)/(2440)/1000)
		
		k = k + 1
	NEE_annual= npmean(Fc_filled)*float((1800*48*(n_L1/(60.0/avgtime*24))*12/44/1000.0))
	GPP_annual = npmean(GPP)*float((1800*48*(n_L1/(60.0/avgtime*24))*12/44/1000.0))
	RE_annual = npmean(RE)*float((1800*48*(n_L1/(60.0/avgtime*24))*12/44/1000.0))
	NEE_std_annual = Common.stdn1(Fsc_daily)/sqrt(n_L1/(60.0/avgtime*24))*(n_L1/(60.0/avgtime*24))
	GPP_std_annual = Common.stdn1(GPP_daily)/sqrt(n_L1/(60.0/avgtime*24))*(n_L1/(60.0/avgtime*24))
	RE_std_annual = Common.stdn1(RE_daily)/sqrt(n_L1/(60.0/avgtime*24))*(n_L1/(60.0/avgtime*24))
	
	print 'NEE_annual', NEE_annual
	print 'GPP_annual', GPP_annual
	print 'RE_annual', RE_annual
	print 'NEE_std_annual', NEE_std_annual
	print 'GPP_std_annual', GPP_std_annual
	print 'RE_std_annual', RE_std_annual
	
	print '-------------------------------------------------------------------'
	print 'Calculating daily mean ETs'
	print '-------------------------------------------------------------------'
	print 'calculation of daily mean. Unit seg_start_i [C g/m2/day].'
	print '-------------------------------------------------------------------'

	
	k = 0
	for i in range(0, n_L1, num_point_per_day):
		for j in range(i,i + num_point_per_day):
			LE_daily[k] = LE_daily[k] \
				+ LE_filled[j]*(60*float(avgtime)/(2440*1000))
		k = k + 1    


	# npmean(Fc_filled)
	LE_annual = npmean(LE_filled)*(1800.0*48.0*float(n_L1/(60.0/avgtime*24))/2440.0/1000.0)
	LE_std_annual = Common.stdn1(LE_daily)/sqrt(n_L1/float(60.0/avgtime*24.0))*float(n_L1/(60.0/avgtime*24.0))

	print 'LE_annaul', LE_annual
	print 'LE_std_annaul', LE_std_annual
	
	print '-------------------------------------------------------------------'
	print 'Calculating daily npmean heating rate'
	print '-------------------------------------------------------------------'
	print 'calculation of daily npmean heating rate. Unit seg_start_i [MJ/m2/day].'
	print '-------------------------------------------------------------------'

	k = 0
	for i in range(0, n_L1, num_point_per_day):
		for j in range(i,i + num_point_per_day):
			H_daily[k] = H_daily[k] \
				+ H_filled[j]*(60*float(avgtime)/(1004*1.0))/(10E6)
		k = k + 1

	H_annual = sum(H_daily)
	H_std_annual = Common.stdn1(H_daily)
	
	print 'H_annaul', H_annual
	print 'H_std_annaul', H_std_annual

	
	for i in range(len(Fsc)):
		file_plot_str = StringIO()
		file_plot_str.write(str(date[i])			+ ',') 		#1
		file_plot_str.write(str(Fsc[i]) 			+ ',') 		#2
		file_plot_str.write(str(Fc_filled[i]) 		+ ',') 		#3
		file_plot_str.write(str(LEsc[i]) 			+ ',') 		#4
		file_plot_str.write(str(LE_filled[i]) 		+ ',') 		#5
		file_plot_str.write(str(Hsc[i]) 			+ ',') 		#6
		file_plot_str.write(str(H_filled[i]) 		+ '\n') 	#7
		

		output_plot_string = file_plot_str.getvalue()
		
		output_plot_2_fp.write(output_plot_string)
	output_plot_2_fp.close()
	
	
	#For output
	#Assume data start from 0:00
	output_Fsc_daily = npzeros(n_L1)
	output_GPP_daily = npzeros(n_L1)
	output_RE_daily = npzeros(n_L1)
	output_ET_daily = npzeros(n_L1)
	output_LE_daily = npzeros(n_L1)
	output_H_daily = npzeros(n_L1)
	
	j = 0
	for i in range(n_L1):
		output_Fsc_daily[i] = Fsc_daily[j]
		output_GPP_daily[i] = GPP_daily[j]
		output_RE_daily[i] = RE_daily[j]
		output_ET_daily[i] = ET_daily[j]
		output_H_daily[i] = H_daily[j]
		output_LE_daily[i] = LE_daily[j]
		if((i+1) % num_point_per_day == 0):
			j = j + 1
			

	for i in range(n_L1):
		file_str = StringIO()

		file_str.write(str(output_ET_daily[i]) + ',') 		#1
		
		file_str.write(str(Fc_filled[i]) + ',' )			#2
		file_str.write(str(output_Fsc_daily[i])   + ',' )	#3
		
		file_str.write(str(GPP[i]) + ',' )					#4
		file_str.write(str(output_GPP_daily[i]) + ',')		#5
		file_str.write(str(GPP_annual) + ',')				#6
		file_str.write(str(GPP_std_annual) + ',')			#7
		
		file_str.write(str(H_filled[i]) + ',')				#8
		file_str.write(str(output_H_daily[i]) + ',')		#9
		file_str.write(str(H_annual) + ',')					#10
		file_str.write(str(H_std_annual) + ',')				#11
		
		file_str.write(str(LE_filled[i]) + ',')				#12
		file_str.write(str(output_LE_daily[i]) + ',')		#13
		file_str.write(str(LE_annual) + ',')				#14
		file_str.write(str(LE_std_annual) + ',')			#15
		
		file_str.write(str(NEE_annual) + ',')				#16
		file_str.write(str(NEE_std_annual) + ',')			#17
		
		file_str.write(str(output_RE_daily[i]) + ',')		#18
		file_str.write(str(RE_annual) + ',')				#19
		file_str.write(str(RE_std_annual) + ',')			#20
		
		file_str.write(str(co2[i]) + ',')					#21
		file_str.write(str(rsdn[i]) + ',')					#22
		file_str.write(str(ea[i]) + ',')					#23
		file_str.write(str(h2o[i]) + ',')					#24
		file_str.write(str(Ta[i]) + ',')					#25
		file_str.write(str(vpd[i]) + '\n' )					#26
	
		output_string = file_str.getvalue()
		
		output_fp.write(output_string)

	output_fp.close()
	
	return 'L2 Done'
