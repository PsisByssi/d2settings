import tkinter as tk
import tkinter.ttk as ttk
from pprint import pprint
import os
import time
import sched

from PIL import Image as PImage	
from PIL import ImageTk
import tkquick.gui.style_defaults as style_defaults

import gui_d2settings
import d2_func

class SplashScreen(tk.Toplevel):
	toolPhotoObjs=[]
	imgdir= 'img'
	def __init__(self, root):
		tk.Toplevel.__init__(self, root)
		self.overrideredirect(True)			# Hides the Window Border
		ws = self.winfo_screenwidth()
		hs = self.winfo_screenheight()	
		w=640
		h=400
		x = (ws/2) - (w/2)
		y = (hs/2) - (h/2)
		self.geometry('%dx%d+%d+%d' % (w, h, x, y))
		self.attributes("-topmost", True)
		imgobj = PImage.open(os.path.join(self.imgdir, 'splash.png'))	
		imgobj = ImageTk.PhotoImage(imgobj) 
		button = ttk.Label(self, image=imgobj)
		self.toolPhotoObjs.append(imgobj) 		# keep a reference to image or garbage collected
		button.pack(expand=1,fill='both')
		
class MainApplication():
	def __init__(self):
		self.root = tk.Tk()
		style_defaults.TIMS_bg = "#232327"
		style_defaults.TIMS_fg = "white"
		style_defaults.TIMS_fg_heading = '#e0e0e0'
		self.ttk_style = style_defaults.loadStyle(self.root)
		self.ttk_style.configure('TEntry', foreground='white', fieldbackground="#5a0b08")
		
		#~ self.splash = SplashScreen(self.root)
		#~ self.splash.after(10000, self.splash.destroy)
		
		self.cfg_settings, self.bind_settings, self.ahk_settings = d2_func.read_settings()	# Read autoexe.cfg into array
		self.auto_exec = d2_func.load_exec_into_memory()									# This is what we modify and save
		self.main_gui = gui_d2settings.Gui_Main(self.root, self)
		self.main_gui.load_cfg(self.cfg_settings, self.bind_settings, self.ahk_settings)	# Load The Users Data into Gui									
		#~ pprint(self.auto_exec.data)
		self.root.mainloop()
		
if __name__ == '__main__': 
	main = MainApplication() 
