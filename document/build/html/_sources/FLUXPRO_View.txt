:mod:`FLUXPRO_View`
======================
.. function:: EVT_RESULT(win, func)

.. class:: ResultEvent(Thread)
  
  .. method:: __init__(self, notify_window)

.. class:: Compute_FLUXPRO(Thread)
  
  .. method:: __init__(self, notify_window)
  .. method:: run_FLUX(self, input_cr5000_path, 	input_cr23x_path, input_L2_1_path, 	input_L2_2_path, output_dir_path, button_run)
  .. method:: abort(self)

.. class:: Plot_FLUXPRO(Thread)
  
  .. method:: __init__(self, notify_window)
  .. method:: plot_FLUX(self, output_dir_path, button_plot)
  .. method:: abort(self)
  
.. class:: Input_panel(wx.Panel)
  
  .. method:: __init__(self, parent, textctrl_log, *args, **kwargs)
  .. method:: OnRun(self, event)
  .. method:: OnCancel(self, event)
  .. method:: OnOpen(self, event)
  .. method:: OnPlot(self, event)
  .. method:: OnCancel(self, event)
  .. method:: OpenDirDlg_OUTPUT(self, event)
  
.. class:: Input_notebook(wx.Notebook)
  
  .. method:: __init__(self, parent)

.. class:: Page_L0L1(wx.Panel)
  
  .. method:: __init__(self, parent, *args, **kwargs)
  .. method:: OpenDirDlg_CR5000(self, event)
  .. method:: OpenDirDlg_CR23x(self, event)

.. class:: Page_L2(wx.Panel)
  
  .. method:: __init__(self, parent, *args, **kwargs)
  .. method:: OpenDirDlg_L2_1(self, event)
  .. method:: OpenDirDlg_L2_2(self, event)


.. class:: Output_panel(wx.Panel)
  
  .. method:: __init__(self, parent, *args, **kwargs)
  .. method:: OnSize(self, event)

.. class:: MainFrame(wx.Panel)
  
  .. method:: __init__(self, *args, **kwargs)
  .. method:: OnSize(self, event)
  .. method:: OnOption(self, event)
  .. method:: OnReadme(self, event)
  .. method:: OnManual(self, event)
  .. method:: OnAboutBox(self, event)
  .. method:: OnExit(self, event)
  
.. class:: ReadmeFrame(wx.MiniFrame)
  
  .. method:: __init__(self, parent=None, id = -1, title = 'README')
  .. method:: OnCloseWindow(self, event)

.. class:: OptionFrame(wx.MiniFrame)
  
  .. method:: __init__(self, parent=None, id = -1, title = 'Option')
  .. method:: OnOK(self, event)
  .. method:: OnDefault(self, event)
  .. method:: OnCancel(self, event)
  .. method:: OnCal(self, event)
  .. method:: OnRadioSetRotation(self, event)
  .. method:: OnRadioAGC(self, event)
  
.. class:: RedirectText
  
  .. method:: __init__(self, LogTextCtrl)
  .. method:: __write__(self, string)
  .. method:: write(self, string)
  
.. class:: AboutDialogBox(wx.Frame)
  
  .. method:: __init__(self, parent, id, title)

.. class:: MainApp(wx.App)
  
  .. method:: OnInit(self)