'''
code file: blinkit.py
date: April 2023
comments:
    Gui to play Blink videos
    that have been loaded
    onto a local computer
Using:
    First argument must be path to the FOLDER
    THAT CONTAINS the "blink" folder from the USB drive.
    This folder should contain ONLY the "blink" folder.
    Program uses "SMPlayer" (Linux)

Timezones:
0 US/Eastern
1 US/Central
2 US/Mountain
3 US/Pacific
4 US/Alaska
5 US/Hawaii

command takes 2 arguments - Example:
  python blinkit.py Documents/BlinkStuff 2
blink folder is in Documents/BlinkStuff
timezone is Mountain (nbr 2)

Note:
    Not all countries observe Daylight Saving time
    and some apply it in a different way. Additionally, the dates when
    Daylight Saving time begins and ends may vary from country to country.
    This program, as it currently stands, does assume the US timezone behaviors
    with regard to Daylight Savings and Standard time.
'''
import pytz
import os
import sys
import subprocess
from tkinter.font import Font
from ttkbootstrap import *
from ttkbootstrap.constants import *
from tkinter import Listbox
import datetime

# from tkinter import filedialog
# from tkinter import messagebox
# from tkinter import simpledialog

class Application(Frame):
    ''' main class docstring '''
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.pack(fill=BOTH, expand=True, padx=4, pady=4)
        self.create_widgets()

    def create_widgets(self):
        ''' creates GUI for app '''

        self.dateTimeLabel = Label(self, text="video actual date time",
                                   anchor=CENTER)
        self.dateTimeLabel.grid(row=0, column=1, sticky='we')

        self.lst = Listbox(self, width=80)
        self.lst.grid(row=1, column=1, sticky='nswe', padx=(5, 0), pady=5)
        self.rowconfigure(1, weight=1, pad=2)
        self.columnconfigure(1, weight=1)

        self.lst.bind("<<ListboxSelect>>", self.on_select_list)

        listOfVideos = []
        def get_directory_contents(path):
            for item in os.listdir(path):
                full_path = os.path.join(path, item)
                if os.path.isfile(full_path):
                    if full_path.find("/blink/") < 0:
                        continue
                    listOfVideos.append(full_path)
                elif os.path.isdir(full_path):
                    # skip output of directory name
                    get_directory_contents(full_path)

        get_directory_contents(sys.argv[1])

        listOfVideos.sort()

        for item in listOfVideos:
            self.lst.insert(END, item)

        self.scy = Scrollbar(self, orient=VERTICAL, command=self.lst.yview)
        self.scy.grid(row=1, column=2, sticky='wns')  # use nse
        self.lst['yscrollcommand'] = self.scy.set

        btnframe = Frame(self)
        btnframe.grid(row=3, column=1, columnspan=2)

        btnplay = Button(btnframe, text='Play', command=self.btnplay_clicked)
        btnplay.grid(row=1, column=1, padx=10)

        btnclose = Button(btnframe, text='Close', command=save_location)
        btnclose.grid(row=1, column=2, padx=10)

    def btnplay_clicked(self, e=None):
        ''' launch in player if "Video" '''
        subprocess.Popen(["smplayer", "-minigui", self.video])

    def on_select_list(self, event):
        list_item = self.lst.curselection()
        fp = self.lst.get(list_item[0])
        self.video = str(fp)  # for use in btnplay_clicked
        # display the actual date-time of the video in self.dateTimeLabel
        actDateTime = getRealDateTime(self.video)
        self.dateTimeLabel.config(text=actDateTime)

#
#   Functions to get the ACTUAL date-time of the video
#
def utc_to_cdt(utc_time, shift):
    # Convert UTC time to datetime object
    utc_datetime = datetime.datetime.strptime(utc_time, '%Y-%m-%d %H:%M:%S')
    # Convert UTC time to American Central Time
    cdt_datetime = utc_datetime - datetime.timedelta(hours=shift) - datetime.timedelta(minutes=0)
    # Format the CDT time string
    cdt_time = cdt_datetime.strftime('%Y-%m-%d %I:%M:%S %P')
    return cdt_time

def cnvfile(utcdate):
    ''' This function could be modified to accomodate different timezones
    for now it just uses US/Central. '''
    # Set the timezone you want to check
    timezone = pytz.timezone(zonename)
    # Get the current date and time in the timezone
    now = datetime.datetime.now(timezone)
    # Check if the timezone is currently in Daylight Saving Time
    is_dst = timezone.localize(datetime.datetime.now()).dst() != datetime.timedelta(0)
    if is_dst:
        # The timezone is currently in Daylight Saving Time
        actualFileDateTime = utc_to_cdt(utcdate, zoneDaylight)  # US/Central 'America/Chicago'
    else:
        # The timezone is currently in Standard Time
        actualFileDateTime = utc_to_cdt(utcdate, zoneStandard)  # US/Central 'America/Chicago'
    return f"{actualFileDateTime} {zonename}"

def getRealDateTime(filename):
    # get the last modification time of the file as a timestamp
    timestamp = os.path.getmtime(filename)
    # convert the timestamp to a human-readable date string
    date = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
    basename = os.path.basename(filename)  # get rid of the path
    fn = basename[:8]  # just the UTC time
    fn = fn.replace("-", ":")
    utc_dt = f"{date} {fn}"  # format the UTC file datetime
    # Now get the current timezone in 12-hour format
    return cnvfile(utc_dt)


# configure timezone inputs from command line args

zonetime = [("US/Eastern", 5, 4),
            ("US/Central", 6, 5),
            ("US/Mountain", 7, 6),
            ("US/Pacific", 8, 7),
            ("US/Alaska", 9, 8),
            ("US/Hawaii", 10, 9)
            ]

if len(sys.argv) < 3: # Needs arguments to run
    print('\nMissing args: 1 path to folder containing blink, 2 timezone NUMBER')
    for item, zone in enumerate(zonetime):
        print(item, zone[0])
    print("\nExample:")
    print("  ... blinkit.py Documents/BlinkStuff 2")
    print("blink folder is in Documents/BlinkStuff")
    print("timezone is Mountain\n")
    sys.exit()

tz = int(sys.argv[2])
zonename = zonetime[tz][0]
zoneStandard = zonetime[tz][1]
zoneDaylight = zonetime[tz][2]


# change working directory to path for this file
p = os.path.realpath(__file__)
os.chdir(os.path.dirname(p))

# THEMES
# 'cosmo', 'flatly', 'litera', 'minty', 'lumen',
# 'sandstone', 'yeti', 'pulse', 'united', 'morph',
# 'journal', 'darkly', 'superhero', 'solar', 'cyborg',
# 'vapor', 'simplex', 'cerculean'
root = Window("BlinkIt", "darkly", "camera.png")

# UNCOMMENT THE FOLLOWING TO SAVE GEOMETRY INFO
def save_location(e=None):
    ''' executes at WM_DELETE_WINDOW event - see below '''
    with open("winfo", "w") as fout:
        fout.write(root.geometry())
    root.destroy()

# UNCOMMENT THE FOLLOWING TO SAVE GEOMETRY INFO
if os.path.isfile("winfo"):
    with open("winfo") as f:
        lcoor = f.read()
    root.geometry(lcoor.strip())


root.protocol("WM_DELETE_WINDOW", save_location)  # UNCOMMENT TO SAVE GEOMETRY INFO
Sizegrip(root).place(rely=1.0, relx=1.0, x=0, y=0, anchor='se')
# root.resizable(0, 0) # no resize & removes maximize button
# root.minsize(w, h)  # width, height
# root.maxsize(w, h)
# root.overrideredirect(True) # removed window decorations
# root.iconphoto(False, PhotoImage(file='icon.png'))
# root.attributes("-topmost", True)  # Keep on top of other windows

Application(root)

root.mainloop()
