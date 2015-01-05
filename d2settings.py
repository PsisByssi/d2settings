import tkinter as tk
import tkinter.ttk as ttk

import gui_d2settings

class MainApplication():
	def __init__(self):
		self.root = tk.Tk()
		main_gui = gui_d2settings.Gui_Main(self.root)
		
		
		
		
		self.root.mainloop()
		
if __name__ == '__main__': 
	main = MainApplication() 
