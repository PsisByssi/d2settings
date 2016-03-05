import tkinter as tk
from tkinter import messagebox
import sys
import os
import shutil
import logging

from tkquick.gui.tools import rate_limited
import tkquick.gui.style_defaults as style_defaults
import tkquick.gui.maker as maker
from timstools import InMemoryWriter
from timstools import ignored as suppress
import peasoup
import esky

import gui_d2settings
import d2_func
#TBD IN setup.py wit cxfreeze can i del the manifest shit?
APP_NAME = 'd2settings'
GENERAL_CFG_FILE = 'flags.cfg'                          
LOG_FILE = 'lastrun.log'

LOG_UPDATER_USERNAME = 'log_updater'
LOG_UPDATER_PASSWORD = 'updateing1!Hthefriggenlogs'
LOG_UPDATER_HOST = 'ftp.dynamicnotetaking.com'
LOG_UPDATER_PORT = 2222

class MyAppBuilder(peasoup.AppBuilder):
    # THIS IS MIRROERED FROM UNCRUMPLED SO
    def uac_bypass(self, *args, **kwargs):
        result = peasoup.AppBuilder.uac_bypass(self, *args, **kwargs)
        return self.esky_patherize(result)

    def esky_patherize(self, path_and_file):   #TBD I THINK ESKY HAS A FUNC THAT DOES THIS
        '''Don't want to get cfg files etc rewritten on new app updates!
        This moves our data file paths into the proper place
        when i find where to put data files on posix i have to change this TBD
        this runs only on portably installed stuff'''
        if not self.is_installed() and hasattr(sys, 'frozen'):
            # the esky appdata holds new releases and so on our program resides in a subfolder here
            # we dump our data files and cfg files here when operating in a non installed mode
            appdata_path = os.path.join(esky.util.appdir_from_executable(sys.executable), 'data^-^')
            self.appdata_path = appdata_path # Todo make this whole api better.
            os.makedirs(appdata_path, exist_ok=True)
            file = path_and_file.split(os.sep)[-1]
            return os.path.join(appdata_path, file)
        else:
            path = os.path.join(os.path.dirname(__file__), 'data^-^')
            self.appdata_path = path
            os.makedirs(path, exist_ok=True)
            return path_and_file

    @staticmethod
    def rel_path(*file_path):
        '''
        gives relative paths to files, works when frozen or unfrozen
        to get the root path just pass in the string __file__
        '''
        if hasattr(sys, 'frozen'):
            if file_path[0] == '__file__':
                return os.path.dirname(sys.executable)
            return os.path.join(os.path.dirname(sys.executable), *file_path)
        else:
            if file_path[0] == '__file__':
                return os.path.dirname(os.path.realpath(__file__))
            return os.path.join(os.path.dirname(__file__), *file_path)

    @staticmethod
    def __file__():
        '''
        the __file__ doesn't work when frozen, this works always
        '''
        if hasattr(sys, 'frozen'):
            return sys.executable
        else:
            return __file__

class MainApplication(MyAppBuilder):
    def __init__(self, args):
        super().__init__(args)
        # This initializes the appdata_path variable..
        self.esky_patherize(os.getcwd())

    def start(self):
        self.ab = peasoup.AppBuilder(self.__file__())

        self.DEVELOPING = DEVELOPING
        
        self.root = tk.Tk()
        maker.center_window(self.root, 1000, 800)
        self.root.withdraw()
        style_defaults.TIMS_bg = "#232327"
        style_defaults.TIMS_fg = "white"
        style_defaults.TIMS_fg_heading = '#e0e0e0'
        style_defaults.TIMS_bgButton = 'red'
        if self.ab.is_installed():
            self.ttk_style = style_defaults.loadStyle(self.root)
        else:
            path = self.rel_path('img', 'plastik')
            print(path)
            self.ttk_style = style_defaults.loadStyle(self.root, plastik_folder=path)
        # self.ttk_style.configure('TEntry', foreground='white', fieldbackground='#5a0b08', insertbackground='red')
        self.entry_cfg = {'bg':'#5a0b08','insertbackground':'white', 'fg':'white', 'width':'18'}
        self.ttk_style.configure('TButton', background ='red')
        self.ttk_style.configure('hotkeygrabber.TLabel',    foreground='white', 
                                                            background='#5a0b08',
                                                            relief='raised',
                                                            borderwidth=3,
                                                            justify='center')
        self.ttk_style.map('hotkeygrabber.TLabel', relief=[('focus','sunken'),('disabled','ridge')],
                                                    background=[('disabled','grey')],
                                                    foreground=[('disabled','maroon')])

        global GENERAL_CFG_FILE
        self.create_cfg(GENERAL_CFG_FILE)
        self.check_if_open()

        if self.first_run:
            self.first_time_setup()

        auto_exec_file, ahk_file = self.setup_exec_stuff()

        self.cfg_settings, bind_settings = d2_func.read_autoexec(auto_exec_file)
        ahk_settings = d2_func.read_ahk_file(ahk_file)
        self.auto_exec = InMemoryWriter(auto_exec_file)
        self.ahk_file = InMemoryWriter(ahk_file)
            
        self.main_gui = gui_d2settings.Gui_Main(self.root, self)
        self.main_gui.load_cfg(self.cfg_settings, bind_settings, ahk_settings)          # Load The Users Data into Gui                                  
        
        # if not DEVELOPING:
        #     self.splash = gui_d2settings.SplashScreen(self.root)
        #     self.splash.after(10000, self.splash.destroy)
        self.root.deiconify()
        self.root.mainloop()

    def first_time_setup(self):
        '''
        Tries to get the steampath, otherwise prompts the user for a path to save to
        '''
        toplevel = tk.Toplevel(self.root)
        self.root.after(1000, gui_d2settings.WelcomeMessage, toplevel, self)
        self.cfg['user_pref'] = {}
        d2_func.find_d2_path(self.cfg['user_pref'], self.appdata_path)
        if not self.cfg['user_pref'].get('steam_path'):
            messagebox.showinfo('Steam folder not found', 'Unable To find the steam folder, please navigate to the steam folder!') #tbd make the documentation match this folder
            self.root.wait_window(gui_d2settings.UserPreferences(toplevel,self))
        self.cfg.save()

    def setup_exec_stuff(self):
        # if new user and an exiting tims config ask about using or making a new one
        # if a normal existing conig just tell them it is getting renamed
        # if old user just load tims config. if anything is funny allow for usage
        # TODO and prompt for settings before saving fuck
        if DEVELOPING:
            dota_folder = self.rel_path('__file__')
            auto_exec_file = 'autoexec.cfg'
            ahk_file = 'dota_binds.ahk'
        else:
            dota_folder = os.path.join(self.cfg['user_pref']['steam_path'],
                                       'steamapps', 'common', 'dota 2 beta', 'game', 'dota', 'cfg')
            auto_exec_file = os.path.join(dota_folder, 'autoexec.cfg')
            ahk_file = os.path.join(dota_folder, 'dota_binds.ahk')
        logging.info('source : %s' % auto_exec_file)
        logging.info('source : %s' % ahk_file)

        def d2settings_exec_header():
            with open(auto_exec_file, 'r') as opened_exec:
                opened_exec.readline()
                header = opened_exec.readline()
                if 'Tims Dota Config' in header:
                    return True
                else:
                    return False

        inst_args = (dota_folder, auto_exec_file, ahk_file, self.rel_path('__file__'))
        if self.first_run:
            if not os.path.isfile(auto_exec_file):
                d2_func.install_requirements(*inst_args,
                                            overwrite=False)
            else:
                if d2settings_exec_header():
                    use_existing = messagebox.askyesno('Existing D2settings autoexec.cfg file found',
'An existing d2settings autoexec cfg file was found, would you like to use it? \
 Clicking no will create a new one with defaults and rename the old one',
                                                    parent=self.root)
                    if not use_existing:
                        # backup an existing d2setting execfile on first run
                        self.backup_existing(dota_folder, auto_exec_file, ahk_file)
                        d2_func.install_requirements(*inst_args,
                                                    overwrite=False)
                    else:
                        # Mainly as i move shit around while developing
                        d2_func.install_requirements(*inst_args,
                                                    overwrite=False)

                else:
                    # backup an existing Non d2setting execfile on first run
                    self.backup_existing(dota_folder, auto_exec_file, ahk_file)
                    messagebox.showinfo('backing up your old execfile', 'Your existing exec file has been renamed and moved into backup/')
                    d2_func.install_requirements(*inst_args,
                                                overwrite=False)
        else:
            if not d2settings_exec_header():
                if os.path.isfile(auto_exec_file):
                    do = messagebox.askyesnocancel('The d2settings exec file is missing', 'The d2settings exec has been removed..\
\n Would you like to do a fresh install and overide any existing settings?\n \
Yes (overwrite), No (Install without overwrite), Cancel (do nothing)')
                    if do:
                        d2_func.install_requirements(*inst_args,
                                                    overwrite=True)
                    elif do == False:
                        d2_func.install_requirements(*inst_args,
                                                    overwrite=False)
                    elif do == None:
                        pass
                else:
                    messagebox.showerror('The d2settings exec file is missing', 'A non d2settings exec has been detected\n \
Back it up somewhere and remove it before using d2settings...')
                sys.exit()
            else:
                # Just a sanity check incase the user deleted some of our files..
                d2_func.install_requirements(*inst_args,
                                            overwrite=False)

        return auto_exec_file, ahk_file



    def backup_existing(self, dota_folder, auto_exec_file, ahk_file):
        '''
        Moves the execfile and ahk file and backs them up
        '''
        backup_file = os.path.join(dota_folder, 'backup', 'my_old_autoexec.cfg')
        num = 1
        try:
            os.makedirs(os.path.join(dota_folder, 'backup'))
        except FileExistsError:
            while 1:
                backup_file = os.path.join(dota_folder, 'backup', 'my_old_autoexec_{0}.cfg'.format(num))
                if os.path.isfile(backup_file):
                    num += 1
                else:
                    break
        peasoup.set_windows_permissions(auto_exec_file)
        shutil.move(auto_exec_file, backup_file)
        peasoup.set_windows_permissions(backup_file)
        backup_ahk = os.path.join(dota_folder, 'backup', 'my_old_ahk_{0}.ahk'.format(num))
        shutil.move(ahk_file, backup_ahk)
        peasoup.set_windows_permissions(backup_ahk)
        shutil.rmtree(os.path.join(dota_folder, 'hp'))


    @rate_limited(1/2, mode='kill')                     # Max one message every 2 seconds
    def send_ui_feedback(self, message, image=None):    # Show a message and or image to the user for confirmation or a message etc
        '''
        Pass in a message and an optional image
        image can be either a file or 1 or 0 for default
        confirm and fail image.
        '''
        print('in ui feedbck')
        if image == 1:
            image = 'thumbs_up.png'
        elif image == 0:
            image = 'thumbs_down.png'
        
        @rate_limited(1/6, mode='kill')
        def reset():
            # self.after is now restricted to clear the text once max per 6 seconds
            def after_reset():              
                label.set('')
                icon.config(image='')
            self.root.after(5000, after_reset)
        label   = self.main_gui.variables['status']
        label.set(message)
        #~ self.mainGui.tbarRef['status'][0].config(width='50')
        self.main_gui.tbarRef['status'][0].config(anchor='center')
        icon = self.main_gui.tbarRef['status_icon'][0]
        #~ icon.config(anchor='w') 
        #~ icon.config(width='30') 
        if image:
            self.main_gui.update_image(icon,image)              #tbd wtf? check this function, its a mixin but make this used as a class image more clear what is happening
        reset()                                                 #clear


    def update_application(self):
        updater_url = 'https://github.com/timeyyy/dota2-settings-tweaker/tree/gh-pages'
        if DEVELOPING:
            updater_url = 'http://localhost:8000/'
        logging.info('update url is: %s ' % updater_url)
        if hasattr(sys, "frozen"):
            froz_app = esky.Esky(sys.executable, updater_url)
            logging.info(
                "We are Frozen! - active version: %s" %
                froz_app.active_version)
            logging.info(
                'Root status is : %s' %
                ('yes' if froz_app.has_root() else 'No'))
            logging.info('Trying to get root')
            logging.info(froz_app.get_root())
            new_version = froz_app.find_update()
            logging.info('New version of our app -> {0}'.format(new_version))
            if DEVELOPING:
                self.root.after(1000, tk.messagebox.showinfo,'hi', 'version haha ' + froz_app.active_version)
            if new_version:
                logging.info('Starting auto update')
                froz_app.auto_update()
                logging.info('Starting reinitialize')
                froz_app.reinitialize()
                froz_app.drop_root()
                logging.info(
                    'Finished auto update starting clean up operations')
                # tbd thread safe here?
                if messagebox.askyesno(
                        'D2settings Updated!', 'A new version of D2settings has been installed\n Restart D2settings now?'):
                    self.tkinter_queue.put(self.restart)
                    self.tkinter_queue.put(self.root.quit)
            else:
                # TBD check if the version has already been run once fine
                # before cleaning up
                logging.info('No updates found')
                logging.info('Running cleanup of esky')
                froz_app.cleanup()
                logging.info('Running esky reinitialize')
                froz_app.reinitialize()

    
if __name__ == '__main__':
    DEVELOPING = False
    if len(sys.argv) == 2 and sys.argv[1] in ('developing', 'develop'):
        DEVELOPING = True
    if DEVELOPING:
        sys.setrecursionlimit(150)
        print('-- files will be read from cwd')
        print('-- files will be saved as xzy_saved.xyz')
        print('-- Splash screen will be hidden')

    app_framework_instance = MyAppBuilder(MyAppBuilder.__file__())
    LOG_FILE = peasoup.add_date(LOG_FILE)
    LOG_FILE = app_framework_instance.uac_bypass(LOG_FILE)
    peasoup.setup_logger(LOG_FILE)
    if not DEVELOPING:
        with suppress(Exception):
            raven_client = peasoup.setup_raven()
    logging.info('Developer status is: %s'% DEVELOPING)
    tk.CallWrapper = peasoup.gui.TkErrorCatcher
   
    try:
        main = MainApplication(MyAppBuilder.__file__())
        main.pcfg['log_file'] = LOG_FILE
        main.start()
    except Exception as err:
        main.logexception(logger=main.logger)
        restarter = peasoup.Restarter()
    finally:
        main.shutdown()
        sys.exit()

'''
auto attack off
a, will start autoattacking shit around,
s,h - dont attack shit, exact same...

auto attack on
s, cancels attak but he will attack again and move
h, will attack again in range

if jukeing both will urn to spot before waiting next command, to get a hit off in trees u have to use a click on ground

special
hold turns auto attack on, u can acheive auto attacko on with movemnt by auto attack ground

autoattack fails becaks it always defaults to most closest unit, when chasing and u want to attack just use a click on ground, dont use stop..
you should rarley be using hold it is for lazy people
'''
