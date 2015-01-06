import tkinter as tk
import tkinter.ttk as ttk

from timstools import ignored
from timstools import MaxInput, TimedOut, event_clock
from defaults_gui import *  

class HotKeyGrabberMaker(tk.Frame):
	'''
	Used for getting user input from the keyboard
	Subclass this function and change the variables in a start
	method to change options, defaults shown below
	self.time_out = 3000
	self.max_vars = 3
	Custom Display Format
	
	'''
	time = []						#holds time between key presses
	captured = []					#holds results      
	format_start, format_end = ('<','>')	
	time_out = 3000
	max_vars = 3
	text = 'Click to enter a hot key..'
	conf = {'width':30}
	def __init__(self, parent=None,app = None):
		tk.Frame.__init__(self, parent, relief='flat',borderwidth=0)
		self.pack(expand=1, fill='both')   		
		self.app = app
		self.start()
		self.makeWidgets()
		with ignored(AttributeError):
			self.ent.config(**self.conf)	
	def start(self):
		pass
	def duplicate_err_handle(self,event,**kwargs):
		pass
	def on_key_press(self,event):	#parses the values	
		print('in on key_press')
		try:
			print(self.time)
			print(self.captured)
			event_clock(event,
						timevar=self.time,
						timemax=self.time_out,
						entries=self.captured,
						maxentries=self.max_vars)
		except(MaxInput,TimedOut) as err:
			print('should be reseting..')
			print()
			self.reset()
			self.captured = [event.keysym]	# keep the last value the user entered
			
			if err.__class__ == MaxInput:
				pass
				#~ self.max_input_handle
			msg = 'Field reset - {0}'.format(err)		#move this to the subclassed function 
			self.app.send_ui_feedback(msg, image=False)
		else:
			print('no error')
			print()
			self.captured.append(event.keysym)
			#~ print(event.keycode,'event.keycode')
			#~ print(event.char,'event.char')
			#~ print(event.keysym,'event.keysym')
			#~ keycode = HOTKEY.modders[event.keysym]
			#~ print(keycode,'keycode from vkcodes',str(keycode).encode())
	
			#~ if event.keysym == 'BackSpace':
				#~ print('bspace')
			#~ elif event.keysym == 'Tab':
				#~ print('tab')
			with ignored(IndexError):			# if the user holds down a key, prevents it from spammin in multiple times
				if self.captured[-1] == self.captured[-2]:
					del self.captured[-1]		#stops the capture list from filling up and reseting the event clock
					self.duplicate_err_handle(event)
					#~ raise DuplicateKeyPressed
					return 'break'
								
		x= self.format_start +' %s %s ' % (self.captured[-1], self.format_end)	#the last added char is formated 
		#~ print(x)
		self.entvar.set(self.entvar.get()+x)
		return 'break'								#stops tkinter using default binding to insert typed text
	
	def reset(self,event=None):
		self.entvar.set('')
		self.time = []
	
	def validate_hk(func_hk_values):			#i did a decorator because its a clear seperation of logic
		'''
		Tbd, atm im assuming no modifyers after a key is os independant
		also that modifyer key key is os independant and ok	
		both testesd on windows
		
		'''
		class ModifyerAfterKeyError(Exception):
			pass
		def on_call(*args):
			hk_list = func_hk_values(*args)
			print(hk_list,'the hklist')
			for i, hk in enumerate(hk_list):
				print(i,hk,'i and hk')
				if hk in HOTKEY.vk_codes and i+2 != len(hk_list):			#If a key and not the last hotkey
					print()
					print(hk_list[i + 1],'hk[i + 1]')
					
					if hk_list[i + 1] in HOTKEY.modders:						#If next hotkey is a modifyer like ctrl or shift
						raise ModifyerAfterKeyError
					
			return hk_list
		return on_call
	
	#~ @validate_hk
	def get(self):
		'''Get a list of the entered keys without formating'''
		if self.entvar.get() == self.text:
			return None
		else:
			chars = [char for char in self.entvar.get().split() 
					if char not in (self.format_start,self.format_end)]  
			return chars
	
	def set(self, hotkeyvalues):
		'''set a str with formatting
		pass in a list'''
		formatted = (self.format_start +' %s %s ' % (item, self.format_end) 
										 for item in hotkeyvalues)
		formatted = ''.join(formatted)
		print(formatted)
		self.entvar.set(formatted)
	
	def makeWidgets(self):
		def on_focus():												
			self.ent.focus()
			self.reset()
			self.capture = []								#Reset doesnt touch this so manually reset
			
		self.ent = ttk.Entry(self, **c_pentry)
		ttk.Style().map(self.ent['style'],
						foreground=[('disabled','black')])	#making disabled state not dull text
		self.ent.config(state = 'disabled')					#removing cursor 
		self.entvar = tk.StringVar()
		self.entvar.set(self.text)
		self.ent.config(textvariable=self.entvar, takefocus=True)
		self.ent.bind('<Key>',  self.on_key_press)
		self.ent.bind('<Button-1>',lambda event: on_focus())
		self.ent.bind('<FocusIn>', self.reset)
		self.ent.pack(expand=1, fill='both')
