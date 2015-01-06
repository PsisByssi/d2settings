import tkinter as tk
import tkinter.ttk as ttk
import defaults_gui
import gui_d2settings

class MainApplication():
	def __init__(self):
		self.root = tk.Tk()
		self.ttk_style = defaults_gui.loadStyle(self.root)
		self.main_gui = gui_d2settings.Gui_Main(self.root)
		
		self.main_gui.load_cfg()
		
		self.root.mainloop()
		
if __name__ == '__main__': 
	main = MainApplication() 
