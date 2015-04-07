import tkinter as tk
import tkinter.ttk as ttk
from pprint import pprint

import tkquick.gui.style_defaults as style_defaults
from timstools import InMemoryWriter

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
		self.auto_exec = InMemoryWriter('autoexec.cfg')									# This is what we modify and save
		self.ahk_file = InMemoryWriter('dota_binds.ahk')
		self.main_gui = gui_d2settings.Gui_Main(self.root, self)
		self.main_gui.load_cfg(self.cfg_settings, self.bind_settings, self.ahk_settings)	# Load The Users Data into Gui									
		#~ pprint(self.auto_exec.data)
		self.root.mainloop()
	
		
if __name__ == '__main__': 
	main = MainApplication() 

'''
auto attack off
a, will start autoattacking shit around,
s,h - dont attack shit, exact same...

auto attack on
s, cancels attak but he will attack again and move
h, will attack again in range

if jukeing both will urn to spot before waiting next command, to get a hit off in trees u have to use a click on ground

special
hold turns auto attack on, u can acheive auto attacko on with movemnt by auto attack ground

autoattack fails becaks it always defaults to most closest unit, when chasing and u want to attack just use a click on ground, dont use stop..
you should rarley be using hold it is for lazy people



'''
