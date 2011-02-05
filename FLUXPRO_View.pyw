# -*- coding: utf-8 -*-
import sys, os
if hasattr(sys, 'setdefaultencoding'):
	sys.setdefaultencoding(sys.getfilesystemencoding())
import wx
from threading import *
import subprocess
import FLUXPRO_L0
import FLUXPRO_Plot

L0_Object = FLUXPRO_L0.L0()

#Option Variable
global_st_PFR_method = True
global_st_double_method = False
global_st_third_method = False
global_st_agc = True
global_st_L0 = False
global_st_L1 = False
global_st_L2 = False
global_st_E0_const = True

global_hm = 40.0
global_d0 = 14.0
global_zm = float(global_hm - global_d0)
global_thrsh = 4.5

global_default_st_PFR_method = True
global_default_st_double_method = False
global_default_st_third_method = False
global_default_st_agc = True
global_default_st_L2 = False

global_default_hm = 40.0
global_default_d0 = 14.0
global_default_zm = 26.0
global_default_thrsh = 4.5

# Define notification event for thread completion
EVT_RESULT_ID = wx.NewId()

def EVT_RESULT(win, func):
	#Define Result Event
	win.Connect(-1, -1, EVT_RESULT_ID, func)
	
class ResultEvent(wx.PyEvent):
	#Simple event to carry arbitrary result data.
	def __init__(self, data):
		#Init Result Event.
		wx.PyEvent.__init__(self)
		self.SetEventType(EVT_RESULT_ID)
		self.data = data

class Compute_FLUXPRO(Thread):
	#Reference Link : http://wiki.wxpython.org/LongRunningTasks
	def __init__(self, notify_window):
		Thread.__init__(self)
		self._notify_window = notify_window
		self._want_abort = False
	
	#do real computation
	#def run_FLUX(self, 	input_cr5000_path, 	input_cr23x_path, input_L2_1_path, input_L2_2_path, output_dir_path, button_run):	
	def run_FLUX(self, output_dir_path, button_run, *args):	

		global global_st_L0
		global global_st_L1
		global global_st_L2
		
		#self.input_cr5000_path = input_cr5000_path
		#self.input_cr23x_path 	= input_cr23x_path
		#self.input_L2_1_path	= input_L2_1_path
		#self.input_L2_2_path	= input_L2_2_path
		
		self.output_dir_path 	= output_dir_path
		self.button_run			= button_run
		print 'Start Process.'
		
		if(global_st_L0 == True and global_st_L1 == False and global_st_L2 == False):
			self.Path_1st 			= args[0]
			self.Path_2nd			= args[1]	
			self.input_L0_cr5000_path 	= self.Path_1st
			self.input_L0_cr23x_path 	= self.Path_2nd
			result = L0_Object.main_func(self.input_L0_cr5000_path, self.input_L0_cr23x_path, self.output_dir_path)
			if self._want_abort:
				# Use a result of None to acknowledge the abort (of
				# course you can use whatever you'd like or even
				# a separate event type)
				wx.PostEvent(self._notify_window, ResultEvent(None))
				return
			print result
			if(result == 'L0 failed'):
				self.button_run.Enable()
				return result
				
		elif(global_st_L0 == False and global_st_L1 == True and global_st_L2 == False):
			import FLUXPRO_L1
			
			global global_st_agc
			global global_thrsh
			global global_zm
			
			result = FLUXPRO_L1.L1(self.output_dir_path, st_agc_condition = global_st_agc, thrsh = global_thrsh, zm = global_zm)
			if self._want_abort:
				# Use a result of None to acknowledge the abort (of
				# course you can use whatever you'd like or even
				# a separate event type)
				wx.PostEvent(self._notify_window, ResultEvent(None))
				return
			print result
			if(result == 'L1 failed'):
				self.button_run.Enable()
				return result
			
		elif(global_st_L0 == False and global_st_L1 == False and global_st_L2 == True):
			self.Path_1st 			= args[0]
			self.Path_2nd			= args[1]	
			self.input_L2_1_path	= self.Path_1st
			self.input_L2_2_path	= self.Path_2nd
			import FLUXPRO_L2
			global global_st_E0_const
			self.E0_const = global_st_E0_const
			result = FLUXPRO_L2.L2(self.input_L2_1_path, self.input_L2_2_path, self.output_dir_path, self.E0_const)
			if self._want_abort:
				# Use a result of None to acknowledge the abort (of
				# course you can use whatever you'd like or even
				# a separate event type)
				wx.PostEvent(self._notify_window, ResultEvent(None))
				return
			print result
			if(result == 'L2 failed'):
				self.button_run.Enable()
				return result

		print 'End Process'	
		wx.PostEvent(self._notify_window, ResultEvent(result))
		self.button_run.Enable()
		return result
		
	def abort(self):
		#"""abort worker thread."""
		# Method for use by main thread to signal an abort
		self._want_abort = True
		
class Plot_FLUXPRO(Thread):
	#Reference Link : http://wiki.wxpython.org/LongRunningTasks
	def __init__(self, notify_window):
		Thread.__init__(self)
		self._notify_window = notify_window
		self._want_abort = False
	
	def plot_FLUX(self, output_dir_path, button_plot):	

		global global_st_L0
		global global_st_L1
		global global_st_L2
		
		self.output_dir_path 	= output_dir_path
		self.button_plot		= button_plot
		print 'Start Process.'
		
		if(global_st_L0 == False and global_st_L1 == True and global_st_L2 == False):
			
			result = FLUXPRO_Plot.Plot_L1(self.output_dir_path)
			if self._want_abort:
				# Use a result of None to acknowledge the abort (of
				# course you can use whatever you'd like or even
				# a separate event type)
				wx.PostEvent(self._notify_window, ResultEvent(None))
				return
			print result

		elif(global_st_L0 == False and global_st_L1 == False and global_st_L2 == True):
			result = FLUXPRO_Plot.Plot_L2(self.output_dir_path)
			if self._want_abort:
				# Use a result of None to acknowledge the abort (of
				# course you can use whatever you'd like or even
				# a separate event type)
				wx.PostEvent(self._notify_window, ResultEvent(None))
				return
			print result
			
		
		print 'End Plot'	
		wx.PostEvent(self._notify_window, ResultEvent(result))

		self.button_plot.Enable()
		
	def abort(self):
		#"""abort worker thread."""
		# Method for use by main thread to signal an abort
		self._want_abort = True

class Input_panel(wx.Panel):
	def __init__(self, parent, textctrl_log, *args, **kwargs):
		wx.Panel.__init__(self, parent, *args, **kwargs)
		self.parent = parent
		
		self.textctrl_log = textctrl_log
		
		#Static Box	
		self.staticbox_output = wx.StaticBox(self, wx.ID_ANY, \
			label='Output', name='staticBox_output', style=0)
		
		#Path
		if(hasattr(sys,'frozen')):
			current_path = sys.executable
		else:
			current_path = sys.path[0]
		current_path = os.getcwd()
		#output_default_path = os.path.split(current_path)[0]
		output_default_path = current_path
		output_default_path = os.path.join(output_default_path, 'output')
		
		self.output_path = output_default_path
		
		#dir browse output
		self.dirbrowse_statictext_output = wx.StaticText(self, wx.ID_ANY, label='Output',style=0, \
			name='dir_output',size = (64, 15))
		self.dirbrowse_statictext_output.SetToolTip(wx.ToolTip('Output file is fixed'))
		self.dirbrowse_textctrl_output = wx.TextCtrl(self, wx.ID_ANY, name='dir_output', style=0, value = output_default_path, size = (200, 15))
		self.dirbrowse_textctrl_output.SetToolTip(wx.ToolTip('Output file name is fixed'))
		self.button_output = wx.Button(self, wx.ID_ANY, label='Browse', name='Browse', style=0)
		self.button_output.SetToolTipString('Browse')
		
		self.output_path = self.dirbrowse_textctrl_output.GetValue()	
		
		#Bottom Button
		self.button_run = wx.Button(self, wx.ID_ANY, label='Run', name='Run', style=0)
		self.button_run.SetToolTipString('Process')

		self.button_cancel = wx.Button(self, wx.ID_ANY, label='Cancel', name='Cancel', style=0)
		self.button_cancel.SetDefault()
		self.button_cancel.SetToolTipString('Cancel; Terminate Program')
		self.button_cancel.SetThemeEnabled(False)
		
		self.button_plot = wx.Button(self, wx.ID_ANY, label='Plot', name='Plot', style=0)
		self.button_plot.SetToolTipString('Plotting graph')
		
		self.button_opendir = wx.Button(self, wx.ID_ANY, label='Open', name='Open', style=0)
		self.button_opendir.SetToolTipString('Open output folder')
		
		##Button Event
		#Event handler;button handler
		self.button_run.Bind(wx.EVT_BUTTON, self.OnRun)
		self.button_cancel.Bind(wx.EVT_BUTTON, self.OnCancel)
		self.button_opendir.Bind(wx.EVT_BUTTON, self.OnOpen)
		self.button_plot.Bind(wx.EVT_BUTTON, self.OnPlot)
		
		#Event handler;directory button handler
		self.button_output.Bind(wx.EVT_BUTTON, self.OpenDirDlg_OUTPUT)
		
		#Input file NoteBook
		self.nb_obj = Input_Notebook(self)
		
		##Sizers
		self.left_sizer = wx.BoxSizer(wx.VERTICAL)
		
		self.sizer_output = wx.StaticBoxSizer(self.staticbox_output, wx.HORIZONTAL)
		self.sizer_output.Add(self.dirbrowse_statictext_output, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
		self.sizer_output.Add(self.dirbrowse_textctrl_output,0, wx.EXPAND, 0)
		self.sizer_output.Add(self.button_output,  wx.FIXED_MINSIZE|wx.ALIGN_CENTER_VERTICAL)
		
		self.btn_sizer_basic = wx.BoxSizer(wx.HORIZONTAL )
		self.btn_sizer_option = wx.BoxSizer(wx.HORIZONTAL)
		
		self.btn_sizer_basic.AddSpacer((70, 10))
		self.btn_sizer_basic.Add(self.button_run)
		self.btn_sizer_basic.AddSpacer((60, 10))
		self.btn_sizer_basic.Add(self.button_cancel)
		
		self.btn_sizer_option.AddSpacer((70, 10))
		self.btn_sizer_option.Add(self.button_plot)
		self.btn_sizer_option.AddSpacer((60, 10))
		self.btn_sizer_option.Add(self.button_opendir)
		
		self.left_sizer.AddSpacer(5)
		self.left_sizer.Add(self.nb_obj, flag=wx.ALL|wx.EXPAND)
		self.left_sizer.AddSpacer(30)
		self.left_sizer.Add(self.sizer_output, flag=wx.ALL|wx.EXPAND)
		self.left_sizer.AddSpacer(30)
		self.left_sizer.Add(self.btn_sizer_basic, flag=wx.ALL|wx.EXPAND)
		self.left_sizer.AddSpacer(20)
		self.left_sizer.Add(self.btn_sizer_option, flag=wx.ALL|wx.EXPAND)
		self.left_sizer.SetSizeHints(self)
		self.SetSizer(self.left_sizer)

		#Ready for computation
		self.Computation_obj = Compute_FLUXPRO(self)
		#And indicate we don't have a worker thread yet
		self.worker_compute = None
		self.worker_plot = None

	def OnRun(self, event):
		self.button_run.Disable()
		
		#Get output path	
		self.output_path = self.dirbrowse_textctrl_output.GetValue()
		if(os.path.exists(self.output_path) == False):
			os.mkdir(self.output_path)
			
		self.output_dir_path = self.output_path
		self.textctrl_log.Clear()
		
		global global_st_L0
		global global_st_L1
		global global_st_L2
		
		#Set global_st_L0, global_st_L1, global_st_L2
		if(self.nb_obj.GetSelection() == 0):
			global_st_L0 = True
			global_st_L1 = False
			global_st_L2 = False
		elif(self.nb_obj.GetSelection() == 1):
			global_st_L0 = False
			global_st_L1 = True
			global_st_L2 = False
		elif(self.nb_obj.GetSelection() == 2):
			global_st_L0 = False
			global_st_L1 = False
			global_st_L2 = True
		

		if not self.worker_compute:
			self.worker_compute = Compute_FLUXPRO(self)

		if(global_st_L0 == True and global_st_L1 == False and global_st_L2 == False):	
			self.input_cr5000_path = self.nb_obj.tabL0.filebrowse_textctrl_input_cr5000.GetValue()
			self.input_cr23x_path = self.nb_obj.tabL0.filebrowse_textctrl_input_cr23x.GetValue()
			if((self.input_cr5000_path != '') and (self.input_cr23x_path != '')):
				result_compute = self.worker_compute.run_FLUX(self.output_dir_path, self.button_run, self.input_cr5000_path, self.input_cr23x_path)
			else:
				print 'Failed;Check input path'
				return
				
		elif(global_st_L0 == False and global_st_L1 == True and global_st_L2 == False):	
			result_compute = self.worker_compute.run_FLUX(self.output_dir_path, self.button_run)
				
		elif(global_st_L0 == False and global_st_L1 == False and global_st_L2 == True):	
			self.input_L2_1_path = self.nb_obj.tabL2.filebrowse_textctrl_input_L2_1.GetValue()
			self.input_L2_2_path = self.nb_obj.tabL2.filebrowse_textctrl_input_L2_2.GetValue()
			
			if((self.input_L2_1_path != '') and (self.input_L2_2_path != '')):
				result_compute = self.worker_compute.run_FLUX(self.output_dir_path, self.button_run, self.input_L2_1_path, self.input_L2_2_path)
				
			else:
				print 'Failed;Check input path'
				return
		
		
		self.button_run.Enable()
	
	def OnCancel(self, event):
		self.output_remove_path = os.path.join(self.output_path, 'L1.dat')
		if(L0_Object.output_fp):
			L0_Object.output_fp.close()
		if(os.path.isfile(self.output_remove_path) == True):
			os.remove(self.output_remove_path)
			
		if self.worker_compute:
			self.worker_compute.abort()
	
		self.button_run.Enable()
		print 'Process stopped.'

	def OnOpen(self, event):
		output_path = self.dirbrowse_textctrl_output.GetValue()
		output_dir_path = self.output_path
		cmd = "explorer " + str(output_dir_path)
		subprocess.Popen(cmd)

	def OnPlot(self, event):
		self.button_plot.Disable()	
		#Get output path	
		self.output_path = self.dirbrowse_textctrl_output.GetValue()
		if(os.path.exists(self.output_path) == False):
			os.mkdir(self.output_path)
			
		self.output_dir_path = self.output_path
		self.textctrl_log.Clear()
		
		global global_st_L0
		global global_st_L1
		global global_st_L2
		
		#Set global_st_L0, global_st_L1, global_st_L2
		if(self.nb_obj.GetSelection() == 0):
			global_st_L0 = True
			global_st_L1 = False
			global_st_L2 = False
			dlg = wx.MessageDialog(parent=self.parent, message="Plotting is not supported on L0!", caption="Warning!", style=wx.OK | wx.ICON_WARNING)
			dlg.ShowModal()
			dlg.Destroy()
			self.button_plot.Enable()
			return
		elif(self.nb_obj.GetSelection() == 1):
			global_st_L0 = False
			global_st_L1 = True
			global_st_L2 = False
		elif(self.nb_obj.GetSelection() == 2):
			global_st_L0 = False
			global_st_L1 = False
			global_st_L2 = True
			

		if not self.worker_plot:
			self.worker_plot = Plot_FLUXPRO(self)
		
		if((self.output_dir_path != '')):
			result_compute = self.worker_plot.plot_FLUX(self.output_dir_path, self.button_run)
		else:
			print 'Failed;Check input path'
			return
		
		self.button_plot.Enable()
	
	def OpenDirDlg_OUTPUT(self, event):
		dlg = wx.DirDialog(self, "Choose a Directory", style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
		if dlg.ShowModal() == wx.ID_OK:
			self.dirbrowse_textctrl_output.SetValue(dlg.GetPath())
			self.output_path = dlg.GetPath()    

class Input_Notebook(wx.Notebook):
	def __init__(self, parent):
		wx.Notebook.__init__(self, parent, id=wx.ID_ANY, style=0
							#wx.BK_DEFAULT
							#wx.BK_TOP 
							#wx.BK_BOTTOM
							#wx.BK_LEFT
							#wx.BK_RIGHT
							)
	

		self.tabL0 = Page_L0(self)
		self.AddPage(self.tabL0, "L0")
		
		self.tabL1 = Page_L1(self)
		self.AddPage(self.tabL1, "L1")

		self.tabL2 = Page_L2(self)
		self.AddPage(self.tabL2, "L2")

class Page_L0(wx.Panel):
	def __init__(self, parent, *args, **kwargs):
		wx.Panel.__init__(self, parent, *args, **kwargs)
		self.parent = parent
		#file browse cr5000
		
		self.staticbox_input = wx.StaticBox(self, wx.ID_ANY, \
			label='Input', name='staticBox_input', style=0)

		self.filebrowse_statictext_input_cr5000 = wx.StaticText(parent=self, id=wx.ID_ANY, label="Eddy data", name='file_static_cr5000', size = (60, 15))
		self.filebrowse_textctrl_input_cr5000 = wx.TextCtrl(parent=self, id=wx.ID_ANY, name='dir_static_cr5000', style=0, size=(200,15))
		self.filebrowse_textctrl_input_cr5000.SetToolTip(wx.ToolTip('Click browse button'))
		
		#Button cr5000
		self.button_cr5000 = wx.Button(parent=self, id=wx.ID_ANY, label='Browse', name='Browse_cr5000', style=0)
		self.button_cr5000.SetToolTipString('Browse')
		
		#file browse cr23x
		self.filebrowse_statictext_input_cr23x = wx.StaticText(parent=self, id=wx.ID_ANY, label="MET data" , style=0, name='file_static_cr23x',size = (60, 15))
		self.filebrowse_textctrl_input_cr23x = wx.TextCtrl(parent=self, id=wx.ID_ANY, name='dir_static_cr23x', style=0, size=(200,15))
		self.filebrowse_textctrl_input_cr23x.SetToolTip(wx.ToolTip('Click browse button'))\
		
		#Button cr23x
		self.button_cr23x = wx.Button(parent=self, id=wx.ID_ANY, label='Browse', name='Browse_cr23x', style=0)
		self.button_cr23x.SetToolTipString('Browse')
		
		self.staticbox_sizer_input_1 = wx.StaticBoxSizer(self.staticbox_input, wx.VERTICAL)
		
		self.sizer_cr5000 = wx.BoxSizer(wx.HORIZONTAL)
		self.sizer_cr5000.Add(self.filebrowse_statictext_input_cr5000, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
		self.sizer_cr5000.Add(self.filebrowse_textctrl_input_cr5000, 0, wx.EXPAND, 0)
		self.sizer_cr5000.Add(self.button_cr5000, wx.FIXED_MINSIZE|wx.ALIGN_CENTER_VERTICAL)
		
		#cr23x
		self.sizer_cr23x = wx.BoxSizer(wx.HORIZONTAL)
		self.sizer_cr23x.Add(self.filebrowse_statictext_input_cr23x, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
		self.sizer_cr23x.Add(self.filebrowse_textctrl_input_cr23x,0, wx.EXPAND, 0)
		self.sizer_cr23x.Add(self.button_cr23x, wx.FIXED_MINSIZE|wx.ALIGN_CENTER_VERTICAL)
		
		self.staticbox_sizer_input_1.Add(self.sizer_cr5000, 0, wx.EXPAND, 5)
		self.staticbox_sizer_input_1.Add((40,20))
		self.staticbox_sizer_input_1.Add(self.sizer_cr23x, 0, wx.EXPAND, 5)
		
		self.SetSizerAndFit(self.staticbox_sizer_input_1)
		self.staticbox_sizer_input_1.SetSizeHints(self)
		self.SetSizer(self.staticbox_sizer_input_1)
		
		self.button_cr5000.Bind(wx.EVT_BUTTON, self.OpenFileDlg_CR5000)
		self.button_cr23x.Bind(wx.EVT_BUTTON, self.OpenFileDlg_CR23X)
		
	def OpenFileDlg_CR5000(self, event):
		dlg = wx.FileDialog(self, "Choose a File", style=wx.OPEN)
		if dlg.ShowModal() == wx.ID_OK:
			#self.SetStatusText('You selected CR5000\'s input directory: %s\n' % dlg.GetPath())
			self.filebrowse_textctrl_input_cr5000.SetValue(dlg.GetPath())
			self.input_cr5000_path = dlg.GetPath()
		
	def OpenFileDlg_CR23X(self, event):
		dlg = wx.FileDialog(self, "Choose a File", style=wx.OPEN)
		if dlg.ShowModal() == wx.ID_OK:
			#self.SetStatusText('You selected CR23X\'s input directory: %s\n' % dlg.GetPath())
			self.filebrowse_textctrl_input_cr23x.SetValue(dlg.GetPath())
			self.input_cr23x_path = dlg.GetPath()	

			
class Page_L1(wx.Panel):
	def __init__(self, parent, *args, **kwargs):
		wx.Panel.__init__(self, parent, *args, **kwargs)
		self.parent = parent
	
		self.L1_Text = '''
\n You must have 'ResultL0.csv' \n in your output folder to execute L1
'''
		
		self.L1_Label = wx.StaticText(self, -1, self.L1_Text, style=wx.ALIGN_CENTER)
		self.L1_Label_Sizer = wx.BoxSizer(wx.VERTICAL)
		
		
		
		self.L1_Label_Sizer.Add(self.L1_Label, proportion=0, flag=wx.EXPAND, border=5)
		
		self.SetAutoLayout(True)
		self.SetSizerAndFit(self.L1_Label_Sizer)
		self.L1_Label_Sizer.SetSizeHints(self)
		self.SetSizer(self.L1_Label_Sizer)
		
		self.Centre()
		self.Layout()
        


class Page_L2(wx.Panel):
	def __init__(self, parent, *args, **kwargs):
		wx.Panel.__init__(self, parent, *args, **kwargs)
		self.parent = parent
		
		self.staticbox_input_L2 = wx.StaticBox(self, wx.ID_ANY, \
			label='Input_L2', name='staticBox_input_L2', style=0)    
		
		#file browse L2_1
		self.filebrowse_statictext_input_L2_1 = wx.StaticText(parent=self, id=wx.ID_ANY, label="FromL1" , style=0, name='file_static_L2_1',size = (60, 15))
		self.filebrowse_textctrl_input_L2_1 = wx.TextCtrl(parent=self, id=wx.ID_ANY, name='dir_static_cr23x', style=0, size=(200,15))
		self.filebrowse_textctrl_input_L2_1.SetToolTip(wx.ToolTip('Click browse button'))\
		
		#button L2_1
		self.button_L2_1 = wx.Button(parent=self, id=wx.ID_ANY, label='Browse', name='Browse_L2_1', style=0)
		self.button_L2_1.SetToolTipString('Browse')
		
		#file browse L2_2
		self.filebrowse_statictext_input_L2_2 = wx.StaticText(parent=self, id=wx.ID_ANY, label="RevisedL1" , style=0, name='file_static_L2_2',size = (60, 15))
		self.filebrowse_textctrl_input_L2_2 = wx.TextCtrl(parent=self, id=wx.ID_ANY, name='dir_static_cr23x', style=0, size=(200,15))
		self.filebrowse_textctrl_input_L2_2.SetToolTip(wx.ToolTip('Click browse button'))\
		
		#button L2_2
		self.button_L2_2 = wx.Button(parent=self, id=wx.ID_ANY, label='Browse', name='Browse_L2_2', style=0)
		self.button_L2_2.SetToolTipString('Browse')
		
		self.staticbox_sizer_input_2 = wx.StaticBoxSizer(self.staticbox_input_L2, wx.VERTICAL)
		
		self.sizer_L2_1 = wx.BoxSizer(wx.HORIZONTAL)
		self.sizer_L2_1.Add(self.filebrowse_statictext_input_L2_1, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
		self.sizer_L2_1.Add(self.filebrowse_textctrl_input_L2_1,0, wx.EXPAND, 0)
		self.sizer_L2_1.Add(self.button_L2_1, wx.FIXED_MINSIZE|wx.ALIGN_CENTER_VERTICAL)
		
		self.sizer_L2_2 = wx.BoxSizer(wx.HORIZONTAL)
		self.sizer_L2_2.Add(self.filebrowse_statictext_input_L2_2, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
		self.sizer_L2_2.Add(self.filebrowse_textctrl_input_L2_2,0, wx.EXPAND, 0)
		self.sizer_L2_2.Add(self.button_L2_2, wx.FIXED_MINSIZE|wx.ALIGN_CENTER_VERTICAL)
		
		self.staticbox_sizer_input_2.Add(self.sizer_L2_1, 0, wx.EXPAND, 5)
		self.staticbox_sizer_input_2.Add((40,20))
		self.staticbox_sizer_input_2.Add(self.sizer_L2_2, 0, wx.EXPAND, 5)
		
		self.SetSizerAndFit(self.staticbox_sizer_input_2)
		self.staticbox_sizer_input_2.SetSizeHints(self)
		self.SetSizer(self.staticbox_sizer_input_2)
		
		self.button_L2_1.Bind(wx.EVT_BUTTON, self.OpenFileDlg_L2_1)
		self.button_L2_2.Bind(wx.EVT_BUTTON, self.OpenFileDlg_L2_2)
		
	def OpenFileDlg_L2_1(self, event):
		dlg = wx.FileDialog(self, "Choose a File", style=wx.OPEN)
		if dlg.ShowModal() == wx.ID_OK:
			#self.SetStatusText('You selected L2_1\'s input directory: %s\n' % dlg.GetPath())
			self.filebrowse_textctrl_input_L2_1.SetValue(dlg.GetPath())
			self.input_L2_1_path = dlg.GetPath()
	
	def OpenFileDlg_L2_2(self, event):
		dlg = wx.FileDialog(self, "Choose a File", style=wx.OPEN)
		if dlg.ShowModal() == wx.ID_OK:
			#self.SetStatusText('You selected L2_2\'s input directory: %s\n' % dlg.GetPath())
			self.filebrowse_textctrl_input_L2_2.SetValue(dlg.GetPath())
			self.input_L2_2_path = dlg.GetPath()

class Output_panel(wx.Panel):
	def __init__(self, parent, *args, **kwargs):
		wx.Panel.__init__(self, parent, *args, **kwargs)
		self.parent = parent
		
		self.textctrl_output_console = wx.TextCtrl(parent=self, id=wx.ID_ANY,name
			='OutputConsole', style=wx.TE_MULTILINE|wx.TE_RICH2, value='', size=(450, 300))
		self.textctrl_output_console.SetToolTipString('Output message console')
		self.textctrl_output_console.SetEditable(False)
		self.textctrl_output_console.Layout()
		
		self.redir = RedirectText(self.textctrl_output_console)
		sys.stdout = self.redir
		sys.stderr = self.redir
		
		self.staticBox_message = wx.StaticBox(self, wx.ID_ANY, label='Log', name='staticBox_message', style=0)
		
		self.right_sizer = wx.StaticBoxSizer(self.staticBox_message, wx.VERTICAL)
		self.right_sizer.Add(self.textctrl_output_console, wx.EXPAND|wx.RIGHT)
		self.SetSizer(self.right_sizer)
		self.Bind(wx.EVT_SIZE, self.OnSize)
	
	def OnSize(self, event):
		size = event.GetSize()
		self.textctrl_output_console.SetSize(size)
		self.SetSizerAndFit(self.right_sizer)
		event.Skip()
	
class MainFrame(wx.Frame):
	def __init__(self, *args, **kwargs):
		#Frame init
		wx.Frame.__init__(self, None, id=wx.ID_ANY, title="FLUX PRO", style= wx.CAPTION|wx.SYSTEM_MENU|wx.CLOSE_BOX)
		
		
		self.Output_panel = Output_panel(self, style = wx.NO_BORDER)
		self.Input_panel = Input_panel(self, style = wx.NO_BORDER, textctrl_log = self.Output_panel.textctrl_output_console)
		
		#Set Environment
		if(hasattr(sys,'frozen')):
			icon_path = sys.executable
		else:
			icon_path = sys.path[0]
		icon_path = os.getcwd()
		icon_path = os.path.join(icon_path, 'data')
		icon_path = os.path.join(icon_path, 'icon.ico')
		self.SetIcon(wx.Icon(icon_path, wx.BITMAP_TYPE_ICO))
		self.SetToolTip(wx.ToolTip('FLUX PRO'))
		self.SetBackgroundColour(wx.NullColor)
		self.SetAutoLayout(True)
		self.SetBackgroundStyle(wx.BG_STYLE_SYSTEM)
		
		#configure statusbar
		self.CreateStatusBar()
		self.SetStatusText("FLUX PRO : koFLUX Data Processing Program")

		#Configure menu
		self.menu = wx.Menu()
		self.menu_option = self.menu.Append(-1, "&Option", "Change options")
		
		self.menu.AppendSeparator()

		self.menu_readme = self.menu.Append(-1, "&Readme", "View README")
		self.menu_manual = self.menu.Append(-1, "&Manual", "View MANUAL")
		self.menu_about = self.menu.Append(-1, "&About", "More information about the program")
		
		self.menu.AppendSeparator()

		self.menu_exit = self.menu.Append(-1, "&Exit", "Quit the program")

		#Configure menubar
		self.menuBar = wx.MenuBar()
		self.menuBar.Append(self.menu, "&File")

		self.SetMenuBar(self.menuBar)
			
		
		#Event handler;menu event handler
		self.Bind(wx.EVT_MENU, self.OnOption, self.menu_option)
		self.Bind(wx.EVT_MENU, self.OnReadme, self.menu_readme)
		self.Bind(wx.EVT_MENU, self.OnManual, self.menu_manual)
		self.Bind(wx.EVT_MENU, self.OnAboutBox, self.menu_about)
		self.Bind(wx.EVT_MENU, self.OnExit, self.menu_exit)
		
		
		#self.main_sizer = wx.FlexGridSizer(rows = 1, cols = 2, hgap = 5, vgap = 5)
		self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)
		self.main_sizer.Add(self.Input_panel, proportion=0, flag = wx.EXPAND|wx.ALL, border=5)
		self.main_sizer.Add(self.Output_panel, proportion=0, flag = wx.EXPAND|wx.ALL, border=5)
		
		self.main_sizer.Layout()
		self.main_sizer.SetSizeHints(self)
		self.SetSizer(self.main_sizer)
		self.Output_panel.Fit()
		self.SetSizerAndFit(self.main_sizer)

	def OnSize(self, event):
		size = event.GetSize()
		self.Output_panel.SetSize(size)
		self.SetSizerAndFit(self.main_sizer)
		event.Skip()
		self.Output_panel.Refresh()
	
	def OnOption(self, evnet):
		self.MyOptionFrame = OptionFrame(self)
		self.MyOptionFrame.Show()
		return True

	def OnReadme(self, event):
		#self.MyReadmeFrame = ReadmeFrame(self)
		#self.MyReadmeFrame.Show()
		if(hasattr(sys,'frozen')):
			readme_path = sys.executable
		else:
			readme_path = sys.path[0]
		readme_path = os.getcwd()
		readme_path = os.path.join(readme_path, 'doc')
		readme_path = os.path.join(readme_path, 'readme.html')
		#readme_path = os.path.join('file://', readme_path)
		readme_path = 'file://' + readme_path
		import webbrowser 
		webbrowser.open(readme_path)
	
	def OnManual(self, event):
		
		if(hasattr(sys,'frozen')):
			manual_path = sys.executable
		else:
			manual_path = sys.path[0]
		manual_path = os.getcwd()
		manual_path = os.path.join(manual_path, 'doc')
		manual_path = os.path.join(manual_path, 'manual.html')
		#manual_path = os.path.join('file://', manual_path)
		manual_path = 'file://' + manual_path
		import webbrowser 
		webbrowser.open(manual_path)
		
	def OnAboutBox(self, event):
		description = """FLUX PRO is KoFlux Data Processing Program written with Python"""
		
		license = """Biometeorology Lab, Dept. of Atmospheric Sciences at Yonsei University.\n For more information, read "CONDITION of USE" in README"""
		
		info = wx.AboutDialogInfo()
		
		if(hasattr(sys,'frozen')):
			logo_path = sys.executable
		else:
			logo_path = sys.path[0]
		logo_path = os.getcwd()
		#logo_path = os.path.split(logo_path)[0]	
		logo_path = os.path.join(logo_path, 'data')
		logo_path = os.path.join(logo_path, 'logo.jpg')
		info.SetIcon(wx.Icon(logo_path, wx.BITMAP_TYPE_JPEG))
		info.SetName('FLUX PRO')
		info.SetVersion('0.1.1')
		info.SetDescription(description)
		info.SetCopyright('(C) 2010 KoFlux')
		info.SetWebSite('http://www.koflux.org')
		info.SetLicence(license)

		wx.AboutBox(info)
		
	def OnExit(self, event):
		self.Close(True)

class ReadmeFrame(wx.MiniFrame):
	def __init__(self, parent=None, id = -1, title = 'README'):
		wx.MiniFrame.__init__(self, parent, id, title, style=wx.DEFAULT_FRAME_STYLE)
		self.Readme_panel = wx.Panel(self)
		
		self.textctrl_readme = wx.TextCtrl(parent=self.Readme_panel, id=wx.ID_ANY, name='Reame', style=wx.TE_MULTILINE, value='', size=(500,400))
		self.textctrl_readme.SetToolTipString('README')
		self.textctrl_readme.SetEditable(False)
		self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
		
		self.readme_sizer = wx.BoxSizer(wx.VERTICAL)
		
		self.readme_sizer.Add(self.textctrl_readme, 0, wx.EXPAND, 10)
				
		self.readme_sizer.Fit(self)
		self.readme_sizer.SetSizeHints(self)
		if(hasattr(sys,'frozen')):
			readme_path = sys.executable
		else:
			readme_path = sys.path[0]
		readme_path = os.path.join(readme_path, 'doc')
		readme_path = os.path.join(readme_path, 'readme.html')
		
		try:
			self.f = open(readme_path, 'r')
		except IOError:
			print 'IOError; README.txt doesn\'t exist', readme_path
		except Error:
			print 'Unknown Error: There is a problem opening README.txxt', readme_path

		if(self.f):
			self.textctrl_readme.SetValue(self.f.read())
		else:
			self.textctrl_readme.SetValue('doc\readme.html does\'t exist')
		
	
	def OnCloseWindow(self, event):
		self.Destroy()

class OptionFrame(wx.MiniFrame):
	def __init__(self, parent=None, id = -1, title = 'Option'):
		global global_st_PFR_method
		global global_st_double_method
		global global_st_third_method
		global global_st_agc
		global global_st_L2
		
		global global_hm
		global global_d0
		global global_zm
		global global_thrsh
		
		global global_default_st_PFR_method
		global global_default_st_double_method
		global global_default_st_third_method
		global global_default_st_agc
		global global_default_st_L2
		
		global global_default_hm
		global global_default_d0
		global global_default_zm
		global global_default_thrsh
		
		
		wx.MiniFrame.__init__(self, parent, id, title, size = (300, 300), pos = ( 500 , 200), style=wx.DEFAULT_FRAME_STYLE)
		Option_panel = wx.Panel(self)
		
		#Load previous setting to temporarily option value
		self.tmp_st_PFR_method = global_st_PFR_method
		self.tmp_st_double_method = global_st_double_method
		self.tmp_st_third_method = global_st_third_method
		self.tmp_st_agc = global_st_agc
		self.tmp_st_E0_const = global_st_E0_const
		self.tmp_thrsh = global_thrsh
		
		self.tmp_hm = global_hm
		self.tmp_d0 = global_d0
		self.tmp_zm = global_zm
		
		
		
		RotationList = ['Planar Fit', 'Double', 'Double + 3rd']
		AGCList = ['AGC ON', 'AGC OFF']
		
		self.rb_rotation  = wx.RadioBox(Option_panel, -1, "Rotation", (10,10),\
			wx.DefaultSize, RotationList, 1, wx.RA_SPECIFY_COLS)
		self.rb_rotation.Bind(wx.EVT_RADIOBOX, self.OnRadioSetRotation)

		#self.rb_agc  = wx.RadioBox(Option_panel, -1, "AGC", (10, 120),\
		#    wx.DefaultSize, AGCList, 1, wx.RA_SPECIFY_COLS)
		#self.rb_agc.Bind(wx.EVT_RADIOBOX, self.OnRadioAGC)
		#
		#if(self.tmp_st_agc == True):
		#    self.rb_agc.SetSelection(0)
		#else:
		#    self.rb_agc.SetSelection(1)
		
		self.chk_agc = wx.CheckBox(parent=Option_panel,id=-1,label="AGC",pos=wx.Point(20,120),size=wx.Size(50,20))
		if(self.tmp_st_agc == True):
			self.chk_agc.SetValue(True)
		self.chk_E0_const = wx.CheckBox(parent=Option_panel,id=-1,label="E0_Const",pos=wx.Point(20,150),size=wx.Size(80,20))
		if(self.tmp_st_E0_const == True):
			self.chk_E0_const.SetValue(True)
		
		
		
		self.statictext_hm = wx.StaticText(parent=Option_panel, id=wx.ID_ANY, label='Hm', pos=wx.Point(160, 20), size=wx.Size(20, 20), style=0, name='Hm')
		self.statictext_hm.SetToolTip(wx.ToolTip('Measurement height'))
		
		self.statictext_d0 = wx.StaticText(parent=Option_panel, id=wx.ID_ANY, label='d0', pos=wx.Point(160, 50), size=wx.Size(20, 20), style=0, name='d0')
		self.statictext_d0.SetToolTip(wx.ToolTip('zero-plane displacement height'))
		
		self.statictext_label_zm = wx.StaticText(parent=Option_panel, id=wx.ID_ANY, label='zm', pos=wx.Point(160, 80), size=wx.Size(20, 20), style=0, name='zm')
		self.statictext_label_zm.SetToolTip(wx.ToolTip('effective height (= hm - d0)'))
		
		self.textctrl_hm = wx.TextCtrl(parent=Option_panel, id=wx.ID_ANY, name='TEXTCTRL_HM', pos=wx.Point(200, 20), size=wx.Size(65,25), value=str(self.tmp_hm))
		self.textctrl_hm.SetToolTipString('Measurement height')
		self.textctrl_hm.SetEditable(True)
		
		self.textctrl_d0 = wx.TextCtrl(parent=Option_panel, id=wx.ID_ANY, name='TEXTCTRL_HM', pos=wx.Point(200, 50), size=wx.Size(65,25), value=str(self.tmp_d0))
		self.textctrl_d0.SetToolTipString('zero-plane displacement height')
		self.textctrl_d0.SetEditable(True)
		
		#update tmp_hm, tmp_d0, tmp_zm for calculation
		self.textctrl_zm = wx.TextCtrl(parent=Option_panel, id=wx.ID_ANY, name='TEXTCTRL_HM', pos=wx.Point(200, 80), size=wx.Size(65,25), value=str(self.tmp_zm))
		self.textctrl_zm.SetEditable(False)
		
		self.option_button_calculate = wx.Button(parent = Option_panel, id=wx.ID_ANY, label='calculate', name='Cancel', pos=wx.Point(170, 115), size=wx.Size(70, 22), style=0)
		self.option_button_calculate.SetDefault()
		self.option_button_calculate.SetThemeEnabled(False)
		
		self.statictext_thrsh = wx.StaticText(parent=Option_panel, id=wx.ID_ANY, label='Thrsh', pos=wx.Point(145, 160), size=wx.Size(45, 20), style=0, name='Thrsh')
		self.statictext_thrsh.SetToolTip(wx.ToolTip('Threshold Value for L1'))
		
		self.textctrl_thrsh = wx.TextCtrl(parent=Option_panel, id=wx.ID_ANY, name='TEXTCTRL_thrsh', pos=wx.Point(200, 160), size=wx.Size(65,25), value=str(global_thrsh))
		self.textctrl_thrsh.SetToolTipString('Threshold Value for L1')
		self.textctrl_thrsh.SetEditable(True)
		
		if(self.tmp_st_PFR_method == True and self.tmp_st_double_method == False and self.tmp_st_third_method == False ):
			self.rb_rotation.SetSelection(0)
		elif(self.tmp_st_PFR_method == False and self.tmp_st_double_method == True and self.tmp_st_third_method == False ):
			self.rb_rotation.SetSelection(1)
		elif(self.tmp_st_PFR_method == False and self.tmp_st_double_method == False and self.tmp_st_third_method == True ):
			self.rb_rotation.SetSelection(2)
		else:
			print 'Option Error'
			return 'Option_Failed'
		
		self.option_button_ok = wx.Button(parent = Option_panel, id= wx.ID_ANY, label='OK', name='OK', pos=wx.Point(35, 220), size=wx.Size(60, 30), style=0)
		self.option_button_ok.SetThemeEnabled(False)
		
		self.option_button_default = wx.Button(parent = Option_panel, id= wx.ID_ANY, label='Default', name='Default', pos=wx.Point(125, 220), size=wx.Size(60, 30), style=0)
		self.option_button_default.SetThemeEnabled(False)
		
		
		self.option_button_cancel = wx.Button(parent = Option_panel, id= wx.ID_ANY, label='Cancel', name='Cancel', pos=wx.Point(215, 220), size=wx.Size(60, 30), style=0)
		self.option_button_cancel.SetDefault()
		self.option_button_cancel.SetThemeEnabled(False)
		
			
		self.option_button_default.Bind(wx.EVT_BUTTON, self.OnDefault)
		self.option_button_ok.Bind(wx.EVT_BUTTON, self.OnOK)
		self.option_button_cancel.Bind(wx.EVT_BUTTON, self.OnCancel)
		self.option_button_calculate.Bind(wx.EVT_BUTTON, self.OnCal)
		
	def OnOK(self, event):
		global global_st_PFR_method
		global global_st_double_method
		global global_st_third_method
		global global_st_agc
		global global_st_E0_const
		
		global global_hm
		global global_d0
		global global_zm
		
		global global_thrsh
		#Update global option value

		self.tmp_hm = float(self.textctrl_hm.GetValue())
		self.tmp_d0 = float(self.textctrl_d0.GetValue())
		self.tmp_zm = float(self.tmp_hm - self.tmp_d0)
		self.tmp_thrsh = float(self.textctrl_thrsh.GetValue())
		
		if(self.chk_agc.IsChecked() == True):
			self.tmp_st_agc = True
		else:
			self.tmp_st_agc = False
			
		if(self.chk_E0_const.IsChecked() == True):
			self.tmp_st_E0_const = True
		else:
			self.tmp_st_E0_const = False
	
		global_st_PFR_method = self.tmp_st_PFR_method
		global_st_double_method = self.tmp_st_double_method
		global_st_third_method = self.tmp_st_third_method
		global_st_agc = self.tmp_st_agc
		global_st_E0_const = self.tmp_st_E0_const
		
		global_hm = self.tmp_hm
		global_d0 = self.tmp_d0
		global_zm = self.tmp_zm
		
		global_thrsh = self.tmp_thrsh
		
		#apply option value to L0
		#in L1, option variable passed by parameter
		L0_Object.bind_option(global_st_PFR_method, global_st_double_method, global_st_third_method, global_st_agc, float(global_hm), float(global_d0), float(global_zm))
		self.Close(True)
		
	def OnDefault(self, event):
		global global_st_PFR_method
		global global_st_double_method
		global global_st_third_method
		global global_st_agc
		
		global global_hm
		global global_d0
		global global_zm
		
		global global_thrsh
		
		global global_default_st_PFR_method
		global global_default_st_double_method
		global global_default_st_third_method
		global global_default_st_agc
		
		global global_default_hm
		global global_default_d0
		global global_default_zm
		global global_default_thrsh
		#Update global option value

		global_st_PFR_method = global_default_st_PFR_method
		global_st_double_method = global_default_st_double_method
		global_st_third_method = global_default_st_third_method
		global_st_agc = global_default_st_agc
		
		global_hm = global_default_hm
		global_d0 = global_default_d0
		global_zm = global_default_zm
		global_thrsh = global_default_thrsh
		
		self.rb_rotation.SetSelection(0)
		self.textctrl_hm.SetValue(str(global_hm))
		self.textctrl_d0.SetValue(str(global_d0))
		self.textctrl_zm.SetValue(str(global_zm))
		self.textctrl_thrsh.SetValue(str(global_thrsh))
		
		self.chk_agc.SetValue(True)
		self.chk_E0_const.SetValue(True)
	
	def OnCancel(self, event):
		self.Close(True)

	def OnCal(self, event):
		self.tmp_hm = self.textctrl_hm.GetValue()
		self.tmp_d0 = self.textctrl_d0.GetValue()
		self.tmp_zm = float(self.tmp_hm) - float(self.tmp_d0)
		self.textctrl_zm.SetValue(str(self.tmp_zm))
	
	def OnRadioSetRotation(self, event):
		if(self.rb_rotation.GetSelection() == 0):
			self.tmp_st_PFR_method = True
			self.tmp_st_double_method = False
			self.tmp_st_third_method = False
			
		elif(self.rb_rotation.GetSelection() == 1):
			self.tmp_st_PFR_method = False
			self.tmp_st_double_method = True
			self.tmp_st_third_method = False
		elif(self.rb_rotation.GetSelection() == 2):
			self.tmp_st_PFR_method = False
			self.tmp_st_double_method = False
			self.tmp_st_third_method = True
		else:
			print 'Option Error'
			return 'Option_failed'
				
	def OnRadioAGC(self, event):
		if(str(self.rb_rotation.GetSelection()) == 'AGC_ON'):
			self.tmp_st_agc = True
		else:
			self.tmp_st_agc = False
	
class RedirectText:
	def __init__(self, LogTextCtrl):
		self.out_text_ctrl = LogTextCtrl
	
	def __write__(self, string):
		self.out_text_ctrl.WriteText(string)
	
	def write(self, string):
		self.out_text_ctrl.WriteText(string)

class AboutDialogBox(wx.Frame):
	def __init__(self, parent, id, title):
		wx.Frame.__niit__(self, parent, id, title, size = (260, 200))
	
class MainApp(wx.App):
	def OnInit(self):
		frame = MainFrame(None, -1, 'FLUXPRO', wx.DEFAULT_FRAME_STYLE)
		frame.Centre()
		frame.Show(True)
		#self.SetTopWindow(True)
		self.SetTopWindow(frame)
		
		return True
		
app = MainApp(redirect = False)
app.MainLoop()