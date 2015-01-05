from collections import OrderedDict
import contextlib
import json 
import os
import threading
import time
from functools import wraps

import pysftp

def tkinter_breaker(func):
	"""
	decorator to stop tkinter propagtion default bindings,
	tkinter clinds a ladder of bindings, see http://effbot.org/tkinterbook/tkinter-events-and-bindings.htm
	problem is if the user holds ctrl and presses i it will propgate up
	so i added kills for the higher levels, 
	"""
	#tbd, finish climb to higher levels,mmm probably just kill normally without decorator
	@wraps(func)
	def oncall(*args):
		func(*args)
		return "break"
	return oncall


def universal_setup(): #lost this sigh have to remake
	pass
	
def easy_put(srv,file):
	'''
	sets config for uploading files with pysftp
	'''
	channel = srv.sftp_client.get_channel()
	channel.lock.acquire()
	channel.out_window_size += os.stat(file).st_size *1.1	# bit more bytes incase packet loss
	channel.out_buffer_cv.notifyAll()
	channel.lock.release()
	srv.put(file)

class InMemoryWriter():
	"""
	Used to defer saving and opening files to later controllers
	just write data to here
	"""
	def __init__(self):
		self.data=[]
	def write(self, stuff):
		self.data.append(stuff)
	def writelines(self, passed_data):
		for item in passed_data:
			self.data.append(item)
	def close(self):
		self.strData=json.dumps(self.data)	#turned into str
class InMemoryReader():	#http://www.diveintopython3.net/iterators.html

	def __init__(self,data):
		self.data=data
	def __iter__(self):
		self.i=0
		return self
	def __next__(self):
		if self.i+1 > len(self.data):	
			 raise StopIteration  
		requested=self.data[self.i]
		self.i+=1
		return requested
			
	def close(self):
		print('in reader close method')
		#~ self.strData=json.dumps(self.data)	#turned into str

@contextlib.contextmanager
def ignored(*exceptions,details=None):
	try:
		yield
	except exceptions as e:
		
		if details and details in str(e):	#skip what was wanting to be skipped
			pass
		elif details:		#if details not in str but details passed in raise
			raise e

def SCREAM(message,note=None,header='$(#)@$() ---SCREAMMM ----!!!!!'):
	"""
	NICE VISABLE MESSAGE FOR DEBUGGING SCREAMMM RAWR
	DO YOU SEE ME KNOW!!!
	"""
	print()
	print('!@#$%^&*()!@#$%^&*(!@#$%^&*-----')
	print()
	if note != None:
		#~ message =[message,'---->',note]
		header =[header,'-->  ', note]
	print(header)
	print(message)
	print()
	print('!@#$%^&*()!@#$%^&*(!@#$%^&*-----')
	print('ENDING THE SCREAM-- IT ALL goes silent now..')
	print()

def DPRINT(message,note=None,header='--------- Debug Below----------'):
	#~ return					# USED FOR NOT PRINTING XD
	"""
	Debug Print, easier to see XD
	"""
	#~ for i in flattenUntil(message,list):
		#~ print('LIST')
		#~ print(i)
	print()
	if note != None:
		#~ message =[message,'---->',note]
		header =[header,'-->  ', note]
	print(header)
	print(message)
	print()

@staticmethod
def PDICT(objD,comparison=None):	#object Dictionary, Prints each key value on a line
	print('----------Start of Dict-----------')
	if type(objD)!=dict:objD=objD.__dict__
	if comparison==None:
		if type(objD)==dict:	
			sortedObj = OrderedDict(sorted(objD.items()))
			for key, value in sortedObj.items():
				print([key,'  ---> 	',value])
	elif type(objD)==dict:	#comparison dict method		### TBD
		sortedObj = OrderedDict(sorted(objD.items()))
		sortedObj2 = OrderedDict(sorted(comparison.items()))
		
		for key,key2 in zip(sortedObj.keys(),sortedObj2.keys()):
			#~ print(key,key2)
			if not sortedObj.get(key2):
				print('First Object: Doesnt contain key :  '+key2+'        from Second Object')
			#~ if not sortedObj2.get(key):
				#~ print(str(comparison)+': Doesnt contain key:'+key+'from :'+str(objD))
	print('----------end of dict----------')

def PTYPE(obj):	#TBD
	print('----------- Printing Types---------')
	for i in obj:
		print(type(obj))
		try:
			print(obj.__name__)#FAILS..
		except:
			pass
	print('-----------Fin Print Types -----------')

def PMETHODS(obj): #prints all methods
	print('-------Printing Methods---------------')
	a=[method for method in dir(obj) if callable(getattr(obj, method))]
	#~ print(a)
	for i in a:
		print(i)
	print('-------------methods fin--------------')
def only_numerics(seq):
    seq_type= type(seq)
    return seq_type().join(filter(seq_type.isdigit, seq))
  
def toggle(btn,tog=[0]):
	'''
	a list default argument has a fixed address
	'''
	tog[0] = not tog[0]
	if not tog[0]:
		return False
	else:
		return True

def TkErrorCatcher(func):	
	'''
	Used To catch errors through functions raised from the event loop
	in tkinter. 
	
	More for tool builders
	
	when i send in the orignal args to the rror handle its passing in self again
	found out if its a method function or a normal function then delete the old self
	http://stackoverflow.com/questions/19227724/check-if-a-function-uses-classmethod
	
	sigh in the end all you accomplish is changing a raised error into a function call
	
	just call the function directly... 
	
	this is only useful for handling errors that i didnt invoke
	
	for a wrapped function on_key_press required setup
	
	self.on_key_press.__dict__['on_error'] = {DuplicateKeyPressed: self.duplicate_err_handle} # Bound function methods have to be accessed like this...
	self.on_key_press.__dict__['exceptions'] = (DuplicateKeyPressed,)
	
	than from in on_key_press you can do
	raise DuplicateKeyPressed and it will be handled by self.duplicate_err_handle
	'''								
	def on_call(*args,**kwargs):
		on_error = on_call.on_error 			# rebinding names so its cleaner code below
		err_args = on_call.err_args 
		exceptions = on_call.exceptions
		err_kwargs = on_call.err_kwargs
		try:
			print('trying func now')
			func(*args, **kwargs)
		except exceptions as err:
			if type(on_error) == dict:				# Either on_error is a dict mapping exceptions to handlers or a generic function
				print('dict')
				if err.__class__ in on_error:
					key = err.__class__
					print('using error type as key')
				else:
					key = 'default'
				if not err_args:				# Don't pass arguments in to recieve the original function arguments
					print('setting args')
					err_args = {key: args}
				if not err_kwargs:
					err_kwargs = {key: kwargs}
				print('running : %s' % (on_error[key]))
				print(len(err_args[key]))
				print()
				print(err_kwargs[key])
				on_error[key](*err_args[key],**err_kwargs[key])
			else:
				print('type on error not dict')					
				print(type(on_error))					
				if not err_args:				# Don't pass arguments in to recieve the original function arguments
					err_args =  args
					print('passing default args')
				if not err_kwargs:
					err_kwargs = kwargs
				print('running : %s' % (on_error))
				on_error(*err_args, **err_kwargs)
		else:
			pass
		finally:
			pass	
	on_call.on_error = lambda *args, **kwargs: 0					# Bound method variables
	on_call.err_args = ()
	on_call.exceptions = Exception
	on_call.err_kwargs = {}
	return on_call


class TimedOut(Exception):
	pass
class MaxInput(Exception):
	pass
class FirstInput(Exception):
	pass
def event_clock(event,timevar,timemax,entries=None,maxentries=None):	
	'''
	returns False when time between events is greater then time specified
	returns False when entries is equal to the max entries
	timevar is a list that has the time of the event/events
	'''
	timevar.append(event.time)	#at least two time variables
	if len(timevar) > 1:		
		if timevar[-1]-timevar[-2] >= timemax:	# time to exit
			raise TimedOut('maximum time beweent input exceeded :  %d seconds' % (timemax *0.001))
		elif len(entries) == maxentries:		# Also time to exit
			raise MaxInput('maximum input exceeded : %s' % maxentries)
	#~ else:
		#~ raise FirstInput
def ttk_manual(style, widgets):
	@TraceCalls()
	def iseven(n):
		yield True if n == 0 else isodd(n - 1)
	@TraceCalls()
	def isodd(n):
		yield False if n == 0 else iseven(n - 1)
	print(list(iseven(7)))
	s = style
	if type(widgets) not in (list,tuple):
		widgets = [widgets]

	#~ return
	
	for item in widgets:	# widgets is the passed in items e.g TButton, TLabel etc
		#~ print(list(flatten(s.layout(item))))	
		print(flatten(s.layout(item)))
		#~ holder = []
		#~ for i in flatten(s.layout(item)):
			#~ holder.append(i)
		#~ print()
		#~ print(holder)
		return
	
		print('Layout of Elements: %s -s.layout()'%(item))
		print()
		layout = s.layout(item)
		print(layout[0])
		print()
		print(layout[0][0])
		print()
		print(layout[0][0])
		print()
		print(layout[0][1].keys())
		print()
		#~ print(layout[0][1].keys())
		print()
		for key,value in layout[0][1].items():
			print(key)
			print(	value)
		#~ print(layout[1][0])
		print()
		#~ print(layout[0][01])
			#~ print('printint')
			#~ print(layout)
			#~ print()
		#~ print(s.layout(item))
		
def error_to_bool(func,*args):
	#~ print(args)
	try:
		func(*args)
		#~ print('t')
		return True
	except:
		#~ print('false')
		return False

basestring = (str,bytes)
#~ typestruct = (type(list),type(dict),type(tuple))
import sys
from functools import wraps
class TraceCalls(object):
    """ Use as a decorator on functions that should be traced. Several
        functions can be decorated - they will all be indented according
        to their call depth.
    """
    def __init__(self, stream=sys.stdout, indent_step=2, show_ret=False):
        self.stream = stream
        self.indent_step = indent_step
        self.show_ret = show_ret

        # This is a class attribute since we want to share the indentation
        # level between different traced functions, in case they call
        # each other.
        TraceCalls.cur_indent = 0

    def __call__(self, fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            indent = ' ' * TraceCalls.cur_indent
            argstr = ', '.join(
                [repr(a) for a in args] +
                ["%s=%s" % (a, repr(b)) for a, b in kwargs.items()])
            self.stream.write('%s%s(%s)\n' % (indent, fn.__name__, argstr))

            TraceCalls.cur_indent += self.indent_step
            ret = fn(*args, **kwargs)
            TraceCalls.cur_indent -= self.indent_step

            if self.show_ret:
                self.stream.write('%s--> %s\n' % (indent, ret))
            return ret
        return wrapper
@TraceCalls()
def flatten(l, typestruct=(list,tuple),global_count=''):
	def track(global_count,count):
		return
		global_count = global_count.split(',')
		try:
			current = int(global_count[-1])
		except ValueError:	#errors out on first level
			current = int(global_count[0])
		new = current + count
		global_count.append(str(new))
		global_count = ','.join(global_count)
		string = 'Global: '+global_count+' current: '+str(current)+' new: '+str(new)
		return string
		print(string)
	if global_count:
		#each level is seperated by a comma with deeper levels being on the right
		global_count = global_count + '.0'
		current = 0
	else:
		global_count = '0,'
	
	for i, el in enumerate(l):
		if isinstance(el, typestruct) and not isinstance(el, basestring):
			for j, sub in enumerate(flatten(el)):
				#~ print('USING RECURSION ELEMENT')
				print('Element:',sub,'	:',track(global_count,j))
				return sub
		
		elif isinstance(el,dict) and not isinstance(el, basestring):
			for j, (key, value) in enumerate(el.items()):
				print('dict key:',key,'	:',track(global_count,j))
				return key
				if isinstance(value, typestruct) and not isinstance(value, basestring):
					for k, sub in enumerate(flatten(value)):
						#~ print('USING RECURSION ELEMENT')
						print('dict value:',sub,'	:',track(global_count,k))
						return sub
				else:
					print('dict value:',value,'	:',track(global_count,j))
					return value
			
		else:
			print('top level el I:',el,'	:',track(global_count,i))
			return el

			
def flattenUntil(l,typestruct=(list,dict,tuple)):
	if isinstance(l, typestruct): #only return elements of typestruct dont go deepeter
		for el in l:
			if isinstance(el, typestruct):	#if the next element is a typestruct
				for subel in flattenUntil(el):
					if isinstance(subel,typestruct):
						yield subel
				yield el	
					

def traverse(item):
    try:
        for i in iter(item):
            for j in traverse(i):
                yield j
    except TypeError:
        yield item
        #~ 
def chain(*iterables):
    # chain('ABC', 'DEF') --> A B C D E F
    for it in iterables:
        for element in it:
            yield element		

def sysArgsDict(argv):
	opts = {}
	while argv:
		if argv[0][0] == '-':
			opts[argv[0]] = argv[1]
			argv = argv[2:]
		else:
			opts[argv[0]] = argv[0]
			argv = argv[1:]
	return opts

def inIf(items,Check):
	for i in items:
		if i in check:
			yield i
		else:
			yield False


def unique_int(values):
	'''
	if a list looks like 3,6
	if repeatedly called will return 1,2,4,5,7,8
	'''
	last = 0
	for num in values:	#generate a unique number
		if last not in values:	#num is  uniquie (will return numbers if the list has skips so p1 p2 p5,
			#~ print('checking if last not in
			break
		else:				#number already exists
			last += 1
	return last				#looped till end, then it was plussed so just return new value

def next_highest_num(values):
	'''
	The next highest number will be returned
	if a list looks like 2,3,19
	will return 20,21,22 on succesive calls
	'''

	if not values:
		return 0
		
	for last_num in reversed(sorted(values)):
		return last_num + 1

				

def rate_limited(max_per_second, mode='wait'):
	"""
	Decorator that make functions not be called faster than
	
	set mode to kill to just ignore requests that are faster than the 
	rate.
	"""
	lock = threading.Lock()
	min_interval = 1.0 / float(max_per_second)

	def decorate(func):
		last_time_called = [0.0]

		@wraps(func)
		def rate_limited_function(*args, **kwargs):
			lock.acquire()
			
			elapsed = time.clock() - last_time_called[0]
			left_to_wait = min_interval - elapsed
		
			if not last_time_called[0] or elapsed > min_interval:	# Allows the first interval to not have to wait
				pass
			
			elif left_to_wait > 0:
				if mode == 'wait':
					time.sleep(left_to_wait)
				elif mode == 'kill':
					lock.release()
					return
					
			lock.release()

			ret = func(*args, **kwargs)
			last_time_called[0] = time.clock()
			return ret

		return rate_limited_function

	return decorate
	
@rate_limited(2, mode='wait') # 2 per second at most
def print_num_wait(num):
	print (num )

@rate_limited(2, mode='kill') # 2 per second at most
def print_num_kill(num):
	print(num)
	
if __name__ == "__main__":
	print("Mode is Kill")
	print("100 print requests sent to decorated function")
	for i in range(1,100):
		print_num_kill(i) 
	
	print("sleeping for 1 seconds")
	time.sleep(1)
	print_num_kill(9999)
	
	print()
	print('Mode is Wait - default')
	print("100 print requests sent to decorated function")
	for i in range(1,100):
		print_num_wait(i) 
	print('fin')
