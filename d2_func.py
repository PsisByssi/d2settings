from pprint import pprint
import csv
import time

from timstools import InMemoryWriter
from timstools import ignored
from timstools import only_numerics

def read_settings():
	cfg_settings = {}
	bind_settings = {}
	
	def remove_crud(row,INDEX=1):								
		cfg_values = []
		for i, value in enumerate(row[INDEX:]):
			for j, sub_sec in enumerate(value.split('\t')):	# Break out the tabs and remove paranthesis
				sub_sec = sub_sec.replace('(','')
				sub_sec = sub_sec.replace(')','')
				cfg_values.append(sub_sec)	 	
				if 'tooltip' in sub_sec:
					tip_text = ' '.join(row[INDEX+i+1:])
					tip_text = tip_text[:tip_text.index(')')] 
					cfg_values.append(tip_text)		
		return cfg_values

	with open('autoexec.cfg', 'r', newline='') as f:
		reader = csv.reader(f, delimiter=' ')
		for i, row in enumerate(reader):
			try:
				char = row[0][0]			# first char in first item
			except IndexError:
				pass
			else:
				if char:
					if row[0] == 'bind':		# Handling the binds
						setting = row[1]
						cfg_values = remove_crud(row, INDEX=2)
						bind_settings[setting] = cfg_values 
					elif row[0] == 'alias':
						if row[1] == 'hptoggle':
							cfg_settings['hptoggle'] = i
					elif char != '/':
						setting = row[0]
					elif row[0] == '//IGNORE':	# Handling the Ignore Comments and blank lines
						setting = '//IGNORE {0}'.format(row[1])
					else:						# Commented lines
						continue
					cfg_values = remove_crud(row)
					cfg_settings[setting] = cfg_values			# save the setting and values
	#~ pprint(cfg_settings)
	#~ pprint(bind_settings)
	ahk_settings = read_ahk_file()
	return cfg_settings, bind_settings, ahk_settings

def read_ahk_file():
	# We do not need to write a dota name for what its mapped to, just check what button is mapped
	# in the cfg, and match it like that.
	ahk_bind_settings = {}
	#~ return ahk_bind_settings
	with open('dota_binds.ahk', 'r', newline='') as file:
		reader = csv.reader(file, delimiter=' ')
		#~ non_empty_rows = ((i, row) for i, row in enumerate(reader) if row and row[0] and row[0][0] !=';' )
		#~ for i, row in non_empty_rows:
			#~ print(row)
			#~ for j, col in enumerate(row):
		ahk_commands = ((i,j, row, col) for i, row in enumerate(reader) if row and row[0] and row[0][0] !=';'
							for j, col in enumerate(row) if col[-2:] == '::')
		for i,j, row, col in ahk_commands:
			#~ print(col)
			try:
				if row[j+1] == 'send':			# we only care about non multiline binds so	
					dota_hotkey = row[j+2]
					dota_hotkey = dota_hotkey.replace('{','')	# this annotation stop ahk from sending the key as a char to windows
					dota_hotkey = dota_hotkey.replace('}','')
					ahk_hotkey = row[:j+1]
					ahk_hotkey[-1] = ahk_hotkey[-1][:-2] # remove the :: syntax from the end
					with ignored(IndexError):
						if '&' == ahk_hotkey[1]:
							del ahk_hotkey[1]
					#~ print(dota_hot_key,j)	
					#~ print(ahk_hot_key,j)	
					ahk_bind_settings[dota_hotkey] = ahk_hotkey
			except IndexError:pass	
				
				#~ if col == 'send':				# Identify the hotkeys			
		#				#~ print(row)
						#~ ahk_hotkey = []
						#~ for k in range(0,j-1):		# we have to remove the :: from the last hotkey
							#~ if k == j-1:				
								#~ ahk_hotkey.append(col[k][0:-2])
							#~ else:
								#~ ahk_hotkey.append(col[k])		
						#~ print(row)		
						#~ try:
							#~ key_to_send = col[j+1] 
						#~ except IndexError:
							#~ key_to_send = col[j]			# i.e LWIN:: return
		#~ #				#~ key_to_send = key_to_send[1:-1]	# remove brackets add start and end 
						#~ ahk_bind_settings[key_to_send] = ahk_hotkey
	#~ pprint(ahk_bind_settings)
	return ahk_bind_settings
	
def load_exec_into_memory():
	# All Lines are loaded into memory and wrote to file after all edits are made
	exec_file = InMemoryWriter()
	with open('autoexec.cfg', 'r') as file: 
		exec_file.writelines(file)			  # about 18k in memory ^^
	return exec_file

def save_settings(exec_file, selected_setting, value):
	IGNORE = False
	def quotes_on_strings(value):	
		value = "\"{0}\"".format(value)
		return value
	print('Trying to save the setting, ',selected_setting)
	if selected_setting.split('_')[-1] == 'default':		# A row is being muted/unmuted
		selected_setting = selected_setting.replace('_default','')
		IGNORE = True
	for i, row in enumerate(exec_file):
		if selected_setting in row:
			print('found the row', row)
			break						# have the position now have to edit it
	else:
		print('Couldnt find the setting in the file... make sure its in theree')
		return
	
	split_row = row.split(' ')	
	if IGNORE == True:						# User is muting or unmuting a row
		print('muting or unmuting')
		if split_row[0] == '//IGNORE':
			if value == 0:
				new_row = row[len('//IGNORE '):]
				print('OLD_ROW: ',repr(row))
				print('NEW_ROW: ',repr(new_row))	
				exec_file.data[i] = new_row
		else:
			if value == 1:
				new_row = '//IGNORE '+row
				print('OLD_ROW: ',repr(row))
				print('NEW_ROW: ',repr(new_row))	
				exec_file.data[i] = new_row
	elif split_row[0] == selected_setting:
		value = quotes_on_strings(value)
		old_value = split_row[1].split('\t')[0]
		rest_of_row = row[len(selected_setting + old_value)+1:]	
		new_row = '{0} {1}{2}'.format(selected_setting, value, rest_of_row)
		#~ print('split0',split_row[0],'VALUE',value,'REST',repr(rest_of_row))
		print('OLD_ROW: ',repr(row))
		print('NEW_ROW: ',repr(new_row))
		exec_file.data[i] = new_row
	elif split_row[0] == 'bind':
		try:
			value = quotes_on_strings(value[0]) 
		except IndexError:
			value = '"empty"'	# have to see what is legal with valve
		old_value = split_row[1].split('\t')[0]
		rest_of_row = row[len('bind '+ old_value):]	
		new_row = 'bind {0}{1}'.format(value, rest_of_row)
		#~ print('split0',split_row[0],'VALUE',value,'REST',repr(rest_of_row))
		print('OLD_ROW: ',repr(row))
		print('NEW_ROW: ',repr(new_row))
		exec_file.data[i] = new_row
	else:									# user has modified a row that is already muted
		print('modified a row that is already muted !')
		value = quotes_on_strings(value)		
		old_value = split_row[2].split('\t')[0]
		rest_of_row = row[len('//IGNORE {0} {1}'.format(selected_setting, old_value)):]	
		new_row = '//IGNORE {0} {1}{2}'.format(selected_setting, value, rest_of_row)
		#~ print('split0',split_row[0],'VALUE',value,'REST',repr(rest_of_row))
		print('OLD_ROW: ',repr(row))
		print('NEW_ROW: ',repr(new_row))
		exec_file.data[i] = new_row

def save_hptoggle(app, widget):
	lb = widget.caller.formRef['selectedheroeslistbox'].listbox
	index = app.cfg_settings['hptoggle']+5
	for hero in lb.get(0, 'end'):
		if hero not in lb.master.options:		# Adding New Hero
			#~ print('adding new hero!', hero)
			for i, row in enumerate(app.auto_exec.data[index:index+10]):	
				if 'hp' not in row:			
					prev_row = app.auto_exec.data[index+i-1]		# Modify previous row
					rest_of_row = prev_row[: -len(prev_row.split(' ')[-1])]
					num = int(only_numerics(prev_row.split(' ')[1]))
					new_end = '"hp{0}"'.format(num+1)
					new_prev_row = '{0}{1}\n'.format(rest_of_row, new_end)
					del app.auto_exec.data[index+i]
					app.auto_exec.data[index+i-1] = new_prev_row	# Create new row
					new_row = 'alias "hp{0}" "clear;numkeysclear;exec {1}_hp.cfg;alias textecho {0}toload;output_text_to_screen; alias hptoggle hp1"\n\n'.format(num+1 , hero)	# Create new row
					app.auto_exec.data[index+i] = new_row
					break
	for orig_hero in lb.master.options:
		if orig_hero not in lb.get(0, 'end'):	# Removing a hero
			#~ print('remove', orig_hero)
			for i, row in enumerate(app.auto_exec.data[index:index+6]):		# Identify row to remove
				if not row:pass
				split_row = row.split(' ')
				hero_name = split_row[3].split('_hp.cfg')[0]
				if orig_hero == hero_name:
					next_alias_name = split_row[-1]
					hero_row_index = index+i
					#~ print('removing row',app.auto_exec.data[hero_row_index])
					del app.auto_exec.data[hero_row_index]					# Remove Row
					break
			prev_row = app.auto_exec.data[hero_row_index-1]					# Modifiy Prev row
			prev_num = int(only_numerics(prev_row.split(' ')[-1]))
			next_num = int(only_numerics(next_alias_name))
			if prev_num > next_num:  					# The Entry deleted was the last hptoggle
				rest_of_row = prev_row[:-len(prev_row.split(' ')[-1])]
				#~ print('rest of row', rest_of_row)	
				new_row = '{0}{1}'.format(rest_of_row, next_alias_name)
				#~ print('new row',new_row)
				del app.auto_exec.data[hero_row_index-1]
				app.auto_exec.data[hero_row_index-1] = new_row
			else:										# Reasign all the ones that come after
				for i, row in enumerate(app.auto_exec.data[hero_row_index:hero_row_index+10]):
					end = int(only_numerics(row.split(' ')[-1]))
					prev_row = app.auto_exec.data[hero_row_index+i-1]
					try:
						prev_row_start = int(only_numerics(prev_row.split(' ')[1]))
					except ValueError:			# the first row
						prev_row_start = 0
					new_start ='"hp{0}"'.format(prev_row_start+1)
					prev_row_end = int(only_numerics(prev_row.split(' ')[-1]))
					if end != 1:
						end = end-1
					new_end = '"hp{0}"'.format(end)
					#~ print('new_end!', new_end)
					rest_of_row = row[len('alias') + len(row.split(' ')[1]) : -len(row.split(' ')[-1])]
					#~ print('rest of row',rest_of_row)
					new_row = 'alias {0}{1}{2}\n'.format(new_start, rest_of_row, new_end)
					#~ print('new row', new_row) # NOW DO WHEN THEY DELTE THE FIRST ONE!
					#~ print('old',row)
					app.auto_exec.data[hero_row_index+i] = new_row
					if prev_row_end > end:				# Reached the last row i.e leave it pointing to the first hp toggle
						break
	lb.master.options = lb.get(0, 'end')

def load_keys_hptoggle(self):
	# Loads the key binds from hp100_hp.cfg, the other hp.cfg files all use the same
	with open('hp/hp100_hp.cfg') as hp:
		keys = []
		for row in hp:
			if row:
				keys.append(row.split(' ')[1])
		for i, value in zip(range(1,11), keys):
			self.formRef['hpkey'+str(i)].set(value)

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
			'KP_Next': 'kp_pgdn', 			#TEST THIS ONE
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
			'Button-2': 'mouse2',	#mouse 2 in tkinter is middle button when avaliable 
			'tbd': 'mouse3', 
			'tbd': 'mouse4', 
			'tbd': 'mouse5', 
			'Pause': 'pause'}

def valve_key_parser(passed_key):
	try:
		valve_key = valve_key_list[passed_key]
		return valve_key
	except KeyError:
		#~ print('e')
		for key, value in key_list.items():
			#~ print('e')
			if passed_key == value:
				#~ print('retu', value)
				return key			# going from valve key to a tkinter key
		else:
			return passed_key


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
			#~ 'Insert': 'ins', 
			#~ 'Delete': 'del', 
			'Next': 'Pgdn', 
			'Prior': 'PgUp', 
			'KP_End': 'End',
			'KP_Home': 'NumpadHome',
			'KP_Up': 'NumpaduUp', 
			'KP_Prior': 'NumpadPgUp', 
			'KP_Left': 'NumpadLeft ', 
			'KP_Clear': 'kp_5 ',			# This is the numlock off and then the numpad 5 button! 
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
			'Button-2': 'MButton',	#mouse 2 in tkinter is middle button when avaliable 
			'Button-3': 'RButton',	#mouse 2 in tkinter is middle button when avaliable 

			#~ 'Pause': 'Pause',
			'Num_Lock': 'NumLock',
			'Scroll_Lock': 'ScrollLock',
			'Caps_Lock': 'CapsLock'
				}


if __name__ == '__main__':
	import tttimer
	#~ print(help(tttimer))
	
	DICT = {}
	LIST = []
	for i in range(0,500000):
		LIST.append(i*150)
		DICT.update({i:i*150})
	def lister():
		with open('dota_binds.ahk', 'r', newline='') as file:
			reader = csv.reader(file, delimiter=' ')
			for i, row in enumerate(reader):
				if row and row[0] and row[0][0]!=';':
					#~ print(row)
					#~ print(row)
					pass
	def dicter():
		with open('dota_binds.ahk', 'r', newline='') as file:
			reader = csv.reader(file, delimiter=' ')
			non_empty_rows = ((i, row) for i, row in enumerate(reader) if row and row[0] and row[0][0] !=';' )
			for i, row in non_empty_rows:
				#~ print(row)
				pass
	print('start')
	print(tttimer.total(1,lister))
	print(tttimer.total(1,dicter))
	
