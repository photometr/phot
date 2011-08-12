# -*- coding: utf-8 -*-

from filter_image import filter_image

def sigma_filter( inpimag, sigma=3, box_width=3, all_pix=True):
    bw2 = box_width**2
    mean = filter_image(inpimag,box_width,all_pix)*bw2 - inpimag
    mean = mean/float(bw2-1)

    imdev = (inpimag - mean)**2
    fact = float(sigma**2)/(bw2-2)
    imvar = fact*(filter_image(imdev,box_width,all_pix)*bw2 - imdev)

    wok = imdev < imvar
    if not wok.all(): mean[wok] = inpimag[wok]
    return mean
