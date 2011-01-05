#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np
from scipy import ndimage
from scipy.signal import convolve

a = np.array([[1.,2,3,4,5,6,7,8,9,10],
	      [1.,2,3,4,5,6,7,8,9,10],
	      [1.,2,3,4,5,6,7,8,9,10],
	      [1.,2,3,4,5,6,7,8,9,10],
	      [1.,2,3,4,5,6,7,8,9,10],
	      [1.,2,3,4,5,6,7,8,9,10],
	      [1.,2,3,4,5,6,7,8,9,10],
	      [1.,2,3,4,5,6,7,8,9,10],
	      [1.,2,3,4,5,6,7,8,9,10],
	      [1.,2,3,4,5,6,7,8,9,10]])

f = [i/2. for i in range(250)]
g = [f for i in range(350)]
#a = np.array(g)

def mirror(inpim):
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
  #newim = []
  #extim = mirror(inpim)
  #for v in range(1,len(extim)-1):
    #newline = []
    #for h in range(1,len(extim[0])-1):
      #subarr = extim[v-1:v+2,h-1:h+2]
      #newline.append(subarr.mean())
    #newim.append(newline)
  #outim = np.array(newim)
  minpim = mirror(inpim)
  k = 1./9
  gate = np.array([[k,k,k],[k,k,k],[k,k,k]])
  #gate = np.array([[1.,1.,1.],[1.,1.,1.],[1.,1.,1.]])
  outim = convolve(minpim,gate,mode='valid')
  return outim
  
#def fun(neighb):
#  return neighb.mean()

#for i in range(200):
#b = ndimage.generic_filter(a, fun, footprint = [[1, 1, 1],[1, 1, 1],[1, 1, 1]], mode='mirror')

#print b
for i in range(1):
  outim = filter_image( a )
  print outim
  #print len(outim),len(outim[0])
