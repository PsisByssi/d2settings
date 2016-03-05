import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from tkinter import filedialog
import json
from pprint import pprint
import glob
import webbrowser
import logging

from PIL import Image as PImage 
from PIL import ImageTk
import tkquick.gui.maker as maker
from tkquick.gui.style_defaults import *
from tkquick.gui import batteries
from tkquick.gui import tooltip
import timstools
from timstools import ignored

import d2_func

ass=0

label_centered = dict(c_labelHS,**{'anchor':'center'})

#~ DOTA_HOTKEYS = {}  # keys that are taken
#~ DISABLED_KEYS = {} # counts the num of clashses a key has currently

grabber_validator =  batteries.ValidateGrabbers(NORMAL = {},
                                                DISABLED = {},
                                                automatic_disable = True,
                                                automatic_enable = True,
                                                grabber_name_attrib = 'form_name')
class BindKeyGrabber(batteries.HotKeyGrabber):
    def start(self):
        self.reset_on_click = False
        self.reset_on_focus = False
        self.custom_input = d2_func.valve_key_list
        self.max_keys = 1
        self.conf = {'width':15, 'cursor':'hand2', 'anchor':'center'}
        self.text='...'
        def loopem(setting):
            for tab in self.app.main_gui.formRef['settings'].widget_ref.values():
                widget = tab.formRef.get(setting)
                if widget:
                    return widget
            else:
                return None
        grabber_validator.get_grabber_from_name = loopem
        self.validate_multiple_grabbers = grabber_validator
                
class AhkGrabber(batteries.HotKeyGrabber):
    def start(self):
        self.reset_on_click = False
        self.reset_on_focus = False
        self.custom_input = d2_func.valve_key_list
        self.capture_mouse = [2]
        self.conf = {'cursor':'hand2', 'anchor':'center','padding':[5,0,5,0]}
        self.text='...'
        self.validate_multiple_grabbers = grabber_validator
        
def add_default_field(customForm):
    # Instead of manually adding the rows to custom form builder.
    # Each item that has a reference name in the dictionary gets a default value field
    for i, row in enumerate(customForm[:]):
        for col in row:
            if col[2]:                          # get the reference name and add default to the end
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
                if col[2]:                          # get the reference name and add remap to the end
                    def_ref = col[2]+'_remap'
                    new_row = list(row) 
                    new_row.append((AhkGrabber, None, def_ref, cfg_grid,{}))
                    del customForm[i]
                    customForm.insert(i, new_row)
                    break

def add_headings(customForm,width=3):
    if width == 4:
        customForm.insert(0,
                ((ttk.Label, 'Setting',None,        cfg_gridEW, label_centered),
                (ttk.Label, 'Dota Hotkey',None,     cfg_gridEW, label_centered),
                (ttk.Label, 'Use (default)',None,       cfg_gridEW, label_centered),
                (ttk.Label, 'Remap Hotkey',None,        cfg_gridEW, label_centered))) 
        customForm.insert(1,
                ((ttk.Separator,    None,None,dict(cfg_gridEW,**{'columnspan':'4'}),{}),),)
    elif width == 3:
        customForm.insert(0,
                ((ttk.Label, 'Setting',None,        cfg_gridEW, label_centered),
                (ttk.Label, 'Dota Hotkey',None,     cfg_gridEW, label_centered),
                (ttk.Label, 'Use (default)',None,       cfg_gridEW, label_centered),)) 
        customForm.insert(1,
                ((ttk.Separator,    None,None,dict(cfg_gridEW,**{'columnspan':'3'}),{}),),)
        
class Gui_Main(maker.GuiMakerWindowMenu):
    imgdir = 'img/'
    def start(self):
        self.style = {'bg':'grey75','bd':5,'relief':'flat'}
        self.customForm =   [
        (SettingsNoteBook, '','settings',       cfg_grid, {})]          
        self.toolBar = [((['save.png'], self.save_cfg,  {'side': tk.RIGHT},c_button),
                        (['reload.png'], self.reload_cfg, {'side': tk.RIGHT},c_button),
                        (['settings.png'], self.preferences , {'side': tk.RIGHT},c_button),
                        (ttk.Label, '','status_icon', {'fill':'both','expand':'no','side':'right'}, dict(c_label,**{'padding':'7'})),
                        (ttk.Label, '','status', cfg_packL, c_labelHS))]
    def finish(self):
        def change_normal(event):
            event.widget.changed = True
        def change_class(event):
            event.widget.master.caller.changed = True       
        for tab in self.formRef['settings'].widget_ref.values():        # The notebook tabs
            for widget in tab.formRef.values():                         # adds binds to all the widgets to track their changes
                if isinstance(widget, batteries.HotKeyGrabber):
                    widget.bind('<FocusIn>', change_normal, add='+')    # when saving i just have to check the widget saved in formRef, because that is what we mark here
                elif isinstance(widget, ttk.Checkbutton):
                    widget.bind('<Button-1>', change_normal, add='+')
                elif isinstance(widget, HpSegment.HpToggleSelector):
                    for listbox_class in widget.formRef.values():
                        listbox_class.listbox.bind('<Button-1>', change_class, add='+')
                else:
                    widget.bind('<Key>', change_normal, add='+')    
        self.app.root.bind('<F1>', self.help_me)
    
    def help_me(self, event):
        if isinstance(event.widget, ttk.Notebook):
            #~ print('WE GOT A NOTEBOOK')
            widget = event.widget
        else:
            #~ print('looping', repr(event.widget))
            widget = event.widget 
            while 1:
                try:
                    widget = widget.master
                except AttributeError:
                    print('Todo launch screen help error')
                    return
                #~ print(repr(widget))
                if isinstance(widget, ttk.Notebook):
                    break
        selected_tab = widget.select()
        selected_tab = widget.nametowidget(selected_tab)
        try:
            selected_tab.help_url
            help_url = selected_tab.help_url+'.html'
        except AttributeError as e:
            print(e)
            help_url = 'index.html'
        if timstools.internet_on(): # If we can get an internet connection
            #~ webbrowser.open(help_url)    # atm on interents hosting of the stuff so just local
        #~ else:
            help_dir = os.path.join(*('help','_build','html')) 
            webbrowser.open(os.path.join(help_dir,help_url))
        
    def load_cfg(self, cfg, bind_cfg, ahk_cfg):
        def set_default_value(set_checkbox_on=False):
            global ass
            ass += 1
            try:            
                try:
                    try:
                        index = cfg_values.index('Default') + 1
                    except ValueError:
                        index = cfg_values.index('default') + 1
                except ValueError:return                                    # No default Value Set  
                else:           
                    default_val = cfg_values[index]                     
                    widg = tab.formRef[setting+'_default']
            except KeyError:
                print('Key Error ', setting)
                pprint(tab.formRef)
            else:
                #~ print(ass,'setting and widg:', setting,'   ', repr(widg))
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
                except Exception:pass                                   # No Value Set
                else:
                    text = cfg_values[index]
                    widg = tab.formRef[setting]
                    tooltip.ToolTip(widg, delay=200, text=text)
                    widg.tooltip_text = text
        
        for tab in self.formRef['settings'].widget_ref.values():        #The notebook tabs
            for setting, tkvar in tab.variables.items():
                for cfg_setting, cfg_values in cfg.items():
                    if setting == cfg_setting:                          # We are only dealing with settings that are not ignored!
                        if cfg_values[0] not in ('//'):                 # The setting has a value associated with it
                            tkvar.set(cfg_values[0])
                        else:                                           # These settings require no argument they are on by being presetn
                            tkvar.set(1)
                        set_default_value()
                        set_tooltip()
                        break
                    elif '//IGNORE' in cfg_setting:                     # Commented Out Values
                        cfg_setting = cfg_setting.split(' ')[-1]        # Remove the //IGNORE
                        if setting == cfg_values[0]:
                            if cfg_values[0] not in ('//'):             # The setting has a value associated with it
                                tkvar.set(cfg_values[1])
                                set_default_value(set_checkbox_on=1)
                                set_tooltip()
                            else:                                       # These settings require no argument they are on by being presetn
                                set_default_value(set_checkbox_on=1)
                                tkvar.set(1)
                                set_tooltip()
                            break
            for setting, widg in tab.formRef.items():                   # Handle the bind settings from the autoexec
                for bind_setting, bind_values in bind_cfg.items():              
                    bind_value = bind_setting    
                    if setting in bind_values:                          # Atm i'm allowing myself to place the tag anywhere in the values 
                        widg.original_value = bind_value
                        widg.set(bind_value)                            
                        grabber_validator.add_key(bind_value, setting)
                        with ignored(KeyError):
                            ahk_widg = tab.formRef[setting+'_remap']    # See if there is a remapped hoteky
                            ahk_value = ahk_cfg[bind_value.lower()]
                            ahk_widg.original_value = ahk_value
                            no_symbols = d2_func.convert_akh_symbols(ahk_value, ahk_widg)
                            tk_form = ahk_widg.key_parser(no_symbols, d2_func.ahk_key_list)
                            valve_form = ahk_widg.key_parser(tk_form, v=False)
                            grabber_validator.add_key(valve_form, setting+'_remap')
                            #~ print('before parse',ahk_value, ' then ', no_symbols, ' tkform ',tk_form)
                            #~ print('after parse', valve_form)
                            ahk_widg.set(valve_form, case='lower')
                        break
                        
    def reload_cfg(self):
        pprint(d2_func.DISABLED_KEYS)
        print('TBD FFS!!')
    
    def preferences(self):
        UserPreferences(tk.Toplevel(), self.app)
        
    def save_cfg(self):
        disabled_keys = grabber_validator.get_disabled_states()
        if disabled_keys:
            text = []
            text.insert(0, 'The following keys have conflicting values, please fix them!')
            for key, value in disabled_keys.items():
                text.append('     Key:   ' +key)
                for setting in value:
                    text.append('\t'+setting)
            text = '\n'.join(text)
            messagebox.showinfo('Duplicate key binds', text)
            return
        # Only gets the values and rates the widgets that have been changed
        for tab in self.formRef['settings'].widget_ref.values():        # The notebook tabs
            for setting, widget in tab.formRef.items(): 
                if hasattr(widget, 'changed') and widget.changed:           
                    widget.changed = False
                    try:
                        value = widget.get()
                    except AttributeError:              
                        if isinstance(widget, ttk.Checkbutton):         
                            tkvar = tab.variables[setting]
                            value = tkvar.get()
                        elif isinstance(widget, HpSegment.HpToggleSelector):    
                            d2_func.save_hptoggle(self.app, widget)
                            continue
                    if 'hpkey' in setting:
                        d2_func.save_hp_keys(setting, value)
                    elif '_remap' in setting:
                        try:
                            d2_func.save_ahk(self, self.app.ahk_file, tab, widget, setting, value)
                        except TypeError:
                            logging.info('handled error generated when user adds a remap key when no key')
                    elif 'courier_msg' == setting:
                        d2_func.save_courier_msg(self.app.auto_exec, self.app.cfg_settings, setting, value)
                    else:
                        d2_func.save_settings(self.app.auto_exec, setting, value)
                        if isinstance(widget, BindKeyGrabber):
                            # Ensure that Dota ahks that are remapped have there remapped values updated if the dota value changes
                            try:
                                ahk_grabber = tab.formRef[setting+'_remap']
                            except KeyError:
                                continue
                            ahk_hk = ahk_grabber.get()
                            with ignored(AttributeError):
                                if ahk_hk != ahk_grabber.original_value:
                                    d2_func.save_ahk(self, self.app.ahk_file, tab, ahk_grabber, setting+'_remap', ahk_hk)                   
        
        if not self.app.DEVELOPING:
            self.app.auto_exec.save(self.app.cfg['user_pref'][self.app.cfg['user_pref']['save_mode']]+'\\autoexec.cfg')
            logging.info('Finished saving using mode :'+self.app.cfg['user_pref']['save_mode'])
            logging.info(self.app.cfg['user_pref'][self.app.cfg['user_pref']['save_mode']]+'\\autoexec.cfg')
        else:
            self.app.auto_exec.save('autoexec_saved.cfg')
        print('saved')
        self.app.send_ui_feedback('Saved Successfully', 1)
        
class SettingsNoteBook(maker.GuiNoteBook):          # Main controller notebook, used to switch the pain on the right of the treeviewer
    def start(self):
        self.background = '#232327'
        self.style = {'bg':'#232327','bd':5,'relief':'flat'}
        # self.nbStyle = {'style':'imgTNotebook'}
        #~ self.conPack = {'expand':'1','fill':'both', 'side':'top'}
        #~ self.config(padx=40,pady=40)     
        self.widgList = [ProgramSetup,MiscSettings,NetGraph,InternetSettings,MacroSettings,PerformanceSettings,PainFadeSettings,StandardMenu,HpSegment,Testing]
        self.tabText = ['Launch','Misc','NetGraph','Internet','Macros','Performance','Damage Delay', 'Standard Options','Hp Segment','Test Scripts']
        #~ self.nbStyle=c_hiddenNotebook    # only woring in main not in running from script
        self.widgSide = ['nsew','nsew','nsew','nsew','nsew','nsew','nsew','nsew','nsew','nsew','nsew']
        self.padding=[10, 10, 10, 10, 10, 10, 10, 10, 10, 10]
    def finish(self):
        for i in range(0,len(self.widgList)):       # Makes the frame grab focus instead of the hotkeygrabber
            self.widget_ref[i].configure(takefocus=1)

class ProgramSetup(maker.GuiMakerWindowMenu):
    help_url = 'launch'
    def start(self):
        self.customForm =   [
            ((ttk.Label, 'Reload autoexec.cfg Hotkey',None,     cfg_grid,{}),
            (BindKeyGrabber, '','reload_exec_hotkey',       cfg_grid,{})),
            
            ((ttk.Label, 'Help Text',None,      cfg_grid,{}),
            (BindKeyGrabber, '','help_hotkey',      cfg_grid,{})),
            
            ((ttk.Label, 'Turn Text Mode Off',None,     cfg_grid,{}),
            (BindKeyGrabber, '','text_off_hotkey',      cfg_grid,{})),
    
            ((ttk.Checkbutton, 'novid','novid',     cfg_grid,{}),
            (ttk.Label, 'Skips valve intro video',None, cfg_grid,{})),
            
            ((ttk.Checkbutton, 'console','console',     cfg_grid,{}),
            (ttk.Label, 'Enables consoles in game (default hotkey is `)',None,  cfg_grid,{})),
            
            ((ttk.Checkbutton, 'windowed -w # -h # -noborder','novid',      cfg_grid,{}),
            (ttk.Label, 'Window mode with no border, REPLACE # WITH YOUR DESIRED',None, cfg_grid,{}))]
        add_default_field(self.customForm)
        add_headings(self.customForm, width=3)
class PainFadeSettings(maker.GuiMakerWindowMenu):
    def start(self):
        #~ self.app.entry_cfg = {'bg':'#5a0b08','insertbackground':'white', 'fg':'white'}
        
        self.customForm =   [
            ((ttk.Label, 'dota_health_hurt_decay_time_max',None,        cfg_grid, {}),
            (tk.Entry, '','dota_health_hurt_decay_time_max',        cfg_grid, self.app.entry_cfg)),
            
            ((ttk.Label, 'dota_health_hurt_decay_time_min',None,        cfg_grid,{}),
            (tk.Entry, '','dota_health_hurt_decay_time_min',        cfg_grid, self.app.entry_cfg)),
            
            ((ttk.Label, 'dota_health_hurt_delay',None,     cfg_grid,{}),
            (tk.Entry, '','dota_health_hurt_delay',     cfg_grid, self.app.entry_cfg)),
            
            ((ttk.Label, 'dota_pain_decay',None,        cfg_grid,{}),
            (tk.Entry, '','dota_pain_decay',        cfg_grid, self.app.entry_cfg)),
            
            ((ttk.Label, 'dota_pain_factor',None,       cfg_grid,{}),
            (tk.Entry, '','dota_pain_factor',       cfg_grid, self.app.entry_cfg)),
            
            ((ttk.Label, 'dota_pain_fade_rate',None,        cfg_grid,{}),
            (tk.Entry, '','dota_pain_fade_rate',        cfg_grid, self.app.entry_cfg)),
            
            ((ttk.Label, 'dota_pain_multiplier',None,       cfg_grid,{}),
            (tk.Entry, '','dota_pain_multiplier',       cfg_grid, self.app.entry_cfg))]
        add_default_field(self.customForm)
        add_headings(self.customForm, width=3)
class InternetSettings(maker.GuiMakerWindowMenu):
    def start(self):
        self.customForm =   [
            ((ttk.Label, 'rate', None,      cfg_grid,{}),
            (tk.Entry, '', 'rate',      cfg_grid, self.app.entry_cfg)),
            
            ((ttk.Label, 'cl_updaterate',None,      cfg_grid,{}),
            (tk.Entry, '','cl_updaterate',      cfg_grid, self.app.entry_cfg)),
            
            ((ttk.Label, 'cl_cmdrate',None,     cfg_grid,{}),
            (tk.Entry, '','cl_cmdrate',     cfg_grid, self.app.entry_cfg)),
            
            ((ttk.Label, 'cl_interp',None,      cfg_grid,{}),
            (tk.Entry, '','cl_interp',      cfg_grid, self.app.entry_cfg)),
            
            ((ttk.Label, 'cl_interp_ratio',None,        cfg_grid,{}),
            (tk.Entry, '','cl_interp_ratio',        cfg_grid, self.app.entry_cfg)),
            
            ((ttk.Label, 'cl_smoothtime',None,      cfg_grid,{}),
            (tk.Entry, '','cl_smoothtime',      cfg_grid, self.app.entry_cfg))]
        add_default_field(self.customForm)
        add_headings(self.customForm, width=3)

class PerformanceSettings(maker.GuiNoteBook):
    class LowReccommended(maker.GuiMakerWindowMenu):
        def start(self):
            self.customForm =   [
                ((ttk.Label, 'dota_cheap_water', None,      cfg_grid,{}),
                (tk.Entry, '', 'dota_cheap_water',      cfg_grid, self.app.entry_cfg)),
                
                ((ttk.Label, 'cl_globallight_shadow_mode', None,        cfg_grid,{}),
                (tk.Entry, '', 'cl_globallight_shadow_mode',        cfg_grid, self.app.entry_cfg)),
                
                ((ttk.Label, 'r_deferred_height_fog',None,      cfg_grid,{}),
                (tk.Entry, '','r_deferred_height_fog',      cfg_grid, self.app.entry_cfg)),
                
                ((ttk.Label, 'r_deferred_simple_light',None,        cfg_grid,{}),
                (tk.Entry, '','r_deferred_simple_light',        cfg_grid, self.app.entry_cfg)),
                
                ((ttk.Label, 'r_screenspace_aa',None,       cfg_grid,{}),
                (tk.Entry, '','r_screenspace_aa',       cfg_grid, self.app.entry_cfg)),
                
            add_default_field(self.customForm)
            add_headings(self.customForm, width=3)
    class LowNext(maker.GuiMakerWindowMenu):
        def start(self):
            self.customForm =   [               
                ((ttk.Label, 'props_break_max_pieces',None,     cfg_grid,{}),
                (tk.Entry, '','props_break_max_pieces',     cfg_grid, self.app.entry_cfg)),
                
                ((ttk.Label, 'ragdoll_sleepaftertime',None,     cfg_grid,{}),
                (tk.Entry, '','ragdoll_sleepaftertime',     cfg_grid, self.app.entry_cfg)),
                
                ((ttk.Label, 'g_ragdoll_fadespeed',None,        cfg_grid,{}),
                (tk.Entry, '','g_ragdoll_fadespeed',        cfg_grid, self.app.entry_cfg)),
                
                ((ttk.Label, 'g_ragdoll_important_maxcount',None,       cfg_grid,{}),
                (tk.Entry, '','g_ragdoll_important_maxcount',       cfg_grid, self.app.entry_cfg)),
                
                ((ttk.Label, 'g_ragdoll_lvfadespeed',None,      cfg_grid,{}),
                (tk.Entry, '','g_ragdoll_lvfadespeed',      cfg_grid, self.app.entry_cfg)),
                
                ((ttk.Label, 'g_ragdoll_maxcount',None,     cfg_grid,{}),
                (tk.Entry, '','g_ragdoll_maxcount',     cfg_grid, self.app.entry_cfg)),
                
                ((ttk.Label, 'cl_detaildist',None,      cfg_grid,{}),
                (tk.Entry, '','cl_detaildist',      cfg_grid, self.app.entry_cfg)),
                
                ((ttk.Label, 'cl_detailfade',None,      cfg_grid,{}),
                (tk.Entry, '','cl_detailfade',      cfg_grid, self.app.entry_cfg)),
                
                ((ttk.Label, 'locator_text_drop_shadow',None,       cfg_grid,{}),
                (tk.Entry, '','locator_text_drop_shadow',       cfg_grid, self.app.entry_cfg)),
                
                ((ttk.Label, 'gpu_mem_level',None,      cfg_grid,{}),
                (tk.Entry, '','gpu_mem_level',      cfg_grid, self.app.entry_cfg)),
                
                ((ttk.Label, 'mem_level',None,      cfg_grid,{}),
                (tk.Entry, '','mem_level',      cfg_grid, self.app.entry_cfg)),
                
                ((ttk.Label, 'dota_minimap_use_dynamic_mesh',None,      cfg_grid,{}),
                (tk.Entry, '','dota_minimap_use_dynamic_mesh',      cfg_grid, self.app.entry_cfg)),
                
                ((ttk.Label, 'mat_bumpmap',None,        cfg_grid,{}),
                (tk.Entry, '','mat_bumpmap',        cfg_grid, self.app.entry_cfg)),
                
                ((ttk.Label, 'mat_specular',None,       cfg_grid,{}),
                (tk.Entry, '','mat_specular',       cfg_grid, self.app.entry_cfg)),
                
                ((ttk.Label, 'mat_phong',None,      cfg_grid,{}),
                (tk.Entry, '','mat_phong',      cfg_grid, self.app.entry_cfg)),
                
                
                ((ttk.Label, 'mp_usehwmvcds',None,      cfg_grid,{}),
                (tk.Entry, '','mp_usehwmvcds',      cfg_grid, self.app.entry_cfg)),
                
                ((ttk.Label, 'mp_usehwmmodels',None,        cfg_grid,{}),
                (tk.Entry, '','mp_usehwmmodels',        cfg_grid, self.app.entry_cfg))]
            add_default_field(self.customForm)
            add_headings(self.customForm, width=3)
    class LowNextNext(maker.GuiMakerWindowMenu):
        def start(self):
            self.customForm =   [
                ((ttk.Label, 'r_worldlights',None,      cfg_grid,{}),
                (tk.Entry, '','r_worldlights',      cfg_grid, self.app.entry_cfg)),
                
                ((ttk.Label, 'r_decals',None,       cfg_grid,{}),
                (tk.Entry, '','r_decals',       cfg_grid, self.app.entry_cfg)),
                
                ((ttk.Label, 'r_decal_overlap_count',None,      cfg_grid,{}),
                (tk.Entry, '','r_decal_overlap_count',      cfg_grid, self.app.entry_cfg)),
                
                ((ttk.Label, 'r_worldlightmin',None,        cfg_grid,{}),
                (tk.Entry, '','r_worldlightmin',        cfg_grid, self.app.entry_cfg)),
                
                ((ttk.Label, 'r_drawmodeldecals',None,      cfg_grid,{}),
                (tk.Entry, '','r_drawmodeldecals',      cfg_grid, self.app.entry_cfg)),
                
                ((ttk.Label, 'r_decalstaticprops',None,     cfg_grid,{}),
                (tk.Entry, '','r_decalstaticprops',     cfg_grid, self.app.entry_cfg)),
                
                ((ttk.Label, 'r_flashlightdepthtexture',None,       cfg_grid,{}),
                (tk.Entry, '','r_flashlightdepthtexture',       cfg_grid, self.app.entry_cfg)),
                
                ((ttk.Label, 'r_rainparticledensity',None,      cfg_grid,{}),
                (tk.Entry, '','r_rainparticledensity',      cfg_grid, self.app.entry_cfg)),
                
                ((ttk.Label, 'r_shadowfromworldlights',None,        cfg_grid,{}),
                (tk.Entry, '','r_shadowfromworldlights',        cfg_grid, self.app.entry_cfg)),
                
                ((ttk.Label, 'r_DrawDetailProps',None,      cfg_grid,{}),
                (tk.Entry, '','r_DrawDetailProps',      cfg_grid, self.app.entry_cfg)),
                
                ((ttk.Label, 'r_FlashlightDetailProps',None,        cfg_grid,{}),
                (tk.Entry, '','r_FlashlightDetailProps',        cfg_grid, self.app.entry_cfg)),
                
                ((ttk.Label, 'r_shadow_deferred_downsample',None,       cfg_grid,{}),
                (tk.Entry, '','r_shadow_deferred_downsample',       cfg_grid, self.app.entry_cfg)),
                
                ((ttk.Label, 'r_WaterDrawReflection',None,      cfg_grid,{}),
                (tk.Entry, '','r_WaterDrawReflection',      cfg_grid, self.app.entry_cfg)),
                
                ((ttk.Label, 'r_renderoverlayfragment',None,        cfg_grid,{}),
                (tk.Entry, '','r_renderoverlayfragment',        cfg_grid, self.app.entry_cfg))]
            add_default_field(self.customForm)
            add_headings(self.customForm, width=3)
    class LowLastResort(maker.GuiMakerWindowMenu):
        def start(self):
            self.customForm = [
                ((ttk.Label, 'r_shadowmaxrendered',None,        cfg_grid,{}),
                (tk.Entry, '','r_shadowmaxrendered',        cfg_grid, self.app.entry_cfg)),
                
                ((ttk.Label, 'r_flashlightrendermodels',None,       cfg_grid,{}),
                (tk.Entry, '','r_flashlightrendermodels',       cfg_grid, self.app.entry_cfg)),
                
                ((ttk.Label, 'r_shadows',None,      cfg_grid,{}),
                (tk.Entry, '','r_shadows',      cfg_grid, self.app.entry_cfg)),
                
                ((ttk.Label, 'r_3dsky',None,        cfg_grid,{}),
                (tk.Entry, '','r_3dsky',        cfg_grid, self.app.entry_cfg)),
                
                ((ttk.Label, 'r_flashlightnodraw',None,     cfg_grid,{}),
                (tk.Entry, '','r_flashlightnodraw',     cfg_grid, self.app.entry_cfg)),
                
                ((ttk.Label, 'mat_force_low_quality_shadows',None,      cfg_grid,{}),
                (tk.Entry, '','mat_force_low_quality_shadows',      cfg_grid, self.app.entry_cfg)),
                
                ((ttk.Label, 'mat_filtertextures',None,     cfg_grid,{}),
                (tk.Entry, '','mat_filtertextures',     cfg_grid, self.app.entry_cfg)),
                
                ((ttk.Label, 'mat_disable_bloom',None,      cfg_grid,{}),
                (tk.Entry, '','mat_disable_bloom',      cfg_grid, self.app.entry_cfg)),
                
                ((ttk.Label, 'mat_disable_fancy_blending',None,     cfg_grid,{}),
                (tk.Entry, '','mat_disable_fancy_blending',     cfg_grid, self.app.entry_cfg))]
            add_default_field(self.customForm)
            add_headings(self.customForm, width=3)
    class High(maker.GuiMakerWindowMenu):
        def start(self):
            self.customForm = [
                ((ttk.Label, 'snd_mix_async',None,      cfg_grid,{}),
                (tk.Entry, '','snd_mix_async',      cfg_grid, self.app.entry_cfg)),
                
                ((ttk.Label, 'cl_phys_maxticks',None,       cfg_grid,{}),
                (tk.Entry, '','cl_phys_maxticks',       cfg_grid, self.app.entry_cfg)),
                
                ((ttk.Label, 'mat_grain_enable',None,       cfg_grid,{}),
                (tk.Entry, '','mat_grain_enable',       cfg_grid, self.app.entry_cfg)),
                
                ((ttk.Label, 'mat_local_contrast_enable',None,      cfg_grid,{}),
                (tk.Entry, '','mat_local_contrast_enable',      cfg_grid, self.app.entry_cfg)),
                
                ((ttk.Label, 'mat_motion_blur_enabled',None,        cfg_grid,{}),
                (tk.Entry, '','mat_motion_blur_enabled',        cfg_grid, self.app.entry_cfg)),
                
                ((ttk.Label, 'mat_picmip',None,     cfg_grid,{}),
                (tk.Entry, '','mat_picmip',     cfg_grid, self.app.entry_cfg)),
                
                ((ttk.Label, 'r_shadowrendertotexture',None,        cfg_grid,{}),
                (tk.Entry, '','r_shadow_half_update_rate',      cfg_grid, self.app.entry_cfg)),
                
                ((ttk.Label, 'r_threadeddetailprops',None,      cfg_grid,{}),
                (tk.Entry, '','r_threadeddetailprops',      cfg_grid, self.app.entry_cfg))
                ]
            add_default_field(self.customForm)
            add_headings(self.customForm, width=3)
    def start(self):
        self.background = '#232327'
        self.widgList = [self.LowReccommended, self.LowNext, self.LowNextNext, self.LowLastResort, self.High]
        self.tabText = ['Reccommended','Now try these','Or try these','only if you are desperate','High Performance settings!']
        #~ self.nbStyle=c_hiddenNotebook    # only woring in main not in running from script
        self.widgSide = ['nsew','nsew','nsew','nsew','nsew','nsew','nsew','nsew']
    def finish(self):
        for tab in self.widget_ref.values():
            self.variables.update(tab.variables)
            self.formRef.update(tab.formRef)

class NetGraph(maker.GuiMakerWindowMenu):
    def start(self):        
        self.customForm =   [
            ((ttk.Label, 'Netgraph Toggle Hotkey',None,     cfg_grid,{}),
            (BindKeyGrabber, '','netgraph_hotkey',      cfg_grid,{})),
        ]
        add_default_field(self.customForm)
        add_remap_field(self.customForm)
        add_headings(self.customForm, width=4)
class MiscSettings(maker.GuiMakerWindowMenu):   
    def start(self):
        self.customForm =   [
            ((ttk.Label, 'Deny on right mouse click',None,  cfg_grid,{}),
            (ttk.Checkbutton, None,'dota_force_right_click_attack',     cfg_grid,{})),
            
            ((ttk.Label, 'minimap hero icon size',None,     cfg_grid,{}),
            (tk.Entry, '','dota_minimap_hero_size',     cfg_grid, self.app.entry_cfg)),
            
            ((ttk.Label, 'Threshold delay to accept minimap clicks',None,       cfg_grid,{}),
            (tk.Entry, '','dota_minimap_misclick_time',     cfg_grid, self.app.entry_cfg)),
            
            ((ttk.Label, 'dota_recent_event (jump to last ping)',None,      cfg_grid,{}),
            (BindKeyGrabber, '','dota_recent_event',        cfg_grid,{})),
            
            ((ttk.Label, 'Health segmenting in the lifebar',None,       cfg_grid,{}),
            (tk.Entry, '','dota_health_per_vertical_marker',        cfg_grid, self.app.entry_cfg)),
            
            ((ttk.Label, 'Disable mouse wheel zoom',None,       cfg_grid,{}),
            (tk.Entry, '','dota_camera_disable_zoom',       cfg_grid, self.app.entry_cfg)),
            
            ((ttk.Label, 'dota_minimap_ping_duration',None,     cfg_grid,{}),
            (tk.Entry, '','dota_minimap_ping_duration',     cfg_grid, self.app.entry_cfg)),
            
            ((ttk.Label, 'dota_minimap_rune_size',None,     cfg_grid,{}),
            (tk.Entry, '','dota_minimap_rune_size',     cfg_grid, self.app.entry_cfg)),
            
            ((ttk.Label, 'dota_minimap_tower_defend_distance',None,     cfg_grid,{}),
            (tk.Entry, '','dota_minimap_tower_defend_distance',     cfg_grid, self.app.entry_cfg)),
            
            #~ ((ttk.Label, 'Escape key allowed to hide game UI',None,  cfg_grid,{}),
            #~ (ttk.Checkbutton, None,'gameui_allowescape',     cfg_grid,{})),
            
            #~ ((ttk.Label, 'Escape key allowed to show game UI',None,  cfg_grid,{}),
            #~ (ttk.Checkbutton, None,'gameui_allowescapetoshow',       cfg_grid,{}))
            ]

        add_default_field(self.customForm)
        add_remap_field(self.customForm)
        add_headings(self.customForm, width=3)
class MacroSettings(maker.GuiMakerWindowMenu):
    help_url = 'macros'
    def start(self):
        self.customForm =   [                       
            ((ttk.Label, 'Courier Deliver & Message',None,      cfg_grid,{}),
            (BindKeyGrabber, '','courier_hotkey',       cfg_grid,{})),
            
            (maker.BLANK,
            (tk.Entry, 'enter message here', 'courier_msg', cfg_grid, self.app.entry_cfg)), #https://www.youtube.com/watch?v=M1WyPCLz0jk
            
            ((ttk.Label, 'Courier to base macro',None,      cfg_grid,{}),
            (BindKeyGrabber, '','courier_base_hotkey',      cfg_grid,{})),
            
            ((ttk.Label, 'Courier to secret shop macro',None,       cfg_grid,{}),
            (BindKeyGrabber, '','courier_secret_hotkey',        cfg_grid,{})),
            
            ((ttk.Label, 'Courier stash items macro',None,      cfg_grid,{}),
            (BindKeyGrabber, '','courier_stash_hotkey',     cfg_grid,{})),
        
            ((ttk.Label, 'Courier grab stash items macro',None,     cfg_grid,{}),
            (BindKeyGrabber, '','courier_grab_hotkey',      cfg_grid,{})),
        
            ((ttk.Label, 'Courier transfer items macro',None,       cfg_grid,{}),
            (BindKeyGrabber, '','courier_transfer_hotkey',      cfg_grid,{})),
        
            ((ttk.Label, 'Courier speed burst macro',None,      cfg_grid,{}),
            (BindKeyGrabber, '','courier_speed_hotkey',     cfg_grid,{})),
        
            ((ttk.Label, 'Toggle Rune Spots & Hero',None,       cfg_grid,{}),
            (BindKeyGrabber, '','runechecker_hotkey',       cfg_grid,{})),
            
            ((ttk.Label, 'Top Rune',None,       cfg_grid,{}),
            (BindKeyGrabber, '','toprune_hotkey',       cfg_grid,{})),
            
            ((ttk.Label, 'Bot Rune',None,       cfg_grid,{}),
            (BindKeyGrabber, '','botrune_hotkey',       cfg_grid,{})),
            
            ((ttk.Label, 'Smart attack',None,       cfg_grid,{}),
            (BindKeyGrabber, '','smart_attack_hotkey',      cfg_grid,{})),
            
            ((ttk.Label, 'Smart stop',None,     cfg_grid,{}),
            (BindKeyGrabber, '','smart_stop_hotkey',        cfg_grid,{})),
            
            ((ttk.Label, 'Smart hold',None,     cfg_grid,{}),
            (BindKeyGrabber, '','smart_hold_hotkey',        cfg_grid,{}))]
        add_default_field(self.customForm)
        add_remap_field(self.customForm)
        add_headings(self.customForm, width=4)
    def finish(self):
        tooltip_text = ['Lvl 6',
                        'Lvl 11',
                        'Lvl 16', 
                        'Aghanim\'s Scepter Lvl 6',
                        'Aghanim\'s Scepter Lvl 11',
                        'Aghanim\'s Scepter Lvl 16',
                        'Aghs Lvl 6 without magic resistance',
                        'Aghs Lvl 11 without magic resistance',
                        'Aghs Lvl 16 without magic resistance',
                        'Used in Hp100 for 1000'
                        ]
        #~ for i, text in zip(range(1,11), tooltip_text):   
            #~ widg = self.formRef['hpkey'+str(i)]
            #~ tooltip.ToolTip(widg, delay=200, text=text)
        
class Testing(maker.GuiMakerWindowMenu):
    help_url = 'testing'
    def start(self):
        self.customForm =   [
            ((ttk.Label, 'Enable/Disable Test key',None,        cfg_grid,{}),
            (BindKeyGrabber, '','testing_lock_hotkey',      cfg_grid,{})),
            
            ((ttk.Label, 'Test Mode Hotkey',None,       cfg_grid,{}),
            (BindKeyGrabber, '','test_mode_hotkey_exception',       cfg_grid,{}))]
        add_default_field(self.customForm)
        add_headings(self.customForm)
        add_remap_field(self.customForm)
class HpSegment(maker.GuiMakerWindowMenu):
    help_url = 'hptoggle'
    class HpToggleSelector(maker.GuiMaker):
        class SelectedHeroes(maker.MakerScrolledList):
            def start(self):
                self.use_default_event_handler = True
                self.options = []
                index = self.app.cfg_settings['hptoggle']   
                for i, row in enumerate(self.app.auto_exec[index:]):
                    if not row:pass 
                    elif 'hp' in row:
                        row = row.split(' ')
                        if 'hp.cfg' in row[3]:
                            hero_name = row[3].split('_hp.cfg')[0].split('\\')[-1]
                            self.options.append(hero_name)
                    else:
                        break
            def run_command(self, selection=0):
                with ignored(IndexError):
                    if len(self.listbox.get(0,'end')) != 1:             # minimum one entry
                        self.listbox.delete(self.listbox.curselection()[0])
                        self.styleList()
                        self.caller.formRef['allheroes'].listbox.insert(tk.END, selection)
                        self.caller.formRef['allheroes'].styleList()
            def finish(self):
                self.listbox.config(selectmode='single')        
        class AllHeroes(maker.MakerScrolledList):
            def start(self):
                self.use_default_event_handler = True
                self.options = []
                for file in glob.glob('hp/*_hp.cfg'):
                    file = file.split(os.sep)[-1]
                    file = file.split('_hp.cfg')[0]
                    self.options.append(file)
            def run_command(self, selection=0):
                other_lb = self.caller.formRef['selectedheores'].listbox
                if selection not in other_lb.get(0, 'end'):
                    self.caller.formRef['selectedheores'].listbox.insert(tk.END, selection)
                    self.caller.formRef['selectedheores'].styleList()
                    self.remove_items_as_needed()
                    self.styleList()
            def finish(self):
                self.listbox.config(selectmode='single')
            def remove_items_as_needed(self):                   # remove items from the right side if they are present on the left
                for hp_config in self.caller.formRef['selectedheores'].listbox.get(0, 'end'):
                    for index, acfg in enumerate(self.listbox.get(0, 'end')):
                        if hp_config == acfg:
                            self.listbox.delete(index)
            
        class AddRemove(maker.GuiMaker):
            def start(self):
                self.imgdir = 'img/'
                self.toolPhotoObjs = []
                self.customForm = [         #TBD WHY IS LAMBDA NEEDED BELOW IT NDOESNT WORK WITHOUT IT WTF
                    (maker.BLANK,
                    (ttk.Button, ['up.png'], '', cfg_grid,  {'command':lambda:self.caller.formRef['selectedheores'].move_up()}),
                    maker.BLANK),
                    #~ ('ass',lambda:0,{},{}),
                    ((ttk.Button, ['left.png'], '', cfg_grid, {'command':lambda:self.caller.formRef['allheroes'].handle_list()}),
                    (ttk.Button, ['down.png'], '', cfg_grid, {'command':lambda:self.caller.formRef['selectedheores'].move_down()}),
                    (ttk.Button, ['right.png'], '', cfg_grid, {'command':lambda:self.caller.formRef['selectedheores'].handle_list()}))]
        def start(self):
            self.customForm = [
            ((ttk.Label, 'Heroes to Toggle', '', cfg_gridEW, label_centered),
            maker.BLANK,
            (ttk.Label, 'All Hp Configurations', '', cfg_gridEW, label_centered)),
            
            ((self.SelectedHeroes, '','selectedheores', cfg_grid, {}),
            (self.AddRemove,'','',cfg_grid,{}),
            (self.AllHeroes, '','allheroes',    cfg_grid,{}))
            ]
        def finish(self):
            self.formRef['allheroes'].remove_items_as_needed()
    
    def start(self):
        self.customForm =   [
            #~ ((self.HpToggleSelector, '','hptoggleselector', cfg_grid, {})),
            
            ((ttk.Label, 'Toggle Hero','',      cfg_grid,{}),
            (BindKeyGrabber, '','hptoggle_hotkey',  cfg_grid,{})),
            
            ((ttk.Label, '1st','',  cfg_grid,{}),
            (BindKeyGrabber,'','hpkey1',        cfg_grid,{})),
            
            ((ttk.Label, '2nd','',  cfg_grid,{}),
            (BindKeyGrabber,'','hpkey2',        cfg_grid,{})),
            
            ((ttk.Label, '3rd','',  cfg_grid,{}),
            (BindKeyGrabber,'','hpkey3',        cfg_grid,{})),
            
            ((ttk.Label, '4th','',  cfg_grid,{}),
            (BindKeyGrabber,'','hpkey4',        cfg_grid,{})),
            
            ((ttk.Label, '5th','',  cfg_grid,{}),
            (BindKeyGrabber,'','hpkey5',        cfg_grid,{})),
            
            ((ttk.Label, '6th','',  cfg_grid,{}),
            (BindKeyGrabber,'','hpkey6',        cfg_grid,{})),
            
            ((ttk.Label, '7th','',  cfg_grid,{}),
            (BindKeyGrabber,'','hpkey7',        cfg_grid,{})),
            
            ((ttk.Label, '8th','',  cfg_grid,{}),
            (BindKeyGrabber,'','hpkey8',        cfg_grid,{})),
            
            ((ttk.Label, '9th','',  cfg_grid,{}),
            (BindKeyGrabber,'','hpkey9',        cfg_grid,{})),
            
            ((ttk.Label, '10th','', cfg_grid,{}),
            (BindKeyGrabber,'','hpkey10',       cfg_grid,{}))]
        add_default_field(self.customForm)
        add_remap_field(self.customForm)
        add_headings(self.customForm, width=4)
    
    def makeWidgets(self):
        toggler = self.HpToggleSelector(self, self.app)
        toggler.pack()
        self.formRef['hptoggleselector'] = toggler

    def finish(self):
        tooltip_text = ['Lvl 6',
                        'Lvl 11',
                        'Lvl 16', 
                        'Aghanim\'s Scepter Lvl 6',
                        'Aghanim\'s Scepter Lvl 11',
                        'Aghanim\'s Scepter Lvl 16',
                        'Aghs Lvl 6 without magic resistance',
                        'Aghs Lvl 11 without magic resistance',
                        'Aghs Lvl 16 without magic resistance',
                        'Used in Hp100 for 1000']
        d2_func.load_keys_hptoggle(self)
        for i, text in zip(range(1,11), tooltip_text):  
            widg = self.formRef['hpkey'+str(i)]
            tooltip.ToolTip(widg, delay=200, text=text)

class AboutPage(maker.GuiMakerWindowMenu):
    def start(self):
        self.customForm =   [
            ((ttk.Checkbutton, 'dota_force_right_click_attack','dota_force_right_click_attack',     cfg_grid,{}),
            (ttk.Label, 'Deny on right mouse click',None,   cfg_grid,{})),
        
            ((ttk.Label, 'dota_pain_fade_rate',None,        cfg_grid,{}),
            (tk.Entry, '','dota_pain_fade_rate',        cfg_grid, self.app.entry_cfg)),
            
            ((ttk.Label, 'Netgraph Toggle Hotkey',None,     cfg_grid,{}),
            (BindKeyGrabber, '','netgraph_hotkey',      cfg_grid,{}))]
        add_default_field(self.customForm)
class StandardMenu(maker.GuiMakerWindowMenu):
    def start(self):
        self.customForm =   [
            #~ ((ttk.Checkbutton, '','',        cfg_grid,{}),
            #~ (ttk.Label, '',None, cfg_grid,{})),
        
            ((ttk.Label, 'dota_camera_speed',None,      cfg_grid,{}),
            (tk.Entry, '','dota_camera_speed',      cfg_grid, self.app.entry_cfg)),
            
            ((ttk.Label, 'dota_camera_accelerate',None,     cfg_grid,{}),
            (tk.Entry, '','dota_camera_accelerate',     cfg_grid, self.app.entry_cfg)),
            
            ((ttk.Label, 'dota_player_multipler_orders',None,       cfg_grid,{}),
            (tk.Entry, '','dota_player_multipler_orders',       cfg_grid, self.app.entry_cfg)),
            
            ((ttk.Label, 'dota_player_units_auto_attack',None,      cfg_grid,{}),
            (tk.Entry, '','dota_player_units_auto_attack',      cfg_grid, self.app.entry_cfg)),
            
            ((ttk.Label, 'dota_ability_quick_cast',None,        cfg_grid,{}),
            (tk.Entry, '','dota_ability_quick_cast',        cfg_grid, self.app.entry_cfg)),
            
            ((ttk.Label, 'dota_hud_healthbar_number',None,      cfg_grid,{}),
            (tk.Entry, '','dota_hud_healthbar_number',      cfg_grid, self.app.entry_cfg)),
            
            ((ttk.Label, 'dota_killcam_show',None,      cfg_grid,{}),
            (tk.Entry, '','dota_killcam_show',      cfg_grid, self.app.entry_cfg)),
            
            ((ttk.Label, 'dota_screen_shake',None,      cfg_grid,{}),
            (tk.Entry, '','dota_screen_shake',      cfg_grid, self.app.entry_cfg)),
            
            ((ttk.Label, 'dota_always_show_player_names',None,      cfg_grid,{}),
            (tk.Entry, '','dota_always_show_player_names',      cfg_grid, self.app.entry_cfg)),
            
            ((ttk.Label, 'dota_select_courier',None,        cfg_grid,{}),
            (BindKeyGrabber, '','dota_select_courier',      cfg_grid,{})),
            
            ((ttk.Label, 'Main Ability 1',None,     cfg_grid,{}),
            (BindKeyGrabber, '','Main_Ability_1',       cfg_grid,{})),
            
            ((ttk.Label, 'Main Ability 2',None,     cfg_grid,{}),
            (BindKeyGrabber, '','Main_Ability_2',       cfg_grid,{})),
            
            ((ttk.Label, 'Main Ability Ultimate',None,      cfg_grid,{}),
            (BindKeyGrabber, '','Main_Ability_Ultimate',        cfg_grid,{})),
            
            ((ttk.Label, 'Secondary Ability 1',None,        cfg_grid,{}),
            (BindKeyGrabber, '','Secondary_Ability_1',      cfg_grid,{})),
            
            ((ttk.Label, 'Secondary Ability 2',None,        cfg_grid,{}),
            (BindKeyGrabber, '','Secondary_Ability_2',      cfg_grid,{})),
            
            ((ttk.Label, 'Itemslot 1',None,     cfg_grid,{}),
            (BindKeyGrabber, '','Itemslot_1',       cfg_grid,{})),
            
            ((ttk.Label, 'Itemslot 2',None,     cfg_grid,{}),
            (BindKeyGrabber, '','Itemslot_2',       cfg_grid,{})),
            
            ((ttk.Label, 'Itemslot 3',None,     cfg_grid,{}),
            (BindKeyGrabber, '','Itemslot_3',       cfg_grid,{})),
            
            ((ttk.Label, 'Itemslot 4',None,     cfg_grid,{}),
            (BindKeyGrabber, '','Itemslot_4',       cfg_grid,{})),
            
            ((ttk.Label, 'Itemslot 5',None,     cfg_grid,{}),
            (BindKeyGrabber, '','Itemslot_5',       cfg_grid,{})),
            
            ((ttk.Label, 'Itemslot 6',None,     cfg_grid,{}),
            (BindKeyGrabber, '','Itemslot_6',       cfg_grid,{})),
            ]
        add_default_field(self.customForm)
        add_headings(self.customForm, 4)
        add_remap_field(self.customForm)
        
class D2(maker.GuiMakerWindowMenu):
    def start(self):
        self.customForm =   [
            ((ttk.Checkbutton, '','',       cfg_grid,{}),
            (ttk.Label, '',None,    cfg_grid,{})),
        
            ((ttk.Label, '',None,       cfg_grid,{}),
            (tk.Entry, '','here',       cfg_grid, self.app.entry_cfg)),
            
            ((ttk.Label, '',None,       cfg_grid,{}),
            (BindKeyGrabber, '','here',     cfg_grid,{}))]
        #~ add_default_field(self.customForm)
        #~ add_headings(self.customForm)
        #~ add_remap_field(self.customForm)

########################################################################
#           Non dota settings related Gui elements
########################################################################

class SplashScreen(tk.Toplevel):
    toolPhotoObjs=[]
    imgdir= 'img'
    def __init__(self, root):
        tk.Toplevel.__init__(self, root)
        self.overrideredirect(True)         # Hides the Window Border
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
        self.toolPhotoObjs.append(imgobj)       # keep a reference to image or garbage collected
        button.pack(expand=1,fill='both')

class UserPreferences(maker.GuiMaker):      
    toolPhotoObjs=[]
    imgdir= 'img/'
    def start(self):
        self.conPack = {}
        LABEL_CONFIG = {'background':'white','foreground':'black', 'padding':(8, 2, 10, 2)}
        self.customForm = [
                ((ttk.Label, 'Steam directory path', '' , cfg_grid, {}),
                (ttk.Label, '', 'steam_path', cfg_gridEW, LABEL_CONFIG),
                (ttk.Button, ['folder.png'], '', cfg_grid, {'command':self.set_steam_path})),
                
                (ttk.Radiobutton, 'Automatically save files to the dota folder (requires admin permissions): ', 'save_mode', dict(cfg_grid,**{'columnspan':'3'}), {'value':'steam_path'}),
                (ttk.Radiobutton, 'Save to another directory, you will have to copy the files in manually (no admin permissions required): ','save_mode', dict(cfg_grid,**{'columnspan':'3'}), {'value':'alt_path'}),
                
                ((ttk.Label, 'Alternative save directory path', '' , cfg_grid, {}),
                (ttk.Label, '', 'alt_path', cfg_gridEW, LABEL_CONFIG),
                (ttk.Button, ['folder.png'], '', cfg_grid, {'command':self.set_alternative_path})),
                (ttk.Button, ['tick.png'], '',  dict(cfg_gridE,**{'columnspan':'3'}), {'command':self.save})]
                
    def finish(self):
        self.custFrm.config(padding=10)
        self.variables['steam_path'].set(self.app.cfg['user_pref']['steam_path'])
        self.variables['alt_path'].set(self.app.cfg['user_pref']['alt_path'])
        self.variables['save_mode'].set(self.app.cfg['user_pref']['save_mode'])
        
    def set_alternative_path(self):
        folder = filedialog.askdirectory(title='Set alternative output path',
                                        parent=self,
                                        initialdir=self.app.cfg['user_pref']['alt_path'])
        self.variables['alt_path'].set(folder)      # updates the value in the gui
        self.app.cfg['user_pref']['alt_path'] = folder  # for saving
        
    def set_steam_path(self):
        folder = filedialog.askdirectory(title='Set path to dota folder',
                                        parent=self,
                                        initialdir=self.app.cfg['user_pref']['steam_path'])
        self.variables['steam_path'].set(folder)
        self.app.cfg['user_pref']['steam_path'] = folder    # for saving
        
    def save(self):
        save_mode = self.variables['save_mode'].get()
        if not save_mode:
            messagebox.showinfo('Setting Required',
                                'Please select a save mode',
                                parent=self)
        else:
            self.app.cfg['user_pref']['save_mode'] = save_mode
            with open(self.app.DOTA_PATH_CFG, 'w') as outfile:
                outfile.write(json.dumps(self.app.cfg['user_pref']))
            self.parent.destroy()

class WelcomeMessage():
    text= '''
This appears to be your first time using d2settings! 

Welcome.

Before you can get started you have to enter a few settings.
Consider following the online documentaion here:

You can also press F1 for tab specific help or hold the mouse over
an option to get tooltip help if it is avaliable for that setting.
    
If you have a previous auto_exec file it will be renamed myold_autoexec.cfg
    '''
    def __init__(self, parent, app=None, text=None):
        if text:
            self.text = text
        messagebox.showinfo('Hallo', self.text, parent=parent)
        
if __name__ == '__main__':
    root = tk.Tk()
    UserPreferences(root)
    #~ main_gui = Gui_Main(root)
    #~ print(help(tk))
    root.mainloop()
    pass
