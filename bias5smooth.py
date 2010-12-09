#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
This program reads a raw fit image and subtracts
bias and dark images, performing their median
filtration before subtracting.
In the work directory will be created (automatically) subdirectory
'\goodfits'. 5 bias images should be named bias*.fit
Dark images are obtained every 1.5-2 hours, 3 images
in each series, named
dark1001.fit, dark1002.fit, dark1003.fit
...
darkN1001.fit, darkN002.fit, darkN003.fit
First series - before all other images for this night.

 CAUTION: the original files are not deleted to avoid possible mistakes
 You will need to delete them when you are sure that all files are converted
correctly
Made by V. Larionov 13.03.2004 in IDL.
Corrected 06.06.2008
Rewritten in Python 10.12.2010
'''
import sys, os
import ConfigParser

if sys.platform == "linux2": # Linux kernel 2.x
  import Tkinter, tkFileDialog
  import st7.progrbar
else:                        # Windows
  import win32gui
  import st7.progrbarwin
  from win32com.shell import shell, shellcon

# Reading config
config = ConfigParser.RawConfigParser()
config.read('config.cfg')

initdirlin = config.get('ST7B', 'initdirlin')
initdirwin = config.get('ST7B', 'initdirwin')

# Choosing working folder
if sys.platform == "linux2":
  root = Tkinter.Tk(className="bias5smooth")
  m = st7.progrbar.Meter(root, relief='ridge', bd=3)
  m.pack(fill='x')
  m.set(0.0, 'Waiting for working folder...')
  dirname = tkFileDialog.askdirectory(parent=root,initialdir=initdirlin,title='Please Choose folder')
else:
  desktop_pidl, ignore = shell.SHILCreateFromPath(initdirwin, 0)
  pidl, disp_name, image_list = shell.SHBrowseForFolder(
    win32gui.GetDesktopWindow(),
    desktop_pidl,
    "Please Choose folder",
    0,
    None,
    None
  )
  PBDlgTemp = st7.progrbarwin.MakeDlgTemplate() #progressbar window
  m = st7.progrbarwin.TestDialog(PBDlgTemp)
  m.CreateWindow()
  dirname = shell.SHGetPathFromIDList(pidl)

os.chdir(dirname)

