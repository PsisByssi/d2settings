import tkinter as tk
import tkinter.ttk as ttk
from pprint import pprint

import tkquick.gui.style_defaults

import gui_d2settings
import d2_func

class MainApplication():
	def __init__(self):
		self.root = tk.Tk()
		self.ttk_style = tkquick.gui.style_defaults.loadStyle(self.root)
		self.main_gui = gui_d2settings.Gui_Main(self.root, self)
		
		self.cfg_settings, self.bind_settings, self.ahk_settings = d2_func.read_settings()	# Read autoexe.cfg into array
		
		self.main_gui.load_cfg(self.cfg_settings, self.bind_settings, self.ahk_settings)	# Load The Users Data into Gui
		self.auto_exec = d2_func.load_exec_into_memory()
		#~ pprint(self.auto_exec.data)
		#~ self.root.mainloop()

	
		
if __name__ == '__main__': 
	main = MainApplication() 
