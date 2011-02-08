# -*- coding: utf-8 -*-
import numpy as np
from scipy import linalg as lin
import sys, os
if hasattr(sys, "setdefaultencoding"): 
	sys.setdefaultencoding(sys.getfilesystemencoding()) 
import csv
import copy
from math import *
from cStringIO import StringIO

class L0:
	"""Docstring for class L0."""
	#constructor
	def __init__(self):

		#averaging time as minutes
		
		self.a_time = 30
		#leap? number of days in one year
		self.num_day = 366
		#number of data in one year
		self.num_time = (60 / self.a_time) * 24 * 365
		#number of variables( cr5000 )
		self.num_var_cr5000 = 53                #number of variable(cr5000)
		self.num_var_cr23x = 30                    #number of variable(cr23x)
		self.num_direction = 8                    #
		self.num_day_per_segment = 28            #processing every "nday"

		self.wdc = [0.0, 45.0, 90.0, 135.0, 180.0, 225.0, 270.0, 315.0, 360.0]

		#state_variable
		self.st_PFR_method = True
		self.st_third_rotation = False
		self.st_double_rotation = False
		self.st_quality = False
		self.st_agc = True

		self.st_error = False

		self.dim_p = (self.num_direction, 3, 3)
		self.dim_b_and_c = (self.num_direction, 3)
		self.dim_xcov = (4, 3)

		#array
		self.p = np.zeros(self.dim_p)
		self.a = np.zeros(3)
		self.b = np.zeros(self.dim_b_and_c)
		self.c = np.zeros(self.dim_b_and_c)
		self.um = np.zeros(3)
		self.su = np.zeros(4)
		self.xcov = np.zeros(self.dim_xcov)
		self.rflx = np.zeros(4)

		#variable
		#self.data           = ' '
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
		self.omega            = 0.0
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

		#list
		self.filelist_input_cr5000 = []
		self.filelist_input_cr23x = []
		self.raw_data_input_cr5000 = []
		self.raw_data_input_cr23x = []
		self.output_fp = 0

	def initialize(self):
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

	def bind_option(self, PFR, double, third, agc, hm, d0, zm):
		self.st_PFR_method = PFR
		self.st_double_rotation = double
		self.st_third_rotation = third
		self.st_agc = agc
		self.hm = hm
		self.d0 = d0
		self.zm = zm

	def main_func(self, path_cr5000, path_cr23x, output_dir_path):
		Rv = 461.51

		#Input and output file open

		self.output_dir_path = output_dir_path

		self.output_log = os.path.join(self.output_dir_path, 'ValueError.log')
		self.output_filename = os.path.join(self.output_dir_path, 'ResultL0.csv')
		try:
			self.output_fp = open(self.output_filename, 'w+')
			self.output_log = open(self.output_log, 'w+')
		except IOError:
			print 'IOError;Check Output File: ', self.output_filename
			return 'L0 failed'

		self.input_path_cr5000 = path_cr5000
		self.input_path_cr23x = path_cr23x

			
		self.file_input_cr5000 = path_cr5000
		self.file_input_cr23x = path_cr23x

		print 'File name : '
		print '   ', self.file_input_cr5000
		print '   ', self.file_input_cr23x

		try:
			self.input_cr5000_fp = open(self.file_input_cr5000, 'r')
		except IOError:
			print "IO error;Check the input File: ", self.file_input_cr5000
			return 'L0 failed'
		except Error:
			print "Unexpected Open Error: ",self.file_input_cr5000
			self.file_input_cr5000.close()
			return 'L0 failed'
			
		try:
			self.input_cr23x_fp = open(self.file_input_cr23x, 'r')
		except IOError:
			print "IO error;Check the input File: ", self.file_input_cr23x
			return 'L0 failed'
		except Error:
			print "Unexpected Open Error: ", self.file_input_cr23x
			self.file_input_cr23x.close()
			return 'L0 failed'

		#Read data from input file
		try:
			csv_data_input_cr5000 = csv.reader(self.input_cr5000_fp, \
			delimiter = '\t', quotechar = '#')
		except csv.Error:
			print "Parse Error;Check the input File: ", self.file_input_cr5000
		except:
			print "Unexpected Read Error: ", self.file_input_cr5000

		try:
			csv_data_input_cr23x = csv.reader(self.input_cr23x_fp, \
			delimiter = '\t', quotechar = '#')
		except csv.Error:
			print "Parse Error;Check the input File: ", self.file_input_cr23x
		except:
			print "Unexpected Read Error: ", self.file_input_cr23x

		raw_data_input_cr23x = []
		raw_data_input_cr5000 = []
		for row in csv_data_input_cr23x:
			raw_data_input_cr23x.append(row)
		for row in csv_data_input_cr5000:
			raw_data_input_cr5000.append(row)

		raw_data_input_cr5000 = self.data_check(raw_data_input_cr5000)
		raw_data_input_cr23x = self.data_check(raw_data_input_cr23x)

		num_row = 1

		#Divide the data every segment (e. g. 28 days) only in PFR method
		#factor using dividing segment
		self.num_data_segment = 60 / self.a_time * 24 \
		* self.num_day_per_segment
		#for handling last segment
		lim_data_segment = int(csv_data_input_cr5000.line_num \
		/ self.num_data_segment) + 1
		#count segment number
		cur_data_segment = 0

		if(self.st_PFR_method == True):
			for cur_data_segment in range(lim_data_segment):
				if(cur_data_segment < lim_data_segment - 1):
					line_limit = (cur_data_segment + 1) * self.num_data_segment
				else:
					line_limit = csv_data_input_cr5000.line_num

				self.p = np.zeros(self.dim_p)
				self.b = np.zeros(self.dim_b_and_c)
				self.c = np.zeros(self.dim_b_and_c)
				self.um = np.zeros(3)
				
				
				#Read and compute pfr_wd and pmatrix method
				for row_cnt in range(cur_data_segment * \
					self.num_data_segment, \
					line_limit):

					row_cr5000 = raw_data_input_cr5000[row_cnt]
					row_cr23x = raw_data_input_cr23x[row_cnt]
					if(len(row_cr5000) < self.num_var_cr5000):
						for i in range(self.num_var_cr5000 - len(row_cr5000)):
							row_cr5000.append(float('-9999.9'))
					if(len(row_cr23x) < self.num_var_cr23x):
						for i in range(self.num_var_cr23x - len(row_cr23x)):
							row_cr23x.append(float('-9999.9'))

					for i in range(1, len(row_cr5000)):
						row_cr5000[i] = float(row_cr5000[i])
						if(fabs(row_cr5000[i]) >= 99999):
							row_cr5000[i] = 9999.9

					self.read_line(self.file_input_cr5000, self.file_input_cr23x, \
					row_cr5000, row_cr23x, row_cnt)

					num_row = num_row + 1

					#to handle remainder, divide two cases
					#general case
					
					if(self.st_quality == False):
						return_wd = self.pfr_wd(self.wd)
						self.pmatrix(return_wd)
				
				for i in range(self.num_direction):
					self.pf_method(i)
				
				for row_cnt in range(cur_data_segment * \
					self.num_data_segment, \
					line_limit):
					row_cr5000 = raw_data_input_cr5000[row_cnt]
					row_cr23x = raw_data_input_cr23x[row_cnt]
					if(len(row_cr5000) < self.num_var_cr5000):
						for i in range(self.num_var_cr5000 - len(row_cr5000)):
							row_cr5000.append(float('-9999.9'))
					if(len(row_cr23x) < self.num_var_cr23x):
						for i in range(self.num_var_cr23x - len(row_cr23x)):
							row_cr23x.append(float('-9999.9'))

					for i in range(1, len(row_cr5000)):
						row_cr5000[i] = float(row_cr5000[i])
						if(fabs(row_cr5000[i]) >= 99999):
							row_cr5000[i] = 9999.9

					self.initialize()
					self.read_line(self.file_input_cr5000, self.file_input_cr23x, \
					row_cr5000, row_cr23x, row_cnt)	

					return_wd = self.pfr_wd(self.wd)
					self.pfrotation(return_wd, num_row)
					self.wpl()
					self.qcontrol(num_row)
					self.conductance(num_row)
					self.output()
					

		else:
			for row_cnt in range(len(raw_data_input_cr5000)):
				row_cr5000 = raw_data_input_cr5000[row_cnt]
				row_cr23x = raw_data_input_cr23x[row_cnt]
				
				if(len(row_cr5000) < self.num_var_cr5000):
					for i in range(self.num_var_cr5000 - len(row_cr5000)):
						row_cr5000.append(float('-9999.9'))
				if(len(row_cr23x) < self.num_var_cr23x):
					for i in range(self.num_var_cr23x - len(row_cr23x)):
						row_cr23x.append(float('-9999.9'))
						
				for i in range(1, len(row_cr5000)):
					row_cr5000[i] = float(row_cr5000[i])
					if(fabs(row_cr5000[i]) >= 99999):
						row_cr5000[i] = 9999.9

				self.read_line(self.file_input_cr5000, self.file_input_cr23x, \
				row_cr5000, row_cr23x, row_cnt)

				self.rotation12(num_row)

				if(self.st_third_rotation == True):
					self.rotation3()
				self.wpl()
				self.qcontrol(num_row)
				self.conductance(num_row)
				self.output()
		


		self.input_cr5000_fp.close()
		self.input_cr23x_fp.close()
		self.output_fp.close()
		self.output_log.close()
		if(self.st_error == True):
			print 'Check error log file[ValueError.log]'
		return 'L0 Done'

	#treat Nan and Inf value
	def data_check(self, raw_data):
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

	#Parsing data (data's positions are hardcoded)
	def read_line(self, file_input_cr5000, file_input_cr23x, \
	row_cr5000, row_cr23x, cnt_row):
		Rv = 461.51
		#Check Timestamp
		self.st_quality = False
		try:
			if(row_cr5000[0] != row_cr23x[0]):
				self.output_log.write("inconsistent timestamp in two_files: "\
				+ '\t'+str(file_input_cr5000)+'\t'+str(file_input_cr23x)+'\t' \
				+ str(cnt_row)+'\n')
				self.st_error = True
			elif(abs(int(float(row_cr5000[25]))) >= 9999):
				self.output_log.write("Skip the data due to spike in sonic data"\
				+ '\t'+str(file_input_cr5000)+'\t'+str(row_cr5000[0])+'\t' \
				+str(row_cr5000[25])+'\t' + str(cnt_row)+'\n')
				self.st_quality = True
				self.st_error = True
				
			elif(abs(int(float(row_cr5000[28]))) >= 9999):
				self.output_log.write("Skip the data due to spike in IRGA data"\
				+ '\t'+str(file_input_cr5000)+'\t'+str(row_cr5000[0])+'\t' \
				+str(row_cr5000[28])+'\t' + str(cnt_row)+'\n')
				self.st_quality = True
				self.st_error = True
		except IndexError:
			print 'IndexError during reading input file. line number : ', cnt_row + 1
			
			
		#print int(float(row_cr5000[25])), int(float(row_cr5000[28]))
		try:
			self.date = row_cr5000[0]
			
			if(abs(float(row_cr5000[25])) >= 9999 \
			or abs(float(row_cr5000[39])) < 1000):            
				self.st_quality = True

			self.um[0] = float(row_cr5000[25])
			self.um[1] = float(row_cr5000[26])
			self.um[2] = float(row_cr5000[27])
		except IndexError:
			print 'IndexError during reading input file(Eddy data). line number : ', cnt_row + 1
		
		try:
			self.su[0] = sqrt(float(row_cr5000[13]))
		except ValueError:
			print 'Value Error;Read data;Check Input data :date, cv_Ux_Ux'
		except IndexError:
			print 'IndexError during reading input file(Eddy data). line number : ', cnt_row + 1
		
		try:
			self.su[1] = sqrt(float(row_cr5000[18]))
		except ValueError:
			print 'Value Error;Read data;Check Input data :date, cv_Uy_Uy'
		except IndexError:
			print 'IndexError during reading input file(Eddy data). line number : ', cnt_row + 1
			
		try:
			self.su[2] = sqrt(float(row_cr5000[7]))
		except ValueError:
			print 'Value Error;Read data;Check Input data :date, cv_Uz_Uz'
		except IndexError:
			print 'IndexError during reading input file(Eddy data). line number : ', cnt_row + 1
			
		try:
			self.su[3] = sqrt(float(row_cr5000[24]))
		except ValueError:
			print 'Value Error;Read data;Check Input data :date, cv_Ts_Ts'
		except IndexError:
			print 'IndexError during reading input file(Eddy data). line number : ', cnt_row + 1
		try:
			self.xcov[0][0] = float(row_cr5000[8])
			self.xcov[0][1] = float(row_cr5000[14])
			self.xcov[0][2] = float(row_cr5000[9])

			self.xcov[1][0] = float(row_cr5000[17])
			self.xcov[1][1] = float(row_cr5000[21])
			self.xcov[1][2] = float(row_cr5000[12])

			self.xcov[2][0] = float(row_cr5000[15])
			self.xcov[2][1] = float(row_cr5000[19])
			self.xcov[2][2] = float(row_cr5000[10])

			self.xcov[3][0] = float(row_cr5000[16])
			self.xcov[3][1] = float(row_cr5000[20])
			self.xcov[3][2] = float(row_cr5000[11])

			self.co2 = float(row_cr5000[28])
			#Unit conversion from "kPa" to "hPa"
			if(float(row_cr5000[31]) != 99999):
				self.press = float(row_cr5000[31]) * 10
			

			if(self.st_quality == False):
				self.Ta = float(row_cr5000[30])
				self.ea = (float(row_cr5000[29]) / 1000) * Rv * (self.Ta + 273.15) / 100
			else:
				self.Ta = 9999.9
				self.ea = 9999.9

			#Rainfall
			self.prec = 0
			self.prec = (float(row_cr5000[51]) + float(row_cr5000[52])) / 2.0
			if(float(row_cr5000[51]) == -9999.9 and float(row_cr5000[52]) == -9999.9):
				self.prec = 0.0
			#Wind direction
			self.wd = float(row_cr5000[33])
			#Total number of data used in calculting statistics
			self.num_used_data = float(row_cr5000[39])
			#AGC value from LI7500
			self.agc = float(row_cr5000[50])
		except IndexError:
			print 'IndexError during reading input file(Eddy data). line number : ', cnt_row + 1
		
		try:
			#Net radiation
			self.net_radiation = float(row_cr23x[10] )
			#PAR
			self.qt = float(row_cr23x[30])

			self.rflx[0] = float(row_cr23x[3])
			self.rflx[1] = float(row_cr23x[5])
			self.rflx[2] = float(row_cr23x[4])
			self.rflx[3] = float(row_cr23x[6])

			#must be modified
			self.g = float(row_cr23x[10]) / 10.0
		except IndexError:
			print 'IndexError during reading input file.(MET data) line number : ', cnt_row + 1

	#Check P Matrix 
	def check_p(self):
		for i in range(0, self.num_direction):
			if(self.p[i][0][0] < 0.0):
				print \
					"Warning; small number of data in p matrix: idx, p"
				print i, self.p[i][0][0]
				return 'L0 failed'
				#sys.exit()

	#Determine PFR_Method Wind direction
	def pfr_wd(self, wd):
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

	#P matrix Operation
	def pmatrix(self, wd):
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

	#Do PF_method
	def pf_method(self, wd):
		dim_lu = (3 , 3)
		lu = np.zeros(dim_lu)
		piv = np.zeros(3)
		solution = np.zeros(3)
		
		#Copy object from c to b (wd are determined from pfr_wd)
		#Preservation of c values
		self.b[wd] = copy.deepcopy(self.c[wd])
		try:
			#LU Decomposition for the least square method
			lu, piv = lin.lu_factor(self.p[wd])
			#LU Backsubstitution for getting "b" values
			solution = lin.lu_solve((lu, piv), self.b[wd])
			
		except ZeroDivisionError:
			print 'L0;ZeroDivisionError;PF_Method'
		except RuntimeWarning, e:
			print 'L0;RuntimeWarning;', e
		
		self.p[wd] = copy.deepcopy(lu)
		self.b[wd] = copy.deepcopy(solution)
		
		#Reference : Eqn.(42) in Wilczak et al.(1000)
		try:
			self.p[wd][2][0] = - self.b[wd][1] \
				/ sqrt(self.b[wd][1] * self.b[wd][1] + self.b[wd][2] * self.b[wd][2] + 1.0)
			self.p[wd][2][1] = - self.b[wd][2] \
				/ sqrt(self.b[wd][1] * self.b[wd][1] + self.b[wd][2] * self.b[wd][2] + 1.0)
			self.p[wd][2][2] = 1.0 \
				/ sqrt(self.b[wd][1] * self.b[wd][1] + self.b[wd][2] * self.b[wd][2] + 1.0)
		except ZeroDivisionError:
			print 'L0;ZeroDivisionError;Pf_Method'
		
		#Reference : Eqn.(44) in Wilczak et al. (1000)
		#Reference : sb : sin(beta), cb : cos(beta), sa : sin(alpha), ca : cos(alpha)
		try:
			sb = -self.p[wd][2][1] \
				/ sqrt(self.p[wd][2][1] * self.p[wd][2][1] + self.p[wd][2][2] * self.p[wd][2][2])
			cb =  self.p[wd][2][2] \
				/ sqrt(self.p[wd][2][1] * self.p[wd][2][1] + self.p[wd][2][2] * self.p[wd][2][2])
			sa = self.p[wd][2][0]
			ca = sqrt(self.p[wd][2][1] * self.p[wd][2][1] + self.p[wd][2][2] * self.p[wd][2][2])
		except ZeroDivisionError:
			print 'L0;ZeroDivisionError;Pf_Method'
			
		#Calculation of P matrix
		self.p[wd][0][0] = ca
		self.p[wd][0][1] = sa * sb
		self.p[wd][0][2] = - sa * cb
		#Reference : P = (CD)^T Eqn.(26)
		self.p[wd][1][0] = 0.0
		self.p[wd][1][1] = cb
		self.p[wd][1][2] = sb
		
	
	def pfrotation(self, wd, num_row):
		#"eta" is angel between the mean streamline and each-run stream line
		#Coordinate rotation by Planar Fit Method
		ui = 0
		vi = 0
		wi = 0

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
					(self.p[wd][i][0] * self.p[wd][i][1] * self.xcov[0][1] \
					+   self.p[wd][i][1] * self.p[wd][i][2] * self.xcov[0][2] \
					+   self.p[wd][i][2] * self.p[wd][i][0] * self.xcov[0][0]) \
				+ (self.p[wd][i][2] ** 2) * (self.b[wd][0] ** 2)
			
			
		#Rotation of vertical turbulent fluxes
		self.uw \
			= self.p[wd][0][0] * self.p[wd][2][0] * self.su[0] * self.su[0] \
			+ self.p[wd][0][1] * self.p[wd][2][1] * self.su[1] * self.su[1] \
			+ self.p[wd][0][2] * self.p[wd][2][2] * self.su[2] * self.su[2] \
			+ (self.p[wd][0][0] * self.p[wd][2][1] + self.p[wd][0][1] * self.p[wd][2][0]) * self.xcov[0][1] \
			+ (self.p[wd][0][0] * self.p[wd][2][2] + self.p[wd][0][2] * self.p[wd][2][0]) * self.xcov[0][0] \
			+ (self.p[wd][0][1] * self.p[wd][2][2] + self.p[wd][0][2] * self.p[wd][2][1]) * self.xcov[0][2] \
			+ self.p[wd][0][2] * self.p[wd][2][2] * self.b[wd][2] * self.b[wd][2]

		self.vw \
			= self.p[wd][1][0] * self.p[wd][2][0] * self.su[0] * self.su[0] \
			+ self.p[wd][1][1] * self.p[wd][2][1] * self.su[1] * self.su[1] \
			+ self.p[wd][1][2] * self.p[wd][2][2] * self.su[2] * self.su[2] \
			+ (self.p[wd][1][0] * self.p[wd][2][1] + self.p[wd][1][1] * self.p[wd][2][0]) * self.xcov[0][1] \
			+ (self.p[wd][1][0] * self.p[wd][2][2] + self.p[wd][1][2] * self.p[wd][2][0]) * self.xcov[0][0] \
			+ (self.p[wd][1][1] * self.p[wd][2][2] + self.p[wd][1][2] * self.p[wd][2][1]) * self.xcov[0][2] \
			+ self.p[wd][1][2] * self.p[wd][2][2] * self.b[wd][2] * self.b[wd][2]

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
			print 'Value Error;PF rotation;Check Input data or v < 0:date, v, num_row'
			print '  ', self.date, v[0], v[1], v[2], num_row

		self.ustar = sqrt(sqrt(self.uw * self.uw + self.vw * self.vw))
		
		#pfrotation_additional = rotation1 (Function name is changed)
		self.pfrotation_additional(num_row)

	def pfrotation_additional(self, num_row):
		su0 = np.zeros(2)
		u = np.zeros(2)
		v = np.zeros(2)
		
		try:
			self.a[0] = atan(self.um[1] / self.um[0])
			ce = self.um[0] \
				/ (sqrt(self.um[0] * self.um[0] + self.um[1] * self.um[1]))
			se = self.um[1] \
				/ (sqrt(self.um[0] * self.um[0] + self.um[1] * self.um[1]))
		except ZeroDivisionError:
			print 'L0;ZeroDivisionError;Pf_Rotation'

		ce2 = ce * ce
		se2 = se * se

		#Calculation of variance from standard deviation
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

		u[0] =  self.um[0] * ce + self.um[1] * se
		u[1] = -self.um[0] * se + self.um[1] * ce

		v[0] = su0[0] * ce2 + su0[1] * se2 +  2.0 * uv0 * ce * se
		v[1] = su0[0] * se2 + su0[1] * ce2 -  2.0 * uv0 * ce * se

		self.uw = uw0 * ce + vw0 * se
		self.uv = uv0 * (ce2 - se2) - su0[0] * ce * se + su0[1] * ce * se
		self.vw = vw0 * ce - uw0 * se

		self.vt = vt0 * ce - ut0 * se
		self.vc = vc0 * ce - uc0 * se
		self.vq = vq0 * ce - uq0 * se
		
		if(u[1] < 1e-15):
			u[1] = 0.0
		self.um[0] = u[0]
		self.um[1] = u[1]
		try:
			self.su[0] = sqrt(v[0])
			self.su[1] = sqrt(v[1])
		except ValueError:
			print 'Value Error;pfrotation_additional;Check Input data or v < 0:date, v, num_row'
			print '  ', self.date, v[0], v[1], num_row

	def rotation12(self, num_row):
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
			ce = self.um[0] / (sqrt(self.um[0]**2 + self.um[1]**2))
		except ZeroDivisionError:
			print 'ZeroDivisionError;Rotation12; check um value: um, num_row'
			print self.um[0], self.um[1], num_row
		
		try:
			se = self.um[1] / (sqrt(self.um[0]**2 + self.um[1]**2))
		except ZeroDivisionError:
			print 'ZeroDivisionError;Rotation12; check um value: um, num_row'
			print self.um[0], self.um[1], num_row
		
		try:
			ct = sqrt(self.um[0]**2 + self.um[1]**2) \
					/ sqrt(self.um[0]**2 + self.um[1]**2 + self.um[2]**2)
		except ZeroDivisionError:
			print 'ZeroDivisionError;Rotation12; check um value: um, num_row'
			print self.um[0], self.um[1], self.um[2], num_row
		try:
			st = self.um[2] \
				/ sqrt(self.um[0]**2 + self.um[1]**2 + self.um[2]**2)
		except ZeroDivisionError:
			print 'L0;ZeroDivisionError;12_rotation'
		ce2 = ce * ce
		se2 = se * se
		ct2 = ct * ct
		st2 = st * st

		#Calculation of variance from standard deviation
		self.su[0] = self.su[0] * self.su[0]
		self.su[1] = self.su[1] * self.su[1]
		self.su[2] = self.su[2] * self.su[2]
		
		u[0] =  self.um[0] * ct * ce + self.um[1] * ct * se + self.um[2] * st
		u[1] = -self.um[0] * se      + self.um[1] * ce
		u[2] = -self.um[0] * st * ce - self.um[1] * st * se + self.um[2] * ct

		v[0] = self.su[0] * ct2 * ce2 \
			+ self.su[1] * ct2 * se2 \
			+ self.su[2] * st2 \
			+ 2.0 * self.xcov[0][1] * ct2 * ce * se \
			+ 2.0 * self.xcov[0][0] * ct * st * ce    \
			+ 2.0 * self.xcov[0][2] * ct * st * se
		v[1] = self.su[0] * se2 + self.su[1] * ce2 \
			- 2.0 * self.xcov[0][1] * ce * se
		v[2] = self.su[0] * st2 * ce2 \
			+ self.su[1] * st2 * se2 \
			+ self.su[2] * ct2 \
			+ 2.0 * self.xcov[0][1] * st2 * ce * se \
			- 2.0 * self.xcov[0][0] * ct * st * ce \
			- 2.0 * self.xcov[0][2] * ct * st * se
		self.uw = self.xcov[0][0] * ce * (ct2 - st2) \
			- 2.0 * self.xcov[0][1] * ct * st * ce * se \
			+ self.xcov[0][2] * se * (ct2 - st2) \
			- self.su[0] * ct * st * ce2 \
			- self.su[1] * ct * st * se2 \
			+ self.su[2] * ct * st
		self.uv = self.xcov[0][1] * ct * (ce2 - se2) \
			+ self.xcov[0][2] * st * ce \
			- self.xcov[0][2] * st * se \
			- self.su[0] * ct * ce * se \
			+ self.su[1] * ct * ce * se
		self.vw = self.xcov[0][2] * ct * ce \
			- self.xcov[0][0] * ct * se \
			- self.xcov[0][1] * st * (ce2 - se2) + self.su[0] * st * ce * se \
			- self.su[1] * st * ce * se

		self.wt = self.xcov[1][2] * ct \
			- self.xcov[1][0] * st * ce \
			- self.xcov[1][1] * st * se
		self.wc = self.xcov[2][2] * ct \
			- self.xcov[2][0] * st * ce \
			- self.xcov[2][1] * st * se
		self.wq = self.xcov[3][2] * ct \
			- self.xcov[3][0] * st * ce \
			- self.xcov[3][1] * st * se

		self.vt = self.xcov[1][1] * ce - self.xcov[1][0] * se
		self.vc = self.xcov[2][1] * ce - self.xcov[2][0] * se
		self.vq = self.xcov[3][1] * ce - self.xcov[3][0] * se

		self.um = copy.deepcopy(u)
		for i  in range(0,3):
			#self.um[i] = copy.deepcopy(u[i])
			try:
				self.su[i] = sqrt(v[i])
			except ValueError:
				print 'Value Error;rotation 12;Check Input data or v < 0:date, v'
				print '  ', self.date, v[0], v[1], v[2]
				#sys.exit()
		self.ustar = sqrt(sqrt(self.uw * self.uw + self.vw * self.vw))

	def rotation3(self):
		try:
			self.a[2]  = 1.0/2.0 * atan(2.0 * self.vw \
				/ (self.su[1] * self.su[1] - self.su[2] * self.su[2]))
		except ZeroDivisionError:
			print 'L0;ZeroDivisionError;Rotation3'

		sp = sin(self.a[2])
		cp = cos(self.a[2])

		uw_t = -self.uv * sp + self.uw * cp
		vw_t = (self.su[2] * self.su[2] - self.su[1] * self.su[1]) * cp * sp \
			+ self.vw * (cp * cp - sp * sp)

		self.uw = copy.deepcopy(uw_t)
		self.vw = copy.deepcopy(vw_t)
		self.wt = -self.vt * sp + self.wt * cp
		self.wc = -self.vc * sp + self.wc * cp
		self.wq = -self.vq * sp + self.wq * cp

	def wpl(self):
		#Constant
		ma = 28.964    	#mean molecular weight (g/mol)
		mv = 18.015    	#molecular weight of water vapor (g/mol)
		Rd = 287.04 	#gas constant for dry air (J/kg/K)
		Rv = 461.51 	#gas constant for water vapor (J/kg/K)
		mu = ma/mv

		#If there are pressure and temperature measurements,
		#we can get the information on air density accurately
		#from ideal gas law

		#Unit Conversion from degree to Kelvin
		Tak = self.Ta + 273.15

		#Dry air pressure (hPa)
		Pd = self.press - self.ea

		#Co2 Density from observation (mg/m^3)
		rho_c = self.co2 / (1000.0 * 1000.0)
		try:
			#dry air density = Pa / (Rd * Ta)
			self.rho_a = (Pd * 100.0) / (Rd * Tak)

			#Water Vapor density
			self.rho_v = self.ea * 100.0 / (Rv * Tak)

			self.rho = self.press * 100.0 / (Rd * Tak)
			c_sigma = self.rho_v / self.rho_a
		except ZeroDivisionError:
			print 'L0;ZeroDivisionError;WPL'
		
		#Unit conversions for WPL correction
		#from g/m2/s to kg/m2/s
		self.wq = self.wq / 1000.0
		#from mg/m2/s to kg/m2/s
		self.wc = self.wc / (1000.0 * 1000.0)

		#WPL correction for latent heat flux and CO2 flux
		#Reference : Eqn. (43) in Webb et al.(1980)
		self.wbar = mu / (1.0 + mu * c_sigma) * self.wq / self.rho_a \
			+ self.wt * Tak
		#Reference : Eqn. (25)
		self.wq = (1.0 + mu * c_sigma)  \
			* (self.wq + (self.rho_v / Tak) * self.wt)
		#Reference : Eqn. (24)
		self.wc = self.wc + mu * (rho_c / self.rho_a) * self.wq \
			+ (1.0 + mu * c_sigma) * (rho_c / Tak) * self.wt

		#Unit Recovery
		#From kg/m^2/s to g/m^2/s
		self.wq = self.wq * 1000.0
		#From kg/m^2/s to mg/m^2/s
		self.wc = self.wc * (1000 * 1000)

	def conductance(self, num_row):
		#Constant(Parameter)
		#DATA a -> es_coef
		#coefficients for calculating es
		es_coef = (13.3185, 1.9760, 0.6445, 0.1299)
		#stefan-Bltzmann constant
		stb = 5.67e-8
		ep = 0.622

		#Formula for lambda is smae with one in SiB2 code
		#Careful treatment of units of each variable

		#Calculation of mixing ratio
		q = ep * (self.ea * 100.0) / \
			((ep-1.0) * (self.ea*100.0) + self.press)
		#Heat capacity
		cp = 1004.67 * (1 + 0.87 * q)
		#unit is J/kg
		#Heat of vaporization
		#lambda -> c_lambda, gamma -> c_gamma because of reserved word lambda
		c_lambda = (2501300.0 - 2366.0 * self.Ta)
		#psychrometric constant`
		c_gamma = (cp * self.press) / (ep * c_lambda)
		#Sensible heat flux (W/m^2)
		H = self.rho * cp * self.wt
		#latent Heat flux (W/m^2)
		LE = self.rho * (c_lambda / 1000.0) * self.wq
		#Available energy (=H+LE)
		av = H + LE

		#Calculation of saturation vapor pressure
		#    and each change to temperature
		#See the book of Brutsaert (Evaporation into the Atmosphere)

		Tak = self.Ta + 273.15
		Tr = 1.0 - (373.15 / Tak)
		es = 1013.25 * exp( es_coef[0] * Tr \
			- es_coef[1] * Tr * Tr - es_coef[2] * Tr * Tr * Tr \
			- es_coef[3] * Tr * Tr * Tr * Tr)
		#delta -> c_delta
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
				print 'ZeroDivisionError;Conductance; check rho, cp, vdf: rho, Vdf, num_row'
				print self.rho, self,Vdf, num_row
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
				print 'ZeroDivisionError;Conductance; check epsilon and gi and ga: epsilon, gi, ga, num_row'
				print epsilon, self.gi, self.ga, num_row
			#Canopy conductance
			try:
				self.gc = 1.0 / self.gc
			except ZeroDivisionError:
				print 'ZeroDivisionError;Conductance; check gc: gc, num_row'
				print self.gc, num_row
			self.omega = (1.0 + epsilon) / (1.0 + epsilon + self.ga / self.gc)
			self.gr = 4.0 * stb * (Tak * Tak * Tak) / self.rho / cp

	def qcontrol(self, num_row):
		#Constant
		gc = 9.81     #gravity constant
		kc = 0.4    #von Karman Constant
		crv = 1.0     #Critical value of I.T.C.

		Tak = self.Ta + 273.15
		c = np.zeros(2)
		
		#if(self.uw < 0.0):        
		L = - self.ustar * self.ustar * self.ustar \
			/ (kc * gc / Tak* self.wt)
		try:
			self.zeta = self.zm / L
		except ZeroDivisionError:
			print 'ZeroDivisionError;q control; check L: L, num_row'
			print L, num_row
		"""
		else:
			self.zeta = 9999.9
			self.st_quality = False
			print 'Positive momentum flux happen!'
			print 'Bad Quality   positive momentum flux'
			return 0
		
		if(self.um[0] < 0.05):
			self.quality = False
			print 'Low Wind speed:    < 1.0m/s'
			return 0
		
		if(self.zeta > -0.4):
			c[0] = 1.4
			c[1] = 0.0
		else:
			c[0] = 1.9
			c[1] = 1.0 / 3.0
		
		itc = 0.0
		itc_obs = 0.0
		
		if(self.zeta < 1.0):
			itc = c[0] * pow((1.0 - self.zeta), c[1])
		else:
			itc = c[0]
			
		itc_obs = self.su[2] / sqrt(-self.uw)
		diff = abs((itc - itc_obs)/itc)
		
		
		if(diff > crv):
			self.quality = True
			
			print 'Bad Quality   out of ange of I.T.C of w'
			print 'itc:', itc, '    itc_obs: ',itc_obs
			return 0
		"""
		
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
		file_str.write(str(self.wd) + ',')				#30 or 29
		file_str.write(str(self.qt) + '\n')				#31 or 30

		self.output_string = file_str.getvalue()
		
		self.output_fp.write(self.output_string)

		#if(self.st_agc == True):
		#    output_string = str(self.date) + ',' 
		#	+ str(self.um[0]) + ',' + str(self.um[1]) + ',' + str(self.um[2]) + ',' + str(self.su[0]) \
		#    + ',' + str(self.su[1]) + ',' + str(self.su[2]) + ',' + str(self.su[3]) + ',' + 
		#	str(self.Ta) + ',' + str(self.ea) + ',' + str(self.co2) + ',' + str(self.net_radiation) + ',' + \
		#    str(self.rflx[0]) + ',' + str(self.rflx[1]) + ',' + str(self.rflx[2]) + ',' + str(self.rflx[3]) + \
		#    ',' + str(self.g) + ',' + str(self.prec) + ',' + str(self.press) + ',' +  \
		#	str(self.ga) + ',' + str(self.gc) + ',' + str(self.gi) + ',' + str(self.gr) + ',' + \
		#    str(H) + ',' + str(LE) + ',' + str(F_co2) + ',' + \
		#    str(self.ustar) + ',' + str(self.num_used_data) + ',' + \
		#    str(self.agc) + ',' + str(self.wd) + ',' + str(self.qt) + '\n'
		#    self.output_fp.write(output_string)
		#else:
		#    output_string = str(self.date) + ',' + str(self.um[0]) + ',' + \
		#        str(self.um[1]) + ',' + str(self.um[2]) + ',' + str(self.su[0]) \
		#        + ',' + str(self.su[1]) + ',' + str(self.su[2]) + ',' + \
		#        str(self.su[3]) + ',' + str(self.Ta) + ',' + str(self.ea) + \
		#        ',' + str(self.co2) + ',' + str(self.net_radiation) + ',' + \
		#        str(self.rflx[0]) + ',' + str(self.rflx[1]) + ',' + \
		#        str(self.rflx[2]) + ',' + str(self.rflx[3]) + \
		#        ',' + str(self.g) + ',' + str(self.prec) + ',' + \
		#        str(self.press) + ',' +  str(self.ga) + ',' + str(self.gc) \
		#        + ',' + str(self.gi) + ',' + str(self.gr) + ',' + \
		#        str(H) + ',' + str(LE) + ',' + str(F_co2) + ',' + \
		#        str(self.ustar) + ',' + str(self.num_used_data) + ',' + \
		#        str(self.wd) + ',' + str(self.qt) + '\n'
		#    self.output_fp.write(output_string)