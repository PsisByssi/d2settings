import csv
import glob
import os
import json
import logging
import winreg

from timstools import InMemoryWriter
from timstools import ignored
from timstools import only_numerics

valve_key_list = {'Tab': 'tab', 
            'Return': 'enter', 
            'Escape': 'escape', 
            'Space': 'space', 
            'BackSpace': 'backspace', 
            'Up': 'uparrow', 
            'Down': 'downarrow', 
            'Left': 'leftarrow', 
            'Right': 'rightarrow', 
            'Alt_L': 'alt', 
            'Alt_R': 'alt', 
            'Control_L': 'ctrl', 
            'Control_R': 'ctrl', 
            'Shift_L': 'shift', 
            'Shift_R': 'shift', 
            'Insert': 'ins', 
            'Delete': 'del', 
            'Next': 'pgdn', 
            'Prior': 'pgup', 
            'KP_End': 'end',
            'KP_Home': 'kp_home',
            'KP_Up': 'kp_uparrow', 
            'KP_Prior': 'kp_pgup', 
            'KP_Left': 'kp_leftarrow ', 
            'KP_5': 'kp_5 ', 
            'KP_Right': 'kp_rightarrow', 
            'KP_End': 'kp_end', 
            'KP_Down': 'kp_downarrow', 
            'KP_Next': 'kp_pgdn',           #TEST THIS ONE
            'KP_Enter': 'kp_enter', 
            'KP_Insert': 'kp_ins', 
            'KP_Delete': 'kp_del', 
            'KP_Divide': 'kp_slash',
            'KP_Multiply': 'kp_multiply', 
            'KP_Subtract': 'kp_minus', 
            'KP_Add': 'kp_plus', 
            'Caps_Lock': 'capslock', 
            'tbd': 'joy1', 
            'tbd': 'joy2', 
            'tbd': 'joy3', 
            'tbd': 'joy4', 
            'tbd': 'aux1', 
            'tbd': 'mwheeldown', 
            'tbd': 'mwheelup', 
            'Button-1': 'mouse1', 
            'Button-2': 'mouse2',   #mouse 2 in tkinter is middle button when avaliable 
            'tbd': 'mouse3', 
            'tbd': 'mouse4', 
            'tbd': 'mouse5', 
            'Pause': 'pause'}

ahk_key_list = {
            #~ 'Tab': 'tab', 
            #~ 'Return': 'enter', 
            #~ 'Escape': 'escape', 
            #~ 'Space': 'space', 
            #~ 'BackSpace': 'backspace', 
            'Up': 'Up', 
            'Down': 'Down', 
            'Left': 'Left', 
            'Right': 'Right', 
            'Alt_L': 'LAlt', 
            'Alt_R': 'RAlt', 
            'Control_L': 'LCtrl', 
            'Control_R': 'RCtrl', 
            'Shift_L': 'LShift', 
            'Shift_R': 'RShift', 
            'Win_L': 'LWin', 
            #~ 'Insert': 'ins', 
            #~ 'Delete': 'del', 
            'Next': 'Pgdn', 
            'Prior': 'PgUp', 
            'KP_End': 'End',
            'KP_Home': 'NumpadHome',
            'KP_Up': 'NumpaduUp', 
            'KP_Prior': 'NumpadPgUp', 
            'KP_Left': 'NumpadLeft ', 
            'KP_Clear': 'kp_5 ',            # This is the numlock off and then the numpad 5 button! 
            'KP_Right': 'NumpadRight', 
            'KP_End': 'NumpadEnd', 
            'KP_Down': 'NumpadDown', 
            'KP_Next': 'NumpadPgDn',    
            'KP_Enter': 'NumpadEnter', 
            'KP_Insert': 'NumpadIns', 
            'KP_Delete': 'NumpadDel', 
            'KP_Divide': 'NumpadDiv',
            'KP_Multiply': 'NumpadMult', 
            'KP_Subtract': 'NumpadSub', 
            'KP_Add': 'NumpadAdd',
            'tbd': 'joy1', 
            'tbd': 'joy2', 
            'tbd': 'joy3', 
            'tbd': 'joy4', 
            'tbd': 'aux1', 
            'tbd': 'mwheeldown', 
            'tbd': 'mwheelup', 
            'Button-1': 'LButton', 
            'Button-2': 'MButton',  #mouse 2 in tkinter is middle button when avaliable 
            'Button-3': 'RButton',  #mouse 2 in tkinter is middle button when avaliable 
            'Num_Lock': 'NumLock',
            'Scroll_Lock': 'ScrollLock',
            'Caps_Lock': 'CapsLock'}

ahk_symbols = {                 # These have to be used when binding, however they look nasty so hencethe double mapping
        'LWin':'#',
        'LAlt': '!', 
        'RAlt': '!', 
        'LCtrl': '^', 
        'RCtrl': '^', 
        'LShift': '+', 
        'RShift': '+'}

def read_autoexec(auto_exec_file):
    cfg_settings = {}
    bind_settings = {}
    
    def remove_crud(row,INDEX=1):                               
        cfg_values = []
        for i, value in enumerate(row[INDEX:]):
            for j, sub_sec in enumerate(value.split('\t')): # Break out the tabs and remove paranthesis
                sub_sec = sub_sec.replace('(','')
                sub_sec = sub_sec.replace(')','')
                cfg_values.append(sub_sec)      
                if 'tooltip' in sub_sec:
                    tip_text = ' '.join(row[INDEX+i+1:])
                    tip_text = tip_text[:tip_text.index(')')] 
                    cfg_values.append(tip_text)     
        return cfg_values

    with open(auto_exec_file, 'r', newline='') as f:
        reader = csv.reader(f, delimiter=' ')
        for i, row in enumerate(reader):
            try:
                char = row[0][0]            # first char in first item
            except IndexError:
                pass
            else:
                if char:
                    if row[0] == 'bind':        # Handling the binds
                        setting = row[1]
                        if '\t' in setting:     # remove any tabs after the hotkey
                            setting = setting.split('\t')[0]    
                        cfg_values = remove_crud(row, INDEX=2)
                        bind_settings[setting] = cfg_values 
                        if 'courier_hotkey' in cfg_values:
                            cfg_settings['courier_msg'] = [cfg_values[0].split(';')[1].split('say_team')[-1].strip(), i]
                    elif row[0] == 'alias':
                        if row[1] == 'hptoggle':
                            cfg_settings['hptoggle'] = i + 1
                    elif char != '/':
                        setting = row[0]
                    elif row[0] == '//IGNORE':  # Handling the Ignore Comments and blank lines
                        setting = '//IGNORE {0}'.format(row[1])
                    else:                       # Commented lines
                        continue
                    cfg_values = remove_crud(row)
                    cfg_settings[setting] = cfg_values          # save the setting and values
    return cfg_settings, bind_settings

def read_ahk_file(ahk_file):
    ahk_bind_settings = {}
    with open('dota_binds.ahk', 'r', newline='') as file:
        reader = csv.reader(file, delimiter=' ')
        #~ non_empty_rows = ((i, row) for i, row in enumerate(reader) if row and row[0] and row[0][0] !=';' )
        #~ for i, row in non_empty_rows:
            #~ print(row)
            #~ for j, col in enumerate(row):
        ahk_commands = ((i,j, row, col) for i, row in enumerate(reader) if row and row[0] and row[0][0] !=';'
                            for j, col in enumerate(row) if col[-2:] == '::')
        for i,j, row, col in ahk_commands:
            try:
                if row[j+1] == 'send':          # we only care about non multiline binds so
                    dota_hotkey = row[j+2][1:]
                    dota_hotkey = dota_hotkey.split('}')[0]
                    ahk_hotkey = row[:j+1]
                    ahk_hotkey[-1] = ahk_hotkey[-1][:-2] # remove the :: syntax from the end
                    with ignored(IndexError):
                        if '&' == ahk_hotkey[1]:
                            del ahk_hotkey[1]
                    for key, value in ahk_key_list.items():
                        if dota_hotkey == value:
                            valverised = valve_key_list[key]
                            break
                        else:
                            valverised = dota_hotkey
                    ahk_bind_settings[valverised] = ahk_hotkey
            except IndexError:pass

                #~ if col == 'send':                # Identify the hotkeys
        #               #~ print(row)
                        #~ ahk_hotkey = []
                        #~ for k in range(0,j-1):       # we have to remove the :: from the last hotkey
                            #~ if k == j-1:
                                #~ ahk_hotkey.append(col[k][0:-2])
                            #~ else:
                                #~ ahk_hotkey.append(col[k])
                        #~ print(row)
                        #~ try:
                            #~ key_to_send = col[j+1]
                        #~ except IndexError:
                            #~ key_to_send = col[j]         # i.e LWIN:: return
        #~ #                #~ key_to_send = key_to_send[1:-1]  # remove brackets add start and end
                        #~ ahk_bind_settings[key_to_send] = ahk_hotkey
    #~ pprint(ahk_bind_settings)
    return ahk_bind_settings
    
def save_settings(exec_file, selected_setting, value):
    IGNORE = False
    def quotes_on_strings(value):   
        value = "\"{0}\"".format(value)
        return value
    logging.info('Trying to save the setting, %s' %selected_setting)
    if selected_setting.split('_')[-1] == 'default':        # A row is being muted/unmuted
        selected_setting = selected_setting.replace('_default','')
        IGNORE = True
    for i, row in enumerate(exec_file):
        if selected_setting in row:
            logging.info('found the row: %s' % row)
            break                       # have the position now have to edit it
    else:
        logging.warning('Couldnt find the setting in the file... make sure its in theree')
        return
    split_row = row.split(' ')  
    if IGNORE == True:                      # User is muting or unmuting a row
        logging.info('muting or unmuting')
        if split_row[0] == '//IGNORE':
            if value == 0:
                new_row = row[len('//IGNORE '):]
                logging.info('OLD_ROW: %s' %repr(row))
                logging.info('NEW_ROW: %s' %repr(new_row))  
                exec_file[i] = new_row
        else:
            if value == 1:
                new_row = '//IGNORE '+row
                logging.info('OLD_ROW: %s' %repr(row))
                logging.info('NEW_ROW: %s' %repr(new_row))  
                exec_file.data[i] = new_row
    elif split_row[0] == selected_setting:
        value = quotes_on_strings(value)
        old_value = split_row[1].split('\t')[0]
        rest_of_row = row[len(selected_setting + old_value)+1:] 
        new_row = '{0} {1}{2}'.format(selected_setting, value, rest_of_row)
        logging.info('OLD_ROW: %s' %repr(row))
        logging.info('NEW_ROW: %s' %repr(new_row))
        exec_file[i] = new_row
    elif split_row[0] == 'bind':
        try:
            value = quotes_on_strings(value[0]) 
        except IndexError:
            value = '"empty"'   # have to see what is legal with valve
        old_value = split_row[1].split('\t')[0]
        rest_of_row = row[len('bind '+ old_value):] 
        new_row = 'bind {0}{1}'.format(value, rest_of_row)
        logging.info('OLD_ROW: %s' %repr(row))
        logging.info('NEW_ROW: %s' %repr(new_row))
        exec_file[i] = new_row
    else:                                   # user has modified a row that is already muted
        print('modified a row that is already muted !')
        value = quotes_on_strings(value)        
        old_value = split_row[2].split('\t')[0]
        rest_of_row = row[len('//IGNORE {0} {1}'.format(selected_setting, old_value)):] 
        new_row = '//IGNORE {0} {1}{2}'.format(selected_setting, value, rest_of_row)
        logging.info('OLD_ROW: %s' %repr(row))
        logging.info('NEW_ROW: %s' %repr(new_row))
        exec_file[i] = new_row

def save_hptoggle(app, widget):
    print('In save hp toggle')
    lb = widget.formRef['selectedheores'].listbox
    index = app.cfg_settings['hptoggle']
    
    line_breaks = 0
    for offset, row in enumerate(app.auto_exec[index:]):    # Remove the old data
        if row == '\n': 
            line_breaks = line_breaks + 1
        if line_breaks == 2:                                # On the Seconds line break
            del app.auto_exec[index : index+offset]
            break
    first_section_length = len(lb.get(0, 'end'))
    text_echoes = []
    for pos, hero in enumerate(lb.get(0, 'end')):   
        print(pos)
        start = pos + 1
        end = pos + 2
        if first_section_length-1 == pos:
            print('Setting end now !')
            end = 1
        new_row = 'alias "hp{0}" "clear;numkeysclear;exec hp\{1}_hp.cfg;alias textecho {0}toload;output_text_to_screen; alias hptoggle hp{2}"\n'.format(start, hero, end)   # Create new row
        app.auto_exec.insert(index+pos, new_row)
        text_echoes.append('alias "{0}toload" "textblank3;echo ----- {1} -----"\n'.format(start, hero))
    for i, row in enumerate(text_echoes):
        app.auto_exec.insert(index+pos+2+i, row)
    app.auto_exec.insert(index+pos+3+i, '\n')

def load_keys_hptoggle(self):
    # Loads the key binds from hp100_hp.cfg, the other hp.cfg files all use the same
    keys = []
    with open('hp/hp100_hp.cfg') as hp:
        for row in hp:
            if row:
                keys.append(row.split(' ')[1])
        for i, value in zip(range(1,11), keys):
            value = value[1:-1] 
            self.formRef['hpkey'+str(i)].set(value)
            
def save_hp_keys(setting, value):
    key_num = int(only_numerics(setting))
    print('key_num', key_num)
    for file in glob.glob('hp/*_hp.cfg'):
        print(file)
        i = 1
        file_writer = InMemoryWriter(file, verbose=True)
        for line in file_writer(copy=True):
            if line.rstrip():
                if i == key_num:
                    old_value = line.split(' ')[1][1:-1]
                    new_line = line.replace(old_value, value[0])
                    file_writer[file_writer.i-1] = new_line
                    break
                i += 1
        file_writer.save()

def save_ahk(gui_main, ahk_file, current_tab, ahk_grabber, setting, value):     
    def hk_to_ahkhk(hotkey_list):
        start = []                          # The hotkey part
        end = []                            # The command to execute
        if len(hotkey_list) == 1:
            tk_form = ahk_grabber.key_parser(hotkey_list[0])
            print('tk_form', tk_form)   #TBD fix the distinctuion between alt_r and alt_l etc depends if valve has a distinction!
            start.append(ahk_grabber.key_parser(tk_form, ahk_key_list) + '::')
        elif len(hotkey_list) == 2 and ahk_grabber.key_parser(hotkey_list[1]) in ahk_grabber.tk_modifiers:      # this enables bindings of just two modifyers, you could also do combinations of keys but thats awkward and takes more work to get the keys to still work as normal keys so cbf
            tk_form = ahk_grabber.key_parser(hotkey_list[0])
            start.append(ahk_grabber.key_parser(tk_form, ahk_key_list))
            start.append('&')
            tk_form2 = ahk_grabber.key_parser(hotkey_list[1])
            start.append(ahk_grabber.key_parser(tk_form2, ahk_key_list) + '::') 
        else:
            hot_key = []                                                                # the hotkey cannot contain spaces in this form
            for part in hotkey_list:
                tk_form = ahk_grabber.key_parser(part)
                if tk_form in ahk_grabber.tk_modifiers:
                    symbol_form = ahk_symbols[ahk_key_list[tk_form]]
                    hot_key.append(symbol_form)
                    continue
                else:
                    hot_key.append(ahk_grabber.key_parser(tk_form, ahk_key_list))
                    break
            hot_key = ''.join(part for part in hot_key)
            start.append(hot_key + '::')
        start.append('send')
        start = ' '.join(start)
        try:
            to_send = bind_grabber.key_parser(bind_grabber.get()[0])
        except TypeError:                   # None Type, cannot create remap key as no key to map to
            return
        end.append(' {{{0}}}'.format(ahk_grabber.key_parser(to_send, ahk_key_list)))
        return start, end       
    print()
    print('save AHK', setting,value)
    bind_grabber = current_tab.formRef[setting.split('_remap')[0]]
    start = []                          # The hotkey part
    end = []                            # The command to execute
    for i, row in enumerate(ahk_file):
        if 'Hot Keys' in row:
            hk_index = i
            break
    for i, row in enumerate(ahk_file[hk_index+1:]):
        if ';----' in row:
            hk_end = hk_index + i
            break
    try:                                    # Modify an existig mapping
        old_hk = ahk_grabber.original_value
        if len(old_hk) == 1:                    # Assembling old_hk from a list into original str
            old_hk_start = old_hk[0] + '::'
        elif len(old_hk) == 2:
            old_hk_start = '{0} & {1}::'.format(old_hk[0], old_hk[1])
        #~ print('old_hk_start', old_hk_start)
        for i, row in enumerate(ahk_file[hk_index:hk_end]): # Looking for the row in the ahk file
            if old_hk_start in row:
                row_index = hk_index + i
                #~ print('FOUND ROW!!!', row)
                break
        start, end = hk_to_ahkhk(value)                     # Building new row and inserting
        ahk_grabber.original_value = [start.split('::')[0]]
        old_row = ahk_file[row_index]
        old_to_send = old_row.split(' ')[2]
        old_to_send_index = old_row.index(old_to_send)
        rest_of_row = old_row[old_to_send_index+len(old_to_send):]
        end.append(rest_of_row)
        end = ' '.join(end)
        ahk_file[row_index] = start + end 
    except AttributeError:                  # Create new ahk mapping that didn't exist before
        hotkey_list = ahk_grabber.get()
        start, end = hk_to_ahkhk(hotkey_list)
        with ignored(AttributeError):       # get comment text from tooltip
            text = ahk_grabber.tooltip_text
        with ignored(AttributeError):
            text = bind_grabber.tooltip_text
        with ignored(AttributeError):
            entry_widget = setting.split('_hotkey')[0]
            for tab in gui_main.formRef['settings'].widget_ref.values():        #The notebook tabs TBD COMMENTS
                for setting, widget in tab.formRef.items():
                    if setting == entry_widget:
                        text = widget.tooltip_text
        try:
            comment = '\t\t\t;{0}\n'.format(text)
            end.append(comment)
        except UnboundLocalError:
            end.append('\n\n')
        end = ' '.join(end)
        ahk_file.insert(hk_end +1, start+end)
    print()
    print(start+end)
    if not gui_main.app.DEVELOPING:
        logging.info(gui_main.app.cfg['user_pref'][gui_main.app.cfg['user_pref']['save_mode']]+'\\ahk_test.ahk')
        ahk_file.save(gui_main.app.cfg['user_pref'][gui_main.app.cfg['user_pref']['save_mode']]+'\\ahk_test.ahk')
    else:
        ahk_file.save('dota_bind_saved.ahk')
    
def convert_akh_symbols(hot_key, ahk_widg):
    '''Changes Modifiyers from symbols into ahk words'''
    reconstructed = []
    if len(hot_key) == 1:               # Hotkey is all one string i.e ^!6
        if len(hot_key[0]) == 1:            # A single Hotkey will never be a modifiyer key or symbol
            reconstructed.append(ahk_widg.key_parser(hot_key[0], ahk_key_list)) 
        else:
            for i, char in enumerate(hot_key[0]):   # All But the last are modifiery keys
                unsymbol = ahk_widg.key_parser(char, ahk_symbols)
                if len(unsymbol) > 1:
                    reconstructed.append(unsymbol)
                else:
                    break
            reconstructed.append(hot_key[0][i:]) 
        return reconstructed
    else:
        return hot_key

def save_courier_msg(exec_file, cfg_settings, setting, value):
    index = cfg_settings[setting][-1]
    old_row = exec_file[index]
    start = old_row[:old_row.index('say_team')]
    end = 'say_team '+ old_row[old_row.index('say_team'):]
    end = end[end.index(';'):]
    new_row = start + 'say_team ' +value + end
    exec_file[index] = new_row
    
def save_courier_macro(gui_main, ahk_file, current_tab, ahk_grabber, setting, value):   #TBD is this still valid? 6/5/2015
    if setting == 'courier_hotkey':pass
    else:
        for i, row in enumerate(ahk_file):
            if 'Courier' in row:
                hk_index = i
                break
        for i, row in enumerate(ahk_file[hk_index+1:]):
            if ';----' in row:
                hk_end = hk_index + i
                break
        old_hk = ahk_grabber.original_value
        if len(old_hk) == 1:                    # Assembling old_hk from a list into original str
            old_hk_start = old_hk[0] + '::'
        elif len(old_hk) == 2:
            old_hk_start = '{0} & {1}::'.format(old_hk[0], old_hk[1])
        print('old_hk_start', old_hk_start)
        for i, row in enumerate(ahk_file[hk_index:hk_end]): # Looking for the row in the ahk file
            if old_hk_start in row:
                row_index = hk_index + i
                print('FOUND ROW!!!', row)
                break
        start, end = hk_to_ahkhk(value)                     # Building new row and inserting
        ahk_grabber.original_value = [start.split('::')[0]]
        old_row = ahk_file[row_index]
        old_to_send = old_row.split(' ')[2]
        old_to_send_index = old_row.index(old_to_send)
        rest_of_row = old_row[old_to_send_index+len(old_to_send):]
        end.append(rest_of_row)
        end = ' '.join(end)
        ahk_file[row_index] = start + end 

def find_d2_path(user_pref, data_folder):
    '''sets the default paths if no cfg file'''
    # user_path is a dict and mutable, no need to return the changes!
    def get_steam_path():
        for reg_thing in (winreg.HKEY_CURRENT_USER,
                          winreg.HKEY_USERS,
                          winreg.HKEY_LOCAL_MACHINE):
            winreg.OpenKey(reg_thing, "Software\\valve\\steam")
            try:
                key = winreg.OpenKey(reg_thing, "Software\\valve\\steam")
                path = winreg.QueryValueEx(key, "SteamPath")[0]
            except FileNotFoundError:
                pass
            else:
                return path
    steam_path = get_steam_path()
    if steam_path:
        user_pref["steam_path"] = steam_path
        user_pref["save_mode"] = "steam_path"
    else:
        user_pref["save_mode"] = "alt_path"
    user_pref["alt_path"] = os.path.join(data_folder, "output")

if __name__ == '__main__':
    pass
