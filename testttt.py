import tkinter as tk
import tkinter.ttk as ttk
import time
from pprint import pprint

from tkquick.gui import batteries
from tkquick.gui.style_defaults import *

class a(batteries.HotKeyGrabberMaker):pass
class b(batteries.HotKeyGrabberMaker):pass
class c(batteries.HotKeyGrabberMaker):pass

root = tk.Tk()
loadStyle(root)
a1 = batteries.HotKeyGrabberMaker(root)
#~ a1.set(['ass'])
b2 = batteries.HotKeyGrabberMaker(root)
#~ b2.set(['ass2'])
a2 = a(root)
#~ a2.set(['ass2'])
b2 = b(root)
#~ b2.set(['ass2'])
b3 = b(root)
#~ b3.set(['ass2'])
root.mainloop()
