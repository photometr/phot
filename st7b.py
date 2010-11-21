#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os, math
import pyfits, datetime
from  st7 import sidereal
from  st7.posang import posang
from  st7.gd2jd import gd2jd
from  st7.gcirc import gcirc
import ephem #http://pypi.python.org/pypi/pyephem/#downloads
import ConfigParser
import st7.progrbar, st7.progrbarwin

if sys.platform == "linux2": # Linux kernel 2.x
  import Tkinter, tkFileDialog
else:                        # Windows
  import win32gui
  from win32com.shell import shell, shellcon

config = ConfigParser.RawConfigParser()
config.read('config.cfg')

fitssuffix = config.get('ST7B', 'fitssuffix')
tabobwin = config.get('ST7B', 'tabobwin')
taboblin = config.get('ST7B', 'taboblin')
initdirlin = config.get('ST7B', 'initdirlin')
initdirwin = config.get('ST7B', 'initdirwin')
telescope = config.get('ST7B', 'telescope')
debug = config.getboolean('ST7B', 'debug')
longitude = config.getfloat('ST7B', 'longitude')
latitude = config.getfloat('ST7B', 'latitude')
elevation = config.getfloat('ST7B', 'elevation')

# Choosing working folder
if sys.platform == "linux2":
  root = Tkinter.Tk(className="st7b")
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

if debug:
  print "Working in ",dirname

# Obtaining list of files within dirname
def dir_list(dirname, *args):
  fileList = []
  for filename in os.listdir(dirname):
    dirfile = os.path.join(dirname, filename)
    if os.path.isfile(dirfile): # use only ordinary files
      if dirfile.endswith(fitssuffix): # use only fit
	fileList.append(dirfile)
  return fileList

filelist = dir_list(dirname)
ratio_of_one_file = 1.0/len(filelist)
perc_done = 0.0 #fraction of files processed

def GetCoords(alp,delt):
  # Translate coords to floating point values
  H = float(alp.split()[0])
  M = float(alp.split()[1])
  S = float(alp.split()[2])
  D = float(delt.split()[0])
  Md = float(delt.split()[1])
  Sd = float(delt.split()[2])
  ra = H + M/60.0 + S/3600.0
  ra = ra * 15
  dec = D + Md/60.0 + Sd/3600.0
  coords = [ra,dec]
  return coords

def format_comment(coor1, coor2, comment):
  comstr = sidereal.dmsUnits.singleToMix(coor1)
  comstr = comstr + sidereal.dmsUnits.singleToMix(coor2)
  comstr = " ".join(map(str,comstr)) # 'd m s d m s'
  comstr = comstr + comment
  return comstr

def red_to_pos(hourang):
  #receives hourang in degrees
  #returns reduced to positive in hours
  if hourang < 0:
    hourang = 24 + hourang/15.0
  else:
    hourang = hourang/15.0
  return hourang

# Working with headers
for fname in filelist:
  if debug:
    print "Working with ", fname
  hdulist = pyfits.open(fname,mode='update')
  hdr = hdulist[0].header
  # Rewriting keywords because CCDOPS doesn't work fine
  bscale = hdulist[0].header['BSCALE']
  hdulist[0].scale('int16', bscale=1.0, bzero=32768)
  hdr.update('BSCALE', bscale)
  ccdtemp = hdulist[0].header['CCD-TEMP']
  hdr.update('CCD-TEMP', ccdtemp)

  exptime = hdulist[0].header['EXPTIME']
  hdr.update('EXPTIME', exptime)
  hdr.update('EACHSNAP', exptime, 'EXPOSURE IN SECONDS')

  naxis1 = hdulist[0].header['NAXIS1']
  naxis2 = hdulist[0].header['NAXIS2']
  datobs = hdulist[0].header['DATE-OBS']
  if len(datobs) == 10:
    timobs = hdulist[0].header['TIME-OBS']
  else:
    timobs = datobs[11:]
    datobs = datobs[:10]

  dtobs = datetime.datetime.strptime(datobs+" "+timobs, "%Y-%m-%d %H:%M:%S.000")
  juldate = gd2jd(dtobs.year,dtobs.month,dtobs.day,dtobs.hour,dtobs.minute,dtobs.second)
  hdr.update('TJD-OBS', juldate, before='DATE-OBS')

  shortobjname = os.path.basename(fname)[:5]

  # Start comparision with tabob
  namobj = []
  alpha = []
  delta = []
  if sys.platform == "linux2":
    fop = open(taboblin,'r')
  else:
    fop = open(tabobwin,'r')
  for line in fop.readlines():
    namobj.append(line.split(",")[0][:5])
    alpha.append(line.split(",")[1])
    delta.append(line.split(",")[2])
  fop.close()

  alp='0 0 0.0'
  delt='0 0 0'
  try:
    i = namobj.index(shortobjname)
    alp = alpha[i]
    delt = delta[i]
  except ValueError:
    i = -1 # Not in list
  crval = GetCoords(alp, delt)

  crp1 = naxis1/2 # FIXME maybe 2.0?
  crp2 = naxis2/2
  crpix = [crp1,crp2]

  try:
    cdelt1 = hdulist[0].header['XPIXSZ']  # FIXME COUNT=old?
    cdelt2 = hdulist[0].header['YPIXSZ']
    cdelt1 = -cdelt1/.018*.000366/1000.0
    cdelt2 = cdelt2/.018*.000366/1000.0
  except:
    cdelt1 = hdulist[0].header['PIXWIDTH']
    cdelt2 = hdulist[0].header['PIXHEIGH']
    cdelt1 = -cdelt1/.018*.000366
    cdelt2 = cdelt2/.018*.000366

  crota1 = 0
  crota2 = 0
  hdr.update('RADECSYS', 'FK5', after='FILTER')
  hdr.update('EQUINOX', 2000.0, after='RADECSYS')
  hdr.update('CTYPE1', 'RA---TAN', after='EQUINOX')
  hdr.update('CRVAL1', crval[0], after='CTYPE1')
  hdr.update('CRPIX1', crpix[0], after='CRVAL1')
  hdr.update('CDELT1', cdelt1, after='CRPIX1')
  hdr.update('CROTA1', crota1, after='CDELT1')
  hdr.update('CTYPE2', 'DEC--TAN', after='CROTA1')
  hdr.update('CRVAL2', crval[1], after='CTYPE2')
  hdr.update('CRPIX2', crpix[1], after='CRVAL2')
  hdr.update('CDELT2', cdelt2, after='CRPIX2')
  hdr.update('CROTA2', crota2, after='CDELT2')

  ramoon = 0.0
  decmoon = 0.0
  #print moonpos( juldate, ramoon ,decmoon)
  gatech = ephem.Observer()
  gatech.long = longitude
  gatech.lat = latitude
  gatech.elevation = elevation
  gatech.date = dtobs.strftime("%Y/%m/%d %H:%M:%S")
  mooncoord = ephem.Moon(gatech)
  ramoon = math.degrees(mooncoord.ra)
  decmoon = math.degrees(mooncoord.dec)
  phase = mooncoord.moon_phase


  Gst = sidereal.SiderealTime.fromDatetime(dtobs)
  Lst = Gst.lst(math.radians(longitude))
  Lst4outp = Lst
  Lst = Lst.hours * 15 #local siderial time - in degrees

  hourangle = red_to_pos(Lst-ramoon)
  h = format_comment(hourangle, decmoon, '')# FIXME where we use it?
  rastar = crval[0]/15.0
  alpstar = crval[0]
  hourstar = red_to_pos(Lst - crval[0])
  delstar = crval[1]
  starcoo = format_comment(crval[0]/15.0, crval[1], ' pointing coords.')
  RADec = sidereal.RADec(math.radians(alpstar), math.radians(delstar))
  aastr = RADec.altAz(math.radians(hourstar*15.0), math.radians(latitude))
  secz = 1.0/math.cos(math.pi*0.5-aastr.alt)
  airmass = str(secz) + ' airmass of the source'
  starcoo2 = format_comment(hourstar, delstar, ' Hour Angle and Dec of the SOURCE')
  dist = gcirc(rastar,delstar,ramoon,decmoon)
  dist = str(round(dist/3600.0,4)) + '  distance to Moon, degrees'
  angle = str(round(posang(1,rastar,delstar,ramoon,decmoon),3))
  angle = angle + ' Pos.angle  of Moon, degrees'

  comment0 = starcoo
  comment1 = format_comment(ramoon/15.0, decmoon, '   RA and Dec of MOON')
  comment2 = format_comment(hourangle, decmoon, '   Hour Angle and Dec of MOON')
  comment3 = str(phase) + '   Moon illuminated fraction'
  comment4 = dist
  comment5 = angle
  comment6 = starcoo2
  comment7 = Lst4outp.__str__()[1:-1] + '  Sidereal time'
  comment8 = airmass

  hdr.update('AIRMASS', secz, after='EACHSNAP')
  hdr.add_comment(comment7) #зв.время
  hdr.add_comment(comment0) #координаты объекта
  hdr.add_comment(comment6) #час. угол и склонение объекта
  hdr.add_comment(comment1) #коорд. Луны
  hdr.add_comment(comment2) #час.угол и склонение Луны
  hdr.add_comment(comment3) #Фаза Луны
  hdr.add_comment(comment4) #расстояние от объекта до Луны
  hdr.add_comment(comment5) #позиц. угол Луны отн. объекта
  hdr.add_comment(comment8) #воздушная масса объекта

  ext = os.path.basename(fname).split(".")[0][-3:]
  objname = os.path.basename(fname).split(".")[0]
  objname = objname[0:len(objname)-3]
  hdr.update('OBJECT', objname)
  hdr.update('TELESCOP', telescope)
  hdr.add_history('Modified by st7b.py '+datetime.datetime.now().strftime("%H:%M %d/%m/%Y"))
  if ext[0] != '0':
    hdulist.flush() # save changes
  else:
    fileout = os.path.join(dirname, objname+'.' + ext)
    try:
      hdulist.writeto(fileout)
    except IOError:
      os.remove(fileout)
      hdulist.writeto(fileout)

  perc_done = perc_done + ratio_of_one_file    #calculate fraction of processed files
  m.set(perc_done)                             #update progress bar

print 'ALL FILES RENAMED, ADDITIONAL INFORMATION INSERTED IN FITS HEADERS'
