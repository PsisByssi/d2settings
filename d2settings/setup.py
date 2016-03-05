
from esky import bdist_esky
from esky.bdist_esky import Executable
from distutils.core import setup
from glob import glob

data_files = [('img', glob(r'.\img\*.*')),
            ('img\plastik', glob(r'.\img\plastik\*.*')),
            ('',['d2settings.exe.manifest']),
            ('hp', glob(r'.\hp\*.*')),
            ('help',glob(r'.\help\*.*')),
            ('output',glob(r'.\output\*.*')),
            ('autobots',glob(r'.\autobots\*.*')),
            ('', ['autoexec.cfg']),
            ('', ['dota_binds.ahk']),]

# executables = [Executable('d2settings.py', icon='Zakafein-Game-Pack-1-Dota2-Bloodseeker.ico', gui_only=True,)]#, targetName = "uncrumpled")]
executables = [Executable('d2settings.py', gui_only=True,)]#, targetName = "uncrumpled")]

ESKY_OPTIONS = {
    "freezer_module": "cxfreeze",
    "includes": ['tkinter'],
    "compress": None,
    }

setup(name="d2settings",
      version = '0.1',
      description = "Dota 2 Settings auto exec gui editor",
      options = { "bdist_esky": ESKY_OPTIONS },
      data_files = data_files,
      scripts = executables)
