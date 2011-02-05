# setup.py
from distutils.core import setup, Extension
import py2exe, sys, os
import glob

from distutils import msvc9compiler
msvc9compiler.VERSION = 9.0

from distutils.filelist import findall
import matplotlib
matplotlibdatadir = matplotlib.get_data_path()
matplotlibdata = findall(matplotlibdatadir)
matplotlibdata_files = []
for f in matplotlibdata:
    dirname = os.path.join('matplotlibdata', f[len(matplotlibdatadir)+1:])
    matplotlibdata_files.append((os.path.split(dirname)[0], [f]))
	
data_files = [
	
	(r'doc', glob.glob(r'D:\Project\FLUX PRO\dist5\distribution\doc\*.*')),
	(r'doc\_doctrees', glob.glob(r'D:\Project\FLUX PRO\dist5\distribution\doc\_doctress\*.*')),
	(r'doc\_downloads', glob.glob(r'D:\Project\FLUX PRO\dist5\distribution\doc\_downloads\*.*')),
	(r'doc\_images', glob.glob(r'D:\Project\FLUX PRO\dist5\distribution\doc\_images\*.*')),
	(r'doc\_sources', glob.glob(r'D:\Project\FLUX PRO\dist5\distribution\doc\_sources\*.*')),
	(r'doc\_static', glob.glob(r'D:\Project\FLUX PRO\dist5\distribution\doc\_static\*.*')),
	(r'src', glob.glob(r'D:\Project\FLUX PRO\dist5\distribution\src\*.*')),
	(r'data', glob.glob(r'D:\Project\FLUX PRO\dist5\distribution\data\*.*')),
	(r'mpl-data', glob.glob(r'C:\Python26\Lib\site-packages\matplotlib\mpl-data\*.*')),
	# Because matplotlibrc does not have an extension, glob does not find it (at least I think that's why)
	# So add it manually here:
	(r'mpl-data', [r'C:\Python26\Lib\site-packages\matplotlib\mpl-data\matplotlibrc']),
	(r'mpl-data\images',glob.glob(r'C:\Python26\Lib\site-packages\matplotlib\mpl-data\images\*.*')),
	(r'mpl-data\fonts',glob.glob(r'C:\Python26\Lib\site-packages\matplotlib\mpl-data\fonts\*.*'))
]
sys.argv.append('py2exe')


FLUX_PRO = dict(
    name = r"FLUX PRO",
	# used for the versioninfo resource
	description = r"KoFLUX Data Processing Program",
	version = "0.1.1",
	company_name = r"KoFLUX",
	dest_base = r"FLUX PRO",
    # what to build
	script = "FLUXPRO_View.pyw",
	uac_info="highestAvailable",
	author=r'Jong su, Kim',
	author_email=r'jongsukim8@gmail.com',
	icon_resource = 'data\icon.ico'
	)


setup(
      windows = [FLUX_PRO],
	  options = {'py2exe': {"compressed": 1,
							'optimize': 2, 
							'includes': ['matplotlib.numerix.random_array', 'FLUXPRO_L0','FLUXPRO_L1', 'FLUXPRO_L2', 'FLUXPRO_Common'],
							'excludes': ['_gtkagg', '_tkagg','bsddb', 'curses', 'email', 'pywin.debugger',
							'pywin.debugger.dbgcon', 'pywin.dialogs', 'tcl','Tkconstants', 'Tkinter'],
							'dll_excludes': ['libgdk-win32-2.0-0.dll',
											'libgobject-2.0-0.dll',
											'libgdk_pixbuf-2.0-0.dll'],
							'packages' : ['matplotlib', 'pytz'],
							
							 }},
      data_files=data_files,
	  
	#   ext_package='FLUXPRO_package',
	#	ext_modules = [
	#	Extension('FLUXPRO_Common', ['distribution\FLUXPRO_Common.py']),
	#	Extension('FLUXPRO_L0', 	['distribution\FLUXPRO_L0.py']),
	#	Extension('FLUXPRO_L1', 	['distribution\FLUXPRO_L1.py']),
	#	Extension('FLUXPRO_L2', 	['distribution\FLUXPRO_L2.py']),
	#	]
)