#!/usr/bin/python
# -*- coding: utf-8 -*-

# converts a gregorian date to julian date
# expects one or two arguments, first is date in dd.mm.yyyy,
# second optional is time in hh:mm:ss. If time is omitted,
# 12:00:00 is assumed

import math, sys, string

def gd2jd(yyyy,mm,dd,hh,mins,sec):
  UT=hh+mins/60.0+sec/3600.0
  total_seconds=hh*3600+mins*60+sec
  fracday=total_seconds/86400.0


  if (100*yyyy+mm-190002.5)>0:
      sig=1
  else:
      sig=-1

  JD = 367*yyyy - int(7*(yyyy+int((mm+9)/12.0))/4.0) + int(275*mm/9.0) + dd + 1721013.5 + UT/24.0 - 0.5*sig +0.5

  return JD
  
