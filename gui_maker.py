#ISSUE1
# ANOTHER PROBLEM, (ttk.Label, 'Work Book Name',	None,cfg_grid,c_label), if used iun ccustomr form and the None field on the left is a '' will not be built...
"""
###############################################################################
An extended Frame that makes window menus and toolbars automatically.
Use GuiMakerFrameMenu for embedded components (makes frame-based menus).
Use GuiMakerWindowMenu for top-level windows (makes Tk8.0 window menus).

See the self-test code for an example layout tree format.

Based on The example from mark lutz

Mostwidgets can be accessed by simply accesiing it and .get or .set
Label requires textvariables, to access text variables use

###############################################################################
"""
import time
import sys
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.messagebox import showinfo
import itertools
import string #used for List Box 
from pprint import pprint
#~ from PIL import ImageTk, Image

from timstools import DPRINT,SCREAM, PDICT, ignored, next_highest_num
from PIL import Image as PImage	# AFTER USING TTK Image not working have to import as soething else...
from PIL import ImageTk

from defaults_gui import *
import defaults_gui
#~ from gui_newWorkbook import Gui_newWorkbook
#~ from gui_newPage import Gui_newPage	
						#http://askubuntu.com/questions/427358/install-pillow-for-python-3
BLANK = (ttk.Label,'','',defaults_gui.cfg_grid,defaults_gui.c_label) #empty tuple for custom form						

class FormBuilder:
	"""
	Returns values as one would expects, an interface for easier unpacking and len methods on results
	Used by custom form and toolbar
	
	First of all recognizes the need (or my lack of knowlegde on unpacking)
	So if it is a single row will use that method to unpack, otherwise another method for multilple row items
	
	Encompasses two different build methods
	
	The coloum is always returned (so that multiple items in rows can be grided)
	
	"""
	def __init__(self,form):
		self.form = form
	
	def __iter__(self):
		for h,item in enumerate(self.form):
			if not isinstance(item[0] ,tuple):	#singles
				#~ print('SINGLES')
				try:								#first way
					for name, action, where, config in ([item]): 			#not sure why its not unpacking item properly.. have to put it in a list wf			
						yield(h,0,name, action, where, config)
				except ValueError as e:				#second way
					if not 'too many' in str(e): 
						raise e	
					for funct,text,dict_name,where,config in ([item]):											
						yield(h,0,funct,text,dict_name,where,config)
			elif isinstance(item[0] ,tuple):	#Multi
				#~ print('MULTI')
				for j,*sub_items in enumerate(item):				#going over sub items
					try:								#first way
						for name, action, where, config in sub_items:
							yield(h,j,name, action, where, config)
					except ValueError as e:				#second way
						if not 'too many' in str(e): 
							raise e	
						for funct,text,dict_name,where,config in sub_items:
							#~ SCREAM('second')
							yield(h,j,funct,text,dict_name,where,config)
	
	#~ def try_types(self):
		#~ try:
			#~ 
		#~ except ValueError as e:	
			#~ if not 'too many' in str(e): 
				#~ raise e	
	#~ def __first_way(self):
		#~ _toolbar_form_evaluate
	#~ def __second_way(self):
	
class GuiApi():							#mixin class, ideally i would attach these to the widgets  created from guimaker
	
	def update_image(self, widget, imgname):	#TBD need to change photoobjs to a dict and then delete the old values
		imgobj = PImage.open(self.imgdir + imgname)
		imgobj = ImageTk.PhotoImage(imgobj)
		widget.config(image=imgobj)
		self.toolPhotoObjs.append(imgobj) # keep a reference or garbage collected
	
			
class GuiMaker(tk.Frame,GuiApi):
	"""
	self.variables = {}		# Tkinter text Variables
	self.widget_ref = {}	# windows creatd from button calls saved in here
	self.formRef= {}		# custom form refernces saved in here
	self.tbarRef ={}		# toolbar button references saved here 
	"""
	menuBar= []		
	toolBar= []		# set these in start()
	customForm =[]
	tbarframe = [({'side':tk.BOTTOM,'fill':tk.X},c_frame)]	
	helpButton = False		#set to true to default to a help button on all windows
	style=None				#default frame style	#Note here this is actually config not style as using old frame not ttk
	customFormPack=None		#Custom Form Config Options
	conPack=None			#Pack Config Options
	customFormStyle=None

	def __init__(self, parent=None,app=None):	# app is assigned here to the gui_maker frame, so elements can call home
		"""
		tbarRef look like {'edit.png': [<tkinter.ttk.Button object at 0x7f885c4c3b70>, {'side': 'right'}]}
		"""
		tk.Frame.__init__(self, parent)
		self.app = app
		self.parent=parent
		self.start()		#for subclass: set menu/toolBar
		if self.style==None:self.config(**cfg_guimaker_frame)
		else:self.config(**self.style)
		#~ self.config(**c_book_frame)
		#~ DPRINT(self['style'])
		if self.conPack==None:self.pack(expand=1,fill='both')
		else:self.pack(**self.conPack)	#WIDGETS MUST NOW PACK THEMSELVES SAD
		self.variables = {}		# Tkinter text Variables
		self.widget_ref = {}	# windows creatd from button calls saved in here
		self.formRef= {}		# custom form refernces saved in here
		self.tbarRef ={}		# toolbar button references saved here 
		try:	#because this fails if i want to inbed this in a notebook or something
			self.makeMenuBar()	#done here: build menu bar
		except:
			pass
		if self.toolBar and  self.tbarframe:
			self.tool_bar_start() 	# build toolbar
		self.custom_form_start()
		self.makeWidgets()		#subclass this
		self.finish()		
	def makeMenuBar(self):
		"""
		make menu bar at the top (Tk8.0 menus below)
		expand=no, fill=x so same width on resize
		"""
		menubar = Frame(self, relief=tk.RAISED, bd=2)
		menubar.pack(side=tk.TOP, fill=tk.X)
		for (name, key, items) in self.menuBar:
			mbutton = Menubutton(menubar, text=name, underline=key)
			mbutton.pack(side='left')
			pulldown = Menu(mbutton)
			self.addMenuItems(pulldown, items)
			mbutton.config(menu=pulldown)
		if self.helpButton:
			Button(menubar, text 	=	'Help',	
			cursor					=	'gumby',
			relief					=	tk.FLAT,
			command					=	self.help).pack(side=tk.RIGHT)
	
	def varCheck(self,funct,thewidg,dict_name,text=None):	#Adds textvariables to widgets on creation from customform and toolbar
		if funct == tk.Entry or funct ==tk.Label or funct == ttk.Entry or funct==ttk.Label:
			tkvar=tk.StringVar()
			thewidg.config(textvariable=tkvar)
			if text != None or type(list):tkvar.set(text)
			self.variables.update({dict_name:tkvar})
			
		elif funct==tk.Radiobutton or funct==tk.Checkbutton or funct== ttk.Checkbutton or funct==ttk.Radiobutton:	
			tkvar=tk.IntVar()		
			#~ DPRINT([thewidg,text],'var update')
			thewidg.config(variable=tkvar)
			if text != None or type(list):tkvar.set(0)
			self.variables.update({dict_name:tkvar})
		#~ else:	## PRE CREATED CLASS METHOD
			#~ self.variables.update({dict_name:thewidg.variables{}})	
	def winRef(self,key_name,widget,parent,lowerparent=None,app=None):		
		"""
		Creates a widget and saves a reference to it in self.widget_ref
		This doesn't return any values
		Pass the key_name that will be used to reference the widget
		e.g as a callback command= lambda: self.winRef('my_win',Toplevel,root)
		e.g or here or use self.winRef('pid_tlev',Gui_pidSelector,root,gui_base.configBase)
		"""
		widr=self.widget_ref	#per instance dict, just making it easier to code XD	
		if widr.get(key_name):	#if exists
			if widr[key_name].toplevel == None:pass#let the program go on
			else:return True	# program still open
		if lowerparent==None and app==None:  
			widr[key_name]=widget(parent)
			#~ print('Simple widget(parent) - >  %s -- %s' % (widget,[parent]))
		elif lowerparent !=None:
			#~ DPRINT((widget,lowerparent,parent,app),'Complex Creation Toplevel(widget,lowerparent,parent,app) - widget(lowerparent(parent),app')
			widr[key_name]=widget(lowerparent(parent),app)
			widr[key_name].toplevel=widr[key_name].parent	#used for closing the toplevel and keeping track of the window, so only one at a time can be open
			widr[key_name].caller=self	#easy reference of the caller of the window
			widr[key_name].toplevel.protocol("WM_DELETE_WINDOW", lambda:self.onClose(key_name))
		elif lowerparent == None and app!=None:	#nested with reference to app, used by notebooks
			widr[key_name]=widget(parent,app)
	def winRefClose(self,instance):
		self.widget_ref[instance].toplevel.destroy()
		self.widget_ref[instance].toplevel=None			
	def gridRef(self,dictionary,widget,name):	# saves a reference to our widgets by grid name
		gridr=dictionary # passed in dict ?
		#~ dictionary[key_name]=widget # Tk root saved in the configbase class for toplevels
		
	def custom_form_start(self):	
		"""
		Classed items created can access home by self.caller
		
		If a class is passed in you can set the text option to a 
		function that will be called. useful with lambdas to pass in parameters
		and so on that are not avaliable at creation time
		"""	
		if self.customForm:	
			frm =ttk.Frame(self)									#new frame for the form which is Gridded
			self.custFrm = frm										#Need a reference for this in gui_editView
			if self.customFormPack==None:frm.pack(side=tk.TOP,expand=1,fill='both')
			else:frm.pack(**self.customFormPack)
			if self.customFormStyle==None:frm.config(**c_frame)
			else:frm.config(**self.customFormStyle)
			
			custom_form = FormBuilder(self.customForm)
			for h,j,*item in custom_form:
				if len(item) == 4: 		#toolbar method
					print('PASS ING, TOOLBAR FORM EVALUATE METHOD NO YET IMPLEMENTED FOR CUSTOM FORM')
					pass						#not yet implemented or TBD
					#~ self._toolbar_form_evaluate(*item,frm=holder[h],h=h,j=j)
				elif len(item) == 5:	#custom form method
					self._custom_form_evaluate(*item,frm=frm,h=h,j=j)
			
	def _custom_form_evaluate(self,funct,text,dict_name,where,config,frm,h,j,default_packager=True):
		"""
		called by make_custom_form, also called by maketoolbar
		This is method 2 used in form builder,
		input looks like :
		
		toolbar doesnt want to use grid packing so we augument it by changing default_package to false
		
		to make an image pass in the text parameter in a list
		"""
		#~ print('ROW', h, 'COL', j)
		if 'tkinter' in str(funct):							#if a tkinter object 
			if type(text)==list:							#for Buttons with photos
				#~ print('image button')
				imgobj = PImage.open(self.imgdir + text[0])	
				imgobj = ImageTk.PhotoImage(imgobj) 
				wid=funct(frm, image=imgobj, **config)
				self.toolPhotoObjs.append(imgobj) 			# keep a reference to image or garbage collected
			elif 'Frame' not in str(funct) and 'Separator' not in str(funct):
				#~ print('normal method' ,text)
				wid = funct(frm, text=text, **config)		#normal method 
			else:
				#~ print('using the frame and sep method')
				wid = funct(frm, **config)					#for frames and seperators with no text element
			if default_packager:
				wid.grid(row=h, column=j, **where)				#grid
			else:
				wid.pack(**where)								#pack
		elif 'tkinter' not in str(funct):					#If a class instance is passed in
			"""
			This method now works by making a frame, as the classed objects are pre packed. So
			The frame is grided, and the passed class object can be pack/grided
			"""
			subfrm=ttk.Frame(frm)
			if default_packager: 
				#~ print('gridding a class object')
				subfrm.grid(row=h,column=j,**where)
			else:
				#~ print('packing a class object')
				subfrm.pack(**where)	#for toolbar etc, when packing is desired
			if self.app== None:
				#~ print('app is none')
				wid = funct(subfrm)	
			else: 
				"""
				so for nested elements created by customform, if there is an app try and
				create it with an app otherwise it will fail and default back to normal, 
				i need to make it so only the ones i intend will fall into this otherwise 
				could get side effects sigh
				"""
				try:		 
					#~ print('creaing with app')
					wid = funct(subfrm,self.app) 
				except TypeError as e:
					if  '__init__()' in str(e):#wid should already be made by the if above... TBD check the statemetn above
						#~ print('had a fail')
						wid=funct(subfrm) 
					else: 
						raise e
			if text:									#pass in functions for setting etc
				print(text)
				text()
			wid.caller=self	#easier accessing of caller then using the self.app.fkds.fsd.	#hopefully doesnt clash with self.caller in winRef
		
		if dict_name and default_packager: 			#save widg reference, if default packager is true then toolbar is creating the files and we don't need the refernece here
				if type(text) != list:						#do not want a text property set for images
					self.varCheck(funct,wid,dict_name,text)
				self.formRef[dict_name]=wid
		elif not default_packager:							#toolbar will handle the referencing
			self.varCheck(funct,wid,dict_name,text)
			return dict_name,wid,where
	
	def addMenuItems(self, menu, items):
		for item in items:			# scan nested items list
			if item == 'separator': # string: add separatoR
				menu.add_separator({})
			elif type(item) == list:	# list: disabled item list
				for num in item:
					menu.entryconfig(num, state=DISABLED)
			elif type(item[2]) != list:
				menu.add_command(	label	= item[0],	# command:
									underline = item[1],# add command
									command	= item[2])	# cmd=callable
			else:
				pullover 	= Menu(menu)
				self.addMenuItems(pullover, item[2])	# sublist:
				menu.add_cascade(label= item[0],			# make submenu
							underline 	= item[1],			# add cascade
							menu		= pullover)
	
	#~ def save(self):
		#~ print('saving')
	def tool_bar_start(self):	
		"""		
		Makes Toolbars, Unlimited # packed how and where u Stipulate
			>>> self.tbarframe = [({'side':'left','fill':Y},c_frame)]
	
		Supports Button Images Using PILLOW
		Supports Two Methods of Building the Toolbars
		You can mix them! 
		
		1# Original Method is tried first, easier and faster creation,
			However it ONLY supports Buttons
		
			>>> self.toolBar = 
			[(['edit.png'], self.layoutEdit, {'side': RIGHT},c_toolBar_button)]	
			
		2# Same method as Custom Form, Requires a Dictionary containg the config options
	
			>>> (ttk.Label,'Title1','dictname',  {'sticky': 'nsew'},c_label)
			
			Do not use blanks here though as everyting is packed I THINK!
		
		"""
		holder=[]
		self.toolPhotoObjs=[]	#to keep reference to imgs, otherwise they will be garbage collected
		for (where,config) in self.tbarframe:	#Creates Frames, there is a default frame as well incase one isn't provided 
			toolbar=ttk.Frame(self,**config)
			toolbar.pack(**where)
			holder.append(toolbar)	
		
		toolbar=FormBuilder(self.toolBar)		#gives us an easy way to unpack
		for h,j,*item in toolbar:
			if len(item) == 4: 	#normal method
				self._toolbar_form_evaluate(*item,frm=holder[h],h=h,j=j)
			elif len(item) == 5:	#custom form method
				#~ frm=ttk.Frame(holder[h],**config)	#need to put it in a frame as custom form uses gridding
				#~ frm.pack(side='left')							#need to allow pack method!
				name,wid,where = self._custom_form_evaluate(*item,frm=holder[h],h=h,j=j,default_packager=False)	#creates it
				if type(name) == list:	#saving references 
					self.tbarRef[name[0]]=[wid,where]
				else:					#saving references 
					self.tbarRef[name]=[wid,where]	#the widg here is actuall
				
	def _toolbar_form_evaluate(self,name, action, where, config,frm,h,j):
		if type(name) == list:	#we have an img button
			imgobj = PImage.open(self.imgdir + name[0])
			#~ imgobj = imgobj.resize(self.imgsizes)	#dont resize here resize b4.
			imgobj = ImageTk.PhotoImage(imgobj)
			wid=ttk.Button(frm,command=action, image=imgobj, **config)
			wid.pack(**where)
			self.toolPhotoObjs.append(imgobj) # keep a reference or garbage collected
			self.tbarRef[name[0]]=[wid,where]
		else:
			wid=ttk.Button(frm, text=name, command=action, **config)
			wid.pack(**where)
			self.tbarRef[name]=[wid,where]
				
	def makeWidgets(self):
		"""
		make 'middle' part last, so menu/toolbar
		is always on top/bottom and clipped last;
		override this default, pack middle any side;
		for grid: grid middle part in a packed frame
		
		Designed to be changed in subclass
		"""
		return None
		name = Label(self,
				width=40, height=10,
				relief=SUNKEN, bg='white',
				text	= self.__class__.__name__,
				cursor = 'crosshair')
		name.pack(expand=1, fill='both', side=TOP)
	
	def help(self):
		"override me in subclass"
		showinfo('Help', 'Sorry, no help for ' + self.__class__.__name__)
	def start(self):
		"override me in subclass: set menu/toolbar with self"
		pass
	def finish(self):
		pass
class MakerRadioButton(tk.Frame):
	"""
	Set self.options like [()], tuple pair of text and value
	"""
	def __init__(self, parent=None):
		tk.Frame.__init__(self, parent)
		self.start()
		self.pack(expand=1, fill='both')                   # make me expandable
		
		self.makeWidgets()
	def start(self):
		pass
	def makeWidgets(self):
		v = tk.StringVar()
		for text,value in self.options:	
			b = Radiobutton(self, text=text, variable=v, value=value)
			b.pack(anchor=W)
		self.var = v
	#~ def handleEvent(self, event):						
			#~ result = self.var.get()                   	              	   
			#~ self.run_command(result)
			
class MakerScrolledList(tk.Frame):		# used for making sublclasses, adds start method 
	result=[]
	def __init__(self, parent=None):
		tk.Frame.__init__(self, parent,padx=3,pady=4,background='white',bd=1,relief=tk.SUNKEN)
		self.parent=parent
		self.start()								
		self.pack(expand=1, fill='both')          
		self.makeWidgets(self.options)
		
	def start(self):
		pass												#add a list for variable self.options 
	def handle_list(self):
		for index in self.listbox.curselection():           	 
			label = self.listbox.get(index)                   	
			self.result.append(label)
		self.run_command()                             	
														 
	def makeWidgets(self, options):
		sbar = tk.Scrollbar(self)
		list = tk.Listbox(self, selectmode='multiple',relief=tk.FLAT, bd=0,highlightthickness=0)
		sbar.config(command=list.yview)                    # xlink sbar and list
		list.config(yscrollcommand=sbar.set)               # move one moves other
		sbar.pack(side=tk.RIGHT, fill=tk.Y)                      # pack first=clip last
		list.pack(side='left', expand=1, fill='both')        # list clipped first
		pos = 0
		for label in options: 				          		# add to listbox
			list.insert(pos, label)                        # or insert(END,label)
			pos += 1                                       # or enumerate(options)
		#~ list.config(selectmode=SINGLE, setgrid=1)       # select,resize modes
		#~ list.bind('<Button-1>', self.handle_list)           # set event handler
		self.listbox = list
		self.listbox.bind('<Any-Key>', self.keyPressed) 	#first letter keyboard searching
		self.styleList()
	def styleList(self):
		for n,dot in enumerate((self.options)):
			if n%2 == 0:	#even
				self.listbox.itemconfig(n, bg='peachpuff2') 
	def run_command(self, selection):                       # redefine me lower
		print('You selected:', selection)
	def keyPressed(self,event):	#searches for a pressed key over the widget and brings it up
		#~ DPRINT('in')
		key=event.keysym
		if len(key)<=1:
			if key in string.ascii_lowercase:	#string is imported
				try:	## before we clear get the selected position if any
					start_n=int(self.listbox.curselection()[0])
				except IndexError:
					start_n=-1
				self.listbox.selection_clear(0, 'end')	## clear the selection.
				
				for n in range(start_n+1, len(self.options)):	## start from previous selection +1
					item=self.options[n]
					if item[0].lower()==key.lower():
						self.listbox.selection_set(first=n)
						self.listbox.see(self.listbox.curselection()[0])	#make it visible
						return
					else:	# has not found it so loop from top
						for n in range(len(self.options)):
							item=self.options[n]
							if item[0].lower()==key.lower():
								self.listbox.selection_set(first=n)
								self.listbox.see(self.listbox.curselection()[0])	#make it visible
								return 
	def updateList(self):	#this needs to be bound , or u could set it up on a call back or something anyway
		self.listbox.delete(0, 'end')
		self.start()
		for thing in self.options:
			self.listbox.insert('end', thing) 
		self.styleList()
class MakerOptionMenu(tk.Frame):	#Used for creating Option Menus
	"""
	Subclass and define a start method
	
	Required Options include:
	
	self.options		-	elements in the drop down menu
	
	Optional settings:
	
	self.butnOptions = {'width':25,'direction':'below'}		- config
	self.heading		s-	heading item for the list
	self.initialValue	-	a heading that lasts until selection change
	self.auto_list_update 	- set to false to stop updating list on click
		
	self.options can be either an iterable as well as a function
		
	To get results:
	use the self.var.get / set tkinter method
	or you can use:  def run_command(self, selection): 
	"""
	heading = None
	last_selected = ''	#internal value for decideding if the value had been updated or not
	auto_list_update = True
	frm_style = None
	conPack = None
	def start(self):
		pass	#redifine lower
	def __init__ (self, parent =None,app=None):
		tk.Frame.__init__(self,parent)
		#~ self.config(takefocus=True)
		self.app = app
		self.parent=parent
		self.start()
		if self.frm_style==None:self.config(**cfg_guimaker_frame)
		else:self.config(**self.frm_style)
		if not hasattr(self,'initialValue'):
			self.initialValue='Select a Key'
		if self.conPack==None:self.pack(expand=1,fill='both')
		else:
			self.pack(**self.conPack)
		self.create_entries()		#creates self.LIST
		self.make_widget(self.LIST)		
		self.finish()
	def finish(self):
		pass
	def make_widget(self,options):
		self.var=tk.StringVar()
		self.var.set(self.initialValue)
		if len(options)==0:options=['empty']
		self.wid=ttk.Menubutton(self,textvariable=self.var)
		if hasattr(self,'butnOptions'):self.wid.config(**self.butnOptions)
		self.wid.menu = tk.Menu(self.wid,tearoff=0)
		self.re_populate()
		self.last_selected = self.var.get()	#initalizing value
		self.wid.config(takefocus=True,menu=self.wid.menu)
		#~ self.wid.config(**self.butnConf)
		self.wid.pack(expand=1, fill='both')
		if self.auto_list_update:
			self.wid.bind('<Button-1>',lambda e:self.re_populate())
	def create_entries(self):
		if self.heading == None:				# no heading
			if type(self.options)==list:self.LIST=self.options			# static list
			else:self.LIST=self.options()								#function that changes
		else: 									# with heading
			if type(self.options)==list:self.LIST=self.options[:]		# static list	
			else: 	self.LIST=self.options()							#function that changes														
			self.LIST.insert(0,self.heading)					

	def run_command(self, selection):             		# redefine me lower
		pass
	
	def get_result(self,value):	#get result after change, this is default method done by polling the list
		if self.auto_list_update:
			self.re_populate()
		self.run_command(value)
		self.var.set(value)		#TBD ISSUE1 this needs to be uncommented on windows, but i think on linux not dbl check!
	
	def re_populate(self):	#http://stackoverflow.com/questions/19794069/tkinter-gui-update-choices-of-an-option-menu-depending-on-a-choice-from-another
		self.create_entries()	#recreates the self.LIST value
		#~ menu = self.wid['menu'] #menu
		menu = self.wid.menu #menu
		menu.delete(0, 'end')		#delete all						
		for string in self.LIST:	#recreate list
			menu.add_command(label=string, 
							command=lambda value=string:
								 self.get_result(value))
	def poll(self):	#tbd delete
		now = self.var.get()
		if now != self.last_selected:
			self.get_result(now)
			self.last_selected = now
		self.after(250, self.poll)
#http://wiki.tcl.tk/20057	# comment on here for mac removing tab visibility
class GuiNoteBook(GuiMaker):
	"""
	pass
	"""
	STYLE_WIDG = {'bg':TIMS_bg}
	headerText=None	#only will add a header if its changed
	tabText=[0,1,2,3,4,5,6,7,8,9,10]	#so no errors if no one sets a tab name
	widgSide=[tk.N,tk.N,tk.N,tk.N,tk.N,tk.N,tk.N,tk.N,tk.N,tk.N,tk.N]
	padding=[0,0,0,0,0,0,0,0,0,0,0]
	
	widgStyle=[STYLE_WIDG,STYLE_WIDG,STYLE_WIDG,STYLE_WIDG,STYLE_WIDG,STYLE_WIDG,STYLE_WIDG,STYLE_WIDG]	# you can also style widgets in class if thats easier
	nbPackConf=None
	nbStyle=None
	#~ def __init__(self,parent=None,app=None):
		#~ Frame.__init__(self, parent)
		#~ self.nB=ttk.Notebook(parent)	#nB for notebook as self is a frame that is defined after gui maker is run
		#~ self.nB.__init__()	#need to initialize the succer fuck that threw me up lol
		#~ GuiMaker.__init__(self,parent,app)
		
		#~ self.pack(expand=0)	#change frame (where label is) pack method
	def makeWidgets(self):
			if self.headerText!=None: ttk.Label(self,text=self.headerText).pack()	# adding label
			#~ self.current = 0
			#~ self._pages = {}	#either reference by here or the widg
			self.nB=ttk.Notebook(self)	#nB for notebook as self is a frame
			#~ self.nB.__init__(self)	#need to initialize the succer fuck that threw me up lol
			if self.nbPackConf==None:self.nB.pack(expand=1,fill='both')
			else: self.nB.pack(**self.nbPackConf)
			if self.nbStyle ==None:self.nB.configure(**c_notebook)
			else: self.nB.configure(**self.nbStyle)
			if self.widgList:
				for i,widg in enumerate(self.widgList): #list of widgets to be added to pages set in start
					#~ try:							# if we pass in a pre created widget made in self this will work otherwise a class which will fire in except
						#~ if widg.master == self.nB:				 # will not work if the notebook isn't the parent
							#~ self.nB.add(widg, text=tabText[i], padding='0.1i',sticky=widgSide[i])
						#~ print('success - try')
					#~ else:
						#~ self.nB.add(widg, text=i, padding='0.1i')
						#~ print('failed - try - widg parent didnt match the notebook this is an error')
					#~ except:	# window not created we were passed a class so lets winRef it up
					#~ if self.parent==self.nB: 
					self.winRef(i,widg,self.nB,None,self.app)
					self.nB.add(self.widget_ref[i],text=self.tabText[i], padding=self.padding[i],sticky=self.widgSide[i])
							
					if self.widgStyle[i]:	
						if type(self.widgStyle[i]) == dict:
							self.widget_ref[i].configure(**self.widgStyle[i])
						else:
							self.widget_ref[i].configure(*self.widgStyle[i])
					
	#~ def finish(self):


class GuiTreeWidget(GuiMaker):
	#http://stackoverflow.com/questions/3794268/command-for-click-on-tkinter-treeview-widget-items-python
	#http://stackoverflow.com/questions/16388380/how-to-prevent-ttk-treeview-item-from-opening-when-double-clicked
	headerText=False	#only will add a header if its changed
	selectedHierachy=[]		#hierachy saved here
	"""
	self.itemClicked = creates heirachy list of selected items, so far saves only text, then passes to run_command
	self.items is interesting lol explian
	for allowing selection of multiple items see the webpage above, second answer under brians about macs and multiple
	
	myBooks=[['b1',['p1','345','456','678'],['p2','3243','4324','2342']]]	# layour required
	"""
	def __init__(self,parent=None,app=None):
		GuiMaker.__init__(self,parent,app)
	
	def makeWidgets(self):
		frm=tk.Frame(self)	#cannot get it to work without this frame wtf, changeing frm to self in even just the label doesnt work, also tried playing with pack method and wtf
		frm.pack()
		self.headerText='take me home'
		if self.headerText: ttk.Label(frm,text=self.headerText).grid()
		self.tree = ttk.Treeview(self)
		self.tree.__init__(frm)
		self.id_ref = {}
		ysb = ttk.Scrollbar(frm, orient='vertical', command=self.tree.yview)
		xsb = ttk.Scrollbar(frm, orient='horizontal', command=self.tree.xview)
		self.tree.configure(yscroll=ysb.set, xscroll=xsb.set)
		self.tree.heading('#0', text='Path', anchor='w')
		if hasattr(self,'items'):self.add_roots('', self.items)	#only add if items have been added
		self.tree.grid(row=0, column=0)
		ysb.grid(row=0, column=1, sticky='ns')
		xsb.grid(row=1, column=0, sticky='ew')
		#~ self.grid()	
		self.tree.tag_bind('ttk', '<<TreeviewSelect>>', self.itemClicked)
	
	def add_roots(self,parent,items,skip=False):	#Skip will miss the item when its the first entry in a list as that is the name of the parent

		for item in items:
			if type(item) == str:
				if not skip:
					oid = self.tree.insert(parent,'end',text=item,open=False,tags=('ttk','aStr'),value='what')	
				else: skip=False 		# skip set back to false
			elif type(item) == list:	# if a gen or list re loop 
				oid = self.tree.insert(parent,'end',text=item[0],open=False,tags=('ttk','aList'))	#text set to first element in the list
				self.add_roots(oid,item,True)	
				
	def itemClicked(self,event):
		self.selectedHierachy=[]
		ID = self.tree.selection()
		#~ print(ID)
		text = self.tree.item(ID,'text')
		self.selectedHierachy.insert(0,text)
		while self.tree.parent(ID):		#Loop through adding text of parent onto list until we reach the parent
			pID=self.tree.parent(ID)
			pText=self.tree.item(pID,'text')	
			self.selectedHierachy.insert(0,pText)
			ID=pID
		#~ print(self.selectedHierachy)
		self.run_command()
	def run_command(self):
		pass
		 
class GuiPanedWindow(tk.Frame):
	sashInfo={}	#{where to find parent in form ref:index of sash,pos}
	style=None				#default frame style	#Note here this is actually config not style as using old frame not ttk
	conPack=None			#Pack Config Options
	def __init__(self, parent=None,app=None):	# app is assigned here to the gui_maker frame, so elements can call home
		tk.Frame.__init__(self, parent)
		self.app = app
		self.parent=parent
		self.formRef=[]
		#~ self.variables = {}	# Tkinter Variables
		#~ self.widget_ref = {} # windows creatd from button calls saved in here
		#~ self.formRef= {}	# custom form refernces saved in here
		self.start()		#for subclass: set menu/toolBar
		if self.style==None:self.config(**cfg_guimaker_frame)
		else:self.config(**self.style)
		#~ self.config(**c_book_frame)
		#~ DPRINT(self['style'])
		if self.conPack==None:self.pack(expand=1,fill='both')
		else:self.pack(**self.conPack)	#WIDGETS MUST NOW PACK THEMSELVES SAD
		#~ self.makeMenuBar()	#done here: build menu bar
		#~ self.makeToolBar() 	#done here: build toolbar
		self.makePanes()
		self.widgSpace=self.masterPane	#need this in all thingies for binding
	
	
	
	def eventMatch(self,event):
		print(event)
		copy_list = self.formRef[:] #MAKES A COPY SO DONT GET INFINTE LOOP ON ADDING TO LIST
		for i,frame in enumerate(copy_list):	# each item is a top level pane so yeah!!!
			for children in frame[0].winfo_children(): # another way would be to analyze the tkinter.result.and.splice.the.dots
				if children == event.widget:
					return self.formRef[i]
					
	def resizeWidgets(self,event,masterpane):
		widg,rowCount,tkVar,mo,MASTER = self.eventMatch(event)
		print(mo)	
		print()
		print(MASTER)
		
		#~ masterpane.panes()
		
	def makePanes(self):	# adds								
		if self.panesList:	
			self.holder=None
			self.itera=0
			#~ self.loopem(self.panesList)
			#~ self.masterPane=self.holder
			def loopem(self,listo, MASTER=self):
				if MASTER != self:
					MASTER == self.holder
				for sideo, UP_DOWN, children in listo:
					#~ print([self.itera,'these are the iterations over the loopem'])
					if self.holder == None: 	# what to do for parent window i.e first run through 
						mo = ttk.PanedWindow(MASTER, orient=UP_DOWN) # master is self i.e frame
						mo.pack(side=sideo, **self.pane_pack_options)
						mo.configure(**self.pane_config)
						#~ mo.config(height=defaults_gui.wgdp_Height)						
						#~ widg,rowCount,tkVar=self.mkWidg(mo,self.itera)	
						#~ mo.add(widg)
						self.holder=mo						
					else:
						#~ if self.itera != len(self.panesList):
						mo = ttk.PanedWindow(MASTER, orient=UP_DOWN)
						MASTER.add(mo)
						mo.bind('<B1-Motion>',lambda event,mo=mo: self.onSashMove(event,mo))
						#~ mo.bind('<Configure>',lambda event: self.resizeWidgets(event,self.masterPane))
						widg,rowCount,tkVar=self.mkWidg(mo,self.itera)		#widg is the frame
						mo.add(widg)
						mo.configure(**self.pane_config)
						#~ mo.pack(**self.pane_pack_options)
						self.formRef.append([widg,rowCount,tkVar,mo,MASTER])	#this will save reference to the frame widget
						self.itera += 1
					if children != None:	#reloop through the children
						loopem(self,children,MASTER=mo)
			#~ if panesList==None:panesList=self.panesList	# sets up the default pane list.
			loopem(self,self.panesList)
			self.masterPane=self.holder
			self.masterPane.bind('<B1-Motion>',lambda event: self.onSashMove(event,self.masterPane))	
			#~ self.masterPane.bind('<Configure>',lambda event: self.resizeWidgets(event,self.masterPane))
			#~ for pane in self.masterPane.panes():
				#~ self.masterPane.paneconfigure(pane,{'sticky':'nsew'})
				
###############################################################################
# Customize for Tk 8.0 main window menu bar, instead of a frame
###############################################################################

GuiMakerFrameMenu = GuiMaker	# use this for embedded component menus
class GuiMakerWindowMenu(GuiMaker):# use this for top-level window menus
	def makeMenuBar(self):
		if self.menuBar != []:
			#~ print('zz')
			menubar = tk.Menu(self.master, tearoff=0)
			#~ print('TBD STUCK HERE WTF')
			self.master.config(menu=menubar)
			
			for (name, key, items) in self.menuBar:
				
				pulldown = tk.Menu(menubar, tearoff=0)
				self.addMenuItems(pulldown, items)
				menubar.add_cascade(label=name, underline=key, menu=pulldown)
				
			if self.helpButton:
				if sys.platform[:3] == 'win':
					menubar.add_command(label='Help', command=self.help)
				else:
					pulldown = tk.Menu(menubar) # Linux needs real pull down
					pulldown.add_command(label='About', command=self.help)
					menubar.add_cascade(label='Help', menu=pulldown)
				
###############################################################################
# Self-test when file run standalone: 'python guimaker.py'
###############################################################################
if __name__ == '__main__':
	from guimixin import GuiMixin	# mix in a help method
	#~ from defaults_gui import *
	root = tk.Tk()
	loadStyle(root)
	#~ import tkinter.ttk as ttk

	menuBar = [
			('File', 0,
				[('Open', 0, lambda:0),	# lambda:0 is a no-op
				('Quit', 0, sys.exit)]),	# use sys, no self here
			('Edit', 0,
				[('Cut',0, lambda:0),
				('Paste', 0, lambda:0)]) ]
	
	
	
	toolBar = [
			(('edit.png', sys.exit, {'side': tk.RIGHT},c_button),('Quit4', sys.exit, {'side': tk.RIGHT},c_button))]
	tbarframe = [({'side':tk.BOTTOM,'fill':tk.X},c_label)]
	
	
	#~ tbarframe = [({'side':RIGHT,'fill':Y},{'cursor':'hand2','relief':SUNKEN, 'bd':10}),
				#~ ({'side':TOP,'fill':X},{'cursor':'hand2','relief':SUNKEN, 'bd':10}),
				#~ ({'side':BOTTOM,'fill':X},{'cursor':'hand2','relief':SUNKEN, 'bd':10})]
	#~ toolBar = [	(Button,['edit.png'], lambda:self.save(), {'side': 'left'},{'width':15,'bd':15,'relief':SUNKEN}),
			#~ (Button,'Quit2', sys.exit, {'side': 'left'},{'width':15,'bd':15,'relief':SUNKEN}),
			#~ ((Button,'Quit3', sys.exit, {'side': RIGHT},{'width':15,'bd':15,'relief':SUNKEN}),(Button,'Quit4', sys.exit, {'side': RIGHT},{'width':15,'bd':15,'relief':SUNKEN}))]

	
	customForm = [(ttk.Label,'Title1','dictname',  {'sticky': 'nsew'},c_label),
			(ttk.Button, 'BUTTON2','dictname',  {'sticky': tk.W,'columnspan':1},c_button),
			((ttk.Radiobutton, 'what c3','dictname', {'sticky': 'nsew'},c_radio),(ttk.Label, 'hi4','dictname',{'sticky': 'nsew'}, c_label))]
	
	
	class TestAppFrameMenu(GuiMixin, GuiMakerFrameMenu):
		def start(self):
			self.menuBar = menuBar
			#~ self.toolBar = toolBar
	class TestAppWindowMenu(GuiMixin, GuiMakerWindowMenu):
		def start(self):
			#~ self.menuBar = menuBar
			#~ self.menuBar=menuBar
			self.num_Toolbars =2
			self.imgdir=''
			self.tbarframe= tbarframe
			self.toolBar = toolBar
			self.customForm	= customForm #Use Default
	class TestAppWindowMenuBasic(GuiMakerWindowMenu):
		def start(self):
			self.menuBar = menuBar
			#~ self.toolBar = toolBar	# guimaker help, not guimixin
	class TimsTest(GuiMakerWindowMenu):
		def start(self):
			self.imgdir=''
			self.menuBar = menuBar
			#~ self.num_Toolbars = 3	# not needed anymor
			self.customForm	= customForm #Use Default
			self.toolBar = toolBar
	class tabbedWidget(GuiNoteBook):
		helpButton = False
		def start(self):
			#~ a=ttk.Frame(self.nB)
			#~ a.pack()
			#~ b=ttk.Frame(self.nB)
			#~ b.pack()
			#~ ttk.Label(a, text='FFS MATE').pack()
			#~ ttk.Label(b, text='if you say so').pack()
			self.headerText='thi sis header lol nice'
			#~ import gui_newPage
			#~ import gui_newWorkbook
			x=gui_newPage.Gui_newPage(self.nB)		#need to import these for the test
			y=gui_newWorkbook.Gui_newWorkbook(self.nB)
			x.pack()
			y.pack()
			self.widgList=[x,y]
	
	class treetest(GuiTreeWidget):
		def start(self):
			myBooks=getFilesOnSysList('books','syslis') # all books on sys, all books
			copy_list=myBooks[:]	
			for i,book in enumerate(copy_list):
				pageList= [value for key,value in dbtools.loadAll('spew',book)]	#pagelist for each book
				#~ DPRINT([i,pageList],'pageslitssfs')
				if len(pageList) < 0 :	#if any of these guys have children
					pageList.insert(0,pageList[0])
					myBooks.insert(i,pageList)
			
			myPages=[x for x in dbtools.loadAll('list',myBooks)]	#now get all pages

			myBooks.insert(0,'Books')#insert name at beginning of book
			myPages.insert(0, 'Pages')
			#~ myHotkeys=dbtools.loadAll('Hotkeys','syslis')
			self.items=[myBooks,myPages]

	###TestAppFrameMenu(Toplevel())	NOT WORKING
	#~ TestAppWindowMenuBasic(Toplevel())
	#~ TestAppWindowMenu(root).pack()
	#~ TimsTest(root)	#18.6.14 TES
	#~ root.pack()
	
	#~ radio=MakerRadioButton(root)
	
	#~ test=tabbedWidget(root)	#14.6.24 this was active, not sure what i was trying to test, doesnt work anyway
	
	class option_menu_test(MakerOptionMenu):
		def start(self):
			self.use_polling = True
			self.options = [1,2,3,4]
		def run_command(self,value):
			print(value)	
	x = option_menu_test(root)
	
	
	root.mainloop()
	
	#~ from defaults_gui import cfg_gui, pane_pack
	#~ v=tk.VERTICAL
	#~ h=tk.HORIZONTAL
	#~ l=tk.LEFT
	#~ r=tk.RIGHT
	#~ t=tk.TOP
	#~ b=tk.BOTTOM	
	#~ 
	#~ class hotkey(GuiPanedWindow):
		#~ def start(self):
			#~ self.pane_pack_options=pane_pack #from defaults
			#~ ##~ self.panesList=[(l,h,None),(l,v,pane_pack,None)]
			#~ self.panesList=[(l,v,[(l,v,[(r,v,None)])])]


	