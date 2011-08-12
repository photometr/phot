#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np
from scipy import ndimage

class Singleton(object):
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(
                                cls, *args, **kwargs)
        return cls._instance

def fun(neighb):
  par = Singleton()
  el = neighb[4]
  subarr = np.delete(neighb,4)
  sigma = subarr.std()
  if el > par._instance[1]*sigma:
    par._instance[2] = True
    return subarr.mean()
  return el

def sf(inpimage,dim,sigma): #FIXME make dim usable
  par = Singleton()
  par._instance = [dim, sigma, True]
  niter = 0
  while par._instance[2] and niter<21:
    par._instance = [dim, sigma, False]
    outimage = ndimage.generic_filter(inpimage, fun, footprint = [[1, 1, 1],[1, 1, 1],[1, 1, 1]])
    niter = niter + 1
  return outimage
