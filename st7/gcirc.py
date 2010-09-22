#!/usr/bin/python
# -*- coding: utf-8 -*-
import math

#Computes rigorous great circle arc distances. 
#RAx in decimal hours, DCx in decimal
#       degrees, DIS in arc seconds 

def gcirc(ra1,dc1,ra2,dc2):
    d2r  = math.pi/180.0
    as2r = math.pi/648000.0
    h2r  = math.pi/12.0
    rarad1 = ra1*h2r
    rarad2 = ra2*h2r
    dcrad1 = dc1*d2r
    dcrad2 = dc2*d2r
    radif  = abs(rarad2-rarad1)
    if radif > math.pi:
        radif = 2.0*math.pi - radif
    cosdis = math.sin(dcrad1)*math.sin(dcrad2) 
    cosdis = cosdis + math.cos(dcrad1)*math.cos(dcrad2)*math.cos(radif)
    dis    = math.acos(cosdis)
    dis = dis/as2r
    return dis
    
