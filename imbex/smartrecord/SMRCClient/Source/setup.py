from distutils.core import setup
import py2exe
import matplotlib
import shutil
import os

setup_dict = dict(
    windows=[{'script': 'application/app.py',
              'dest_base':'SmartRecord'
            }],
    options={
        'py2exe': {
            'compressed': True,
            'includes': ['sip'],
            'excludes': ['_gtkagg', '_tkagg'],
            'dll_excludes': ['MSVCP90.dll']
        }
    },
    data_files=matplotlib.get_py2exe_datafiles()
)

setup(**setup_dict)
setup(**setup_dict)

IHK_PATH = r'C:\Users\mkennert\workspace_pyton\Bachelorarbeit'
DLL_PATH = r'C:\Users\mkennert\AppData\Local\Enthought\Canopy\User\Scripts'

for f in os.listdir(DLL_PATH):
    if f.startswith('mk2') and f.endswith('.dll'):
        shutil.copy2(DLL_PATH + '\\' + f, IHK_PATH + r'\dist')
