#!/usr/bin/python2

#Load libraries
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.stats import norm, sigmaclip
import sys
import pyaneti as pti

#Read the file with all the python functions
execfile('todo-py.py')

#Read the file with the default values
execfile('default.py')

#Read input file
execfile('input_fit.py')

#Print intial configuration
print	''
print	'------------------------------'
print "INITIAL CONFIGURATION"
print	'------------------------------'
print 'is_circular = ', is_circular
print 'iter max = ', maxi
print 'step precision= ', prec
print 'thin factor =', thin_factor
print	'nconv =',nconv
print 'fit RV =', fit_rv
print 'fit Transit =', fit_tr
print	'------------------------------'
print 'Priors'
print	'------------------------------'
print 'T_0 = ', T0
print 'Period = ', P
print 'eccentriciy =', e
print 'periastron =', w
if (fit_tr):
	print 'sin(i) = ', np.sin(ii)
	print 'a/r*	  = ', a
	print 'u1     = ', u1
	print 'u2     = ', u2
	print 'rp/r*  = ', pz
print	'------------------------------'
print 'What am I fitting?'
print	'------------------------------'
print 'fit T0= ', fit_t0
print 'fit P = ', fit_P
print 'fit e = ', fit_e
print 'fit w = ', fit_w
if (fit_tr):
	print 'fit i = ', fit_i
	print 'fit a = ', fit_a
	print 'fit u1= ', fit_u1
	print 'fit u2= ', fit_u2
	print 'fit pz= ', fit_pz
if (fit_rv):
	print 'fit k = ', fit_k
	print 'fit v0= ', fit_v0
print	'------------------------------'
print ''
print	'------------------------------'


#PREPATARION RV DATA
if (fit_rv):

	#Read the data file
	time,rv,err,tspe = np.loadtxt(fname_rv,usecols=(0,1,2,3), \
  	dtype={'names': ('time', 'rv', 'err','telescope'), \
		'formats': ('float', 'float', 'float', 'S1')}, \
		comments='#',unpack=True)

	#Transform rv from km/s to m/s
	if(units_ms):
		ktom = 1000
		rv=rv*ktom
		err=err*ktom
		ylab = 'RV (m/s)'
	
	#These lists have lists with data for the different telescopes
	time_all=[]
	rv_all=[]
	errs_all=[]

	#Number of telescopes
	nt = len(telescopes)

	#tspe is the data with the telescopes read from the file
	for i in range(0,nt):
		time_dum =[]
		rv_dum =[]
		errs_dum =[]
		if (len(telescopes[i]) == 0):
			sys.exit("There is no data for %s"% telescopes[i])
		else:
			for j in range(0,len(tspe)):
				if (tspe[j] == telescopes[i]):
					time_dum.append(time[j])
					rv_dum.append(rv[j])
					errs_dum.append(err[j])
		#The *all variables are lists of lists, each list constains
		# a list with the data of each telescope
			time_all.append(time_dum)
			rv_all.append(rv_dum)
			errs_all.append(errs_dum)

	#The mega* variables contains all telescope data
	mega_rv = []
	mega_time = []
	mega_err  = []
	tlab = []
	for i in range(0,nt): 
		for j in range(0,len(rv_all[i])):
			tlab.append(i)
			mega_rv.append(rv_all[i][j])
			mega_time.append(time_all[i][j])
			mega_err.append(errs_all[i][j])

#The RV data is ready

#PREPARATION TRANSIT DATA

if (fit_tr):

	#Read the data file
	dummyd,dummyf,flag = np.loadtxt(fname_tr,usecols=(2,9,10), \
	comments='\\',unpack=True)

	#Let us take the good data with the flag
	nobin_wflux = []
	nobin_hdate = []
	for i in range(0,len(flag)):
		if ( flag[i] == 0):
			nobin_wflux.append(dummyf[i])
			nobin_hdate.append(dummyd[i])

	nbin = 16

	#bin the data to do fastest test
	hdate, err_hdate = bin_data(nobin_hdate,nbin)
	wflux, errs = bin_data(nobin_wflux,nbin)

	#THIS HAS TO BE DONE AUTOMATICALLY!	

	ntr = 2

	tls = [None]*ntr

	tls[0] = [3217.,3218.]
	tls[1] = [3232.1,3233.1]

	#crash if you do not have more than one transit
	if ( ntr < 2):
		print "you do not have enought transit data!"
		sys.exit("I crashed because I want more data!")
	
	#Each element of these vectors will have the information
	#of a given transit
	xt= [None]*ntr	
	yt= [None]*ntr	
	et= [None]*ntr	

	#Normalize all the transit independently
	for i in range(0,ntr):
		xt[i],yt[i],et[i] = normalize_transit(hdate,wflux,errs,tls[i])

	#Let us put together the information of all the arrays
	megax = np.concatenate(xt)
	megay = np.concatenate(yt)
	megae = np.concatenate(et)

#TRANSIT DATA READY

#PRIORS SECTION

#Let us try to do a guess for the init values
if (fit_rv):
	k0vecmax = [None]*nt
	k0vecmin = [None]*nt
	k0 = 0.0
	for i in range(0,nt):
		k0vecmin[i] = min(rv_all[i])
		k0vecmax[i] = max(rv_all[i])
		k0 = k0 + ( k0vecmax[i] - k0vecmin[i] ) / 2

	k0 = k0 / nt
	v0 = np.zeros(nt)

	for i in range(0,nt):
		v0[i] = ( k0vecmin[i] + k0vecmax[i] ) / 2.0

if (fit_tr):
	T0 = min(xt[0]) + 0.5*(max(xt[0])-min(xt[0]))


#FIT TRANSIT AND RV CURVES
if (fit_rv and fit_tr ):

	what_fit = [int(fit_t0),int(fit_P),int(fit_e),int(fit_w), \
              int(fit_i),int(fit_a),int(fit_u1),int(fit_u2),\
              int(fit_pz), int(fit_k), int(fit_v0)]
	dummy = [T0,P,e,w,ii,a,u1,u2,pz,k0]
	params = np.concatenate((dummy,v0))

	#Call the fit routine
	pti.metropolis_hastings(mega_time,mega_rv,mega_err,tlab \
	,megax, megay, megae, params, prec, maxi, thin_factor, \
	ics, what_fit, nconv)

	#Read the data
	vari,chi2,chi2red,t0o,Po,eo,wo,io,ao,u1o,u2o,pzo,ko =  \
	np.loadtxt('mh_fit.dat', comments='#',unpack=True, \
	usecols=range(0,13))
	vo = [None]*nt
	for i in range(0,nt):
		n = [13+i]
  	vo[i] = np.loadtxt('mh_fit.dat', comments='#', \
		unpack=True, usecols=(n))

#FIT TRANSIT CURVE ONLY
elif ( not fit_rv and fit_tr ):

	flags = [True, True]

	what_fit = [int(fit_t0),int(fit_P),int(fit_e),int(fit_w),  \
              int(fit_i),int(fit_a), int(fit_u1),int(fit_u2),\
            int(fit_pz)]
	params = [T0,P,e,w,ii,a,u1,u2,pz]

	#Call fit routine
	pti.metropolis_hastings_tr_improved(megax, megay, megae,  \
	params, prec, maxi, thin_factor, ics, what_fit,flags,nconv)

	#Read the data
	vari, chi2,chi2red,t0o,Po,eo,wo,io,ao,u1o,u2o,pzo = \
       np.loadtxt('mh_trfit.dat', comments='#',unpack=True)

#FIT RV CURVE ONLY
elif ( fit_rv and not fit_tr ):

	flags = [True, True, True]

	what_fit = [int(fit_t0),int(fit_P),int(fit_e),int(fit_w), \
					    int(fit_k), int(fit_v0)]
	dummy = [T0,P,e,w,k0]
	params = np.concatenate((dummy,v0))
	
	#Call fit routine
	pti.metropolis_hastings_rv(mega_time,mega_rv,mega_err,tlab,\
  params, prec, maxi, thin_factor, ics, what_fit,flags,nconv)

	#Read the data
	vari,chi2,chi2red,t0o,Po,eo,wo,ko = \
	np.loadtxt('mh_rvfit.dat', comments='#', unpack=True,\
	usecols=range(0,8))
	vo = [None]*nt
	for i in range(0,nt):
		n = [8+i]
  	vo[i] = np.loadtxt('mh_rvfit.dat', comments='#', \
		unpack=True, usecols=(n))

#Nothing to fit!
else:
	sys.exit("Nothing to fit!")

#Find the values and errors
t0_val,t0_err = find_vals_gauss(t0o,nconv)
P_val, P_err  = find_vals_gauss(Po,nconv)
e_val,e_err 	= find_vals_gauss(eo,nconv)
w_val,w_err 	= find_vals_gauss(wo,nconv)
w_deg 		= w_val * 180. / np.pi
w_deg_err = w_err * 180. / np.pi
if ( fit_tr ):
	i_val,i_err 	= find_vals_gauss(io,nconv)
	a_val,a_err 	= find_vals_gauss(ao,nconv)
	u1_val,u1_err = find_vals_gauss(u1o,nconv)
	u2_val,u2_err = find_vals_gauss(u2o,nconv)
	pz_val,pz_err = find_vals_gauss(pzo,nconv)
	i_deg 		= i_val * 180. / np.pi
	i_deg_err = i_err * 180. / np.pi
if ( fit_rv ):
	k_val, k_err  = find_vals_gauss(ko,nconv)
	v_val = [None]*nt
	v_err = [None]*nt
	for i in range(0,nt):
		v_val[i], v_err[i] = find_vals_gauss(vo[i],nconv)


#Print the best fit values values
print ('The best fit planet parameters are:')
print ('T0    = %4.4e +/- %4.4e days'%(t0_val,t0_err))
print ('P     = %4.4e +/- %4.4e' 		%(P_val,P_err))
print ('e     = %4.4e +/- %4.4e'			%(e_val,e_err))
print ('w     = %4.4e +/- %4.4e deg'	%(w_deg,w_deg_err))
if (fit_tr):
	print ('i     = %4.4e +/- %4.4e deg' %(i_val,i_err))
	print ('a/r*  = %4.4e +/- %4.4e' 		%(a_val,a_err))
	print ('u1    = %4.4e +/- %4.4e' 		%(u1_val,u1_err))
	print ('u2    = %4.4e +/- %4.4e' 		%(u2_val,u2_err))
	print ('rp/r* = %4.4e +/- %4.4e' 		%(pz_val,pz_err))
if (fit_rv):
	print ('K    = %4.4e +/- %4.4e' 		%(k_val,k_err))
	for i in range(0,nt):
		print ('%s v0 = %4.4e +/- %4.4e' 	%(tspe[i], \
		v_val[i],v_err[i]))


#PLOT TRANSIT
if ( fit_tr ):

	#Move all the points to T0
	for i in range(0,ntr):
		xt[i] = xt[i] - P_val * i

	#Redefine megax with the new xt values
	megax = np.concatenate(xt)
	z_val = pti.find_z(megax,t0_val,P_val,e_val,w_val\
					,i_val,a_val)
	mud_val, mu0_val = pti.occultquad(z_val,u1_val,u2_val\
					,pz_val)
	#Residuals
	res = megay - mud_val

	#Get the model data to do the plot
	nvec = int(1e5)
	dx = ( max(megax) - min(megax) ) / nvec
	xvec = np.zeros(nvec)
	xvec[0] = min(megax) 
	for i in range(1,nvec):
		xvec[i] = xvec[i-1] + dx
	zvec = pti.find_z(xvec,t0_val,P_val,e_val,w_val,i_val,a_val)
	mud, mu0 = pti.occultquad(zvec,u1_val,u2_val,pz_val)
	#Now we have data to plot a nice model

	#Do the plot
	plt.figure(2,figsize=(10,10))
	#Plot the transit light curve
	plt.subplot(211)
	plt.xlim(min(xt[0]),max(xt[0]))
	plt.errorbar(megax,megay,megae,fmt='o',alpha=0.3)
	plt.plot(xvec,mud,'k',linewidth=2.0)
	#Plot the residuals
	plt.subplot(212)
	plt.xlim(min(xt[0]),max(xt[0]))
	plt.errorbar(megax,res,megae,fmt='o',alpha=0.3)
	plt.plot(megax,np.zeros(len(megax)),'k--',linewidth=2.0)
	plt.show()

#PLOT RV CURVE
if ( fit_rv ):

	#Create the RV fitted curve
	n = 5000
	xmin = t0_val
	xmax = t0_val + P_val
	dn = (xmax - xmin) /  n
	rvx = np.empty([n])
	rvx[0] = xmin
	for i in range(1,n):
	  rvx[i] = rvx[i-1] + dn
	if ( is_circular ):
	  rvy = pti.rv_circular(rvx,0.0,t0_val,k_val,P_val)
	else:
	  rvy = pti.rv_curve(rvx,0.0,t0_val,k_val,P_val,e_val,w_val)
	
	res = [None]*nt
	for i in range(0,nt):
 	 if (is_circular):
	    res[i] = pti.rv_circular(time_all[i],0.0,t0_val,\
							 k_val,P_val)
 	 else:
	    res[i] = pti.rv_curve(time_all[i],0.0,t0_val,k_val,\
							 P_val,e_val,w_val)
 	 rv_all[i] = rv_all[i] - v_val[i]
 	 res[i] = rv_all[i] - res[i]
	
	p_rv = scale_period(rvx,t0_val,P_val)
	p_all = [None]*nt
	for i in range(0,nt):
		p_all[i] = scale_period(time_all[i],t0_val,P_val)

	plt.figure(3,figsize=(10,10))
	plt.subplot(311)
	plt.xlabel("Phase")
	plt.ylabel(ylab)
	plt.plot(p_rv,rvy,'k',label=('k=%2.2f m/s'%k_val ))
	mark = ['o', 'd', '^', '<', '>', '8', 's', 'p', '*']
	for i in range(0,nt):
	  plt.errorbar(p_all[i],rv_all[i],errs_all[i],\
		label=telescopes[i],fmt=mark[i],alpha=0.6)
	plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=4,
  	         ncol=4, mode="expand", borderaxespad=0.)
	plt.subplot(312)
	plt.xlabel("Phase")
	plt.ylabel(ylab)
	plt.plot([0.,1.],[0.,0.],'k--')
	for i in range(0,nt):
	  plt.errorbar(p_all[i],res[i],errs_all[i],\
		label=telescopes[i],fmt=mark[i],alpha=0.6)
	plt.show()
