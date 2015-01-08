import tkinter as tk
import tkinter.ttk as ttk
from pprint import pprint

import gui_maker
from defaults_gui import *
import batteries
	
class HotKeyGrabber(batteries.HotKeyGrabberMaker):pass	
	
class Gui_Main(gui_maker.GuiMakerWindowMenu):	#controler of page	
	def start(self):
		#~ self.style = cfg_guimaker_frame.update({'bg':'yellow','bd':'10'})
		#~ self.conPack = {'expand':'1','fill':'both', 'side':'top'}
		self.customForm	= 	[
			(SettingsNoteBook, '','settings',		cfg_grid,c_label)]			
		
	def load_cfg(self, cfg):
		for tab in self.formRef['settings'].widget_ref.values():		#The notebook tabs
			for setting, tkvar in tab.variables.items():
				#~ print(setting)
				for cfg_setting, values in cfg.items():
					if setting == cfg_setting:
						if len(cfg_setting) > 1 and values[0] not in ('//'):	# The setting has a value associated with it
							print('value assocated', values[0])
							print(setting, values)
							print()
							tkvar.set(values[0])
							break
						else:
							print('No Value associated')
							print(setting,values[0])
							print()
							break
				else:
					print('NO MATCH', setting)
				#~ value = tkvar.get()
				#~ print(setting,value)
#~ save_settings([['testing'], ['13']])

class SettingsNoteBook(gui_maker.GuiNoteBook):			# Main controller notebook, used to switch the pain on the right of the treeviewer
	def start(self):
		self.widgList = [LaunchSettings,MiscSettings,NetGraph,InternetSettings,MacroSettings,PerformanceSettings,PainFadeSettings]
		self.tabText = ['Launch','Misc','NetGraph','Internet','Macros','Performance','Damage Delay']
		#~ self.nbStyle=c_hiddenNotebook	# only woring in main not in running from script
		self.widgSide = ['nsew','nsew','nsew','nsew','nsew','nsew','nsew','nsew']


class ProgramSetup(gui_maker.GuiMakerWindowMenu):						
	def start(self):
		self.customForm	= 	[
			((ttk.Checkbutton, 'dota_force_right_click_attack','dota_force_right_click_attack',		cfg_grid,{}),
			(ttk.Label, 'Deny on right mouse click',None,	cfg_grid,{})),
		
			((ttk.Label, 'dota_pain_fade_rate',None,		cfg_grid,{}),
			(ttk.Entry, '','dota_pain_fade_rate',		cfg_grid,{})),
			
			((ttk.Label, 'Reload autoexec.cfg Hotkey',None,		cfg_grid,{}),
			(HotKeyGrabber, '','reset_hotkey',		cfg_grid,{})),
			
			((ttk.Label, 'Turn Text Mode Off Hotkey',None,		cfg_grid,{}),
			(HotKeyGrabber, '','text_off_hotkey',		cfg_grid,{})),
			
			((ttk.Label, 'Unlock Testing Mode Hotkey',None,		cfg_grid,{}),
			(HotKeyGrabber, '','unlock_testmode_hotkey',		cfg_grid,{}))]
			
		
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
		
class PainFadeSettings(gui_maker.GuiMakerWindowMenu):
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
		
class InternetSettings(gui_maker.GuiMakerWindowMenu):
	def start(self):
		self.customForm	= 	[
			((ttk.Label, 'rate', None,		cfg_grid,{}),
			(ttk.Entry, '', 'rate',		cfg_grid,{})),
			
			((ttk.Label, 'cl_updaterate',None,		cfg_grid,{}),
			(ttk.Entry, '','cl_updaterate',		cfg_grid,{})),
			
			((ttk.Label, 'cl_cmdrate',None,		cfg_grid,{}),
			(ttk.Entry, '','cl_cmdrate',		cfg_grid,{})),
			
			
			((ttk.Label, 'cl_interp',None,		cfg_grid,{}),
			(ttk.Entry, '','cl_interp_ratio',		cfg_grid,{})),
			
			((ttk.Label, 'cl_smoothtime',None,		cfg_grid,{}),
			(ttk.Entry, '','cl_smoothtime',		cfg_grid,{})),
			
			((ttk.Label, 'dota_pain_fade_rate',None,		cfg_grid,{}),
			(ttk.Entry, '','dota_pain_fade_rate',		cfg_grid,{})),
			
			((ttk.Label, 'dota_pain_multiplier',None,		cfg_grid,{}),
			(ttk.Entry, '','dota_pain_multiplier',		cfg_grid,{}))]
			

class PerformanceSettings(gui_maker.GuiMakerWindowMenu):
	def start(self):
		self.customForm	= 	[
			((ttk.Label, 'dota_cheap_water', None,		cfg_grid,{}),
			(ttk.Entry, '', 'dota_cheap_water',		cfg_grid,{})),
			
			((ttk.Label, 'r_deferred_height_fog',None,		cfg_grid,{}),
			(ttk.Entry, '','r_deferred_height_fog',		cfg_grid,{})),
			
			((ttk.Label, 'r_deferred_simple_light',None,		cfg_grid,{}),
			(ttk.Entry, '','r_deferred_simple_light',		cfg_grid,{})),
			
			
			((ttk.Label, 'r_screenspace_aa',None,		cfg_grid,{}),
			(ttk.Entry, '','r_screenspace_aa',		cfg_grid,{})),
			
			((ttk.Label, 'mat_vsync',None,		cfg_grid,{}),
			(ttk.Entry, '','mat_vsync',		cfg_grid,{})),
			
			((ttk.Label, 'snd_mix_async',None,		cfg_grid,{}),
			(ttk.Entry, '','snd_mix_async',		cfg_grid,{}))]
class NetGraph(gui_maker.GuiMakerWindowMenu):
	def start(self):		
		self.customForm	= 	[
			((ttk.Label, 'Netgraph Toggle Hotkey',None,		cfg_grid,{}),
			(HotKeyGrabber, '','netgraph_hotkey',		cfg_grid,{})),
			
			((ttk.Label, 'net_graphheight',None,		cfg_grid,{}),
			(ttk.Entry, '','net_graphheight',		cfg_grid,{})),
			
			((ttk.Label, 'net_graphinsetbottom',None,		cfg_grid,{}),
			(ttk.Entry, '','net_graphinsetbottom',		cfg_grid,{})),
			
			((ttk.Label, 'net_graphinsetleft',None,		cfg_grid,{}),
			(ttk.Entry, '','net_graphinsetleft',		cfg_grid,{})),
			
			((ttk.Label, 'net_graphinsetright',None,		cfg_grid,{}),
			(ttk.Entry, '','net_graphheight',		cfg_grid,{})),
			
			((ttk.Label, 'net_graphpos',None,		cfg_grid,{}),
			(ttk.Entry, '','net_graphpos',		cfg_grid,{})),
			
			((ttk.Label, 'net_graphproportionalfont',None,		cfg_grid,{}),
			(ttk.Entry, '','net_graphproportionalfont',		cfg_grid,{})),
			
			((ttk.Label, 'net_graphtext',None,		cfg_grid,{}),
			(ttk.Entry, '','net_graphtext',		cfg_grid,{}))]
		
class MiscSettings(gui_maker.GuiMakerWindowMenu):
	def start(self):
		self.customForm	= 	[
			((ttk.Checkbutton, 'dota_force_right_click_attack','dota_force_right_click_attack',		cfg_grid,{}),
			(ttk.Label, 'Deny on right mouse click',None,	cfg_grid,{})),
			
			((ttk.Checkbutton, 'dota_minimap_hero_size','dota_minimap_hero_size',		cfg_grid,{}),
			(ttk.Label, 'minimap hero icon size',None,	cfg_grid,{})),
			
			((ttk.Checkbutton, 'dota_minimap_misclick_time','dota_minimap_misclick_time',		cfg_grid,{}),
			(ttk.Label, 'Threshold delay to accept minimap clicks',None,	cfg_grid,{})),
			
			((ttk.Checkbutton, 'dota_health_per_vertical_marker','dota_health_per_vertical_marker',		cfg_grid,{}),
			(ttk.Label, 'Health segmenting in the lifebar',None,	cfg_grid,{})),
			
			((ttk.Checkbutton, 'dota_camera_disable_zoom','dota_camera_disable_zoom',		cfg_grid,{}),
			(ttk.Label, 'Disable mouse wheel zoom',None,	cfg_grid,{})),
			
			((ttk.Checkbutton, 'dota_unit_fly_bonus_height','dota_unit_fly_bonus_height',		cfg_grid,{}),
			(ttk.Label, 'Flying height of air units',None,	cfg_grid,{})),
			
			((ttk.Checkbutton, 'dota_unit_fly_bonus_height','dota_unit_fly_bonus_height',		cfg_grid,{}),
			(ttk.Label, 'Flying height of air units',None,	cfg_grid,{})),
			
			((ttk.Checkbutton, 'gameui_allowescape','gameui_allowescape',		cfg_grid,{}),
			(ttk.Label, 'Escape key allowed to hide game UI',None,	cfg_grid,{})),
			
			((ttk.Checkbutton, 'gameui_allowescapetoshow','gameui_allowescapetoshow',		cfg_grid,{}),
			(ttk.Label, 'Escape key allowed to show game UI',None,	cfg_grid,{}))]

class MacroSettings(gui_maker.GuiMakerWindowMenu):
	def start(self):
		self.customForm	= 	[
			((ttk.Label, 'Courier Deliver & Message',None,		cfg_grid,{}),
			(HotKeyGrabber, '','courier_hotkey',		cfg_grid,{}),
			(ttk.Entry, 'msg','enter message here',		cfg_grid,{})),
			
			((ttk.Label, 'Rune Checker',None,		cfg_grid,{}),
			(HotKeyGrabber, '','runechecker_hotkey',		cfg_grid,{})),
			
			((ttk.Label, 'Netgraph Toggle Hotkey',None,		cfg_grid,{}),
			(HotKeyGrabber, '','netgraph_hotkey',		cfg_grid,{})),
			
			((ttk.Label, 'Netgraph Toggle Hotkey',None,		cfg_grid,{}),
			(HotKeyGrabber, '','netgraph_hotkey',		cfg_grid,{}))]

class TestingSettings(gui_maker.GuiMakerWindowMenu):
	def start(self):
		self.customForm	= 	[
		((ttk.Label, 'Help text hotkey',None,		cfg_grid,{}),
		(HotKeyGrabber, '','help_hotkey',		cfg_grid,{}))]
		
class HpSegmentationSettings(gui_maker.GuiMakerWindowMenu):
	def start(self):
		self.customForm	= 	[
			((ttk.Checkbutton, 'dota_force_right_click_attack','dota_force_right_click_attack',		cfg_grid,{}),
			(ttk.Label, 'Deny on right mouse click',None,	cfg_grid,{})),

			((ttk.Label, 'Hp Line Segment Toggle Hotkey',None,		cfg_grid,{}),
			(HotKeyGrabber, '','segment_hotkey',		cfg_grid,{})),

		
			((ttk.Label, 'dota_pain_fade_rate',None,		cfg_grid,{}),
			(ttk.Entry, '','dota_pain_fade_rate',		cfg_grid,{}))]

class AboutPage(gui_maker.GuiMakerWindowMenu):
	def start(self):
		self.customForm	= 	[
			((ttk.Checkbutton, 'dota_force_right_click_attack','dota_force_right_click_attack',		cfg_grid,{}),
			(ttk.Label, 'Deny on right mouse click',None,	cfg_grid,{})),
		
			((ttk.Label, 'dota_pain_fade_rate',None,		cfg_grid,{}),
			(ttk.Entry, '','dota_pain_fade_rate',		cfg_grid,{})),
			
			((ttk.Label, 'Netgraph Toggle Hotkey',None,		cfg_grid,{}),
			(HotKeyGrabber, '','netgraph_hotkey',		cfg_grid,{}))]

class ProgramSetup(gui_maker.GuiMakerWindowMenu):
	def start(self):
		self.customForm	= 	[
			((ttk.Checkbutton, 'dota_force_right_click_attack','dota_force_right_click_attack',		cfg_grid,{}),
			(ttk.Label, 'Deny on right mouse click',None,	cfg_grid,{})),
		
			((ttk.Label, 'dota_pain_fade_rate',None,		cfg_grid,{}),
			(ttk.Entry, '','dota_pain_fade_rate',		cfg_grid,{})),
			
			((ttk.Label, 'Netgraph Toggle Hotkey',None,		cfg_grid,{}),
			(HotKeyGrabber, '','netgraph_hotkey',		cfg_grid,{}))]



if __name__ == '__main__': 

	root = tk.Tk()
	main_gui = Gui_Main(root)
	#~ print(help(tk))
	root.mainloop()
