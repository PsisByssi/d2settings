import tkinter as tk
import tkinter.ttk as ttk
from pprint import pprint

import tkquick.gui.style_defaults as style_defaults

import gui_d2settings
import d2_func
		
class MainApplication():
	def __init__(self):
		self.root = tk.Tk()
		style_defaults.TIMS_bg = "#232327"
		style_defaults.TIMS_fg = "white"
		style_defaults.TIMS_fg_heading = '#e0e0e0'
		self.ttk_style = style_defaults.loadStyle(self.root)
		self.ttk_style.configure('TEntry', foreground='white', fieldbackground="#5a0b08")
		
		#~ self.splash = gui_d2settings.SplashScreen(self.root)
		#~ self.splash.after(10000, self.splash.destroy)
		
		self.cfg_settings, self.bind_settings, self.ahk_settings = d2_func.read_settings()	# Read autoexe.cfg into array
		self.auto_exec = d2_func.load_exec_into_memory()									# This is what we modify and save
		self.main_gui = gui_d2settings.Gui_Main(self.root, self)
		self.main_gui.load_cfg(self.cfg_settings, self.bind_settings, self.ahk_settings)	# Load The Users Data into Gui									
		#~ pprint(self.auto_exec.data)
		self.root.mainloop()
		
if __name__ == '__main__': 
	main = MainApplication() 
