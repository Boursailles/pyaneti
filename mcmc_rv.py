#More information about curve_fit in the following link
#http://docs.scipy.org/doc/scipy-0.16.0/reference/generated/scipy.optimize.curve_fit.html

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import sys

#-----------------------------------
#This function find the eccentry anomaly by using the
#Newton-Rapshon method
#Input values are man -> array, ecc -> float
def find_anomaly(man,ecc,delta=1.e-4,imax=5000):
	#Let us start with a zero value for the anomaly
	anomaly = [0.0]*len(man)
	anomaly = np.array(anomaly)
	#Let us find the eccentric anomally by using Newton-Raphson
	f  = anomaly - ecc * np.sin(anomaly) - man
	df =	   1.0 - ecc * np.cos(anomaly)
	counter = 0
	#Let us do it for all the man values
	for i in range(0,len(man)):
		counter = 0
			#Do we find the zero of f?
		while ( np.absolute(f[i]) >= delta):
			dum = anomaly[i] - f[i] / df[i]
			anomaly[i] = dum
			f[i] = anomaly[i] - ecc * np.sin(anomaly[i]) - man[i]
			df[i]=	1 - ecc * np.cos(anomaly[i])
			#Let us use a counter to get rid off of infinite loops
			counter = counter + 1
			if (counter > imax):
				sys.exit("I am tired!")
	#The result is the eccentric anomaly vector!
	#Now we have the eccentric anomaly, let us calculate
	#The TRUE anomaly
	anomaly = np.sqrt(1+ecc/(1-ecc)) * np.tan(anomaly/2.0)
	anomaly = 2. * np.arctan(anomaly)
	#Now we have calculated the true anomaly :-)!
	return anomaly	
#-------------------------------------
	#This functions gives the rv functions
	#it assumes a circular orbit
def rv_circular(t,rv0,k):
	rv = rv0 - k * np.sin( 2.0 * np.pi * ( t - T0 ) / Porb )
	return rv
#------------------------------------
def rv_curve_rv0(t,rv0,k0,ecc,omega):
	#man is the mean anomally
	man = 2 * np.pi * (t - T0) / Porb
	#call to find_anomaly function to find the eccentric anomaly
	anomaly = find_anomaly(man,ecc)
	#The general equation for rv motion is
	rv = rv0 + k0 * (np.cos( anomaly + omega ) + ecc*np.cos( omega ) ) / np.sqrt(1.0 - ecc*ecc)
	return rv
#------------------------------------
def rv_curve(t,k0,ecc,omega):
	#man is the mean anomally
	man = 2 * np.pi * ( t - T0 ) / Porb
	#call to find_anomaly function to find the eccentric anomaly
	anomaly = find_anomaly(man,ecc)
	#The general equation for rv motion is
	rv = + k0 * (np.cos( anomaly + omega ) + ecc*np.cos( omega ) )  / np.sqrt(1.0 - ecc*ecc)
	return rv
#------------------------------------
#Extract systemic velocities is highly important
#so let us take care with this
def find_rv0(time,fase,err,tpe):
	#Let us first fit assuming a circular orbit 
	#(to first estimate v0 and k0)
	popt,pcov = curve_fit(rv_circular,time,fase,sigma=err)
	#These results will be our first guesses for v0 and k0
	rvc = popt[0]
	sdrvc= np.sqrt(pcov[0][0])
	kc  = popt[1]
	#Now let us fit again now with the guesses as input
	popt,pcov = curve_fit(rv_curve_rv0,time,fase,sigma=err,p0=[rvc,kc,0,0])
	#Let us check if the function is "ellipsable"
	#If we have two points, try to fit an elliptical orbit is not correct
	#If this is the case, the errors wll go to infinite, let us check this
	if ( np.isinf(pcov[0][0]) == True ): #Then the function is not ellipsable
		rv0 = rvc
		sdrv0= sdrvc
	else: #The function is ellipsable, let us keep playing with the fit!
		rv0 = popt[0]
		sdrv0 = pcov[0][0]
		k0 = popt[1]
		w = popt[2]
		#Now we have guesses for rv0, k0 and w, let us re do the fit, now to improve e
		popt,pcov = curve_fit(rv_curve_rv0,time,fase,sigma=err,p0=[rv0,k0,0,w])
		rv0= popt[0]
		sdrv0= np.sqrt(pcov[0][0])
	print ('for %1s -> rv0 = %5.5f +/- %5.5f m/s'%(tpe,rv0,sdrv0))
	return rv0
#-----------------------------
def scale_period(jd,T0,P):
	x = [None]*len(jd)
	for i in range(len(jd)):
		x[i] = ( ( jd[i] - T0 ) % P ) /  P
	return x
#-----------------------------
def planet_mass(mstar,k,P,ecc):
	#Gravitational costant
	Gc = 6.67408e-11 #m^3 / (kgs^2)
	Gc = Gc * 1.989e30 # m^3 / (Msun s^2)
	#period in seconds
	P = P * 24. * 3600
	mpsin = k * ( 2. * np.pi * Gc / P)**(-1./3.)  * \
	mstar**(2./3.) * np.sqrt( 1.0 - ecc*ecc )
	return mpsin
#-----------------------------

#----- HERE THE MAIN PROGRAM STARTS -----#

#Read the input parameters from input_rv.txt
idata = np.loadtxt('input_rv.txt',comments='#',unpack=True,dtype='S')

#Let us use all the read data
Porb = np.float(idata[0])
T0	 = np.float(idata[1])
tpes = idata[2]
fname= idata[3]
mstar= np.float(idata[4])
telescopes = [None]*len(idata[2])
for i in range(0,len(idata[2])):
	telescopes[i] = idata[2][i]
#

#Read the data file
time,fase,err,tspe = np.loadtxt(fname,usecols=(0,1,2,3), \
  dtype={'names': ('time', 'fase', 'err','telescope'), \
	'formats': ('float', 'float', 'float', 'S1')}, \
	comments='#',unpack=True)

#Transform fase from km/s to m/s
fase=fase*1000.
err=err*1000.

#These lists have lists with data for the different telescopes
time_all=[]
fase_all=[]
errs_all=[]

#Number of telescopes
nt = len(telescopes)

#tspe is the data with the telescopes read from the file
for i in range(0,nt):
	time_dum =[]
	fase_dum =[]
	errs_dum =[]
	if (len(telescopes[i]) == 0):
		print ("There is no data for %s"% telescopes[i])
	else:
		for j in range(0,len(tspe)):
			if (tspe[j] == telescopes[i]):
				time_dum.append(time[j])
				fase_dum.append(fase[j])
				errs_dum.append(err[j])
	#The *all variables are lists of lists, each list constains
	# a list with the data of each telescope
		time_all.append(time_dum)
		fase_all.append(fase_dum)
		errs_all.append(errs_dum)

print ("Extracting systemic velocities for the %i telescopes"%nt)
#Find all the systematic velocities and put them in rv0_all
rv0_all=[None]*nt
for i in range(0,nt):
	rv0_all[i] = find_rv0(time_all[i],fase_all[i],errs_all[i],telescopes[i])

#Let us take off the offset for each telescope
for i in range(0,nt): #each i is a different telescope
	for j in range(0,len(fase_all[i])):
		fase_all[i][j] = fase_all[i][j] - rv0_all[i]

#The mega* variables contains all telescope data
mega_fase = []
mega_time = []
mega_err  = []
for i in range(0,nt):
	for j in range(0,len(fase_all[i])):
		mega_fase.append(fase_all[i][j])
		mega_time.append(time_all[i][j])
		mega_err.append(errs_all[i][j])


# MCMC calculation starts here

def find_chi(xd,yd,errs,rv0,k):
	chi2 = 0.0
	xd = np.array(xd)
	mod_i = rv_circular(xd,rv0,k) #model fit
	res = (yd - mod_i) / errs
	for i in range(0,len(yd)):
		chi2 = chi2 + res[i]*res[i]
	return chi2

#Let us initialize the MCMC Metropolis-Hasting algorithm
imcmc = 500000
v0 = 80.0
k0 = 10.0
vmc = np.empty(imcmc)
kmc  = np.empty(imcmc)
vmc[0] = v0
kmc[0] = k0
chi_old = find_chi(mega_time,mega_fase,mega_err,vmc[0],kmc[0]) 
step = 0.1
print 'Calculating %i MCMC steps'%imcmc
for i in range(1,imcmc):
	vmc[i] = vmc[i-1] + ((np.random.rand(1) - 0.5)*2)*step
	kmc[i] = kmc[i-1] + ((np.random.rand(1) - 0.5)*2)*step
	chi_new = find_chi(mega_time,mega_fase,mega_err,vmc[i],kmc[i]) 
	q = np.exp((chi_old - chi_new)/2.0)	
	if ( q < np.random.rand(1) ):
		chi_old = chi_old
		vmc[i] = vmc[i-1]
		kmc[i] = kmc[i-1]
	else:
		chi_old = chi_new

plt.figure(1,figsize=(8,4))
plt.xlabel("Iteration")
plt.ylabel("Value")
plt.plot(vmc,label='v0')
plt.plot(kmc,label='k')
plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=4,
           ncol=4, mode="expand", borderaxespad=0.)
plt.show()

kval = sum(kmc)/imcmc
vval = sum(vmc)/imcmc

# MCMC calculation finishes here

#Now let us calculate the plantary mass
e = 0.0
k = np.absolute(kval)

mpsin = planet_mass(mstar,k,Porb,e)
mjup = 0.0009543
mearth = 0.000003003 

#Print the results
print (' k = %4.4e +/- %4.4e m/s' %(k,0))
#print (' w = %4.4e +/- %4.4e rad' %(w,sigw))
#print (' e = %4.4e +/- %4.4e    ' %(e,sige))

print ('Planet mass of %1.4e M_j (for a %2.2f solar mass star)' % (mpsin/mjup, mstar))

#Let us do a nice plot

#Create the RV fitted curve
n = 500
xmin = T0
xmax = T0 + Porb
dn = (xmax - xmin) /  n  
rvx = np.empty([n])
rvx[0] = xmin 
for i in range(1,n):
	rvx[i] = rvx[i-1] + dn
#rvy = rv_curve(rvx,k,e,w)
rvy = rv_circular(rvx,vval,kval)

p_rv = scale_period(rvx,T0,Porb)
p_all = [None]*nt
for i in range(0,nt):
	p_all[i] = scale_period(time_all[i],T0,Porb)

#error bars -> http://matplotlib.org/1.2.1/examples/pylab_examples/errorbar_demo.html
plt.figure(2,figsize=(8,4))
plt.xlabel("Phase")
plt.ylabel("k (m/s)")
#plt.ylim(1.5*min(rvy),max(rvy)*1.5)
plt.plot(p_rv,rvy,'k',label=('k=%2.2f m/s'%k ))
mark = ['o', 'd', '^', '<', '>', '8', 's', 'p', '*', 'h', 'H', 'D', 'v']
for i in range(0,nt):
	plt.errorbar(p_all[i],fase_all[i],errs_all[i],label=telescopes[i],fmt=mark[i])
#plt.legend()
plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=4,
           ncol=4, mode="expand", borderaxespad=0.)
plt.savefig('rv_fit.png')
plt.show()

