from pprint import pprint
import csv
import time

from timstools import InMemoryWriter

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
					elif char not in ('/','\\'):
						setting = row[0]
					elif row[0] == '//IGNORE':	# Handling the Ignore Comments and blank lines
						setting = '//IGNORE {0}'.format(row[1])
					else:
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
					dota_hot_key = row[j+2]
					ahk_hot_key = row[:j+1]
					ahk_hot_key[-1] = ahk_hot_key[-1][:-2] # remove the :: syntax from the end
					
					print(dota_hot_key,j)	
					print(ahk_hot_key,j)	
					#~ print(col)
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
	def quotes_on_strings(value):
		try:
			int(value)
		except ValueError:				# don't think valve cares but put only strs in the quotes
			value = "\"{0}\"".format(value)
		return value
		
	print('Trying to save the setting, ',selected_setting)
	for i, row in enumerate(exec_file):
		if selected_setting in row:
			break						# have the position now have to edit it
	else:
		print('Couldnt find the setting in the file... make sure its in theree')
		return
	
	split_row = row.split(' ')
	if split_row[0] in (selected_setting, 'bind'):
		try:
			value = quotes_on_strings(value)
		except TypeError:					# a list was returned from the hotkeygrabber. 
			if len(value) == 1:
				value = quotes_on_strings(value[0])
				#TBD HANDLE hotkey of 2 chars wow				
		split_row[1]  = value
		new_row = ' '.join(item for item in split_row)
		print('OLD_ROW: ',row)
		print('NEW_ROW: ',new_row)
		exec_file.data[i] = new_row
	#~ elif: split_row[0] == 'bind':
	#~ pprint(exec_file.data)
	#~ return		//IGNORE
	
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
	
