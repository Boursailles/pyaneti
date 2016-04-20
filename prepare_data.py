#-----------------------------------------------------------
#                       prepare_data.py
#  This file contains all the variable initializations,
#  both for RV and Transit fittings.
#                   O. Barragan, March 2016
#-----------------------------------------------------------


#-----------------------------------------------------------
#                         RV DATA
#-----------------------------------------------------------

if (fit_rv):

	#Read the data file
	#time, RV, errors, and Telescope label
	time,rv,err,tspe = np.loadtxt(fname_rv,usecols=(0,1,2,3), \
  	dtype={'names': ('time', 'rv', 'err','telescope'), \
		'formats': ('float', 'float', 'float', 'S1')}, \
		comments='#',unpack=True)

	#Transform rv from km/s to m/s
	if(units_ms):
		ktom = 1000
		rv   = rv*ktom
		err  = err*ktom
		ylab = 'RV (m/s)'
	
	#These lists have lists with data for 
	#the different telescopes
	time_all = []
	rv_all   = []
	errs_all = []

	#Number of telescopes
	nt = len(telescopes)

	if ( nt < 1 ):
		print 'Please, indicate the telescope labels!'
		sys.exit('')

	#Separate the data for each telescope and create labels
	for i in range(0,nt):
		time_dum = []
		rv_dum   = []
		errs_dum = []
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

	#The mega* variables contains all the data 
	#All this is neccesary because you do not have
	#the same number of data for each telescope
	mega_rv   = []
	mega_time = []
	mega_err  = []
	tlab      = []
	#create mega with data of all telescopes
	for i in range(0,nt): 
		#fill the mega variable with all the data of the
		#telescope i
		for j in range(0,len(rv_all[i])):
			#tlab has the label of the telescope (an integer)
			#this is useful because matches with the index of 
			#the mega variables
			tlab.append(i)
			mega_rv.append(rv_all[i][j])
			mega_time.append(time_all[i][j])
			mega_err.append(errs_all[i][j])

#RV DATA READY

#-----------------------------------------------------------
#                     TRANSIT DATA
#-----------------------------------------------------------

if (fit_tr):

	#Read the data file
	#heliocentric date, dummyf, flag (is it a good datapoint?)
	#Take care with this, it is assuming a corot data file
	dummyd,dummyf,flag = np.loadtxt(fname_tr,usecols=(2,9,10), \
	comments='\\',unpack=True)

        dummyd = dummyd - 16./3600./24.
	#Let us take the good data with the flag
	nobin_wflux = []
	nobin_hdate = []
	for i in range(0,len(flag)):
		if ( flag[i] == 0):
			nobin_wflux.append(dummyf[i])
			nobin_hdate.append(dummyd[i])

	#bin the data each nbin
	hdate = bin_data_median(nobin_hdate,nbin)
	wflux, errs = bin_data_mean(nobin_wflux,nbin)

	#THIS HAS TO BE DONE AUTOMATICALLY!	
	#Find the transits

	ntr = 2

	tls = [None]*ntr

	tls[0] = [3217.,3218.]
	tls[1] = [3232.1,3233.1]

	#crash if you do not have more than one transit
	if ( ntr < 2):
		print "you do not have enought transit data!"
		sys.exit("I crashed because I want more data!")
	
	#Each element of these lists will have the information
	#of a given transit
	xt= [None]*ntr	
	yt= [None]*ntr	
	et= [None]*ntr	

	#Normalize all the transit independently
	#the transit data is inside the limits tls
	for i in range(0,ntr):
		xt[i],yt[i],et[i] = normalize_transit(hdate,wflux,errs,tls[i])

	#Let us put together the information of all the arrays
	#the mega* lists have the data of all the transits
	#in 1D array
	megax = np.concatenate(xt)
	megay = np.concatenate(yt)
	megae = np.concatenate(et)

#TRANSIT DATA READY

