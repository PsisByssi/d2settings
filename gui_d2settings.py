import tkinter as tk
import tkinter.ttk as ttk
from pprint import pprint
import glob

import tkquick.gui.maker as maker
from tkquick.gui.style_defaults import *
from tkquick.gui import batteries
from tkquick.gui import tooltip
from timstools import ignored

import d2_func

label_centered = dict(c_labelHS,**{'anchor':'center'})

class BindKeyGrabber(batteries.HotKeyGrabber):
	def start(self):
		self.reset_on_click = False
		self.reset_on_focus = False
		self.custom_input = d2_func.valve_key_list
	
class AhkGrabber(batteries.HotKeyGrabber):
	def start(self):
		self.reset_on_click = False
		self.reset_on_focus = False
		self.custom_input = d2_func.ahk_key_list
		#~ def set(self, hotkeyvalues):
		#~ formatted = []
		#~ for key in hotkeyvalues:
			#~ formatted.append(d2_func.valve_key_parser(key))	
		#~ batteries.BindKeyGrabberMaker.set(self,formatted)		#call original func

def add_default_field(customForm):
	# Instead of manually adding the rows to custom form builder.
	# Each item that has a reference name in the dictionary gets a default value field
	for i, row in enumerate(customForm[:]):
		for col in row:
			#~ print(col[2])
			if col[2]:							# get the reference name and add default to the end
				def_ref = col[2]+'_default'
				new_row = list(row)
				new_row.append((ttk.Checkbutton, None, def_ref, cfg_grid,{}))
				del customForm[i]
				customForm.insert(i, new_row)
				break

def add_remap_field(customForm):
	# Instead of manually adding the rows to custom form builder.
	# Each BindKeyGrabber item that has a reference name in the dictionary gets a remap field as well
	for i, row in enumerate(customForm[:]):
		for col in row:
			if 'BindKeyGrabber' in col[0].__name__:		
				#~ print(col[0])
				#~ print('remapping...')
				if col[2]:							# get the reference name and add remap to the end
					def_ref = col[2]+'_remap'
					new_row = list(row)	
					new_row.append((AhkGrabber, None, def_ref, cfg_grid,{}))
					del customForm[i]
					customForm.insert(i, new_row)
					break

def add_headings(customForm,width=3):
	if width == 4:
		customForm.insert(0,
				((ttk.Label, 'Setting',None,		cfg_gridEW, label_centered),
				(ttk.Label, 'Dota Hotkey',None,		cfg_gridEW, label_centered),
				(ttk.Label, 'Use (default)',None,		cfg_gridEW, label_centered),
				(ttk.Label, 'Remap Hotkey',None,		cfg_gridEW, label_centered))) 
		customForm.insert(1,
				((ttk.Separator,	None,None,dict(cfg_gridEW,**{'columnspan':'4'}),{}),),)
	elif width == 3:
		customForm.insert(0,
				((ttk.Label, 'Setting',None,		cfg_gridEW, label_centered),
				(ttk.Label, 'Dota Hotkey',None,		cfg_gridEW, label_centered),
				(ttk.Label, 'Use (default)',None,		cfg_gridEW, label_centered),)) 
		customForm.insert(1,
				((ttk.Separator,	None,None,dict(cfg_gridEW,**{'columnspan':'3'}),{}),),)
		
class Gui_Main(maker.GuiMakerWindowMenu):	#controler of page	
	def start(self):
		self.style = {'bg':'grey75','bd':5,'relief':'flat'}
		self.customForm	= 	[
			(SettingsNoteBook, '','settings',		cfg_grid,c_label)]			
		self.toolBar = [(('save', self.save_cfg,  {'side': tk.RIGHT},c_button),
						('reset', self.reload_cfg, {'side': tk.RIGHT},c_button))]
	
	def finish(self):
		# Runs after everything else, see maker
		def change_normal(event):
			event.widget.changed = True
		def change_class(event):
			event.widget.master.changed = True		
		for tab in self.formRef['settings'].widget_ref.values():		# The notebook tabs
			for widget in tab.formRef.values():							# adds binds to all the widgets to track their changes
				#~ print(repr(widget))
				if isinstance(widget, batteries.HotKeyGrabber):
					widget.ent.bind('<FocusIn>', change_class, add='+')	# when saving i just have to check the widget saved in formRef, because that is what we mark here
				elif isinstance(widget, ttk.Checkbutton):
					widget.bind('<Button-1>', change_normal, add='+')
				elif isinstance(widget, maker.MakerScrolledList):
					widget.listbox.bind('<Button-1>', change_class, add='+')
				else:
					widget.bind('<Key>', change_normal, add='+')	
	
	def load_cfg(self, cfg, bind_cfg, ahk_cfg):
		def set_default_value(set_checkbox_on=False,ignore_mode=False):	# Func to set defaults!
			with ignored(KeyError):			# If there is no default value whateva
				try:
					try:
						index = cfg_values.index('Default') + 1
					except ValueError:
						index = cfg_values.index('default') + 1
				except Exception:pass									# No default Value Set	
				else:			
					default_val = cfg_values[index]						
					widg = tab.formRef[setting+'_default']
					widg.config(text = '  ({0})'.format(default_val))
				if set_checkbox_on:
					def_tkvar = tab.variables[setting+'_default']
					def_tkvar.set(1)
		def set_tooltip():
			with ignored(KeyError):
				try:
					try:
						index = cfg_values.index('tooltip') + 1
					except ValueError:
						index = cfg_values.index('Tooltip') + 1
				except Exception:pass							# No Value Set
				else:
					text = cfg_values[index]
					widg = tab.formRef[setting]
					tooltip.ToolTip(widg, delay=200,text=text)
		for tab in self.formRef['settings'].widget_ref.values():		#The notebook tabs
			for setting, tkvar in tab.variables.items():
				for cfg_setting, cfg_values in cfg.items():
					if setting == cfg_setting:				# We are only dealing with settings that are not ignored!
						#~ print(cfg_setting,'cfg setting',cfg_values)
						if cfg_values[0] not in ('//'):	# The setting has a value associated with it
							#~ print('value assocated', cfg_values[0])
							#~ print(setting, cfg_values)
							#~ print()
							tkvar.set(cfg_values[0])
							set_default_value()
							set_tooltip()
						else:								# These settings require no argument they are on by being presetn
							#~ print('No argument setting')
							#~ print(setting,cfg_values)
							#~ if cfg_values[0] == '//':
								
							set_default_value()
							tkvar.set(1)
							set_tooltip()
						break
					elif '//IGNORE' in cfg_setting:					# Commented Out Values
						cfg_setting = cfg_setting.split(' ')[-1]	# Remove the //IGNORE
						if setting == cfg_values[0]:
							if cfg_values[0] not in ('//'):	# The setting has a value associated with it
								#~ print('value assocated', cfg_values[1])
								#~ print(setting, cfg_values)
								#~ print()
								tkvar.set(cfg_values[1])
								set_default_value(set_checkbox_on=1)
								set_tooltip()
							else:								# These settings require no argument they are on by being presetn
								#~ print('No argument setting')
								#~ print(setting, cfg_values)
								#~ if cfg_values[0] == '//':
									
								set_default_value(set_checkbox_on=1)
								tkvar.set(1)
								set_tooltip()
								#~ print()
							break
					else:
						#~ print('NO MATCH', setting)
						pass
			for setting, widg in tab.formRef.items():						# Handle the bind settings from the autoexec
				for bind_setting, bind_values in bind_cfg.items():              
					#~ print('calling set')
					bind_value = bind_setting	 
					if setting in bind_values:						# Atm i'm allowing myself to place the tag anywhere in the values
						widg.set([bind_value])							# Set method on the Hotkeygrabber
						break			
				for ahk_bind_setting, ahk_bind_value in ahk_cfg.items():
					pass

	def reload_cfg(self):
		pass
	def save_cfg(self):
		# Only gets the values and rates the widgets that have been changed
		hp_saved = False												# To prevent listbox being saved twice
		for tab in self.formRef['settings'].widget_ref.values():		# The notebook tabs
			for setting, widget in tab.formRef.items():	
				if hasattr(widget, 'changed') and widget.changed:		 	
					print('changed',repr(widget))
					try:
						value = widget.get()
					except AttributeError:
						if isinstance(widget, batteries.HotKeyGrabber):
							value = widget.var.get()					
						elif isinstance(widget, ttk.Checkbutton):			
							tkvar = tab.variables[setting]
							value = tkvar.get()
						elif isinstance(widget, maker.MakerScrolledList):	
							if not hp_saved:
								hp_saved = True
								d2_func.save_hptoggle(self.app, widget)
							continue
					d2_func.save_settings(self.app.auto_exec, setting, value)	# Edits the in memory file		
		
		with open('autoexec_saved.cfg', 'w') as file:
			for row in self.app.auto_exec:
				file.write(row)
		print('Finished saving')

class SettingsNoteBook(maker.GuiNoteBook):			# Main controller notebook, used to switch the pain on the right of the treeviewer
	def start(self):
		self.style = {'bg':'#232327','bd':5,'relief':'flat'}
		#~ self.conPack = {'expand':'1','fill':'both', 'side':'top'}
		#~ self.config(padx=40,pady=40)		
		self.widgList = [ProgramSetup,MiscSettings,NetGraph,InternetSettings,MacroSettings,PerformanceSettings,PainFadeSettings,StandardMenu,HpSegment]
		self.tabText = ['Launch','Misc','NetGraph','Internet','Macros','Performance','Damage Delay', 'Standard Options','Hp Segment']
		#~ self.nbStyle=c_hiddenNotebook	# only woring in main not in running from script
		self.widgSide = ['nsew','nsew','nsew','nsew','nsew','nsew','nsew','nsew','nsew','nsew']
		self.padding=[10, 10, 10, 10, 10, 10, 10, 10,10]

class ProgramSetup(maker.GuiMakerWindowMenu):						
	def start(self):
		self.customForm	= 	[
			((ttk.Label, 'Reload autoexec.cfg Hotkey',None,		cfg_grid,{}),
			(BindKeyGrabber, '','reload_exec_hotkey',		cfg_grid,{})),
			
			((ttk.Label, 'Help Text',None,		cfg_grid,{}),
			(BindKeyGrabber, '','help_hotkey',		cfg_grid,{})),
			
			((ttk.Label, 'Turn Text Mode Off',None,		cfg_grid,{}),
			(BindKeyGrabber, '','text_off_hotkey',		cfg_grid,{})),
	
			((ttk.Checkbutton, 'novid','novid',		cfg_grid,{}),
			(ttk.Label, 'Skips valve intro video',None,	cfg_grid,{})),
			
			((ttk.Checkbutton, 'console','console',		cfg_grid,{}),
			(ttk.Label, 'Enables consoles in game (default hotkey is `)',None,	cfg_grid,{})),
			
			((ttk.Checkbutton, 'windowed -w # -h # -noborder','novid',		cfg_grid,{}),
			(ttk.Label, 'Window mode with no border, REPLACE # WITH YOUR DESIRED',None,	cfg_grid,{}))]
		add_default_field(self.customForm)
		add_headings(self.customForm, width=3)
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
		add_headings(self.customForm, width=3)
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
		add_headings(self.customForm, width=3)

class PerformanceSettings(maker.GuiNoteBook):
	class LowReccommended(maker.GuiMakerWindowMenu):
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
				(ttk.Entry, '','mat_vsync',		cfg_grid,{}))]
			add_default_field(self.customForm)
			add_headings(self.customForm, width=3)
	class LowNext(maker.GuiMakerWindowMenu):
		def start(self):
			self.customForm	= 	[				
				((ttk.Label, 'props_break_max_pieces',None,		cfg_grid,{}),
				(ttk.Entry, '','props_break_max_pieces',		cfg_grid,{})),
				
				((ttk.Label, 'ragdoll_sleepaftertime',None,		cfg_grid,{}),
				(ttk.Entry, '','ragdoll_sleepaftertime',		cfg_grid,{})),
				
				((ttk.Label, 'g_ragdoll_fadespeed',None,		cfg_grid,{}),
				(ttk.Entry, '','g_ragdoll_fadespeed',		cfg_grid,{})),
				
				((ttk.Label, 'g_ragdoll_important_maxcount',None,		cfg_grid,{}),
				(ttk.Entry, '','g_ragdoll_important_maxcount',		cfg_grid,{})),
				
				((ttk.Label, 'g_ragdoll_lvfadespeed',None,		cfg_grid,{}),
				(ttk.Entry, '','g_ragdoll_lvfadespeed',		cfg_grid,{})),
				
				((ttk.Label, 'g_ragdoll_maxcount',None,		cfg_grid,{}),
				(ttk.Entry, '','g_ragdoll_maxcount',		cfg_grid,{})),
				
				((ttk.Label, 'cl_detaildist',None,		cfg_grid,{}),
				(ttk.Entry, '','cl_detaildist',		cfg_grid,{})),
				
				((ttk.Label, 'cl_detailfade',None,		cfg_grid,{}),
				(ttk.Entry, '','cl_detailfade',		cfg_grid,{})),
				
				((ttk.Label, 'locator_text_drop_shadow',None,		cfg_grid,{}),
				(ttk.Entry, '','locator_text_drop_shadow',		cfg_grid,{})),
				
				((ttk.Label, 'gpu_mem_level',None,		cfg_grid,{}),
				(ttk.Entry, '','gpu_mem_level',		cfg_grid,{})),
				
				((ttk.Label, 'mem_level',None,		cfg_grid,{}),
				(ttk.Entry, '','mem_level',		cfg_grid,{})),
				
				((ttk.Label, 'dota_minimap_use_dynamic_mesh',None,		cfg_grid,{}),
				(ttk.Entry, '','dota_minimap_use_dynamic_mesh',		cfg_grid,{})),
				
				((ttk.Label, 'mat_bumpmap',None,		cfg_grid,{}),
				(ttk.Entry, '','mat_bumpmap',		cfg_grid,{})),
				
				((ttk.Label, 'mat_specular',None,		cfg_grid,{}),
				(ttk.Entry, '','mat_specular',		cfg_grid,{})),
				
				((ttk.Label, 'mat_phong',None,		cfg_grid,{}),
				(ttk.Entry, '','mat_phong',		cfg_grid,{})),
				
				
				((ttk.Label, 'mp_usehwmvcds',None,		cfg_grid,{}),
				(ttk.Entry, '','mp_usehwmvcds',		cfg_grid,{})),
				
				((ttk.Label, 'mp_usehwmmodels',None,		cfg_grid,{}),
				(ttk.Entry, '','mp_usehwmmodels',		cfg_grid,{}))]
			add_default_field(self.customForm)
			add_headings(self.customForm, width=3)
	class LowNextNext(maker.GuiMakerWindowMenu):
		def start(self):
			self.customForm	= 	[
				((ttk.Label, 'r_worldlights',None,		cfg_grid,{}),
				(ttk.Entry, '','r_worldlights',		cfg_grid,{})),
				
				((ttk.Label, 'r_decals',None,		cfg_grid,{}),
				(ttk.Entry, '','r_decals',		cfg_grid,{})),
				
				((ttk.Label, 'r_decal_overlap_count',None,		cfg_grid,{}),
				(ttk.Entry, '','r_decal_overlap_count',		cfg_grid,{})),
				
				((ttk.Label, 'r_worldlightmin',None,		cfg_grid,{}),
				(ttk.Entry, '','r_worldlightmin',		cfg_grid,{})),
				
				((ttk.Label, 'r_drawmodeldecals',None,		cfg_grid,{}),
				(ttk.Entry, '','r_drawmodeldecals',		cfg_grid,{})),
				
				((ttk.Label, 'r_decalstaticprops',None,		cfg_grid,{}),
				(ttk.Entry, '','r_decalstaticprops',		cfg_grid,{})),
				
				((ttk.Label, 'r_flashlightdepthtexture',None,		cfg_grid,{}),
				(ttk.Entry, '','r_flashlightdepthtexture',		cfg_grid,{})),
				
				((ttk.Label, 'r_rainparticledensity',None,		cfg_grid,{}),
				(ttk.Entry, '','r_rainparticledensity',		cfg_grid,{})),
				
				((ttk.Label, 'r_shadowfromworldlights',None,		cfg_grid,{}),
				(ttk.Entry, '','r_shadowfromworldlights',		cfg_grid,{})),
				
				((ttk.Label, 'r_DrawDetailProps',None,		cfg_grid,{}),
				(ttk.Entry, '','r_DrawDetailProps',		cfg_grid,{})),
				
				((ttk.Label, 'r_FlashlightDetailProps',None,		cfg_grid,{}),
				(ttk.Entry, '','r_FlashlightDetailProps',		cfg_grid,{})),
				
				((ttk.Label, 'r_shadow_deferred_downsample',None,		cfg_grid,{}),
				(ttk.Entry, '','r_shadow_deferred_downsample',		cfg_grid,{})),
				
				((ttk.Label, 'r_WaterDrawReflection',None,		cfg_grid,{}),
				(ttk.Entry, '','r_WaterDrawReflection',		cfg_grid,{})),
				
				((ttk.Label, 'r_renderoverlayfragment',None,		cfg_grid,{}),
				(ttk.Entry, '','r_renderoverlayfragment',		cfg_grid,{}))]
			add_default_field(self.customForm)
			add_headings(self.customForm, width=3)
	class LowLastResort(maker.GuiMakerWindowMenu):
		def start(self):
			self.customForm = [
				((ttk.Label, 'r_shadowmaxrendered',None,		cfg_grid,{}),
				(ttk.Entry, '','r_shadowmaxrendered',		cfg_grid,{})),
				
				((ttk.Label, 'r_flashlightrendermodels',None,		cfg_grid,{}),
				(ttk.Entry, '','r_flashlightrendermodels',		cfg_grid,{})),
				
				((ttk.Label, 'r_shadows',None,		cfg_grid,{}),
				(ttk.Entry, '','r_shadows',		cfg_grid,{})),
				
				((ttk.Label, 'r_3dsky',None,		cfg_grid,{}),
				(ttk.Entry, '','r_3dsky',		cfg_grid,{})),
				
				((ttk.Label, 'r_flashlightnodraw',None,		cfg_grid,{}),
				(ttk.Entry, '','r_flashlightnodraw',		cfg_grid,{})),
				
				((ttk.Label, 'mat_force_low_quality_shadows',None,		cfg_grid,{}),
				(ttk.Entry, '','mat_force_low_quality_shadows',		cfg_grid,{})),
				
				((ttk.Label, 'mat_filtertextures',None,		cfg_grid,{}),
				(ttk.Entry, '','mat_filtertextures',		cfg_grid,{})),
				
				((ttk.Label, 'mat_disable_bloom',None,		cfg_grid,{}),
				(ttk.Entry, '','mat_disable_bloom',		cfg_grid,{})),
				
				((ttk.Label, 'mat_disable_fancy_blending',None,		cfg_grid,{}),
				(ttk.Entry, '','mat_disable_fancy_blending',		cfg_grid,{}))]
			add_default_field(self.customForm)
			add_headings(self.customForm, width=3)
	class High(maker.GuiMakerWindowMenu):
		def start(self):
			self.customForm = [
				((ttk.Label, 'snd_mix_async',None,		cfg_grid,{}),
				(ttk.Entry, '','snd_mix_async',		cfg_grid,{})),
				
				((ttk.Label, 'cl_phys_maxticks',None,		cfg_grid,{}),
				(ttk.Entry, '','cl_phys_maxticks',		cfg_grid,{})),
				
				((ttk.Label, 'mat_grain_enable',None,		cfg_grid,{}),
				(ttk.Entry, '','mat_grain_enable',		cfg_grid,{})),
				
				((ttk.Label, 'mat_local_contrast_enable',None,		cfg_grid,{}),
				(ttk.Entry, '','mat_local_contrast_enable',		cfg_grid,{})),
				
				((ttk.Label, 'mat_motion_blur_enabled',None,		cfg_grid,{}),
				(ttk.Entry, '','mat_motion_blur_enabled',		cfg_grid,{})),
				
				((ttk.Label, 'mat_picmip',None,		cfg_grid,{}),
				(ttk.Entry, '','mat_picmip',		cfg_grid,{})),
				
				((ttk.Label, 'r_shadowrendertotexture',None,		cfg_grid,{}),
				(ttk.Entry, '','r_shadow_half_update_rate',		cfg_grid,{})),
				
				((ttk.Label, 'r_threadeddetailprops',None,		cfg_grid,{}),
				(ttk.Entry, '','r_threadeddetailprops',		cfg_grid,{}))
				]
			add_default_field(self.customForm)
			add_headings(self.customForm, width=3)
	def start(self):
		self.widgList = [self.LowReccommended, self.LowNext, self.LowNextNext, self.LowLastResort, self.High]
		self.tabText = ['Reccommended','Now try these','Or try these','only if you are desperate','High Performance settings!']
		#~ self.nbStyle=c_hiddenNotebook	# only woring in main not in running from script
		self.widgSide = ['nsew','nsew','nsew','nsew','nsew','nsew','nsew','nsew']
	def finish(self):
		#~ print(self.widget_ref)
		for tab in self.widget_ref.values():
			self.variables.update(tab.variables)
			#~ self.formRef.update(tab.formRef)
		#~ self.formRef = 
		#~ pprint(self.formRef)
		#~ pprint(self.variables)
class NetGraph(maker.GuiMakerWindowMenu):
	def start(self):		
		self.customForm	= 	[
			((ttk.Label, 'Netgraph Toggle Hotkey',None,		cfg_grid,{}),
			(BindKeyGrabber, '','netgraph_hotkey',		cfg_grid,{})),
			
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
		add_headings(self.customForm, width=4)
class MiscSettings(maker.GuiMakerWindowMenu):	
	def start(self):
		self.customForm	= 	[
			((ttk.Label, 'Deny on right mouse click',None,	cfg_grid,{}),
			(ttk.Checkbutton, None,'dota_force_right_click_attack',		cfg_grid,{})),
			
			((ttk.Label, 'minimap hero icon size',None,		cfg_grid,{}),
			(ttk.Entry, '','dota_minimap_hero_size',		cfg_grid,{})),
			
			((ttk.Label, 'Threshold delay to accept minimap clicks',None,		cfg_grid,{}),
			(ttk.Entry, '','dota_minimap_misclick_time',		cfg_grid,{})),
			
			((ttk.Label, 'dota_recent_event (jump to last ping)',None,		cfg_grid,{}),
			(BindKeyGrabber, '','dota_recent_event',		cfg_grid,{})),
			
			((ttk.Label, 'Health segmenting in the lifebar',None,		cfg_grid,{}),
			(ttk.Entry, '','dota_health_per_vertical_marker',		cfg_grid,{})),
			
			((ttk.Label, 'Disable mouse wheel zoom',None,		cfg_grid,{}),
			(ttk.Entry, '','dota_camera_disable_zoom',		cfg_grid,{})),
			
			((ttk.Label, 'Flying height of air units',None,		cfg_grid,{}),
			(ttk.Entry, '','dota_unit_fly_bonus_height',		cfg_grid,{})),
			
			((ttk.Label, 'dota_minimap_ping_duration',None,		cfg_grid,{}),
			(ttk.Entry, '','dota_minimap_ping_duration',		cfg_grid,{})),
			
			((ttk.Label, 'dota_minimap_rune_size',None,		cfg_grid,{}),
			(ttk.Entry, '','dota_minimap_rune_size',		cfg_grid,{})),
			
			((ttk.Label, 'dota_minimap_tower_defend_distance',None,		cfg_grid,{}),
			(ttk.Entry, '','dota_minimap_tower_defend_distance',		cfg_grid,{})),
			
			((ttk.Label, 'dota_sf_game_end_delay',None,		cfg_grid,{}),
			(ttk.Entry, '','dota_sf_game_end_delay',		cfg_grid,{}))
			
			#~ ((ttk.Label, 'Escape key allowed to hide game UI',None,	cfg_grid,{}),
			#~ (ttk.Checkbutton, None,'gameui_allowescape',		cfg_grid,{})),
			
			#~ ((ttk.Label, 'Escape key allowed to show game UI',None,	cfg_grid,{}),
			#~ (ttk.Checkbutton, None,'gameui_allowescapetoshow',		cfg_grid,{}))
			]

		add_default_field(self.customForm)
		add_remap_field(self.customForm)
		add_headings(self.customForm, width=3)
class MacroSettings(maker.GuiMakerWindowMenu):
	def start(self):
		self.customForm	= 	[						
			((ttk.Label, 'Courier Deliver & Message',None,		cfg_grid,{}),
			(BindKeyGrabber, '','courier_hotkey',		cfg_grid,{})),
			
			(maker.BLANK,
			(ttk.Entry, 'msg','enter message here',	cfg_grid,{})),
			
			((ttk.Label, 'Toggle Rune Spots & Hero',None,		cfg_grid,{}),
			(BindKeyGrabber, '','runechecker_hotkey',		cfg_grid,{})),
			
			((ttk.Label, 'Top Rune',None,		cfg_grid,{}),
			(BindKeyGrabber, '','toprune_hotkey',		cfg_grid,{})),
			
			((ttk.Label, 'Bot Rune',None,		cfg_grid,{}),
			(BindKeyGrabber, '','botrune_hotkey',		cfg_grid,{})),
			
			((ttk.Label, 'Smart attack',None,		cfg_grid,{}),
			(BindKeyGrabber, '','smart_attack_hotkey',		cfg_grid,{})),
			
			((ttk.Label, 'Smart stop',None,		cfg_grid,{}),
			(BindKeyGrabber, '','smart_stop_hotkey',		cfg_grid,{})),
			
			#~ ((ttk.Label, 'Netgraph Toggle Hotkey',None,		cfg_grid,{}),
			((ttk.Label, 'Smart hold',None,		cfg_grid,{}),
			(BindKeyGrabber, '','smart_hold_hotkey',		cfg_grid,{})),
			
			#~ ((ttk.Label, 'Netgraph Toggle Hotkey',None,		cfg_grid,{}),
			#~ (BindKeyGrabber, '','netgraph_hotkey',		cfg_grid,{})),
			
			#~ ((ttk.Label, 'Netgraph Toggle Hotkey',None,		cfg_grid,{}),
			#~ (BindKeyGrabber, '','netgraph_hotkey',		cfg_grid,{}))
			]
		add_default_field(self.customForm)
		add_remap_field(self.customForm)
		add_headings(self.customForm, width=4)
class Testing(maker.GuiMakerWindowMenu):
	def start(self):
		self.customForm	= 	[
			((ttk.Label, 'Mute/unmute testing mode',None,		cfg_grid,{}),
			(BindKeyGrabber, '','testing_lock_hotkey',		cfg_grid,{})),
			
			((ttk.Label, 'Test Mode Hotkey',None,		cfg_grid,{}),
			(BindKeyGrabber, '','test_mode_hotkey_exception',		cfg_grid,{}))]
		add_default_field(self.customForm)
class HpSegment(maker.GuiMakerWindowMenu):
	class SelectedHeroes(maker.MakerScrolledList):
		def start(self):
			self.use_default_event_handler = True
			self.options=[]
			index = self.app.cfg_settings['hptoggle'] + 5	#need to fix csv so it counts blank lines
			#~ print('len! of exec data', len(self.app.auto_exec.data))
			for i, row in enumerate(self.app.auto_exec.data[index:]):	
				if not row:pass
				elif 'hp' in row:
					row = row.split(' ')
					if 'hp.cfg' in row[3]:
						hero_name = row[3].split('_hp.cfg')[0]					
						self.options.append(hero_name)
				else:
					break
			#~ for file in glob.glob('hp/*_hp.cfg'):
				#~ self.options.append(file)
		def run_command(self, selection):
			self.listbox.delete(self.listbox.curselection()[0])
		def finish(self):
			self.listbox.config(selectmode='single')
	class AllHeroes(maker.MakerScrolledList):
		def start(self):
			self.use_default_event_handler = True
			self.options=[]
			for file in glob.glob('hp/*_hp.cfg'):
				file = file.split(os.sep)[-1]
				file = file.split('_hp.cfg')[0]
				self.options.append(file)
		def run_command(self, selection=0):
			selection = self.listbox.get(tk.ANCHOR)
			other_lb = self.caller.formRef['selectedheroeslistbox'].listbox
			if selection not in other_lb.get(0, 'end'):
				other_lb.insert(tk.END, selection)
		def finish(self):
			self.listbox.config(selectmode='single')
	class AddRemove(maker.GuiMaker):
		def start(self):
			self.imgdir = 'img/'
			self.toolPhotoObjs = []
			self.customForm = [
				(ttk.Button, ['left.png'], '', cfg_grid, {}),
				(ttk.Button, ['right.png'], '', cfg_grid, {})]
	def start(self):
		self.customForm	= 	[
			((ttk.Label, 'hptoggle_hotkey','',		cfg_grid,{}),
			(BindKeyGrabber, '','Hero Specific bind toggle Toggle',	cfg_grid,{})),
			
			((self.SelectedHeroes, '','selectedheroeslistbox',	cfg_grid,{}),
			(self.AddRemove,'','',cfg_grid,{}),
			(self.AllHeroes, '','allheroeslistbox',	cfg_grid,{})),
			
			((ttk.Label, '1st Toggle','',	cfg_grid,{}),
			(BindKeyGrabber,'','hpkey1',		cfg_grid,{})),
			
			((ttk.Label, '2nd Toggle','',	cfg_grid,{}),
			(BindKeyGrabber,'','hpkey2',		cfg_grid,{})),
			
			((ttk.Label, '3rd Toggle','',	cfg_grid,{}),
			(BindKeyGrabber,'','hpkey3',		cfg_grid,{})),
			
			((ttk.Label, '4th Toggle','',	cfg_grid,{}),
			(BindKeyGrabber,'','hpkey4',		cfg_grid,{})),
			
			((ttk.Label, '5th Toggle','',	cfg_grid,{}),
			(BindKeyGrabber,'','hpkey5',		cfg_grid,{})),
			
			((ttk.Label, '6th Toggle','',	cfg_grid,{}),
			(BindKeyGrabber,'','hpkey6',		cfg_grid,{})),
			
			((ttk.Label, '7th Toggle','',	cfg_grid,{}),
			(BindKeyGrabber,'','hpkey7',		cfg_grid,{})),
			
			((ttk.Label, '8th Toggle','',	cfg_grid,{}),
			(BindKeyGrabber,'','hpkey8',		cfg_grid,{})),
			
			((ttk.Label, '9th Toggle','',	cfg_grid,{}),
			(BindKeyGrabber,'','hpkey9',		cfg_grid,{})),
			
			((ttk.Label, '10th Toggle','',	cfg_grid,{}),
			(BindKeyGrabber,'','hpkey10',		cfg_grid,{}))]
		add_default_field(self.customForm)
		add_headings(self.customForm)
		add_remap_field(self.customForm)
	def finish(self):
		d2_func.load_keys_hptoggle(self)
class AboutPage(maker.GuiMakerWindowMenu):
	def start(self):
		self.customForm	= 	[
			((ttk.Checkbutton, 'dota_force_right_click_attack','dota_force_right_click_attack',		cfg_grid,{}),
			(ttk.Label, 'Deny on right mouse click',None,	cfg_grid,{})),
		
			((ttk.Label, 'dota_pain_fade_rate',None,		cfg_grid,{}),
			(ttk.Entry, '','dota_pain_fade_rate',		cfg_grid,{})),
			
			((ttk.Label, 'Netgraph Toggle Hotkey',None,		cfg_grid,{}),
			(BindKeyGrabber, '','netgraph_hotkey',		cfg_grid,{}))]
		add_default_field(self.customForm)
class StandardMenu(maker.GuiMakerWindowMenu):
	def start(self):
		self.customForm	= 	[
			#~ ((ttk.Checkbutton, '','',		cfg_grid,{}),
			#~ (ttk.Label, '',None,	cfg_grid,{})),
		
			((ttk.Label, 'dota_camera_speed',None,		cfg_grid,{}),
			(ttk.Entry, '','dota_camera_speed',		cfg_grid,{})),
			
			((ttk.Label, 'dota_camera_accelerate',None,		cfg_grid,{}),
			(ttk.Entry, '','dota_camera_accelerate',		cfg_grid,{})),
			
			((ttk.Label, 'dota_player_multipler_orders',None,		cfg_grid,{}),
			(ttk.Entry, '','dota_player_multipler_orders',		cfg_grid,{})),
			
			((ttk.Label, 'dota_player_units_auto_attack',None,		cfg_grid,{}),
			(ttk.Entry, '','dota_player_units_auto_attack',		cfg_grid,{})),
			
			((ttk.Label, 'dota_ability_quick_cast',None,		cfg_grid,{}),
			(ttk.Entry, '','dota_ability_quick_cast',		cfg_grid,{})),
			
			((ttk.Label, 'dota_hud_healthbar_number',None,		cfg_grid,{}),
			(ttk.Entry, '','dota_hud_healthbar_number',		cfg_grid,{})),
			
			((ttk.Label, 'dota_killcam_show',None,		cfg_grid,{}),
			(ttk.Entry, '','dota_killcam_show',		cfg_grid,{})),
			
			((ttk.Label, 'dota_screen_shake',None,		cfg_grid,{}),
			(ttk.Entry, '','dota_screen_shake',		cfg_grid,{})),
			
			((ttk.Label, 'dota_always_show_player_names',None,		cfg_grid,{}),
			(ttk.Entry, '','dota_always_show_player_names',		cfg_grid,{})),
			
			]
		add_default_field(self.customForm)
		add_headings(self.customForm)
		add_remap_field(self.customForm)
		
class D(maker.GuiMakerWindowMenu):
	def start(self):
		self.customForm	= 	[
			((ttk.Checkbutton, '','',		cfg_grid,{}),
			(ttk.Label, '',None,	cfg_grid,{})),
		
			((ttk.Label, '',None,		cfg_grid,{}),
			(ttk.Entry, '','',		cfg_grid,{})),
			
			((ttk.Label, '',None,		cfg_grid,{}),
			(ttk.Entry, '','',		cfg_grid,{})),
			
			((ttk.Label, '',None,		cfg_grid,{}),
			(ttk.Entry, '','',		cfg_grid,{})),
			
			((ttk.Label, '',None,		cfg_grid,{}),
			(BindKeyGrabber, '','here',		cfg_grid,{}))]
		#~ add_default_field(self.customForm)
		#~ add_headings(self.customForm)
		#~ add_remap_field(self.customForm)

class D2(maker.GuiMakerWindowMenu):
	def start(self):
		self.customForm	= 	[
			((ttk.Checkbutton, '','',		cfg_grid,{}),
			(ttk.Label, '',None,	cfg_grid,{})),
		
			((ttk.Label, '',None,		cfg_grid,{}),
			(ttk.Entry, '','here',		cfg_grid,{})),
			
			((ttk.Label, '',None,		cfg_grid,{}),
			(BindKeyGrabber, '','here',		cfg_grid,{}))]
		#~ add_default_field(self.customForm)
		#~ add_headings(self.customForm)
		#~ add_remap_field(self.customForm)

if __name__ == '__main__': 

	root = tk.Tk()
	main_gui = Gui_Main(root)
	#~ print(help(tk))
	root.mainloop()
