# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------
#                    Program for processing flux data
#
# Record of revision
#        Date         Programmer         Description of change
#    -----------     ------------      -------------------------
#    Dec/26/2008     Jinkyu Hong         Original code
#    Jan/05/2009     Jinkyu Hong        Add spike detection codes
#    Jan/13/2009     Jinkyu Hong        Modify spike detection codes
#    Apr/16/2009     Jinkyu Hong        Modify input file reading
#	 Oct/31/2010	 Jong su, Kim 		Porting MATLAB program to Python
#--------------------------------------------------------------------------

from math import *
import numpy as np
import scipy as sp
import scipy.stats as   spstats
import copy
import os
import csv
from cStringIO import StringIO
#import FLUX_PRO_Common as Common

def L1(output_path, st_agc_condition, thrsh, zm):

	print('Spike Detection')
	print('Before running this program, ')
	print('   please make sure that you correctly set all parameters')

	## Reading input file
	input_path = os.path.join(output_path, 'ResultL0.csv')
	try:
		input_fp = open(input_path, 'r')
	except IOError:
		print "IO errorCheck the input File: ", input_path
		return 'L1 failed'    
	except StandardError:
		print "Unexpected Open Error: ",input_path
		input_fp.close()
		return 'L1 failed'    

	try:
		L1_csv=csv.reader(input_fp, delimiter=',')
	except csv.Error:
		print "Parse ErrorCheck the input File: ", input_path
		return 'L1 failed'    
	except StandardError:
		print "Unexpected Read Error: ", input_path
		return 'L1 failed'    
		
	output_file_path = os.path.join(output_path, 'ResultL1.csv')

	try:
		output_fp = open(output_file_path, 'w+')
	except IOError:
		print "IO errorCheck the output File: ", output_file_path
		return 'L1 failed'
	except Error:
		print "Unexpected Open Error: ", output_file_path
		output_fp.close()
		return 'L1 failed'    
		
	n = 0
	L1_total = []
	for row in L1_csv:
		L1_total.append(row)
		n = n + 1
	#n = len(L1_total)

	date = []
	Fs = np.zeros(n)
	Fc = np.zeros(n)
	Fsc = np.zeros(n)
	LEs = np.zeros(n)
	LEc = np.zeros(n)
	LEsc = np.zeros(n)
	Hs = np.zeros(n)
	Hc = np.zeros(n)
	Hsc = np.zeros(n)
	agc = np.zeros(n)
	rsdn = np.zeros(n)
	net_rad = np.zeros(n)
	Ta = np.zeros(n)
	h2o = np.zeros(n)
	co2 = np.zeros(n)
	press = np.zeros(n)
	iustar = np.zeros(n)
	ustar = np.zeros(n)
	Tak = np.zeros(n)
	Rv = 461.51
	i = 0
	for row in L1_total:
		date.append(str(row[0]))
		Ta[i] = float(row[8])
		h2o[i] = float(row[9])
		co2[i] = float(row[10])
		rsdn[i] = float(row[13])
		press[i] = float(row[18])
		Hc[i] = float(row[23])
		LEc[i] = float(row[24])
		Fc[i] = float(row[25])
		ustar[i] = float(row[26])
		agc[i] = float(row[28])
		Tak[i] = Ta[i] + 273.15
		i = i + 1
	## Define constants for spike detection
	#Determined from option window
	#thrsh = 4.5       # threshold for removing spike using median
	#AGC_condition = False  	# T/F: Use/Non-Use of AGC value for spike detection
	
	st_storage = True        	# T/F: Use/Non-Use of storage fluxes

	bad = 9999.9      # bad value
	bad2 = -9999.9   # bad value
	#Determined from option window
	#zm = 20           # measurement height
	rsdn_limit = 1.0  # Rdsn for night-daytime separation
	avgtime = 30      # averaging time (minutes)
	num_day = 28         # date processing period as the # of days (28 -> 28 days)
	num_point_per_day = 48          # number of data points per day (48 -> 30 min avg time)
	#num_point_per_day = 24          # number of data points per day (24 -> 1hour avg time)
	
	#determine num_point_per_day automatically . using datetime module
	#
	#

	#upper_co2 = 850.0 # upper limit of CO2 concent.(mg/m3)
	#upper_h2o = 45.0  # upper limit of H2O concent. (g/m3)
	#upper_Ta = 40.0   # upper limit of air temperature (oC)
	#lower_Fc = -2.0   # lower limit of daytime CO2 flux (mg/m2/s)
	#lower_LE = -50    # lower limit of LE (W/m2)
	#lower_H = -50     # lower limit of H (W/m2)
	#upper_Fc = 0.35   # upper limit of nighttime CO2 flux (mg/m2/s)
	#upper_LE = 550    # upper limit of LE (W/m2)
	#upper_H = 550     # upper limit of H (W/m2)
	#upper_agc = 95.0  # upper limit of AGC value
	#ustar_limit = 0.03# minimum ustar for filtering out nighttime fluxes
	#Fc_limit = 0.005  # lower limit of Re (ecosystem respiration) (mg/m2/s)
	#gap_limit = 0.025 # 0.025 --> 95# confidence interval
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
	
	#    ## Parameters for plotting
	#    year0 = 2008
	#    xlim = [year0:year0+1]         # plotting range
	#    dt = 0.5/24/365                # 30 min (0.5 hour)
	#    time = [0:n-1]*dt + year0      # construct time array
	#    xticks = {'Jan','Feb','Mar','Apr','May','Jun', \
	#        'Jul','Aug','Sep','Oct','Nov','Dec'}
	#    xinterval= 1/12
	#    titles = mat2str(year0)
	#    scrsz = [100, 500, 2030, 1110]"""

	# PROCESSING DATA
	# calculation of storage fluxes using backward differentiation

	for i in range(1,n):
		try:
			#Fs
			if((isnan(co2[i]) == True) or (isnan(co2[i-1]) == True)):
				Fs[i] = float(0.0)
			else:
				Fs[i] = float((co2[i] - co2[i-1]) / (avgtime * 60) * zm)


			#LEs
			if((isnan(h2o[i]) == True) or (isnan(h2o[i-1]) == True)):
				LEs[i] = float(0.0)
			else:
				LEs[i] = float((h2o[i] - h2o[i-1]) / (avgtime * 60) * zm)
				LEs[i] = LEs[i] * 1000 / Rv / Tak[i] * 100

			#Hs
			if((isnan(Ta[i]) == True) or (isnan(Ta[i-1]) == True)):
				Hs[i] = float(0.0)
			else:
				Hs[i] = float((Ta[i] - Ta[i-1]) / (avgtime * 60) * zm)
		except ZeroDivisionError:
			print 'L1;ZeroDivisionError;', i
	for i in range(1,n):
		if(fabs(Hs[i]) > upper_H):
			Hs[i] = 0.0


		if(fabs(LEs[i]) > upper_LE):
			LEs[i] = 0.0

		if(fabs(Fs[i]) > upper_Fc):
			Fs[i] = 0.0


	Fs[0] = Fs[1]
	LEs[0] = LEs[1]
	Hs[0] = Hs[1]

	for i in range(n):
		if(fabs(Fs[i]) >= bad):
			Fs[i] = float('NaN')


		if(fabs(co2[i]) >= bad):
			co2[i] = float('NaN')
		if(fabs(h2o[i]) >= bad):
			h2o[i] = float('NaN')
		if(fabs(Ta[i]) >= bad):
			Ta[i] = float('NaN')

	for i in range(n):
		if((isnan(ustar[i]) == True) and (ustar[i] < ustar_limit)):
			iustar[i] = 1
		else:
			iustar[i] = 0


	#--------------------------------------------------------------------------
	if(st_storage == True):
		for i in range(n):
			if(Fc[i] <= bad2):
				Fc[i] = float('NaN')
			if(LEc[i] <= bad2):
				LEc[i] = float('NaN')
			if(Hc[i] <= bad2):
				Hc[i] = float('NaN')

		Fsc = copy.deepcopy(Fc + Fs)
		LEsc = copy.deepcopy(LEc)
		Hsc = copy.deepcopy(Hc)
	else:
		for i in range(n):
			if(fabs(Fc[i]) <= bad2):
				Fc[i] = float('NaN')
		Fsc = copy.deepcopy(Fc)
		LEsc = copy.deepcopy(LEc)
		Hsc = copy.deepcopy(Hc)

	for i in range(n):
		if(Fsc[i] <= bad2):
			Fsc[i] = float('NaN')
		if(LEsc[i] <= bad2):
			LEsc[i] = float('NaN')
		if(Hsc[i] <= bad2):
			Hsc[i] = float('NaN')
		if(agc[i] <= bad2):
			agc[i] = float('NaN')
		if(co2[i] <= bad2):
			co2[i] = float('NaN')
		if(h2o[i] <= bad2):
			h2o[i] = float('NaN')
		if(Ta[i] <= bad2):
			Ta[i] = float('NaN')
		if(ustar[i] <= bad2):
			ustar[i] = float('NaN')
	
	#--------------------------------------------------------------------------

	itime=np.ones(n)     # time index (1--> day 0--> night)
	for i in range(n):
		if((rsdn[i] < rsdn_limit) and ((((i+1) % num_point_per_day) < 16) or (((i+1) % num_point_per_day) > 34))):# nighttime condition
			itime[i] = 0
	#for i in range(n):
	#	if((rsdn[i] < rsdn_limit) and ((((i+1) % num_point_per_day) < 8) or (((i+1) % num_point_per_day) > 17))):# nighttime condition
	#		itime[i] = 0

	#--------------------------------------------------------------------------
	num_segment = num_point_per_day * num_day
	num_avg = int(n / num_segment)

	if(st_agc_condition == True):
		j1 = 0
	else:
		j1 = 1
	j2 = 2
	j3 = 3
	j4 = 4
	j5 = 5
	j6 = 6


	x1 = []
	d2 = np.zeros((n, 7))
	for j in range(j1, j6+1):
		if(j == 0):
			x1 = copy.deepcopy(agc)
		if(j == 1):
			x1 = copy.deepcopy(co2)
		if(j == 2):
			x1 = copy.deepcopy(Fsc)
		if(j == 3):
			x1 = copy.deepcopy(h2o)
		if(j == 4):
			x1 = copy.deepcopy(LEsc)
		if(j == 5):
			x1 = copy.deepcopy(Ta)
		if(j == 6):
			x1 = copy.deepcopy(Hsc)

		if(j == 0):
			for i in range(n):
				d2[i][j] = x1[i]
		else:
			for i in range(1, n-1):
				d2[i][j] = (x1[i] - x1[i-1]) - (x1[i+1] - x1[i])

			d2[0][j] = d2[1,j]
			d2[n-1][j] = d2[n-2,j]
		x1 = []
	index = np.zeros(n)
	index2 = np.zeros(n)
	index3 = np.zeros(n)

	nsp = np.zeros((num_avg, j6 + 1))
	nsp2 = np.zeros((num_avg, j6 + 1))
	nsp3 = np.zeros((num_avg, j6 + 1))

	##
	# Main Body:
	# Removig spikes in observed CO2 concentration and CO2 fluxes

	for main_j in range(num_avg):       # loop for segments
		
		seg_start_i = main_j * num_segment
		seg_fin_i = seg_start_i + num_segment - 1
		if((seg_start_i + 2 * num_segment) > n):
			seg_fin_i = n
		
		for j in range(j1, j2+1):           # loop for different variables for CO2 fluxes
			
			index = np.zeros(n)
			d = np.zeros(n)
			dd = []

			for l in range(n):
				d[l] = d2[l][j]
			

			if(j == 0):
				Md = spstats.stats.nanmedian(d)
				d_new = np.zeros(len(d))
				for i in range(len(d)):
					d_new[i] = fabs(d[i])
				MAD = spstats.stats.nanmedian(d_new)
				cr = float(thrsh / 0.6745) * MAD
				for i in range(seg_start_i, seg_fin_i):
					if ((d2[i][j] < Md - cr) or (d2[i][j] > Md + cr)):
						index[i] = 1
					elif(fabs(d2[i][j]) >= upper_agc):
						index[i] = 1
					
					if(index[i] == 1):
						agc[i]   = float('NaN')
						nsp[main_j][j] = nsp[main_j][j] + 1
						
				index2 = copy.deepcopy(index)

			else:
				Md = np.zeros(2)
				MAD = np.zeros(2)
				cr = np.zeros(2)
				for k in range(2):       # day-night separation (1: nighttime / 2: daytime)
					if(k == 0):
						main_k = 0
						for i in range(seg_start_i, seg_fin_i):
							if(j == 2):
								if(Fsc[i] >= upper_Fc):
									index[i] = 1
									

								if(fabs(Fsc[i]) >= bad):
									index[i] = 1
									
								
									

							if (itime[i] == 0):    # nighttime condition
								dd.append(float(d[i]))
					
						Md[k] = spstats.stats.nanmedian(dd)
						ddd = np.zeros(len(dd))
						for l in range(len(dd)):
							ddd[l] = fabs(dd[l] - Md[k])
						MAD[k] = spstats.stats.nanmedian(ddd)
						cr[k] = float(thrsh / 0.6745) * MAD[k]
						
						
						
						for i in range(seg_start_i, seg_fin_i):
							if (itime[i]==0):    # nighttime condition
								if((d2[i][j] < (Md[k] - cr[k])) or (d2[i][j] > (Md[k] + cr[k]))):
									index[i] = 1
									
									nsp[main_j][j] = nsp[main_j][j] + 1
						

								if(isnan(d2[i][j]) == True):
									index[i] = 1
									nsp[main_j][j] = nsp[main_j][j] + 1
									
					else:
						main_k = 0
						for i in range(seg_start_i, seg_fin_i):
							if(j == 1):
								if(co2[i] >= upper_co2):
									index[i] = 1
									
								

							elif(j == 2):
								if(Fsc[i] <= lower_Fc):
									index[i] = 1
									

							if (itime[i] == 1):    # daytime condition
								dd.append(float(d[i]))

						Md[k] = spstats.stats.nanmedian(dd)
						ddd = np.zeros(len(dd))
						for l in range(len(dd)):
							ddd[l] = fabs(dd[l] - Md[k])
						MAD[k] = spstats.stats.nanmedian(ddd)
						cr[k] = float(thrsh / 0.6745) *MAD[k]

						for i in range(seg_start_i, seg_fin_i):
							if (itime[i] == 1):    # daytime condition
								if((d2[i][j] < (Md[k] - cr[k])) or (d2[i][j] > (Md[k] + cr[k]))):
									index[i] = 1
									nsp[main_j][j] = nsp[main_j][j] + 1
									
								

								if(isnan(d2[i][j]) == True):
									index[i] = 1
									nsp[main_j][j] = nsp[main_j][j] + 1
								
								
									

					if(k == 0):
						d = np.transpose(d)
				ka = 0
				for i in range(seg_start_i, seg_fin_i):
					if(index[i] == 1):
						if(i > 938 and main_j == 0):
							ka = ka + 1
						if(j == 1):
							co2[i] = float('NaN')
						elif(j == 2):
							
							Fsc[i] = float('NaN')


	# Loop for different variables for H2O fluxes

		for j in range(j3, j4+1):
			d = np.zeros(n)
			index2 = np.zeros(n)
			dd = []
			for l in range(n):
				d[l] = copy.deepcopy(d2[l][j])
			Md = np.zeros(2)
			MAD = np.zeros(2)
			cr = np.zeros(2)


			# day-night separation (1: nighttime / 2: daytime)
			for k in range(2):
				if (k==1):
					main_k = 0
					for i in range(seg_start_i, seg_fin_i):
						if(j == 4):
							if(LEsc[i] >= upper_LE):
								index2[i] = 1

							if(abs(LEsc[i]) >= bad):
								index2[i] = 1
								
						if (itime[i] == 0):    # nighttime condition
							dd.append(float(d[i]))

					Md[k] = spstats.stats.nanmedian(dd)
					ddd = np.zeros(len(dd))
					for l in range(len(dd)):
						ddd[l] = fabs(dd[l] - Md[k])
					MAD[k] = spstats.stats.nanmedian(ddd)
					cr[k] = float(thrsh / 0.6745) *MAD[k]
					#print Md[k]
					for i in range(seg_start_i, seg_fin_i):
						if (itime[i] == 0):    # nighttime condition
							if((d2[i][j] < (Md[k] - cr[k])) or (d2[i][j] > (Md[k] + cr[k]))):
								index2[i] = 1
								nsp2[main_j][j] = nsp2[main_j][j] + 1
							if(isnan(d2[i][j]) == True):
								index2[i] = 1
								nsp2[main_j][j] = nsp2[main_j][j] + 1

				else:
					main_k = 0
					for i in range(seg_start_i, seg_fin_i):
						if(j == 3):
							if(h2o[i] >= upper_h2o):
								index2[i] = 1
						elif(j == 4):
							if(LEsc[i] <= lower_LE):
								index2[i] = 1
						if (itime[i] == 1):    # daytime condition
							dd.append(float(d[i]))


					Md[k] = spstats.stats.nanmedian(dd)
					ddd = np.zeros(len(dd))
					for l in range(len(dd)):
						ddd[l] = fabs(dd[l] - Md[k])
					MAD[k] = spstats.stats.nanmedian(ddd)
					cr[k] = float(thrsh / 0.6745) *MAD[k]
					#print Md[k]
					for i in range(seg_start_i, seg_fin_i):
						if (itime[i] == 1):    # daytime condition
							if ((d2[i][j] < Md[k] - cr[k]) or (d2[i][j] > Md[k] + cr[k])):
								index2[i] = 1
								nsp2[main_j][j] = nsp2[main_j][j] + 1
							if(isnan(d2[i][j]) == True):
								index2[i] = 1
								nsp2[main_j][j] = nsp2[main_j][j] + 1

				if(k == 1):
					d = np.transpose(d)

			for i in range(seg_start_i, seg_fin_i):
				if(index2[i] == 1):
					if(j == 3):
						h2o[i] = float('NaN')
					elif(j == 4):
						LEsc[i] = float('NaN')

	# Loop for different variables for sensible heat fluxes

		for j in range(j5, j6 + 1):
			d = np.zeros(n)
			index3 = np.zeros(n)
			dd = []
			Md = np.zeros(2)
			MAD = np.zeros(2)
			cr = np.zeros(2)
			#d = copy.deepcopy(d2[j][:])
			for l in range(n):
				d[l] = copy.deepcopy(d2[l][j])
			# day-night separation (1: nighttime / 2: daytime)
			for k in range(2):
				if (k == 1):
					main_k = 0
					for i in range(seg_start_i, seg_fin_i):
						if(j == 6):
							if(Hsc[i] >= upper_H):
								index3[i] = 1
							if(abs(Hsc[i])>=bad):
								index3[i] = 1
								
						if (itime[i] == 0):    # nighttime condition
							dd.append(float(d[i]))


					Md[k] = spstats.stats.nanmedian(dd)
					ddd = np.zeros(len(dd))
					for l in range(len(dd)):
						ddd[l] = fabs(dd[l] - Md[k])
					MAD[k] = spstats.stats.nanmedian(ddd)
					cr[k] = float(thrsh / 0.6745) *MAD[k]
					#print Md[k]
					for i in range(seg_start_i, seg_fin_i):
						if (itime[i] == 0):    # nighttime condition
							if ((d2[i][j] < Md[k]-cr[k]) or (d2[i][j] > Md[k]+cr[k])):
								index3[i] = 1
								nsp3[main_j][j] = nsp3[main_j][j] + 1
							if(isnan(d2[i][j]) == True):
								index3[i] = 1
								nsp3[main_j][j] = nsp[main_j][j] + 1

				else:
					main_k = 0
					for i in range(seg_start_i, seg_fin_i):
						if(j == 5):
							if(Ta[i] >= upper_Ta):
								index3[i] = 1

						elif(j==6):
							if(Hsc[i]<=lower_H):
								index3[i] = 1

						if (itime[i]==1):    # daytime condition
							dd.append(float(d[i]))


					Md[k] = spstats.stats.nanmedian(dd)
					ddd = np.zeros(len(dd))
					for l in range(len(dd)):
						ddd[l] = fabs(dd[l] - Md[k])
					MAD[k] = spstats.stats.nanmedian(ddd)
					cr[k] = float(thrsh / 0.6745) *MAD[k]
					#print Md[k]
					for i in range(seg_start_i, seg_fin_i):
						if (itime[i]==1):    # daytime condition
							if ((d2[i][j]<Md[k]-cr[k]) or (d2[i][j]>Md[k]+cr[k])):
								index3[i] = 1
								nsp3[main_j][j] = nsp3[main_j][j] + 1
							if(isnan(d2[i][j]) == True):
								index3[i] = 1
								nsp3[main_j][j] = nsp3[main_j][j] + 1
					if(k==1):
						d = np.transpose(d)


			for i in range(seg_start_i, seg_fin_i):
				if(index3[i] == 1):
					if(j == 5):
						Ta[i] = float('NaN')
					elif(j == 6):
						Hsc[i] = float('NaN')

	for i in range(n):
		file_str = StringIO()

		file_str.write(str(date[i]) + ',')			#1
			
		file_str.write(str(Fs[i]) + ',')			#2
		file_str.write(str(Fc[i]) + ',')			#3
		file_str.write(str(Fsc[i]) + ',')			#4
		
		file_str.write(str(Hs[i]) + ',')			#5
		file_str.write(str(Hc[i]) + ',')			#6
		file_str.write(str(Hsc[i]) + ',')			#7
		
		file_str.write(str(LEs[i]) + ',')			#8
		file_str.write(str(LEc[i]) + ',')			#9
		file_str.write(str(LEsc[i]) + ',')			#10
		
		file_str.write(str(co2[i]) + ',')			#11
		file_str.write(str(h2o[i]) + ',')			#12
		file_str.write(str(Ta[i]) + ',')			#13
		file_str.write(str(agc[i]) + ',')			#14
		file_str.write(str(ustar[i]) + ',')			#15
		file_str.write(str(itime[i]) + ',')			#16
		file_str.write(str(iustar[i]) + '\n')		#17
		


		output_string = file_str.getvalue()
		
		output_fp.write(output_string)

		#output_string = str(date[i]) + ',' + \
		#str(Fs[i]) + ',' + str(Fc[i]) + ',' + str(Fsc[i]) + ',' + \
		#str(Hs[i]) + ',' + str(Hc[i]) + ',' + str(Hsc[i]) + ',' + \
		#str(LEs[i]) + ',' + str(LEc[i]) + ',' + str(LEsc[i]) + ',' + \
		#str(co2[i]) + ',' + str(h2o[i]) + ',' + str(Ta[i]) + ',' + \
		#str(ustar[i]) + ',' + str(itime[i]) + ',' + str(iustar[i])+'\n'
		#
		#output_fp.write(output_string)

	input_fp.close()
	output_fp.close()
	return 'L1 Done'
