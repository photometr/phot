# -*- coding: utf-8 -*-

import numpy as np
from scipy import ndimage
from scipy.signal import convolve

def mirror(inpim):
  #FIXME too horrible - rewrite it!
  hlen = len(inpim[0])
  vlen = len(inpim)
  
  r = np.array(inpim[:,hlen-2])
  r.shape = vlen,1
  re = np.hstack((inpim,r))
  
  l = np.array(inpim[:,1])
  l.shape = vlen,1
  le = np.hstack((l,re))
  
  u1 = list(np.array(inpim[0,:]))
  u2 = [inpim[1,1]] + u1 + [inpim[1,-2]]
  u = np.array(u2)
  u.shape = 1,hlen+2
  ue = np.vstack((u,le))
  
  b1 = list(np.array(inpim[-1,:]))
  b2 = [inpim[-1,1]] + b1 + [inpim[-1,-2]]
  b = np.array(b2)
  b.shape = 1,hlen+2
  outim = np.vstack((ue,b))
  return outim

def filter_image( inpim, size=3, edges=True ):
  #FIXME size>3 is not implemented yet
  #FIXME edges is always True now
  minpim = mirror(inpim)
  k = 1./9
  gate = np.array([[k,k,k],[k,k,k],[k,k,k]])
  outim = convolve(minpim, gate, mode='valid')
  return outim
