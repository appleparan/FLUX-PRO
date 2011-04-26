# -*- coding: utf-8 -*-

import os
import csv
import copy
import datetime
from math import fabs, sqrt, atan, sin, cos, exp, isnan
from cStringIO import StringIO
import numpy as np
from scipy import linalg as lin
#import FLUXPRO_Common as Common

class L0:
	
	"""	
	Docstring for class L0.
	"""
	
	def __init__(self):
		
		"""
		constructor		
		"""
		#Provided in option
		self.num_day_per_segment = 28
		
		self.num_var_eddy = 53                	# number of variable(eddy)
		self.num_var_met = 30                 	# number of variable(met)
		self.num_direction = 8					# number of wind direction                  

		self.wdc = [0.0, 45.0, 90.0, 135.0, 180.0, 225.0, 270.0, 315.0, 360.0]
		
		#Unique absorption coefficent for water vapor (m^3 / (g cm))
		self.KW = -0.150	
		
		# state_variable
		self.st_PFR_method = True
		self.st_third_rotation = False
		self.st_double_rotation = False
		self.st_quality = False
		self.st_agc = True
		self.st_O2 = False				#Flag for oxygen corrction of KH20

		self.st_error = False

		self.dim_p = (self.num_direction, 3, 3)
		self.dim_b_and_c = (self.num_direction, 3)
		self.dim_xcov = (4, 3)

		# array
		self.p = np.zeros(self.dim_p)
		self.a = np.zeros(3)
		self.b = np.zeros(self.dim_b_and_c)
		self.c = np.zeros(self.dim_b_and_c)
		self.um = np.zeros(3)
		self.su = np.zeros(4)
		self.xcov = np.zeros(self.dim_xcov)
		self.rflx = np.zeros(4)

		# variable initialize
		self.Ta             = 0.0
		self.ea             = 0.0
		self.co2            = 0.0
		self.net_radiation  = 0.0
		self.g              = 0.0
		self.press          = 0.0
		self.prec           = 0.0
		self.rh39m          = 0.0
		self.airt39m        = 0.0
		self.wind39m        = 0.0
		self.qt             = 0.0
		self.vdf            = 0.0
		self.pa             = 0.0
		self.ga             = 0.0
		self.gc             = 0.0
		self.gi             = 0.0
		self.gr             = 0.0
		self.omega          = 0.0
		self.rho_a          = 0.0
		self.rho_v          = 0.0
		self.rho            = 0.0
		self.uv             = 0.0
		self.uw             = 0.0
		self.vw             = 0.0
		self.ut             = 0.0
		self.vt             = 0.0
		self.wt             = 0.0
		self.uq             = 0.0
		self.vq             = 0.0
		self.wq             = 0.0
		self.uc             = 0.0
		self.vc             = 0.0
		self.wc             = 0.0
		self.wd             = 0.0
		self.wbar           = 0.0
		self.mean           = 0.0
		self.zeta           = 0.0
		self.ustar          = 0.0
		self.agc            = 0.0
		self.num_used_data  = 0.0

		self.hm             = 0.0
		self.d0             = 0.0
		self.zm             = 0.0

		self.raw_data_input_eddy = []
		self.raw_data_input_met = []
		self.output_fp = 0

	def init_var(self):
		
		"""
		Initialize variable on every loop		
		"""
		
		self.xcov = np.zeros(self.dim_xcov)
		self.a = np.zeros(3)
		self.um = np.zeros(3)
		self.su = np.zeros(4)
		self.uv         = 0.0
		self.uw         = 0.0
		self.vw         = 0.0
		self.ut         = 0.0
		self.vt         = 0.0
		self.wt         = 0.0
		self.uq         = 0.0
		self.vq         = 0.0
		self.wq         = 0.0
		self.uc         = 0.0
		self.vc         = 0.0
		self.wc         = 0.0

	def load_option(self, PFR, double, third, agc, hm, d0, zm):
		
		"""
		load L0 option value 		
		"""
		
		self.st_PFR_method = PFR
		self.st_double_rotation = double
		self.st_third_rotation = third
		self.st_agc = agc
		self.hm = hm
		self.d0 = d0
		self.zm = zm

	def L0_main(self, path_eddy, path_met, output_dir_path):

		"""
		L0's main function
		
		Keyword arguments:
		path_eddy 		: eddy data input file path
		path_met 		: met data input file path
		output_dir_path : output directory path
		
		Return: 
		'L0 Done'		: If L0 done successfully
		'L0 Failed' 	: If L0 did not done successfully
		"""
		
		# Input and output file open

		output_dir_path = output_dir_path
		output_value_error_log_path = os.path.join(output_dir_path, \
												'L0ValueError.log')
		output_path = os.path.join(output_dir_path, \
												'ResultL0.csv')
		
		try:
			self.output_fp = open(output_path, 'w+')
			self.output_log = open(output_value_error_log_path, 'w+')
		except IOError:
			print 'IOError;Check Output File: ', self.output_path
			return 'L0 failed'

		input_eddy_path = path_eddy
		input_met_path = path_met

		print 'File name : '
		print '   ', input_eddy_path
		print '   ', input_met_path

		try:
			self.input_eddy_fp = open(input_eddy_path, 'r')
		except IOError:
			print "IO error;Check the input File: ", input_eddy_path
			return 'L0 failed'
			
		try:
			self.input_met_fp = open(input_met_path, 'r')
		except IOError:
			print "IO error;Check the input File: ", input_met_path
			return 'L0 failed'

		# read data from input file
		try:
			csv_data_input_eddy = csv.reader(self.input_eddy_fp, \
			delimiter = '\t', quotechar = '#')
		except csv.Error:
			print "Parse Error;Check the input File: ", input_eddy_path
		
		try:
			csv_data_input_met = csv.reader(self.input_met_fp, \
			delimiter = '\t', quotechar = '#')
		except csv.Error:
			print "Parse Error;Check the input File: ", input_met_path
			
		# load data 
		raw_data_input_met = []
		raw_data_input_eddy = []
		for row in csv_data_input_met:
			raw_data_input_met.append(row)
		for row in csv_data_input_eddy:
			raw_data_input_eddy.append(row)

		raw_data_input_eddy = self.data_check(raw_data_input_eddy)
		raw_data_input_met = self.data_check(raw_data_input_met)
		
		self.input_eddy_fp.close()
		self.input_met_fp.close()

		num_row = 1

		#determine num_point_per_day automatically . using datetime module
		date_1st = datetime.datetime.strptime(raw_data_input_met[0][0], "%Y-%m-%d %H:%M")
		date_2nd = datetime.datetime.strptime(raw_data_input_met[1][0], "%Y-%m-%d %H:%M")
		date_diff = date_2nd - date_1st
		self.avgtime = int(date_diff.seconds / 60) # averaging time (minutes)
		self.num_point_per_day = 1440 / self.avgtime # number of data points per day (1440 : minutes of a day)
		
		# Divide the data every segment (e. g. 28 days) only in PFR method
		# factor using dividing segment
		self.num_data_segment = 60 / self.avgtime * 24 \
								* self.num_day_per_segment
		# for handling last segment
		lim_data_segment = int(csv_data_input_eddy.line_num \
								/ self.num_data_segment) + 1
		# count current data segment number
		cur_data_segment = 0

		if(self.st_PFR_method):
			for cur_data_segment in range(lim_data_segment):
				if(cur_data_segment < lim_data_segment - 1):
					line_limit = \
						(cur_data_segment + 1) * self.num_data_segment
				else:
					line_limit = csv_data_input_eddy.line_num

				self.p = np.zeros(self.dim_p)
				self.b = np.zeros(self.dim_b_and_c)
				self.c = np.zeros(self.dim_b_and_c)
				self.um = np.zeros(3)
				
				
				# Read and compute pfr_wd and pmatrix method
				for row_cnt in range(cur_data_segment * \
					self.num_data_segment, \
					line_limit):

					row_eddy = raw_data_input_eddy[row_cnt]
					row_met = raw_data_input_met[row_cnt]
					if(len(row_eddy) < self.num_var_eddy):
						for i in range(self.num_var_eddy - len(row_eddy)):
							row_eddy.append(float('-9999.9'))
					if(len(row_met) < self.num_var_met):
						for i in range(self.num_var_met - len(row_met)):
							row_met.append(float('-9999.9'))

					for i in range(1, len(row_eddy)):
						row_eddy[i] = float(row_eddy[i])
						if(fabs(row_eddy[i]) >= 99999):
							row_eddy[i] = 9999.9

					self.read_line(input_eddy_path, input_met_path,\
					row_eddy, row_met, row_cnt)

					num_row = num_row + 1

					# to handle remainder, divide two cases
					# general case
					
					if(self.st_quality == False):
						return_wd = self.pfr_wd(self.wd)
						self.pmatrix(return_wd)
				
				for i in range(self.num_direction):
					self.pf_method(i)
				
				for row_cnt in range(cur_data_segment * \
					self.num_data_segment, \
					line_limit):
					row_eddy = raw_data_input_eddy[row_cnt]
					row_met = raw_data_input_met[row_cnt]
					
					if(len(row_eddy) < self.num_var_eddy):
						for i in range(self.num_var_eddy - len(row_eddy)):
							row_eddy.append(float('-9999.9'))
					if(len(row_met) < self.num_var_met):
						for i in range(self.num_var_met - len(row_met)):
							row_met.append(float('-9999.9'))

					for i in range(1, len(row_eddy)):
						row_eddy[i] = float(row_eddy[i])
						if(fabs(row_eddy[i]) >= 99999):
							row_eddy[i] = 9999.9

					self.init_var()
					self.read_line(input_eddy_path, input_met_path,\
					row_eddy, row_met, row_cnt)	

					return_wd = self.pfr_wd(self.wd)
					self.pfrotation(return_wd, num_row)
					self.wpl()
					self.qcontrol(num_row)
					self.conductance(num_row)
					self.output()
		# end of st_PFR_emthod=True

		else:
			for row_cnt in range(len(raw_data_input_eddy)):
				row_eddy = raw_data_input_eddy[row_cnt]
				row_met = raw_data_input_met[row_cnt]
				
				if(len(row_eddy) < self.num_var_eddy):
					for i in range(self.num_var_eddy - len(row_eddy)):
						row_eddy.append(float('-9999.9'))
				if(len(row_met) < self.num_var_met):
					for i in range(self.num_var_met - len(row_met)):
						row_met.append(float('-9999.9'))
						
				for i in range(1, len(row_eddy)):
					row_eddy[i] = float(row_eddy[i])
					if(fabs(row_eddy[i]) >= 99999):
						row_eddy[i] = 9999.9

				self.init_var()
				self.read_line(input_eddy_path, input_met_path, \
				row_eddy, row_met, row_cnt)

				self.rotation12(num_row)

				if(self.st_third_rotation == True):
					self.rotation3()
				self.wpl()
				self.qcontrol(num_row)
				self.conductance(num_row)
				self.output()
		# end end of st_PFR_emthod=False

		
		self.output_fp.close()
		self.output_log.close()
		if(self.st_error == True):
			print 'Value error appeared;see [L0ValueError.log]'
		return 'L0 Done'

	
	def data_check(self, raw_data):
		
		"""
		Treat nan and inf value
		
		Keyword arguments:
		@param raw_data : raw data read from input file
		
		Returns:
		@return raw_data : data that nan and inf values are removed 
		"""
		
		for row_cnt in range(len(raw_data)):
			for item_cnt in range(len(raw_data[row_cnt])):
				if(raw_data[row_cnt][item_cnt] == 'Nan' or \
				raw_data[row_cnt][item_cnt] == 'NAN' or \
				raw_data[row_cnt][item_cnt] == 'nan'):
					raw_data[row_cnt][item_cnt] = '-9999.9'

				if(raw_data[row_cnt][item_cnt] == 'Inf' or \
				raw_data[row_cnt][item_cnt] == 'INF' or \
				raw_data[row_cnt][item_cnt] == 'inf'):
					raw_data[row_cnt][item_cnt] = '9999.9'

		return raw_data

	def read_line(self, file_input_eddy, file_input_met, \
	row_eddy, row_met, cnt_row):
		
		"""
		Parsing input data (columns of data are hardcoded)
		
		Keyword arguments:
		@param file_input_eddy		: path of eddy input file 
		@param file_input_met 		: path of met input file
		@param row_eddy 			: a row of eddy raw data
		@param row_met 			: a row of met raw data
		@param cnt_row				: row count
		
		"""
		
		Rv = 461.51
		
		# Check Timestamp
		self.st_quality = False
		try:
			if(row_eddy[0] != row_met[0]):
				self.output_log.write( \
				"inconsistent timestamp in two_files: " +'\t' + \
				str(file_input_eddy) +'\t' + str(file_input_met) +'\t'+ \
				str(cnt_row) +'\n')
				self.st_error = True
			
			elif(abs(int(float(row_eddy[25]))) >= 9999):
				self.output_log.write( \
				"Skip the data due to spike in sonic data" +'\t' + \
				str(file_input_eddy) +'\t'+str(row_eddy[0]) +'\t' + \
				str(row_eddy[25]) +'\t' + str(cnt_row)+'\n')
				self.st_quality = True
				self.st_error = True
				
			elif(abs(int(float(row_eddy[28]))) >= 9999):
				self.output_log.write( \
				"Skip the data due to spike in IRGA data" +'\t' + \
				str(file_input_eddy) +'\t' + str(row_eddy[0]) + '\t' + \
				str(row_eddy[28]) + '\t' + str(cnt_row)+'\n')
				self.st_quality = True
				self.st_error = True
		except IndexError:
			print 'IndexError;Reading data from input file, \
				line number :', cnt_row + 1
			
		try:
			self.date = row_eddy[0]
			
			if(abs(float(row_eddy[25])) >= 9999 \
			or abs(float(row_eddy[39])) < 1000):            
				self.st_quality = True

			self.um[0] = float(row_eddy[25])
			self.um[1] = float(row_eddy[26])
			self.um[2] = float(row_eddy[27])
		except IndexError:
			print 'IndexError;Reading data from input file(Eddy data). \
				line number : ', cnt_row + 1
		
		try:
			self.su[0] = sqrt(float(row_eddy[13]))
		except ValueError:
			print 'Value Error;Read data;Check Input data :date, cv_Ux_Ux'
		except IndexError:
			print 'IndexError;Reading data from input file(Eddy data). \
			line number : ', cnt_row + 1
		
		try:
			self.su[1] = sqrt(float(row_eddy[18]))
		except ValueError:
			print 'Value Error;Read data;Check Input data :date, cv_Uy_Uy'
		except IndexError:
			print 'IndexError;Reading data from input file(Eddy data). \
			line number : ', cnt_row + 1
			
		try:
			self.su[2] = sqrt(float(row_eddy[7]))
		except ValueError:
			print 'Value Error;Read data;Check Input data :date, cv_Uz_Uz'
		except IndexError:
			print 'IndexError;Reading data from input file(Eddy data). \
			line number : ', cnt_row + 1
			
		try:
			self.su[3] = sqrt(float(row_eddy[24]))
		except ValueError:
			print 'Value Error;Read data;Check Input data :date, cv_Ts_Ts'
		except IndexError:
			print 'IndexError;Reading data from input file(Eddy data). \
			line number : ', cnt_row + 1
		try:
			self.xcov[0][0] = float(row_eddy[8])
			self.xcov[0][1] = float(row_eddy[14])
			self.xcov[0][2] = float(row_eddy[9])

			self.xcov[1][0] = float(row_eddy[17])
			self.xcov[1][1] = float(row_eddy[21])
			self.xcov[1][2] = float(row_eddy[12])

			self.xcov[2][0] = float(row_eddy[15])
			self.xcov[2][1] = float(row_eddy[19])
			self.xcov[2][2] = float(row_eddy[10])

			self.xcov[3][0] = float(row_eddy[16])
			self.xcov[3][1] = float(row_eddy[20])
			self.xcov[3][2] = float(row_eddy[11])

			self.co2 = float(row_eddy[28])
			# Unit conversion from "kPa" to "hPa"
			if(float(row_eddy[31]) != 99999):
				self.press = float(row_eddy[31]) * 10			

			if(self.st_quality == False):
				self.Ta = float(row_eddy[30])
				self.ea = (float(row_eddy[29]) / 1000) * Rv * \
							(self.Ta + 273.15) / 100
			else:
				self.Ta = 9999.9
				self.ea = 9999.9

			# Rainfall
			self.prec = 0
			self.prec = (float(row_eddy[51]) + float(row_eddy[52])) / 2.0
			if(float(row_eddy[51]) == -9999.9 and \
				float(row_eddy[52]) == -9999.9):
				self.prec = 0.0
			
			# Wind direction
			self.wd = float(row_eddy[33])
			
			# Total number of data used in calculting statistics
			self.num_used_data = float(row_eddy[39])
			
			# AGC value from LI7500
			self.agc = float(row_eddy[50])
		except IndexError:
			print 'IndexError;Reading data from input file(Eddy data). \
			line number : ', cnt_row + 1
		
		try:
			# Net radiation
			self.net_radiation = float(row_met[10] )

			# PAR
			self.qt = float(row_met[30])

			self.rflx[0] = float(row_met[3])
			self.rflx[1] = float(row_met[5])
			self.rflx[2] = float(row_met[4])
			self.rflx[3] = float(row_met[6])

			# must be modified
			self.g = float(row_met[10]) / 10.0
		except IndexError:
			print 'IndexError;Reading data from input file(MET data) \
			line number : ', cnt_row + 1


	def check_p(self):
		
		"""
		Check P Matrix
		"""
		
		for i in range(0, self.num_direction):
			if(self.p[i][0][0] < 0.0):
				print "P Matrix Warning; \
					small number of data in p matrix: idx, p"
				print i, self.p[i][0][0]
				return 'L0 failed'
				#sys.exit()

	
	def pfr_wd(self, wd):
		"""
		Determine PFR_Method Wind direction
		
		Keyword arguments:
		@param wd : wind direction
		"""
		return_wd_idx = -1

		if( wd >= self.wdc[0] and wd < self.wdc[1]):
			return_wd_idx = 0
		elif( wd >= self.wdc[1] and wd < self.wdc[2]):
			return_wd_idx = 1
		elif( wd >= self.wdc[2] and wd < self.wdc[3]):
			return_wd_idx = 2    
		elif( wd >= self.wdc[3] and wd < self.wdc[4]):
			return_wd_idx = 3    
		elif( wd >= self.wdc[4] and wd < self.wdc[5]):
			return_wd_idx = 4    
		elif( wd >= self.wdc[5] and wd < self.wdc[6]):
			return_wd_idx = 5    
		elif( wd >= self.wdc[6] and wd < self.wdc[7]):
			return_wd_idx = 6       
		elif( wd >= self.wdc[7] and wd < self.wdc[8]):
			return_wd_idx = 7    

		return return_wd_idx

	
	def pmatrix(self, wd):
		
		"""
		P matrix Operation
		
		Keyword arguments:
		@param wd : wind direction
		"""
		
		self.p[wd][0][0] = self.p[wd][0][0] + 1.0
		self.p[wd][0][1] = self.p[wd][0][1] + self.um[0]
		self.p[wd][0][2] = self.p[wd][0][2] + self.um[1]
		self.p[wd][1][0] = self.p[wd][0][1]
		self.p[wd][1][1] = self.p[wd][1][1] + self.um[0] * self.um[0]
		self.p[wd][1][2] = self.p[wd][1][2] + self.um[0] * self.um[1]
		self.p[wd][2][0] = self.p[wd][0][2]
		self.p[wd][2][1] = self.p[wd][1][2]
		self.p[wd][2][2] = self.p[wd][2][2] + self.um[1] * self.um[1]
		
		
		self.c[wd][0] = self.c[wd][0] + self.um[2]
		self.c[wd][1] = self.c[wd][1] + self.um[0] * self.um[2]
		self.c[wd][2] = self.c[wd][2] + self.um[1] * self.um[2]

	
	def pf_method(self, wd):
		
		"""
		Do PF method
		
		Keyword arguments:
		@param wd : wind direction
		"""
		
		dim_lu = (3 , 3)
		lu = np.zeros(dim_lu)
		piv = np.zeros(3)
		solution = np.zeros(3)
		
		# Copy object from c to b (wd are determined from pfr_wd)
		# Preservation of c values
		self.b[wd] = copy.deepcopy(self.c[wd])
		try:
			# LU Decomposition for the least square method
			lu, piv = lin.lu_factor(self.p[wd])
			# LU Backsubstitution for getting "b" values
			solution = lin.lu_solve((lu, piv), self.b[wd])
		except ZeroDivisionError:
			print 'ZeroDivisionError;PF_Method'
		except RuntimeWarning, e:
			print 'RuntimeWarning;', e
		
		self.p[wd] = copy.deepcopy(lu)
		self.b[wd] = copy.deepcopy(solution)
		
		# Reference : Eqn.(42) in Wilczak et al.(1000)
		try:
			self.p[wd][2][0] = - self.b[wd][1] / \
				sqrt(self.b[wd][1] * self.b[wd][1] + \
					self.b[wd][2] * self.b[wd][2] + 1.0)
			self.p[wd][2][1] = - self.b[wd][2] / \
				sqrt(self.b[wd][1] * self.b[wd][1] + \
					self.b[wd][2] * self.b[wd][2] + 1.0)
			self.p[wd][2][2] = 1.0 / \
				sqrt(self.b[wd][1] * self.b[wd][1] + \
					self.b[wd][2] * self.b[wd][2] + 1.0)
		except ZeroDivisionError:
			print 'ZeroDivisionError;Pf_Method'
		
		# Reference : Eqn.(44) in Wilczak et al. (1000)
		try:
			sinbeta = -self.p[wd][2][1] / \
				sqrt(self.p[wd][2][1] * self.p[wd][2][1] + \
					self.p[wd][2][2] * self.p[wd][2][2])
			cosbeta =  self.p[wd][2][2] / \
				sqrt(self.p[wd][2][1] * self.p[wd][2][1] + \
					self.p[wd][2][2] * self.p[wd][2][2])
			sinalpha = self.p[wd][2][0]
			cosalpha = sqrt(self.p[wd][2][1] * self.p[wd][2][1] + \
					self.p[wd][2][2] * self.p[wd][2][2])
		except ZeroDivisionError:
			print 'ZeroDivisionError;Pf_Method'
			
		# Calculation of P matrix
		self.p[wd][0][0] = cosalpha
		self.p[wd][0][1] = sinalpha * sinbeta
		self.p[wd][0][2] = - sinalpha * cosbeta
		# Reference : P = (CD)^T Eqn.(26)
		self.p[wd][1][0] = 0.0
		self.p[wd][1][1] = cosbeta
		self.p[wd][1][2] = sinbeta
		
	
	def pfrotation(self, wd, num_row):
		
		"""
		"eta" is angel between the mean streamline and each-run stream line
		Coordinate rotation by Planar Fit Method
		
		Keyword arguments:
		@param wd 		: wind direction
		@param num_row : the number of row 
		"""

		ui = \
				self.p[wd][0][0] * self.um[0] \
			+   self.p[wd][0][1] * self.um[1] \
			+   self.p[wd][0][2] * self.um[2]
		vi = \
				self.p[wd][1][0] * self.um[0] \
			+   self.p[wd][1][1] * self.um[1] \
			+   self.p[wd][1][2] * self.um[2]
		wi = \
				self.p[wd][2][0] * self.um[0] \
			+   self.p[wd][2][1] * self.um[1] \
			+   self.p[wd][2][2] * self.um[2]

		self.um[0] = ui
		self.um[1] = vi
		self.um[2] = wi

		v = np.zeros(3)
		for i in range(3):
			v[i] = \
			(self.p[wd][i][0] ** 2) * (self.su[0] ** 2) \
				+ (self.p[wd][i][1] ** 2) * (self.su[1] ** 2) \
				+ (self.p[wd][i][2] ** 2) * (self.su[2] ** 2) \
				+ 2.0 * \
					(self.p[wd][i][0] * self.p[wd][i][1] * self.xcov[0][1] 	\
					+ self.p[wd][i][1] * self.p[wd][i][2] * self.xcov[0][2] \
					+ self.p[wd][i][2] * self.p[wd][i][0] * self.xcov[0][0])\
				+ (self.p[wd][i][2] ** 2) * (self.b[wd][0] ** 2)
			
			
		# Rotation of vertical turbulent fluxes
		self.uw \
			= self.p[wd][0][0] * self.p[wd][2][0] * self.su[0] * self.su[0] \
			+ self.p[wd][0][1] * self.p[wd][2][1] * self.su[1] * self.su[1] \
			+ self.p[wd][0][2] * self.p[wd][2][2] * self.su[2] * self.su[2] \
			+ (self.p[wd][0][0] * self.p[wd][2][1] + \
				self.p[wd][0][1] * self.p[wd][2][0]) * self.xcov[0][1] \
			+ (self.p[wd][0][0] * self.p[wd][2][2] + \
				self.p[wd][0][2] * self.p[wd][2][0]) * self.xcov[0][0] \
			+ (self.p[wd][0][1] * self.p[wd][2][2] + \
				self.p[wd][0][2] * self.p[wd][2][1]) * self.xcov[0][2] \
			+ self.p[wd][0][2] * self.p[wd][2][2] * \
				self.b[wd][2] * self.b[wd][2]

		self.vw \
			= self.p[wd][1][0] * self.p[wd][2][0] * self.su[0] * self.su[0] \
			+ self.p[wd][1][1] * self.p[wd][2][1] * self.su[1] * self.su[1] \
			+ self.p[wd][1][2] * self.p[wd][2][2] * self.su[2] * self.su[2] \
			+ (self.p[wd][1][0] * self.p[wd][2][1] + \
				self.p[wd][1][1] * self.p[wd][2][0]) * self.xcov[0][1] \
			+ (self.p[wd][1][0] * self.p[wd][2][2] + \
				self.p[wd][1][2] * self.p[wd][2][0]) * self.xcov[0][0] \
			+ (self.p[wd][1][1] * self.p[wd][2][2] + \
				self.p[wd][1][2] * self.p[wd][2][1]) * self.xcov[0][2] \
			+ self.p[wd][1][2] * self.p[wd][2][2] * \
				self.b[wd][2] * self.b[wd][2]

		self.wt = self.p[wd][2][0] * self.xcov[1][0] \
			+ self.p[wd][2][1] * self.xcov[1][1] \
			+ self.p[wd][2][2] * self.xcov[1][2]
		self.wq = self.p[wd][2][0] * self.xcov[3][0] \
			+ self.p[wd][2][1] * self.xcov[3][1] \
			+ self.p[wd][2][2] * self.xcov[3][2]
		self.wc = self.p[wd][2][0] * self.xcov[2][0] \
			+ self.p[wd][2][1] * self.xcov[2][1] \
			+ self.p[wd][2][2] * self.xcov[2][2]
		
		try:
			self.su[0] = sqrt(v[0])
			self.su[1] = sqrt(v[1])
			self.su[2] = sqrt(v[2])
		except ValueError:
			print 'Value Error;PF rotation;Check Input data or v < 0:\
			date, v, num_row'
			print '  ', self.date, v[0], v[1], v[2], num_row

		self.ustar = sqrt(sqrt(self.uw * self.uw + self.vw * self.vw))
		
		# pfrotation_additional = rotation1 (Function name is changed)
		self.pfrotation_additional(num_row)

	def pfrotation_additional(self, num_row):

		"""
		Additional pfrotation
		
		Keyword arguments:
		@param num_row : the number of row 
		"""
		
		su0 = np.zeros(2)
		u = np.zeros(2)
		v = np.zeros(2)
		
		try:
			self.a[0] = atan(self.um[1] / self.um[0])
			cose = self.um[0] \
				/ (sqrt(self.um[0] * self.um[0] + self.um[1] * self.um[1]))
			sine = self.um[1] \
				/ (sqrt(self.um[0] * self.um[0] + self.um[1] * self.um[1]))
		except ZeroDivisionError:
			print 'ZeroDivisionError;Pf_Rotation'

		cosesquare = cose * cose
		sinesquare = sine * sine

		# Calculation of variance from standard deviation
		su0[0] = self.su[0] * self.su[0]
		su0[1] = self.su[1] * self.su[1]
		uw0 = copy.deepcopy(self.uw)
		vw0 = copy.deepcopy(self.vw)
		uv0 = copy.deepcopy(self.uv)
		ut0 = copy.deepcopy(self.ut)
		vt0 = copy.deepcopy(self.vt)
		uq0 = copy.deepcopy(self.uq)
		vq0 = copy.deepcopy(self.vq)
		uc0 = copy.deepcopy(self.uc)
		vc0 = copy.deepcopy(self.vc)

		u[0] =  self.um[0] * cose + self.um[1] * sine
		u[1] = -self.um[0] * sine + self.um[1] * cose

		v[0] = su0[0] * cosesquare + su0[1] * sinesquare + \
			2.0 * uv0 * cose * sine
		v[1] = su0[0] * sinesquare + su0[1] * cosesquare - \
			2.0 * uv0 * cose * sine

		self.uw = uw0 * cose + vw0 * sine
		self.uv = uv0 * (cosesquare - sinesquare) - \
			su0[0] * cose * sine + su0[1] * cose * sine
		self.vw = vw0 * cose - uw0 * sine

		self.vt = vt0 * cose - ut0 * sine
		self.vc = vc0 * cose - uc0 * sine
		self.vq = vq0 * cose - uq0 * sine
		
		if(u[1] < 1e-15):
			u[1] = 0.0
		self.um[0] = u[0]
		self.um[1] = u[1]
		try:
			self.su[0] = sqrt(v[0])
			self.su[1] = sqrt(v[1])
		except ValueError:
			print 'Value Error;pfrotation_additional;\
				Check Input data or v < 0:date, v, num_row'
			print '  ', self.date, v[0], v[1], num_row


	def rotation12(self, num_row):
		
		"""
		Double rotation
		
		Keyword arguments:
		@param num_row : the number of row 
		"""
		
		u = np.zeros(3)
		v = np.zeros(3)
		
		self.a[0] = atan(self.um[1] / self.um[0])
		try:
			self.a[1] = atan(self.um[2] \
				/ sqrt(self.um[0]**2 + self.um[1]**2))
		except ZeroDivisionError:
			print 'ZeroDivisionError;Rotation12; check um value: um, num_row'
			print self.um[0], self.um[1], num_row
		
		try:
			cose = self.um[0] / (sqrt(self.um[0]**2 + self.um[1]**2))
		except ZeroDivisionError:
			print 'ZeroDivisionError;Rotation12; check um value: um, num_row'
			print self.um[0], self.um[1], num_row
		
		try:
			sine = self.um[1] / (sqrt(self.um[0]**2 + self.um[1]**2))
		except ZeroDivisionError:
			print 'ZeroDivisionError;Rotation12; check um value: um, num_row'
			print self.um[0], self.um[1], num_row
		
		try:
			cost = sqrt(self.um[0]**2 + self.um[1]**2) \
					/ sqrt(self.um[0]**2 + self.um[1]**2 + self.um[2]**2)
		except ZeroDivisionError:
			print 'ZeroDivisionError;Rotation12; check um value: um, num_row'
			print self.um[0], self.um[1], self.um[2], num_row
		try:
			sint = self.um[2] \
				/ sqrt(self.um[0]**2 + self.um[1]**2 + self.um[2]**2)
		except ZeroDivisionError:
			print 'ZeroDivisionError;12_rotation'
		cosesquare = cose * cose
		sinesquare = sine * sine
		costsquare = cost * cost
		sintsquare = sint * sint

		#Calculation of variance from standard deviation
		self.su[0] = self.su[0] * self.su[0]
		self.su[1] = self.su[1] * self.su[1]
		self.su[2] = self.su[2] * self.su[2]
		
		u[0] =  self.um[0] * cost * cose + self.um[1] * cost * sine + \
			self.um[2] * sint
		u[1] = -self.um[0] * sine      	 + self.um[1] * cose
		u[2] = -self.um[0] * sint * cose - self.um[1] * sint * sine + \
			self.um[2] * cost

		v[0] = self.su[0] * costsquare * cosesquare \
			+ self.su[1] * costsquare * sinesquare \
			+ self.su[2] * sintsquare \
			+ 2.0 * self.xcov[0][1] * costsquare * cose * sine \
			+ 2.0 * self.xcov[0][0] * cost * sint * cose    \
			+ 2.0 * self.xcov[0][2] * cost * sint * sine
		v[1] = self.su[0] * sinesquare + self.su[1] * cosesquare \
			- 2.0 * self.xcov[0][1] * cose * sine
		v[2] = self.su[0] * sintsquare * cosesquare \
			+ self.su[1] * sintsquare * sinesquare \
			+ self.su[2] * costsquare \
			+ 2.0 * self.xcov[0][1] * sintsquare * cose * sine \
			- 2.0 * self.xcov[0][0] * cost * sint * cose \
			- 2.0 * self.xcov[0][2] * cost * sint * sine
		self.uw = self.xcov[0][0] * cose * (costsquare - sintsquare) \
			- 2.0 * self.xcov[0][1] * cost * sint * cose * sine \
			+ self.xcov[0][2] * sine * (costsquare - sintsquare) \
			- self.su[0] * cost * sint * cosesquare \
			- self.su[1] * cost * sint * sinesquare \
			+ self.su[2] * cost * sint
		self.uv = self.xcov[0][1] * cost * (cosesquare - sinesquare) \
			+ self.xcov[0][2] * sint * cose \
			- self.xcov[0][2] * sint * sine \
			- self.su[0] * cost * cose * sine \
			+ self.su[1] * cost * cose * sine
		self.vw = self.xcov[0][2] * cost * cose \
			- self.xcov[0][0] * cost * sine \
			- self.xcov[0][1] * sint * \
				(cosesquare - sinesquare) + self.su[0] * sint * cose * sine \
			- self.su[1] * sint * cose * sine

		self.wt = self.xcov[1][2] * cost \
			- self.xcov[1][0] * sint * cose \
			- self.xcov[1][1] * sint * sine
		self.wc = self.xcov[2][2] * cost \
			- self.xcov[2][0] * sint * cose \
			- self.xcov[2][1] * sint * sine
		self.wq = self.xcov[3][2] * cost \
			- self.xcov[3][0] * sint * cose \
			- self.xcov[3][1] * sint * sine

		self.vt = self.xcov[1][1] * cose - self.xcov[1][0] * sine
		self.vc = self.xcov[2][1] * cose - self.xcov[2][0] * sine
		self.vq = self.xcov[3][1] * cose - self.xcov[3][0] * sine

		self.um = copy.deepcopy(u)
		for i  in range(0,3):
			#self.um[i] = copy.deepcopy(u[i])
			try:
				self.su[i] = sqrt(v[i])
			except ValueError:
				print 'Value Error;rotation 12;\
					Check Input data or v < 0:date, v'
				print '  ', self.date, v[0], v[1], v[2]
				#sys.exit()
		self.ustar = sqrt(sqrt(self.uw * self.uw + self.vw * self.vw))


	def rotation3(self):

		"""
		Third rotation
		"""

		try:
			self.a[2]  = 1.0/2.0 * atan(2.0 * self.vw \
				/ (self.su[1] * self.su[1] - self.su[2] * self.su[2]))
		except ZeroDivisionError:
			print 'ZeroDivisionError;Rotation3'

		sinp = sin(self.a[2])
		cosp = cos(self.a[2])

		uw_t = -self.uv * sinp + self.uw * cosp
		vw_t = (self.su[2] * self.su[2] \
			- self.su[1] * self.su[1]) * cosp * sinp \
			+ self.vw * (cosp * cosp - sinp * sinp)

		self.uw = copy.deepcopy(uw_t)
		self.vw = copy.deepcopy(vw_t)
		self.wt = -self.vt * sinp + self.wt * cosp
		self.wc = -self.vc * sinp + self.wc * cosp
		self.wq = -self.vq * sinp + self.wq * cosp

	def wpl(self):
		
		"""
		WPL Correction
		"""
		
		# Constant
		ma = 28.964    	# mean molecular weight (g/mol)
		mv = 18.015    	# molecular weight of water vapor (g/mol)
		Rd = 287.04 	# gas constant for dry air (J/kg/K)
		Rv = 461.51 	# gas constant for water vapor (J/kg/K)
		R = 8.3143e-3	# Universal gas constant ((kPa m^3/(K mol))
		mu = ma/mv
		CO = 0.2095   	# Fraction concentration of oxygen in the atmosphere.
		MO = 32   		# Molecular weight of oxygen (g / mol)
		KO = 0.0045   	# Absorbtion coefficent for oxygen (m^3 / (g cm))

		# If there are pressure and temperature measurements,
		# we can get the information on air density accurately
		# from ideal gas law

		# Unit Conversion from degree to Kelvin
		Tak = self.Ta + 273.15

		# Dry air pressure (hPa)
		Pd = self.press - self.ea
		
		# Co2 Density from observation (mg/m^3)
		rho_c = self.co2 / (1000.0 * 1000.0)
		try:
			# dry air density = Pa / (Rd * Ta)
			self.rho_a = (Pd * 100.0) / (Rd * Tak)

			# Water Vapor density
			self.rho_v = self.ea * 100.0 / (Rv * Tak)

			self.rho = self.press * 100.0 / (Rd * Tak)
			c_sigma = self.rho_v / self.rho_a
		except ZeroDivisionError:
			print 'ZeroDivisionError;WPL'
		
		# Unit conversions for WPL correction
		# from g/m2/s to kg/m2/s
		self.wq = self.wq / 1000.0
		# from mg/m2/s to kg/m2/s
		self.wc = self.wc / (1000.0 * 1000.0)

		# WPL correction for latent heat flux and CO2 flux
		# Reference : Eqn. (43) in Webb et al.(1980)
		self.wbar = mu / (1.0 + mu * c_sigma) * self.wq / self.rho_a \
			+ self.wt * Tak
		
		# Oxygen correction term for KH20
		oc_wq = KO * CO * MO * (self.press / 10) / \
	   		(self.KW * R * Tak * Tak) * self.wt

		if(self.st_O2):
			self.wq = self.wq - oc_wq / 1000.0
			# Eqn. (43) in Webb et al.(1980)
			self.wbar = mu / (1.0 + mu * c_sigma) \
				* self.wq / self.rho_a + self.wt * Tak 
			# Eqn. (25)
			self.wq = (1.0 + mu * c_sigma) \
				* (self.wq + (self.rho_v / Tak) * self.wt) 
			self.wc = self.wc + mu * (rho_c / self.rho_a) * self.wq \
				+ (1.0 + mu * c_sigma) * (rho_c/Tak) * self.wt # Eqn.(24)
		else:
			# Eqn. (43) in Webb et al.(1980)
			self.wbar = mu / (1.0 + mu * c_sigma) \
				* self.wq / self.rho_a + self.wt * Tak 
			# Eqn. (25)
			self.wq = (1.0 + mu * c_sigma) \
				* (self.wq + (self.rho_v / Tak) * self.wt) 
			# Eqn.(24)
			self.wc = self.wc + mu * (rho_c / self.rho_a) * self.wq \
				+ (1.0 + mu * c_sigma) * (rho_c / Tak) * self.wt

		# Reference : Eqn. (25)
		# self.wq = (1.0 + mu * c_sigma)  \
		#	* (self.wq + (self.rho_v / Tak) * self.wt)
		# Reference : Eqn. (24)
		# self.wc = self.wc + mu * (rho_c / self.rho_a) * self.wq \
		#	+ (1.0 + mu * c_sigma) * (rho_c / Tak) * self.wt

		# Unit Recovery
		# From kg/m^2/s to g/m^2/s
		self.wq = self.wq * 1000.0
		#From kg/m^2/s to mg/m^2/s
		self.wc = self.wc * (1000 * 1000)


	def conductance(self, num_row):
		
		"""
		Conductance 
		
		Keyword arguments:
		@param num_row : the number of row
		"""
		
		# Constant(Parameter)
		# DATA a -> es_coef
		# coefficients for calculating es
		es_coef = (13.3185, 1.9760, 0.6445, 0.1299)
		# stefan-Bltzmann constant
		stb = 5.67e-8
		ep = 0.622

		# Formula for lambda is smae with one in SiB2 code
		# Careful treatment of units of each variable

		# Calculation of mixing ratio
		q = ep * (self.ea * 100.0) / \
			((ep-1.0) * (self.ea*100.0) + self.press)
		# Heat capacity
		cp = 1004.67 * (1 + 0.87 * q)
		# unit is J/kg
		# Heat of vaporization
		# lambda -> c_lambda, gamma -> c_gamma because of reserved word lambda
		c_lambda = (2501300.0 - 2366.0 * self.Ta)
		# psychrometric constant`
		c_gamma = (cp * self.press) / (ep * c_lambda)
		# Sensible heat flux (W/m^2)
		H = self.rho * cp * self.wt
		# latent Heat flux (W/m^2)
		LE = self.rho * (c_lambda / 1000.0) * self.wq
		# Available energy (=H+LE)
		av = H + LE

		# Calculation of saturation vapor pressure
		#    and each change to temperature
		# See the book of Brutsaert (Evaporation into the Atmosphere)

		Tak = self.Ta + 273.15
		Tr = 1.0 - (373.15 / Tak)
		es = 1013.25 * exp( es_coef[0] * Tr \
			- es_coef[1] * Tr * Tr - es_coef[2] * Tr * Tr * Tr \
			- es_coef[3] * Tr * Tr * Tr * Tr)
		# delta -> c_delta
		c_delta = 373.15 * es / (Tak * Tak) \
			* (es_coef[0] - 2.0 * es_coef[1] * Tr \
			- 3.0 * es_coef[2] * Tr * Tr  \
			- 4.0 * es_coef[3] * Tr * Tr * Tr)
		self.Vdf = es - self.ea
		epsilon = c_delta/c_gamma

		if(self.st_quality == True):
			self.gi = 9999.9
			self.ga = 9999.9
			self.gc = 9999.9
			self.gr = 9999.9
			self.omega = 9999.9
		else:
			try:
				self.gi = (c_gamma * av) / (self.rho * cp * self.Vdf)
			except ZeroDivisionError:
				print 'ZeroDivisionError;Conductance; \
					check rho, cp, vdf: rho, Vdf, num_row'
				print self.rho, self.Vdf, num_row
			
			try:
				self.ga = 1.0 / (self.um[0] \
					/ (self.ustar * self.ustar) + 4.626 / self.ustar)
			except ZeroDivisionError:
				print 'ZeroDivisionError; check ustar: ustar, num_row'
				print self.ustar
			#self.gc = 1.0 / (self.rho * Vdf / LE * c_lambda \
			#    + 1.0 / self.ga * (epsilon * (H + LE) / LE - (epsilon + 1.0)))
			try:
				self.gc = ((1.0 + H / LE) * (epsilon + self.gi / self.ga ) \
					- epsilon - 1.0) / self.ga
			except ZeroDivisionError:
				print 'ZeroDivisionError;Conductance; \
					check epsilon and gi and ga: epsilon, gi, ga, num_row'
				print epsilon, self.gi, self.ga, num_row
			
			# Canopy conductance
			try:
				self.gc = 1.0 / self.gc
			except ZeroDivisionError:
				print 'ZeroDivisionError;Conductance; check gc: gc, num_row'
				print self.gc, num_row
			self.omega = (1.0 + epsilon) / (1.0 + epsilon + self.ga / self.gc)
			self.gr = 4.0 * stb * (Tak * Tak * Tak) / self.rho / cp


	def qcontrol(self, num_row):
		
		"""
		Q Control 
		
		Keyword arguments:
		@param num_row : the number of row
		"""
		
		# Constant
		gc = 9.81     	# gravity constant
		kc = 0.4		# von Karman Constant
#		crv = 1.0     	# Critical value of I.T.C.

		Tak = self.Ta + 273.15
#		c = np.zeros(2)
		
		#if(self.uw < 0.0):        
		L = - self.ustar * self.ustar * self.ustar \
			/ (kc * gc / Tak* self.wt)
		try:
			self.zeta = self.zm / L
		except ZeroDivisionError:
			print 'ZeroDivisionError;q control; check L: L, num_row'
			print L, num_row
		
#		else:
#			self.zeta = 9999.9
#			self.st_quality = False
#			print 'Positive momentum flux happen!'
#			print 'Bad Quality   positive momentum flux'
#			return 0
#		
#		if(self.um[0] < 0.05):
#			self.quality = False
#			print 'Low Wind speed:    < 1.0m/s'
#			return 0
#		
#		if(self.zeta > -0.4):
#			c[0] = 1.4
#			c[1] = 0.0
#		else:
#			c[0] = 1.9
#			c[1] = 1.0 / 3.0
#		
#		itc = 0.0
#		itc_obs = 0.0
#		
#		if(self.zeta < 1.0):
#			itc = c[0] * pow((1.0 - self.zeta), c[1])
#		else:
#			itc = c[0]
#			
#		itc_obs = self.su[2] / sqrt(-self.uw)
#		diff = abs((itc - itc_obs)/itc)
#		
#		
#		if(diff > crv):
#			self.quality = True
#			
#			print 'Bad Quality   out of ange of I.T.C of w'
#			print 'itc:', itc, '    itc_obs: ',itc_obs
#			return 0
		
	def output(self):
		
		if(self.st_quality == True):
			for i in range(3):
				self.um[i] = -9999.9
			for i in range(4):
				self.su[i] = -9999.9
			H = -9999.9
			LE = -9999.9
			F_co2 = -9999.9
		else:
			#Heat capacity of DRY air (K/kg/K)
			Cp = 1004.67
			#Latent heat of varporization [J/g]
			c_lambda = (2501300.0 - 2366.0 * self.Ta)/(1000.0)

			H = self.rho * Cp * self.wt
			LE = c_lambda * self.wq
			F_co2 = self.wc
			
		if(isnan(self.um[0]) == True):
			self.um[0] = -9999.9
		if(isnan(self.um[1]) == True):
			self.um[1] = -9999.9
		if(isnan(self.um[2]) == True):
			self.um[2] = -9999.9
		if(isnan(self.su[0]) == True):
			self.su[0] = -9999.9
		if(isnan(self.su[1]) == True):
			self.su[1] = -9999.9
		if(isnan(self.su[2]) == True):
			self.su[2] = -9999.9
		if(isnan(self.su[3]) == True):
			self.su[3] = -9999.9    
		if(isnan(self.Ta) == True):
			self.Ta = -9999.9
		if(isnan(self.ea) == True):
			self.ea = -9999.9
		if(isnan(self.co2) == True):
			self.co2 = -9999.9
		if(isnan(self.net_radiation) == True):
			self.net_radiation = -9999.9
		if(isnan(self.rflx[0]) == True):
			self.rflx[0] = -9999.9
		if(isnan(self.rflx[1]) == True):
			self.rflx[1] = -9999.9
		if(isnan(self.rflx[2]) == True):
			self.rflx[2] = -9999.9
		if(isnan(self.rflx[3]) == True):
			self.rflx[3] = -9999.9
		if(isnan(self.g) == True):
			self.g = -9999.9    
		if(isnan(self.prec) == True):
			self.prec = -9999.9
		if(isnan(self.press) == True):
			self.press = -9999.9
		if(isnan(self.ga) == True):
			self.ga = -9999.9
		if(isnan(self.gc) == True):
			self.gc = -9999.9
		if(isnan(self.gi) == True):
			self.gi = -9999.9
		if(isnan(self.gr) == True):
			self.gr = -9999.9
		if(isnan(H) == True):
			H = -9999.9
		if(isnan(LE) == True):
			LE = -9999.9
		if(isnan(F_co2) == True):
			F_co2 = -9999.9
		if(isnan(self.ustar) == True):
			self.ustar = -9999.9
		if(isnan(self.agc) == True):
			self.agc = -9999.9
		if(isnan(self.wd) == True):
			self.wd = -9999.9
		if(isnan(self.qt) == True):
			self.qt = -9999.9

		file_str = StringIO()

		file_str.write(str(self.date) + ',')			#1
			
		file_str.write(str(self.um[0]) + ',')			#2
		file_str.write(str(self.um[1]) + ',')			#3
		file_str.write(str(self.um[2]) + ',')			#4
			
		file_str.write(str(self.su[0]) + ',')			#5
		file_str.write(str(self.su[1]) + ',')			#6
		file_str.write(str(self.su[2]) + ',')			#7
		file_str.write(str(self.su[3]) + ',')			#8
		
		file_str.write(str(self.Ta) + ',')				#9
		file_str.write(str(self.ea) + ',')				#10
		file_str.write(str(self.co2) + ',')				#11
		file_str.write(str(self.net_radiation) + ',')	#12
		
		file_str.write(str(self.rflx[0]) + ',')			#13
		file_str.write(str(self.rflx[1]) + ',')			#14
		file_str.write(str(self.rflx[2]) + ',')			#15
		file_str.write(str(self.rflx[3]) + ',')			#16
		
		file_str.write(str(self.g) + ',')				#17
		file_str.write(str(self.prec) + ',')			#18
		file_str.write(str(self.press) + ',')			#19
		
		file_str.write(str(self.ga) + ',')				#20
						
		file_str.write(str(self.gc) + ',')				#21
		file_str.write(str(self.gi) + ',')				#22
		file_str.write(str(self.gr) + ',')				#23
		file_str.write(str(H) + ',')					#24
		file_str.write(str(LE) + ',')					#25
		file_str.write(str(F_co2) + ',')				#26
		
		file_str.write(str(self.ustar) + ',')			#27
		file_str.write(str(self.num_used_data) + ',')	#28
		if(self.st_agc == True):
			file_str.write(str(self.agc) + ',')			#29
		file_str.write(str(self.wd) + ',')				#30(29)
		file_str.write(str(self.qt) + '\n')				#31(30)

		self.output_string = file_str.getvalue()
		
		self.output_fp.write(self.output_string)