import sys
from cx_Freeze import setup, Executable

INCLUDES = [('img','img'),
            ('d2settings.exe.manifest', ''),
            ('autoexec.cfg', ''),
            ('dota_binds.ahk', ''),
            ('hp', 'hp'),
            ('help', 'help'),
            ('output', 'output'),
            ('autobots', 'autobots'),
			]
buildOptions = dict(packages = ['raven', 'raven.events'],
			excludes=['PySide'],
			include_files=INCLUDES)

base = 'Win32GUI' if sys.platform=='win32' else None
executables = [Executable('d2settings.py', base=base, icon='img/d2.ico')]

setup(name="d2settings",
      version = '0.1',
      description = "Dota 2 Settings auto exec gui editor",
      options = {"build_exe": buildOptions},
      executables = executables)
