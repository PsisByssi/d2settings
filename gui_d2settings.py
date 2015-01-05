import tkinter as tk
import tkinter.ttk as ttk

import gui_maker
from defaults_gui import *

class Gui_Main(gui_maker.GuiMakerWindowMenu):	#controler of page
	def start(self):
		#~ self.style = cfg_guimaker_frame.update({'bg':'yellow','bd':'10'})
		#~ self.conPack = {'expand':'1','fill':'both', 'side':'top'}
		self.customForm	= 	[
			(SettingsNoteBook, '','settingsnotebook',		cfg_grid,c_label)]
			
			
class SettingsNoteBook(gui_maker.GuiNoteBook):			#main controller notebook, used to switch the pain on the right of the treeviewer
	def start(self):
		self.widgList=[LaunchSettings,NetGraph,GameSettings,AllOtherSettings]
		#~ self.nbStyle=c_hiddenNotebook	# only woring in main not in running from script
		self.widgSide=['nsew','nsew','nsew','nsew']
		
class LaunchSettings(gui_maker.GuiMakerWindowMenu):
	def start(self):
		self.customForm	= 	[
			((ttk.Checkbutton, 'novid','novid',		cfg_grid,{}),
			(ttk.Label, 'Skips valve intro video',None,	cfg_grid,{})),
			
			((ttk.Checkbutton, 'console','console',		cfg_grid,{}),
			(ttk.Label, 'Enables consoles in game (default hotkey is `)',None,	cfg_grid,{})),
			
			((ttk.Checkbutton, 'windowed -w # -h # -noborder','novid',		cfg_grid,{}),
			(ttk.Label, 'Window mode with no border, REPLACE # WITH YOUR DESIRED',None,	cfg_grid,{})),
			
			((ttk.Checkbutton, 'novid','novid',		cfg_grid,{}),
			(ttk.Label, 'Skips valve intro video',None,	cfg_grid,{}))]
		
class GameSettings(gui_maker.GuiMakerWindowMenu):
	def start(self):
		self.customForm	= 	[
			((ttk.Label, 'dota_health_hurt_decay_time_max',None,		cfg_grid,{}),
			(ttk.Entry, '','dota_health_hurt_decay_time_max',		cfg_grid,{})),
			
			((ttk.Label, 'dota_health_hurt_decay_time_min',None,		cfg_grid,{}),
			(ttk.Entry, '','dota_health_hurt_decay_time_min',		cfg_grid,{})),
			
			((ttk.Label, 'dota_health_hurt_delay',None,		cfg_grid,{}),
			(ttk.Entry, '','dota_health_hurt_delay',		cfg_grid,{})),
			
			((ttk.Label, 'dota_pain_decay',None,		cfg_grid,{}),
			(ttk.Entry, '','dota_pain_decay',		cfg_grid,{})),
			
			((ttk.Label, 'dota_pain_factor',None,		cfg_grid,{}),
			(ttk.Entry, '','dota_pain_factor',		cfg_grid,{})),
			
			((ttk.Label, 'dota_pain_fade_rate',None,		cfg_grid,{}),
			(ttk.Entry, '','dota_pain_fade_rate',		cfg_grid,{})),
			
			((ttk.Label, 'dota_pain_multiplier',None,		cfg_grid,{}),
			(ttk.Entry, '','dota_pain_multiplier',		cfg_grid,{}))]
		
class AllOtherSettings(gui_maker.GuiMakerWindowMenu):
	def start(self):
		self.customForm	= 	[
			((ttk.Label, 'dota_health_hurt_decay_time_max',None,		cfg_grid,{}),
			(ttk.Entry, '','dota_health_hurt_decay_time_max',		cfg_grid,{})),
			
			((ttk.Label, 'dota_health_hurt_decay_time_min',None,		cfg_grid,{}),
			(ttk.Entry, '','dota_health_hurt_decay_time_min',		cfg_grid,{})),
			
			((ttk.Label, 'dota_health_hurt_delay',None,		cfg_grid,{}),
			(ttk.Entry, '','dota_health_hurt_delay',		cfg_grid,{})),
			
			((ttk.Label, 'dota_pain_decay',None,		cfg_grid,{}),
			(ttk.Entry, '','dota_pain_decay',		cfg_grid,{})),
			
			((ttk.Label, 'dota_pain_factor',None,		cfg_grid,{}),
			(ttk.Entry, '','dota_pain_factor',		cfg_grid,{})),
			
			((ttk.Label, 'dota_pain_fade_rate',None,		cfg_grid,{}),
			(ttk.Entry, '','dota_pain_fade_rate',		cfg_grid,{})),
			
			((ttk.Label, 'dota_pain_multiplier',None,		cfg_grid,{}),
			(ttk.Entry, '','dota_pain_multiplier',		cfg_grid,{}))]
class NetGraph(gui_maker.GuiMakerWindowMenu):
	def start(self):
		self.customForm	= 	[
			((ttk.Label, 'net_graphheight',None,		cfg_grid,{}),
			(ttk.Entry, '64','net_graphheight',		cfg_grid,{})),
			
			((ttk.Label, 'net_graphinsetbottom',None,		cfg_grid,{}),
			(ttk.Entry, '100','net_graphinsetbottom',		cfg_grid,{})),
			
			((ttk.Label, 'net_graphinsetleft',None,		cfg_grid,{}),
			(ttk.Entry, '0','net_graphinsetleft',		cfg_grid,{})),
			
			((ttk.Label, 'net_graphinsetright',None,		cfg_grid,{}),
			(ttk.Entry, '600','net_graphheight',		cfg_grid,{})),
			
			((ttk.Label, 'net_graphpos',None,		cfg_grid,{}),
			(ttk.Entry, '1','net_graphpos',		cfg_grid,{})),
			
			((ttk.Label, 'net_graphproportionalfont',None,		cfg_grid,{}),
			(ttk.Entry, '0','net_graphproportionalfont',		cfg_grid,{})),
			
			((ttk.Label, 'net_graphtext',None,		cfg_grid,{}),
			(ttk.Entry, '1','net_graphtext',		cfg_grid,{}))]
		
class AboutPage(gui_maker.GuiMakerWindowMenu):
	def start(self):
		pass

if __name__ == '__main__': 

	root = tk.Tk()
	main_gui = Gui_Main(root)
	#~ print(help(tk))
	root.mainloop()
