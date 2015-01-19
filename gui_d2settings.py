import tkinter as tk
import tkinter.ttk as ttk
from pprint import pprint
import inspect

import tkquick.gui.maker as maker
from tkquick.gui.style_defaults import *
from tkquick.gui import batteries

import d2_func
	
class HotKeyGrabber(batteries.HotKeyGrabberMaker):
	def start(self):
		self.reset_on_click = False
		self.reset_on_focus = False
		self.custom_input = d2_func.valve_key_list
	
class AhkGrabber(batteries.HotKeyGrabberMaker):
	def start(self):
		self.reset_on_click = False
		self.reset_on_focus = False
		self.custom_input = d2_func.ahk_key_list
		#~ def set(self, hotkeyvalues):
		#~ formatted = []
		#~ for key in hotkeyvalues:
			#~ formatted.append(d2_func.valve_key_parser(key))	
		#~ batteries.HotKeyGrabberMaker.set(self,formatted)		#call original func

def add_default_field(customForm):
	# Instead of manually adding the rows to custom form builder.
	# Each item that has a reference name in the dictionary gets a default value field
	for i, row in enumerate(customForm[:]):
		for col in row:
			if col[2]:							# get the reference name and add default to the end
				def_ref = col[2]+'_default'
				new_row = list(row)
				new_row.append((ttk.Checkbutton, None, def_ref, cfg_grid,{}))
				del customForm[i]
				customForm.insert(i, new_row)
				break

def add_remap_field(customForm):
	# Instead of manually adding the rows to custom form builder.
	# Each HotKeyGrabber item that has a reference name in the dictionary gets a remap field as well
	for i, row in enumerate(customForm[:]):
		for col in row:
			if 'HotKeyGrabber' in col[0].__name__:		
				print(col[0])
				print('remapping...')
				if col[2]:							# get the reference name and add remap to the end
					def_ref = col[2]+'_remap'
					new_row = list(row)	
					new_row.append((AhkGrabber, None, def_ref, cfg_grid,{}))
					del customForm[i]
					customForm.insert(i, new_row)
					break

class Gui_Main(maker.GuiMakerWindowMenu):	#controler of page	
	def start(self):
		#~ self.style = cfg_guimaker_frame.update({'bg':'yellow','bd':'10'})
		#~ self.conPack = {'expand':'1','fill':'both', 'side':'top'}
		self.customForm	= 	[
			(SettingsNoteBook, '','settings',		cfg_grid,c_label)]			
		self.toolBar = [(('save', self.save_cfg,  {'side': tk.RIGHT},c_button),
						('reset', self.reload_cfg, {'side': tk.RIGHT},c_button))]
	
	def finish(self):
		def change_normal(event):
			event.widget.changed = True
		def change_class(event):
			event.widget.master.changed = True	
						
		for tab in self.formRef['settings'].widget_ref.values():		# The notebook tabs
			for widget in tab.formRef.values():							# adds binds to all the widgets to track their changes
				#~ print(repr(widget))
				if isinstance(widget, HotKeyGrabber):
					widget.ent.bind('<Button-1>', change_class)			# when saving i just have to check the widget saved in formRef, because that is what we mark here
				#~ widget.bind('<Button-1>',lambda self, event: self.changed = True)	
				else:
					widget.bind('<Button-1>', change_normal)	
	
	def load_cfg(self, cfg, bind_cfg, ahk_cfg):
		def set_default_value(set_checkbox_on=False,ignore_mode=False):	# Func to set defaults!
			try:
				try:
					index = cfg_values.index('Default') + 1
				except ValueError:
					index = cfg_values.index('default') + 1
			except Exception:pass									# No default Value Set	
			else:			
				default_val = cfg_values[index]						
				widg = tab.formRef[setting+'_default']
				#~ def_tkvar.set('default_val')
				widg.config(text = '  ({0})'.format(default_val))
				#~ print('SETTING DEFAULT VALUE',setting+'_default',default_val)
			if set_checkbox_on:
				def_tkvar = tab.variables[setting+'_default']
				def_tkvar.set(1)
		
		for tab in self.formRef['settings'].widget_ref.values():		#The notebook tabs
			for setting, tkvar in tab.variables.items():
				#~ print(setting)
				#~ continue
				for cfg_setting, cfg_values in cfg.items():
					if setting == cfg_setting:				# We are only dealing with settings that are not ignored!
						#~ print(cfg_setting,'cfg setting',cfg_values)
						if cfg_values[0] not in ('//'):	# The setting has a value associated with it
							#~ print('value assocated', cfg_values[0])
							#~ print(setting, cfg_values)
							#~ print()
							tkvar.set(cfg_values[0])
							set_default_value()
						else:								# These settings require no argument they are on by being presetn
							#~ print('No argument setting')
							#~ print(setting,cfg_values)
							#~ if cfg_values[0] == '//':
								
							set_default_value()
							tkvar.set(1)
							print()
						break
					#~ elif cfg_setting == '//IGNORE' and setting == cfg_values[0] :			# Commented Out Values
					elif '//IGNORE' in cfg_setting:					# Commented Out Values
						cfg_setting = cfg_setting.split(' ')[-1]	# Remove the //IGNORE
						if setting == cfg_values[0]:
							#~ print('MATCHDDDDDD')
							if cfg_values[0] not in ('//'):	# The setting has a value associated with it
								#~ print('value assocated', cfg_values[1])
								#~ print(setting, cfg_values)
								#~ print()
								tkvar.set(cfg_values[1])
								set_default_value(set_checkbox_on=1)
							else:								# These settings require no argument they are on by being presetn
								#~ print('No argument setting')
								#~ print(setting, cfg_values)
								#~ if cfg_values[0] == '//':
									
								set_default_value(set_checkbox_on=1)
								tkvar.set(1)
								#~ print()
							break
					else:
						#~ print('NO MATCH', setting)
						pass
						#~ print()
					#~ value = tkvar.get()
					#~ print(setting,value)
			for setting, widg in tab.formRef.items():						# Handle the bind settings from the autoexec
				for bind_setting, bind_values in bind_cfg.items():              
					#~ print('calling set')
					bind_value = bind_setting	 
					if setting in bind_values:						# Atm i'm allowing myself to place the tag anywhere in the values
						#~ print(setting, bind_values)
						widg.set([bind_value])							# Set method on the Hotkeygrabber
						#~ widg.var.set(['nbegÄ'])
						break			
				for ahk_bind_setting, ahk_bind_value in ahk_cfg.items():
					pass
			
									
	
	def reload_cfg(self):
		pass
	def save_cfg(self):
		# Only gets the values and rates the widgets that have been changed
		for tab in self.formRef['settings'].widget_ref.values():		# The notebook tabs
			for setting, widget in tab.formRef.items():	
				if hasattr(widget, 'changed') and widget.changed:		# If changed 	
					print('changed',repr(widget))
					try:
						value = widget.get()
						print('using get method',value)
					except AttributeError:
						value = widget.var.get()
						print('using VAR method',value)
					d2_func.save_settings(self.app.auto_exec, setting, value)	# Edits the in memory file		
		
		with open('autoexec2.cfg', 'w') as file:
			for row in self.app.auto_exec:
				file.write(row)
		print('Finished saving')
#~ save_settings([['testing'], ['13']])

class SettingsNoteBook(maker.GuiNoteBook):			# Main controller notebook, used to switch the pain on the right of the treeviewer
	def start(self):
		self.widgList = [LaunchSettings,MiscSettings,NetGraph,InternetSettings,MacroSettings,PerformanceSettings,PainFadeSettings]
		self.tabText = ['Launch','Misc','NetGraph','Internet','Macros','Performance','Damage Delay']
		#~ self.nbStyle=c_hiddenNotebook	# only woring in main not in running from script
		self.widgSide = ['nsew','nsew','nsew','nsew','nsew','nsew','nsew','nsew']


class ProgramSetup(maker.GuiMakerWindowMenu):						
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
		add_default_field(self.customForm)
		
class LaunchSettings(maker.GuiMakerWindowMenu):
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
		add_default_field(self.customForm)
class PainFadeSettings(maker.GuiMakerWindowMenu):
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
		add_default_field(self.customForm)
class InternetSettings(maker.GuiMakerWindowMenu):
	def start(self):
		self.customForm	= 	[
			((ttk.Label, 'rate', None,		cfg_grid,{}),
			(ttk.Entry, '', 'rate',		cfg_grid,{})),
			
			((ttk.Label, 'cl_updaterate',None,		cfg_grid,{}),
			(ttk.Entry, '','cl_updaterate',		cfg_grid,{})),
			
			((ttk.Label, 'cl_cmdrate',None,		cfg_grid,{}),
			(ttk.Entry, '','cl_cmdrate',		cfg_grid,{})),
			
			((ttk.Label, 'cl_interp',None,		cfg_grid,{}),
			(ttk.Entry, '','cl_interp',		cfg_grid,{})),
			
			((ttk.Label, 'cl_interp_ratio',None,		cfg_grid,{}),
			(ttk.Entry, '','cl_interp_ratio',		cfg_grid,{})),
			
			((ttk.Label, 'cl_smoothtime',None,		cfg_grid,{}),
			(ttk.Entry, '','cl_smoothtime',		cfg_grid,{}))]
		add_default_field(self.customForm)
class PerformanceSettings(maker.GuiMakerWindowMenu):
	def start(self):
		self.customForm	= 	[
			((ttk.Label, 'dota_cheap_water', None,		cfg_grid,{}),
			(ttk.Entry, '', 'dota_cheap_water',		cfg_grid,{})),
			
			((ttk.Label, 'cl_globallight_shadow_mode', None,		cfg_grid,{}),
			(ttk.Entry, '', 'cl_globallight_shadow_mode',		cfg_grid,{})),
			
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
		add_default_field(self.customForm)
class NetGraph(maker.GuiMakerWindowMenu):
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
			(ttk.Entry, '','net_graphinsetright',		cfg_grid,{})),
			
			((ttk.Label, 'net_graphpos',None,		cfg_grid,{}),
			(ttk.Entry, '','net_graphpos',		cfg_grid,{})),
			
			((ttk.Label, 'net_graphproportionalfont',None,		cfg_grid,{}),
			(ttk.Entry, '','net_graphproportionalfont',		cfg_grid,{})),
			
			((ttk.Label, 'net_graphtext',None,		cfg_grid,{}),
			(ttk.Entry, '','net_graphtext',		cfg_grid,{}))]
		add_default_field(self.customForm)
		add_remap_field(self.customForm)
class MiscSettings(maker.GuiMakerWindowMenu):	
	def start(self):
		self.customForm	= 	[
			((ttk.Label, 'Deny on right mouse click',None,	cfg_grid,{}),
			(ttk.Checkbutton, None,'dota_force_right_click_attack',		cfg_grid,{})),
			
			((ttk.Label, 'minimap hero icon size',None,		cfg_grid,{}),
			(ttk.Entry, '','dota_minimap_hero_size',		cfg_grid,{})),
			
			((ttk.Label, 'Threshold delay to accept minimap clicks',None,		cfg_grid,{}),
			(ttk.Entry, '','dota_minimap_misclick_time',		cfg_grid,{})),
			
			((ttk.Label, 'Health segmenting in the lifebar',None,		cfg_grid,{}),
			(ttk.Entry, '','dota_health_per_vertical_marker',		cfg_grid,{})),
			
			((ttk.Label, 'Disable mouse wheel zoom',None,		cfg_grid,{}),
			(ttk.Entry, '','dota_camera_disable_zoom',		cfg_grid,{})),
			
			((ttk.Label, 'Flying height of air units',None,		cfg_grid,{}),
			(ttk.Entry, '','dota_unit_fly_bonus_height',		cfg_grid,{})),
			
			((ttk.Label, 'Escape key allowed to hide game UI',None,	cfg_grid,{}),
			(ttk.Checkbutton, None,'gameui_allowescape',		cfg_grid,{})),
			
			((ttk.Label, 'Escape key allowed to show game UI',None,	cfg_grid,{}),
			(ttk.Checkbutton, None,'gameui_allowescapetoshow',		cfg_grid,{}))]
		add_default_field(self.customForm)
			
class MacroSettings(maker.GuiMakerWindowMenu):
	def start(self):
		self.customForm	= 	[
			((ttk.Label, 'Courier Deliver & Message',None,		cfg_grid,{}),
			(HotKeyGrabber, '','courier_hotkey',		cfg_grid,{}),
			(ttk.Entry, 'msg','enter message here',		cfg_grid,{})),
			
			((ttk.Label, 'Rune Checker',None,		cfg_grid,{}),
			(HotKeyGrabber, '','runechecker_hotkey',		cfg_grid,{})),
			
			#~ ((ttk.Label, 'Netgraph Toggle Hotkey',None,		cfg_grid,{}),
			#~ (HotKeyGrabber, '','netgraph_hotkey',		cfg_grid,{})),
			
			#~ ((ttk.Label, 'Netgraph Toggle Hotkey',None,		cfg_grid,{}),
			#~ (HotKeyGrabber, '','netgraph_hotkey',		cfg_grid,{}))
			]
		add_default_field(self.customForm)
		add_remap_field(self.customForm)
class TestingSettings(maker.GuiMakerWindowMenu):
	def start(self):
		self.customForm	= 	[
			((ttk.Label, 'Help text hotkey',None,		cfg_grid,{}),
			(HotKeyGrabber, '','help_hotkey',		cfg_grid,{}))]
		add_default_field(self.customForm)
class HpSegmentationSettings(maker.GuiMakerWindowMenu):
	def start(self):
		self.customForm	= 	[
			((ttk.Checkbutton, 'dota_force_right_click_attack','dota_force_right_click_attack',		cfg_grid,{}),
			(ttk.Label, 'Deny on right mouse click',None,	cfg_grid,{})),

			((ttk.Label, 'Hp Line Segment Toggle Hotkey',None,		cfg_grid,{}),
			(HotKeyGrabber, '','segment_hotkey',		cfg_grid,{})),

		
			((ttk.Label, 'dota_pain_fade_rate',None,		cfg_grid,{}),
			(ttk.Entry, '','dota_pain_fade_rate',		cfg_grid,{}))]
		add_default_field(self.customForm)
class AboutPage(maker.GuiMakerWindowMenu):
	def start(self):
		self.customForm	= 	[
			((ttk.Checkbutton, 'dota_force_right_click_attack','dota_force_right_click_attack',		cfg_grid,{}),
			(ttk.Label, 'Deny on right mouse click',None,	cfg_grid,{})),
		
			((ttk.Label, 'dota_pain_fade_rate',None,		cfg_grid,{}),
			(ttk.Entry, '','dota_pain_fade_rate',		cfg_grid,{})),
			
			((ttk.Label, 'Netgraph Toggle Hotkey',None,		cfg_grid,{}),
			(HotKeyGrabber, '','netgraph_hotkey',		cfg_grid,{}))]
		add_default_field(self.customForm)
class ProgramSetup(maker.GuiMakerWindowMenu):
	def start(self):
		self.customForm	= 	[
			((ttk.Checkbutton, 'dota_force_right_click_attack','dota_force_right_click_attack',		cfg_grid,{}),
			(ttk.Label, 'Deny on right mouse click',None,	cfg_grid,{})),
		
			((ttk.Label, 'dota_pain_fade_rate',None,		cfg_grid,{}),
			(ttk.Entry, '','dota_pain_fade_rate',		cfg_grid,{})),
			
			((ttk.Label, 'Netgraph Toggle Hotkey',None,		cfg_grid,{}),
			(HotKeyGrabber, '','netgraph_hotkey',		cfg_grid,{}))]
		add_default_field(self.customForm)


if __name__ == '__main__': 

	root = tk.Tk()
	main_gui = Gui_Main(root)
	#~ print(help(tk))
	root.mainloop()
