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
import pyfits
import numpy as np
from datetime import datetime
from time import mktime
from st7.sigma_filter import sigma_filter

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
goodfdirname = os.path.join(dirname,"goodfits")
try:
  os.mkdir(goodfdirname)
except OSError: # already exists
  pass

# Reading some info
hdulist = pyfits.open("dark1.001")
hdr = hdulist[0].header
xsize = hdr['NAXIS1']
ysize = hdr['NAXIS2']
bzero = hdr['BZERO']
darkexptime = hdr['EXPTIME']

# Bias evaluation
bnames = []
for fn in os.listdir(os.getcwd()):
  if fn.startswith("bias.0"): #FIXME for multiple series of biases
    bnames.append(fn)

allbiases = []
for bias in bnames:
  FitsData, header = pyfits.getdata(bias, 0, header=True)
  allbiases.append(FitsData)

medbias = np.median(np.array(allbiases), axis=0)  #FIXME maybe + bzero?

try:
  pyfits.writeto(os.path.join(goodfdirname,'bias.fts'), medbias, header)
except IOError:
  os.remove(os.path.join(goodfdirname,'bias.fts'))
  pyfits.writeto(os.path.join(goodfdirname,'bias.fts'), medbias, header)

# subtracting bias from each image
names = []
for fn in os.listdir(os.getcwd()):
  if os.path.splitext(fn)[1] == ".FIT": continue
  if fn.startswith("bias"): continue
  if os.path.isdir(fn): continue
  image, header = pyfits.getdata(fn, 0, header=True)
  imagecl = image - medbias + 100 #FIXME why +100?
  try:
    pyfits.writeto(os.path.join(goodfdirname,fn), imagecl, header)
  except IOError:
    os.remove(os.path.join(goodfdirname,fn))
    pyfits.writeto(os.path.join(goodfdirname,fn), imagecl, header)
# bias subtraction finished

# median darks evaluation
# so complicated because we want to handle != 3 number of darks in series
alldarks = filter(lambda x: x.startswith("dark") and
                  os.path.splitext(x)[1][1] == "0",
                  os.listdir(goodfdirname))
darks_no_ext = map(lambda x: os.path.splitext(x)[0], alldarks)
darks = list(set(darks_no_ext)) # makes elements unique

#meddarkdates = []
meddarks = {}
for dark in darks:
  outdark = os.path.join(goodfdirname,dark+".fts")
  curseries = filter(lambda x: os.path.splitext(x)[0] == dark, alldarks)
  curser = map(lambda x: os.path.join(goodfdirname,x), curseries)
  list_of_darks = []
  jd = 0
  gd = 0
  for curdark in curser:
    darkdata, header = pyfits.getdata(curdark, 0, header=True)
    list_of_darks.append(darkdata)
    jd = jd + header['TJD-OBS']
    dtobj = datetime.strptime(header['DATE-OBS'], "%Y-%m-%dT%H:%M:%S.000")
    gd = gd + mktime(dtobj.timetuple()) # to seconds
  jd = jd/len(curser) + header['EXPTIME']/172800. # mean of series
  #meddarkdates.append(jd)
  gd = gd/len(curser) + header['EXPTIME']/172800.
  gd = datetime.fromtimestamp(gd).strftime("%Y-%m-%dT%H:%M:%S")
  meddark = np.median(np.array(list_of_darks), axis=0)
  meandark = meddark.mean()
  meddarks[jd] = meddark
  #FIXME plot graph jd vs meandark
  header.update('TJD-OBS', jd, 'Middle of the series')
  header.update('DATE-OBS', gd, 'Middle of the series')
  header.update('HIERARCH MEAN_DARK', meandark, 'As seen by PyFITS+BZERO-100') #FIXME comment
  try:
    pyfits.writeto(outdark, meddark, header)
  except IOError:
    os.remove(outdark)
    pyfits.writeto(outdark, meddark, header)

# calculating mean darks
meddarkdates = meddarks.keys()
meddarkdates.sort()
meandarks = [meddarks[meddarkdates[0]]]
for i in range(len(meddarkdates)-1):
  meandarks.append((meddarks[meddarkdates[i]]+meddarks[meddarkdates[i+1]])/2.)
meandarks.append(meddarks[meddarkdates[-1]])

# subtracting darks from working files
for fn in os.listdir(goodfdirname):
  if fn.startswith("dark"): continue
  if fn.startswith("bias"): continue
  if os.path.splitext(fn)[1] == "": continue
  imgdata, header = pyfits.getdata(fn, 0, header=True)
  obsjd = header['TJD-OBS']
  objexp = header['EXPTIME']
  for i in range(len(meddarkdates)):
    darkjd = meddarkdates[i]
    if obsjd < darkjd:
      darknew = ((meandarks[i]-100)/darkexptime*objexp - bzero + 100)
      climgdata = imgdata - darknew - bzero + 100 #FIXME why?
      outimag = sigma_filter(climgdata,sigma=5,box_width=3)
      try:
	pyfits.writeto(fn, outimag, header)
      except IOError:
	os.remove(fn)
    elif i == len(meddarkdates)-1:
      darknew = ((meandarks[i+1]-100)/darkexptime*objexp - bzero + 100)
      climgdata = imgdata - darknew - bzero + 100
      outimag = sigma_filter(climgdata,sigma=5,box_width=3)
      try:
	pyfits.writeto(fn, outimag, header)
      except IOError:
	os.remove(fn)
