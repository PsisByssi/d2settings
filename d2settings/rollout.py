import os
import subprocess
from timstools import ignored


with ignored(FileNotFoundError):
		#~ from uncrumpled import GENERAL_CFG_FILE						#deleteding the cfg resets the program defaults
		os.remove('flags.cfg')
		print('Removed Cfg File')
		print()

path = os.getcwd()
subprocess.Popen(['python' ,os.path.join(path,'setup.py'),'bdist_msi']).communicate()
#~ subprocess.Popen([r'']).communicate()
#~ subprocess.Popen([r'D:\STORAGE\Dropbox\programming\d2settings\dota2-settings-tweaker\dist\d2settings-0.2-win32.msi']).communicate()
