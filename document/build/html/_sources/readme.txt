
.. highlightlang:: rest

.. _rst-primer:

README
======
This program is designed to process eddy flux data including coordinate rotation, air density correction, spike detection, and gap-filling, and programmed by the Biometeorology Lab., Dep. of Atmos. Sci. at Yonsei University and Jinkyu Hong.

Source codes are available on \src folder located in program's directory.

Contact Information

* Orginal Code : jkhong@yonsei.ac.kr / jinkyu.hong@gmail.com
* Python Code : jongsukim8@gmail.com

Program Record:
---------------------------------------------------------------------------------------------------------------------
+-------------+----------------+-----------------------------------------------+
|    Date     |    Programmer  |       Description of change                   |
+=============+================+===============================================+
| Feb/28/2002 |   Jinkyu Hong  |        Original Code                          |
+-------------+----------------+-----------------------------------------------+
| Mar/09/2002 |   Jinkyu Hong  |       Add WPL correction                      |
+-------------+----------------+-----------------------------------------------+
| Mar/14/2002 |   Jinkyu Hong  |       Add quality control                     |
+-------------+----------------+-----------------------------------------------+
| Mar/21/2002 |   Jinkyu Hong  |  Add the calculation of conductances          |
+-------------+----------------+-----------------------------------------------+
| Aug/17/2005 |   Jinkyu Hong  |  Modification of WPL and PF rotation routines |
+-------------+----------------+-----------------------------------------------+
| Dec/23/2008 |   Jinkyu Hong  |  Update for new data/modify for pgf compiler  |
+-------------+----------------+-----------------------------------------------+
| Jan/07/2009 |   Jinkyu Hong  |  Update for handling bad data points          |
+-------------+----------------+-----------------------------------------------+
| Jan/13/2009 |   Jinkyu Hong  |  Modification for a new data logger (CR23X)   |
+-------------+----------------+-----------------------------------------------+
| Oct/1/2009  |  Jong su, Kim  |  Porting to Python                            |
+-------------+----------------+-----------------------------------------------+

CONDITION OF USE
------------------
                  
This program is only for scientific research purpose and is originally written with FORTRAN and MATLAB codes.  It has been ported with Python code for a better and convenient use in window application. Accept the conditions below to use the program. 

#. This program should be used only for research applications.
#. This program has been developed for eddy flux calculation by Biometeorology Lab., Dep. of Atmos. Sci. at Yonsei University and no warranty is given as to its suitability for any other purpose and applications. 
#. The Biometeorology Lab. and the programmer, Jinkyu Hong cannot guarantee that the program will correctly work in all circumstances, and will not accept any liability whatsoever for any error or omission in the program
#. The Biometeorology Lab. and Jinkyu Hong retain the proprietary rights and copyright of the program
#. Suitable acknowledgement for the Biometeorology Lab. and Jinkyu Hong is required for any published work using the program.
#. You can share the program with other persons and groups without a permission of the Biometeorology Lab., Dep. of Atmos. Sci. at Yonsei University, only when you accept the terms of conditions above. 

	
Reference
------------

* Hong, J. and J. Kim, 2002, On processing raw data from micrometeorological field experiments, Korean J. Agric. For. Meteorolo... 4, 119-126
* Foken, T. and B. wichura, 1996, Tools for quality assessement of surface-based flux measurements, Boundary-Layer Meteorology, 78. 83-105
* Webb, E. K., G. I. Pearman, R. Leuning, 1980, Correction of flux measurements for density effects due to heat and water vapor transfer, Quart. J. Met. Soc., 106, 85-100
* Wilczak, J. M, S. P. Oncley, S. A. Stage, 2001, Sonic anemometer tilt correction algorithms, Boundary-Layer Meteorology, 99, 127-150

Description of Variables
-------------------------

* nt = total number of lines to be processed
* num_var_($Machine Name) = total number of variables (column) to be processed
* um[3] = mean wind speed
* su[4] = standard deviation of wind speed and temperature
* xcov[4][3] = covariances
* Ta = Air temperature
* ea = Water vapor pressure
* co2 = CO2 density (mg/m3)
* net_radiation = net radiation(W/m2)
* rflx[0] = downward shortwave radiation (W/m2)
* rflx[1] = upward shortwave radiation (W/m2)
* rflx[2] = downward longwave radiation (W/m2)
* rflx[3] = upward longwave radiation (W/m2)
* g = soil heat flux (W/m2)
* prec = precipitation rate (mm)
* pa = atmospheric pressure (kPa)
* vdf = vapor pressure deficit (Pa)
* ga = aerodynamic conductance (m/s)
* gc = surface conductance (m/s)
* gc = surface conductance (m/s)
* gi = climatologicl conductance (m/s)
* gr = radiative conductance (m/s)


Development Environment
-------------------------------
* Developed under 32bit environment
* Python >= 2.6.6
* numpy >= 1.5.0
* scipy >= 0.8.0
* wxPython >= 2.8.11.0(32bit, Unicode)
* matplotlib >= 1.0.0
* sphinx >= 1.0.4

Output File
-------------------------------
* ResultL0.csv : Result of L0
* ResultL1.csv : Result of L1
* ResultL2.csv : Result of L2
* ValueError.log : Warning;data skip due to spike
* Plot_L2_1.csv : Need for plotting(TC, PV value included)
* Plot_L2_2.csv : Need for plotting(do not need to care about it)
* \plotimg	: plot file

Output Header
-------------------------------

* L0 Header :download:`Header_L0.csv <data/Header_L0.csv>`
* L1 Header :download:`Header_L1.csv <data/Header_L1.csv>`
* L2 Header :download:`Header_L2.csv <data/Header_L2.csv>`
* Plot_L2_1 Header :download:`Header_PlotL2.csv <data/Header_PLOT_L2_1.csv>`
* Plot_L2_2 Header :download:`Header_PlotL2.csv <data/Header_PLOT_L2_2.csv>`






