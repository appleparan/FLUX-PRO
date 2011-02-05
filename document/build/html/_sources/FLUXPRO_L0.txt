:mod:`FLUXPRO_L0`
======================

.. class:: L0

  .. method:: __init__(self)
  .. method:: initialize(self)
  .. method:: bind_option(self, PFR, double, third, agc, hm, d0, zm)
  .. method:: main_func(self, path_cr5000, path_cr23x, output_dir_path)
  .. method:: data_check(self, raw_data)
  .. method:: read_line(self, file_input_cr5000, file_input_cr23x, row_cr5000, row_cr23x, cnt_row)
  .. method:: check_p(self)
  .. method:: pfr_wd(self, wd)
  .. method:: pmatrix(self, wd)
  .. method:: pf_method(self, wd)
  .. method:: pfrotation(self, wd, num_row)
  .. method:: pfrotation_additional(self, num_row)
  .. method:: rotation12(self, num_row)
  .. method:: rotation3(self)
  .. method:: wpl(self)
  .. method:: conductance(self, num_row)
  .. method:: qcontrol(self, num_row)
  .. method:: output(self)
  
