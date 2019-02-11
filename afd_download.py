#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 22 13:53:27 2018
###### MODIFIED ##########
@author: allenea

AUTHOR:  Eric Allen, UNIVERSITY OF DELAWARE, ** allenea@udel.edu 

(str) wfo_input = AWIPS ID

- Since I usually use AFD's you can just use the 3 digit station.
- Using 6 will give you the specific product outside of AFDs. One or two WFOs only use 2 characters on occassions. I wouldn't worry about it for general purposes.

I simplified this for you. Just be careful because this will run even if you don't give it a valid AWIPS ID. It'll just be an empty file though.
"""

import time
import os
import wget

def get_single_data(wfo_input, year=None):
    if year is None:
        end = int(time.ctime()[-4:])
        for year in range(1996,end+1):
            get_single_year(wfo_input, year)
    else:
        get_single_year(wfo_input, year)

def get_single_year(wfo_input, year, data_dir = os.getcwd()+'/AFD_DATA/'):
    nextyear = year +1
    if len(wfo_input)==3:
        getFile = "https://mesonet.agron.iastate.edu/cgi-bin/afos/retrieve.py?fmt=text&pil="+str(wfo_input)+"&center=&limit=9999&sdate="+str(year)+"0101&edate="+str(nextyear)+"0101"
        outfile = data_dir + wfo_input +"AFD_"+str(year)+".txt" 

        try:
            os.remove(outfile)
        except OSError:
            pass
        wget.download(getFile, outfile)
        print (outfile)
    
    elif len(wfo_input) == 2:
        if wfo_input == "PQ":
            wfofix = "AFDPQ"
            tmpwfo = "DPQAFD"
        getFile = "https://mesonet.agron.iastate.edu/cgi-bin/afos/retrieve.py?fmt=text&pil="+str(wfofix)+"&center=&limit=9999&sdate="+str(year)+"0101&edate="+str(nextyear)+"0101"
        outfile = data_dir + tmpwfo +"_"+str(year)+".txt" 
        try:
            os.remove(outfile)
        except OSError:
            pass
        wget.download(getFile, outfile)
        print (outfile)
        
    elif len(wfo_input) <6:
        getFile = "https://mesonet.agron.iastate.edu/cgi-bin/afos/retrieve.py?fmt=text&pil="+str(wfo_input)+"&center=&limit=9999&sdate="+str(year)+"0101&edate="+str(nextyear)+"0101"
        outfile = data_dir + wfo_input +"0"+"_"+str(year)+".txt"
        try:
            os.remove(outfile)
        except OSError:
            pass
        wget.download(getFile, outfile)
        print (outfile)
        
    else:
        getFile = "https://mesonet.agron.iastate.edu/cgi-bin/afos/retrieve.py?fmt=text&pil="+str(wfo_input)+"&center=&limit=9999&sdate="+str(year)+"0101&edate="+str(nextyear)+"0101"
        outfile = data_dir + wfo_input +"_"+str(year)+".txt" 
        try:
            os.remove(outfile)
        except OSError:
            pass
        wget.download(getFile, outfile)
        print (outfile)

if __name__ == '__main__':
    get_single_data('AFDCTP')