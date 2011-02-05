# -*- coding: utf-8 -*-
import os, csv, re, time, datetime
import numpy as np
import matplotlib as mpl
mpl.use('wxagg')
import matplotlib.dates as mpldates
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import dircache, re

def Plot_L1(output_path):
	#Load Output Data
	L0_input_path = os.path.join(output_path, 'ResultL0.csv')
	try:
		L0_input_fp = open(L0_input_path, 'r')
	except IOError:
		print "IO errorCheck the input File: ", L0_input_path
		return 'L0 failed'    
	except StandardError:
		print "Unexpected Open Error: ", L0_input_path
		input_fp.close()
		return 'PlotL0 failed'    

	try:
		L0_csv=csv.reader(L0_input_fp, delimiter=',')
	except csv.Error:
		print "Parse ErrorCheck the input File: ", L0_input_path
		return 'L0 failed'    
	except StandardError:
		print "Unexpected Read Error: ", L0_input_path
		return 'L0 failed'    
	
	L1_input_path = os.path.join(output_path, 'ResultL1.csv')
	try:
		L1_input_fp = open(L1_input_path, 'r')
	except IOError:
		print "IO errorCheck the input File: ", L1_input_path
		return 'L1 failed'    
	except StandardError:
		print "Unexpected Open Error: ", L1_input_path
		input_fp.close()
		return 'PlotL1 failed'    

	try:
		L1_csv=csv.reader(L1_input_fp, delimiter=',')
	except csv.Error:
		print "Parse ErrorCheck the input File: ", L1_input_path
		return 'L1 failed'    
	except StandardError:
		print "Unexpected Read Error: ", L1_input_path
		return 'L1 failed'    
	
	L0_total = []
	L1_total = []
	n_L0 = 0
	n_L1 = 0
	
	for row in L0_csv:
		L0_total.append(row)
		n_L0 = n_L0 + 1
	
	for row in L1_csv:
		L1_total.append(row)
		n_L1 = n_L1 + 1
		
	L0_date = []
	L0_Fs = np.zeros(n_L0)
	L0_Fc = np.zeros(n_L0)
	L0_Fsc = np.zeros(n_L0)
	L0_LEs = np.zeros(n_L0)
	L0_LEc = np.zeros(n_L0)
	L0_LEsc = np.zeros(n_L0)
	L0_Hs = np.zeros(n_L0)
	L0_Hc = np.zeros(n_L0)
	L0_Hsc = np.zeros(n_L0)
	L0_agc = np.zeros(n_L0)
	L0_net_rad = np.zeros(n_L0)
	L0_Ta = np.zeros(n_L0)
	L0_h2o = np.zeros(n_L0)
	L0_co2 = np.zeros(n_L0)
	L0_press = np.zeros(n_L0)
	L0_iustar = np.zeros(n_L0)
	L0_ustar = np.zeros(n_L0)
	L0_Tak = np.zeros(n_L0)
	L0_Rv = 461.51
	
	i = 0
	for row in L0_total:
		#L0_date.append(str(row[0]))
		L0_date.append(datetime.datetime.strptime(str(row[0]), "%Y-%m-%d %H:%M"))
		L0_Ta[i] = float(row[8])
		L0_h2o[i] = float(row[9])
		L0_co2[i] = float(row[10])
		L0_net_rad[i] = float(row[11])
		L0_press[i] = float(row[18])
		L0_Hc[i] = float(row[23])
		L0_LEc[i] = float(row[24])
		L0_Fc[i] = float(row[25])
		L0_ustar[i] = float(row[26])
		L0_agc[i] = float(row[28])
		L0_Tak[i] = L0_Ta[i] + 273.15
		i = i + 1

	L1_date = []
	L1_Fs = np.zeros(n_L1)
	L1_Fc = np.zeros(n_L1)
	L1_Fsc = np.zeros(n_L1)
	
	L1_LEs = np.zeros(n_L1)
	L1_LEc = np.zeros(n_L1)
	L1_LEsc = np.zeros(n_L1)
	
	L1_Hs = np.zeros(n_L1)
	L1_Hc = np.zeros(n_L1)
	L1_Hsc = np.zeros(n_L1)
	
	L1_co2 = np.zeros(n_L1)
	L1_h2o = np.zeros(n_L1)
	L1_Ta = np.zeros(n_L1)
	L1_agc = np.zeros(n_L1)
	L1_ustar = np.zeros(n_L1)
	L1_rsdn = np.zeros(n_L1)
	L1_FcPs = np.zeros(n_L1)
	L1_HcPs = np.zeros(n_L1)
	L1_LEcPs = np.zeros(n_L1)
	
	i = 0
	for row in L1_total:
		L1_date.append(datetime.datetime.strptime(str(row[0]), "%Y-%m-%d %H:%M"))
		
		L1_Fs[i] = float(row[1])
		L1_Fc[i] = float(row[2])
		L1_Fsc[i] = float(row[3])
		
		L1_Hs[i] = float(row[4])
		L1_Hc[i] = float(row[5])
		L1_Hsc[i] = float(row[6])
		
		L1_LEs[i] = float(row[7])
		L1_LEc[i] = float(row[8])
		L1_LEsc[i] = float(row[9])
		
		L1_co2[i] = float(row[10])
		L1_h2o[i] = float(row[11])
		L1_Ta[i] = float(row[12])
		L1_agc[i] = float(row[13])
		L1_ustar[i] = float(row[14])
		L1_FcPs[i] = float(L1_Fc[i]+L1_Fs[i])
		L1_HcPs[i] = float(L1_Hc[i]+L1_Hs[i])
		L1_LEcPs[i] = float(L1_LEc[i]+L1_LEs[i])
		
		i = i + 1

	#path check
	plot_path = os.path.join(output_path, 'plotimg')
	#plot_bitmap_path = os.path.join(plot_path, 'bitmap')
	plot_bitmap_path = plot_path
	plot_vector_path = os.path.join(plot_path, 'vector')
	if(os.path.exists(plot_bitmap_path) == False):
		os.mkdir(plot_bitmap_path)
	#if(os.path.exists(plot_vector_path) == False):
	#	os.mkdir(plot_vector_path)
	
	#variable for plotting
	#year0 = int(re.match(r"^(\d{4})[-](\d{2})[-](\d{2}) (\d{1,2})[:](\d{1,2})",L0_date[0]).groups()[0])
	year0 = L1_date[0].year
	upper_co2 = 850.0 # upper limit of CO2 concent.(mg/m3) 
	upper_h2o = 45.0  # upper limit of H2O concent. (g/m3) 
	upper_ta = 40.0   # upper limit of air temperature (oC) 
	lower_Fc = -2.0   # lower limit of daytime_scale CO2 flux (mg/m2/s) 
	lower_LE = -50    # lower limit of LE (W/m2)
	lower_H = -50     # lower limit of H (W/m2)
	upper_Fc = 0.35   # upper limit of nighttime_scale CO2 flux (mg/m2/s)
	upper_LE = 550    # upper limit of LE (W/m2)
	upper_H = 550     # upper limit of H (W/m2)
	upper_agc = 95.0  # upper limit of AGC value
	ustar_limit = 0.03# minimum ustar for filtering out nighttime_scale fluxes 
	Fc_limit = 0.005  # lower limit of Re (ecosystem respiration) (mg/m2/s)
	gap_limit = 0.025 # 0.025 --> 95% confidence interval

	
	time_scale_L1 = mpldates.date2num(L1_date)
	time_scale_L0 = mpldates.date2num(L0_date)
	titles = '$'+'Year \; \ \colon \; \ ' + str(year0) + '$'


	#figure 1
	fig = plt.figure(1)
	fig.suptitle(titles, fontsize=14)
	
	locater = mpldates.MonthLocator(interval = 1)
	formatter = mpldates.DateFormatter('%b')
	
	ax = fig.add_subplot(411)
	plt.ylim(lower_Fc, 1.2)
	ax.set_ylabel('$F_c (mgm^{-2}s^{-1})$', fontsize=7)
	ax.plot_date(time_scale_L1,L1_FcPs,'|', markeredgecolor='k')
	ax.plot_date(time_scale_L1,L1_Fsc,'o', mfc='None', markeredgecolor='r')
	ax.xaxis.set_major_locator(locater)
	ax.xaxis.set_major_formatter(formatter)
	for label in ax.get_xticklabels():
		label.set_fontsize('small')
	for label in ax.get_yticklabels():
		label.set_fontsize('small')
	
	ax = fig.add_subplot(412)
	plt.ylim(550,upper_co2)
	ax.set_ylabel('$CO_2 (mgm^{-3})$', fontsize=7)
	ax.plot_date(time_scale_L0,L0_co2,'|', markeredgecolor='K')
	ax.plot_date(time_scale_L1,L1_co2,'o', mfc='None', markeredgecolor='r')
	ax.xaxis.set_major_locator(locater)
	ax.xaxis.set_major_formatter(formatter)
	for label in ax.get_xticklabels():
		label.set_fontsize('small')
	for label in ax.get_yticklabels():
		label.set_fontsize('small')

	
	ax = fig.add_subplot(413)
	plt.ylim(40,100)
	ax.set_ylabel('$AGC$', fontsize=7)
	ax.plot_date(time_scale_L0,L0_agc,'|', markeredgecolor='k')
	ax.plot_date(time_scale_L1,L1_agc,'o', mfc='None', markeredgecolor='r')
	ax.xaxis.set_major_locator(locater)
	ax.xaxis.set_major_formatter(formatter)
	for label in ax.get_xticklabels():
		label.set_fontsize('small')
	for label in ax.get_yticklabels():
		label.set_fontsize('small')
	
	ax = fig.add_subplot(414)
	plt.ylim(-1,900)
	ax.set_xlabel('$Time (month)$')
	ax.set_ylabel('$Rn (W m^{-2})$', fontsize=7)
	ax.plot_date(time_scale_L0, L0_net_rad,'|', markeredgecolor='k')
	ax.xaxis.set_major_locator(locater)
	ax.xaxis.set_major_formatter(formatter)
	for label in ax.get_xticklabels():
		label.set_fontsize('small')
	for label in ax.get_yticklabels():
		label.set_fontsize('small')
	#plt.savefig(os.path.join(plot_vector_path, 'L1_Figure1.svg'), format = "svg")
	plt.savefig(os.path.join(plot_bitmap_path, 'L1_Figure1.png'), format = "png")
	
	
	#figure 2
	plt.clf()
	fig = plt.figure(2)
	fig.suptitle(titles, fontsize=14)
	
	ax = fig.add_subplot(411)
	plt.ylim(-200,600)
	ax.set_ylabel('$LE (W m^{-2})$', fontsize=7)
	ax.plot_date(time_scale_L1,L1_LEc,'|', markeredgecolor='k')
	ax.plot_date(time_scale_L1,L1_LEsc,'o', mfc='None', markeredgecolor='r')
	ax.xaxis.set_major_locator(locater)
	ax.xaxis.set_major_formatter(formatter)
	for label in ax.get_xticklabels():
		label.set_fontsize('small')
	for label in ax.get_yticklabels():
		label.set_fontsize('small')
	
	ax = fig.add_subplot(412)
	plt.ylim(0,upper_h2o)
	ax.set_ylabel('$Water \ Vapor \ pressure (Pa)$', fontsize=7)
	ax.plot_date(time_scale_L0,L0_h2o,'|', markeredgecolor='k')
	ax.plot_date(time_scale_L1,L1_h2o,'o', mfc='None', markeredgecolor='r')
	ax.xaxis.set_major_locator(locater)
	ax.xaxis.set_major_formatter(formatter)
	for label in ax.get_xticklabels():
		label.set_fontsize('small')
	for label in ax.get_yticklabels():
		label.set_fontsize('small')

	ax = fig.add_subplot(413)
	plt.ylim(40,100)
	ax.set_ylabel('$AGC$', fontsize = 7)
	ax.plot_date(time_scale_L0,L0_agc,'|', markeredgecolor='k')
	ax.plot_date(time_scale_L1,L1_agc,'o', mfc='None', markeredgecolor='r')
	ax.xaxis.set_major_locator(locater)
	ax.xaxis.set_major_formatter(formatter)
	for label in ax.get_xticklabels():
		label.set_fontsize('small')
	for label in ax.get_yticklabels():
		label.set_fontsize('small')
	
	ax = fig.add_subplot(414)
	plt.ylim(-1,900)
	ax.set_xlabel('$Time (month)$')
	ax.set_ylabel('$Rn (W m^{-2})$', fontsize=7)
	ax.plot_date(time_scale_L0, L0_net_rad,'|', markeredgecolor='k')
	ax.xaxis.set_major_locator(locater)
	ax.xaxis.set_major_formatter(formatter)
	for label in ax.get_xticklabels():
		label.set_fontsize('small')
	for label in ax.get_yticklabels():
		label.set_fontsize('small')
		
	#plt.savefig(os.path.join(plot_vector_path, 'L1_Figure2.svg'), format = "svg")
	plt.savefig(os.path.join(plot_bitmap_path, 'L1_Figure2.png'), format = "png")
	
	#figure 3
	plt.clf()
	fig = plt.figure(3)
	fig.suptitle(titles, fontsize=14)
	
	ax = fig.add_subplot(411)
	#plt.xlim(xlim)
	plt.ylim(-200,600)
	ax.set_ylabel('$H (W m^{-2})$', fontsize = 7)
	ax.plot_date(time_scale_L1,L1_HcPs,'|', markeredgecolor='k')
	ax.plot_date(time_scale_L1,L1_Hsc,'o', mfc='None', markeredgecolor='r')
	ax.xaxis.set_major_locator(locater)
	ax.xaxis.set_major_formatter(formatter)
	for label in ax.get_xticklabels():
		label.set_fontsize('small')
	for label in ax.get_yticklabels():
		label.set_fontsize('small')
	
	ax = fig.add_subplot(412)
	#plt.xlim(xlim)
	plt.ylim(-10,upper_ta)
	ax.set_ylabel('$Air\ Temperature (^{\circ}{C})$', fontsize = 7)
	ax.plot_date(time_scale_L0,L0_Ta,'|', markeredgecolor='k')
	ax.plot_date(time_scale_L1,L1_Ta,'o', mfc='None', markeredgecolor='r')
	ax.xaxis.set_major_locator(locater)
	ax.xaxis.set_major_formatter(formatter)
	for label in ax.get_xticklabels():
		label.set_fontsize('small')
	for label in ax.get_yticklabels():
		label.set_fontsize('small')
	
	
	ax = fig.add_subplot(413)
	#plt.xlim(xlim)
	plt.ylim(40,100)
	ax.set_ylabel('$AGC$', fontsize = 7)
	ax.plot_date(time_scale_L0,L0_agc,'|', markeredgecolor='k')
	ax.plot_date(time_scale_L1,L1_agc,'o', mfc='None', markeredgecolor='r')
	ax.xaxis.set_major_locator(locater)
	ax.xaxis.set_major_formatter(formatter)
	for label in ax.get_xticklabels():
		label.set_fontsize('small')
	for label in ax.get_yticklabels():
		label.set_fontsize('small')
	
	ax = fig.add_subplot(414)
	plt.ylim(-1,900)
	ax.set_xlabel('$Time (month)$')
	ax.set_ylabel('$Rn (W m^{-2})$', fontsize = 7)
	ax.plot_date(time_scale_L0, L0_net_rad,'|', markeredgecolor='k')
	ax.xaxis.set_major_locator(locater)
	ax.xaxis.set_major_formatter(formatter)
	for label in ax.get_xticklabels():
		label.set_fontsize('small')
	for label in ax.get_yticklabels():
		label.set_fontsize('small')
	
	#plt.savefig(os.path.join(plot_bitmap_path, 'L1_Figure3.svg'), format = "svg")
	plt.savefig(os.path.join(plot_bitmap_path, 'L1_Figure3.png'))
	
	#figure 4
	plt.clf()
	fig = plt.figure(4)
	ax = fig.add_subplot(111)
	fig.suptitle(titles, fontsize=14)
	plt.xlim(4000,4300)
	plt.ylim(-1.0,1.0)
	ax.set_xlabel('$data\; point$')
	ax.set_ylabel('$F_c (mgm^{-2}s^{-1})$')
	ax.plot(L1_FcPs,'-xk')
	ax.plot(L1_Fsc,'or', mfc = 'None')
	#plt.savefig(os.path.join(plot_bitmap_path, 'L1_Figure4.svg'), format = "svg")
	plt.savefig(os.path.join(plot_bitmap_path, 'L1_Figure4.png'))
	
	plt.clf()
	fig = plt.figure(5)
	ax = fig.add_subplot(111)
	fig.suptitle(titles, fontsize=14)
	plt.xlim(4000,4300)
	plt.ylim(-100.0,550.0)
	ax.set_xlabel('$data point$')
	ax.set_ylabel('$LE (Wm^{-2})$')
	ax.plot(L1_LEcPs,'-xk')
	ax.plot(L1_LEsc,'or', mfc = 'None')
	#plt.savefig(os.path.join(plot_bitmap_path, 'L1_Figure5.svg'), format = "svg")
	plt.savefig(os.path.join(plot_bitmap_path, 'L1_Figure5.png'))
	
	return 'Plot_L1 success'

def Plot_L2(output_path):
	Output_filelist = dircache.listdir(output_path)
	Filelist_Plot_L2_1 = []
	for file in Output_filelist:
		if(re.match(r'^Plot\_L2\_1\_(\d{4})[-](\d{2})[-](\d{2}).csv',file) != None):
			Filelist_Plot_L2_1.append(file)
			
	for fname in Filelist_Plot_L2_1:
		Plot_L2_1_input_path = os.path.join(output_path, fname)
		try:
			Plot_L2_1_input_fp = open(Plot_L2_1_input_path, 'r')
		except IOError:
			print "IO errorCheck the input File: ", Plot_L2_1_input_path
			return 'Plot_L2_1 failed'    
		except StandardError:
			print "Unexpected Open Error: ", Plot_L2_1_input_path
			input_fp.close()
			return 'PlotPlot_L2_1 failed'    

		Plot_L2_1_total = []	
		n_Plot_L2_1 = 0	
		
		try:
			Plot_L2_1_csv=csv.reader(Plot_L2_1_input_fp, delimiter=',')
		except csv.Error:
			print "Parse ErrorCheck the input File: ", Plot_L2_1_input_path
			return 'Plot_L2_1 failed'    
		except StandardError:
			print "Unexpected Read Error: ", Plot_L2_1_input_path
			return 'Plot_L2_1 failed'    
	
		
		for row in Plot_L2_1_csv:
			Plot_L2_1_total.append(row)
			n_Plot_L2_1 = n_Plot_L2_1 + 1
		
		Taylor_date = []	
		A = 0
		B = 0
		TC = np.zeros(n_Plot_L2_1)
		PV = np.zeros(n_Plot_L2_1)
		yfit = np.zeros(n_Plot_L2_1)
		
		i = 0
		for row in Plot_L2_1_total:
			Taylor_date.append(datetime.datetime.strptime(str(row[0]), "%Y-%m-%d %H:%M"))
			A = float(row[1])
			B = float(row[2])
			TC[i] = float(row[3])
			PV[i] = float(row[4])
			yfit[i] = float(row[5])
			i = i + 1

		#year0 = int(re.match(r"^(\d{4})[-](\d{2})[-](\d{2}) (\d{1,2})[:](\d{1,2})",date[0]).groups()[0])
		year0 = Taylor_date[0].year
		time_scale = mpldates.date2num(Taylor_date)
		

		#path check
		plot_path = os.path.join(output_path, 'plotimg')
		#plot_bitmap_path = os.path.join(plot_path, 'bitmap')
		plot_bitmap_path = plot_path
		plot_vector_path = os.path.join(plot_path, 'vector')
		if(os.path.exists(plot_bitmap_path) == False):
			os.mkdir(plot_bitmap_path)
		#if(os.path.exists(plot_vector_path) == False):
		#	os.mkdir(plot_vector_path)
		
		locater = mpldates.MonthLocator(interval = 1)
		formatter = mpldates.DateFormatter('%b')
		
		plt.clf()
		fig = plt.figure(1)
		png_fname = re.match(r'^Plot\_L2\_1\_(\d{4}[-]\d{2}[-]\d{2})*',fname).groups()
		titles = '$'+'Beginning \ Date \; \ \colon \; \ ' + png_fname[0]+'$'
		fig.suptitle(titles, fontsize=14)
		ax = fig.add_subplot(111)
		ax.set_xlabel('$air\; temperature (^{\circ}{C})$')
		ax.set_ylabel('$Ecosystem\; respiration(mgm^{-2}s^{-1})$')
		
		ax.plot(TC,PV,'o', mfc='None', markeredgecolor='b')
		ax.plot(TC,yfit,'o', mfc='None', markeredgecolor='r')
		for label in ax.get_xticklabels():
			label.set_fontsize('small')
		for label in ax.get_yticklabels():
			label.set_fontsize('small')
		
		plt.savefig(os.path.join(plot_path, 'L2_Figure_1_'+png_fname[0]+'.png'))
	
	
	Plot_L2_2_input_path = os.path.join(output_path, 'Plot_L2_2.csv')
	try:
		Plot_L2_2_input_fp = open(Plot_L2_2_input_path, 'r')
	except IOError:
		print "IO errorCheck the input File: ", Plot_L2_2_input_path
		return 'Plot_L2_2 failed'    
	except StandardError:
		print "Unexpected Open Error: ", Plot_L2_2_input_path
		input_fp.close()
		return 'PlotPlot_L2_2 failed'    

	try:
		Plot_L2_2_csv=csv.reader(Plot_L2_2_input_fp, delimiter=',')
	except csv.Error:
		print "Parse ErrorCheck the input File: ", Plot_L2_2_input_path
		return 'Plot_L2_2 failed'    
	except StandardError:
		print "Unexpected Read Error: ", Plot_L2_2_input_path
		return 'Plot_L2_2 failed'    
	
	
	Plot_L2_2_total = []
	
	n_Plot_L2_2 = 0
	
	for row in Plot_L2_2_csv:
		Plot_L2_2_total.append(row)
		n_Plot_L2_2 = n_Plot_L2_2 + 1

	date 		= []
	Fsc 		= np.zeros(n_Plot_L2_2)
	Fc_filled 	= np.zeros(n_Plot_L2_2)
	LEsc 		= np.zeros(n_Plot_L2_2)
	LE_filled 	= np.zeros(n_Plot_L2_2)
	Hsc 		= np.zeros(n_Plot_L2_2)
	H_filled 	= np.zeros(n_Plot_L2_2)
	
	i = 0
	for row in Plot_L2_2_total:
		date.append(datetime.datetime.strptime(str(row[0]), "%Y-%m-%d %H:%M"))
		Fsc[i] 			= float(row[1])
		Fc_filled[i] 	= float(row[2])
		LEsc[i] 		= float(row[3])
		LE_filled[i] 	= float(row[4])
		Hsc[i] 			= float(row[5])
		H_filled[i] 	= float(row[6])
		i = i + 1
	
	#year0 = int(re.match(r"^(\d{4})[-](\d{2})[-](\d{2}) (\d{1,2})[:](\d{1,2})",date[0]).groups()[0])
	year0 = date[0].year
	time_scale = mpldates.date2num(date)
	titles = '$'+'Year \; \ \colon \; \ ' + str(year0)+'$'

	plt.clf()
	fig = plt.figure(2)
	fig.suptitle(titles, fontsize=14)
	ax = fig.add_subplot(111)
	plt.ylim(-1.5, 1.5)
	ax.set_ylabel('$F_c (mgm^{-2}s^{-1})$')
	
	plt.plot_date(time_scale,Fsc,'|', markeredgecolor='b')
	plt.plot_date(time_scale,Fc_filled,'o', mfc='None', markeredgecolor='r')
	ax.xaxis.set_major_locator(locater)
	ax.xaxis.set_major_formatter(formatter)
	for label in ax.get_xticklabels():
		label.set_fontsize('small')
	for label in ax.get_yticklabels():
		label.set_fontsize('small')
	plt.savefig(os.path.join(plot_path, 'L2_Figure2.png'))
	
	#figure 3
	plt.clf()
	fig = plt.figure(3)
	fig.suptitle(titles, fontsize=14)
	ax = fig.add_subplot(111)
	plt.ylim(-100, 600)
	ax.set_ylabel('$LE (W m^{-2})$')
	
	plt.plot_date(time_scale,LEsc,'|', markeredgecolor='b')
	plt.plot_date(time_scale,LE_filled,'o', mfc='None', markeredgecolor='r')
	ax.xaxis.set_major_locator(locater)
	ax.xaxis.set_major_formatter(formatter)
	for label in ax.get_xticklabels():
		label.set_fontsize('small')
	for label in ax.get_yticklabels():
		label.set_fontsize('small')
	plt.savefig(os.path.join(plot_path, 'L2_Figure3.png'))
	
	#figure 4
	plt.clf()	
	fig = plt.figure(4)
	fig.suptitle(titles, fontsize=14)
	plt.ylim(-100, 600)
	ax = fig.add_subplot(111)
	ax.set_ylabel('$H (W m^{-2})$')
	
	plt.plot_date(time_scale,Hsc,'|', markeredgecolor='b')
	plt.plot_date(time_scale,H_filled,'o', mfc='None', markeredgecolor='r')
	ax.xaxis.set_major_locator(locater)
	ax.xaxis.set_major_formatter(formatter)
	for label in ax.get_xticklabels():
		label.set_fontsize('small')
	for label in ax.get_yticklabels():
		label.set_fontsize('small')
	plt.savefig(os.path.join(plot_path, 'L2_Figure4.png'))
	
	return 'Plot_L2 success'

#Plot_L1('D:\Project\FLUX PRO\src\output')
#Plot_L2('D:\Project\FLUX PRO\src\output')