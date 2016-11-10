#!/usr/bin/python2.7

#-----------------------------------------------------------
#                         pyaneti.py
#                        DESCRIPTION
#                   Barragan O, March 2016
#-----------------------------------------------------------

#Load libraries
import numpy as np
import matplotlib.pyplot as plt
import sys
import os
import pyaneti as pti #FORTRAN module

#-------------------------------------------------------------
#                   INITIALIZATION
#-------------------------------------------------------------

#Load the input file
#You have to run the program as ./pyaneti star_name
star = str(sys.argv[1])

#Create path to the input_fit.py file
inf_name = 'inpy/'+star+'/input_fit.py'

#Did you create an input_fit.py file?
if ( not os.path.isfile( inf_name ) ):
  print 'You have not created', inf_name
  sys.exit()

#Read the file with all the python functions
execfile('src/todo-py.py')

#Read the file with the default values
execfile('src/default.py')

#Read input file
execfile(inf_name)

#Prepare data
execfile('src/prepare_data.py')

#Create ouput directory
outdir = 'outpy/' + star + '_out'
if not os.path.exists(outdir):
  os.makedirs(outdir)

#Obtain smart priors based on iput data
if (is_smart_priors ):
  smart_priors()

#if is_circular is turned on, we ensure a circular orbit
check_circular()

#Print intial configuration
print_init()


#-------------------------------------------------------------
#                   FITTING ROUTINES
#-------------------------------------------------------------

if (method == 'new'):
  fit_new_method()

#Joint fit
elif (fit_rv and fit_tr ):
  fit_joint()

#Transit fit
elif ( not fit_rv and fit_tr ):
  fit_transit()

#Radial velocity fit
elif ( fit_rv and not fit_tr ):
  fit_radial_velocity()


#Nothing to fit!
else:
  sys.exit("Nothing to fit!")

#-------------------------------------------------------------
#             	PRINT AND PLOT ROUTINES
#-------------------------------------------------------------

execfile('src/output.py')

#-------------------------------------------------------------
#             	 END pyaneti.py FILE
#-------------------------------------------------------------
