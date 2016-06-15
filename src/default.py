#-----------------------------------------------------------
#                       default.py
#  This file contains the defalut values to run pyaneti.
#  You can change all the values here. You can also control
#	 the values in input_file.py
#                 O. Barragan, March 2016
#-----------------------------------------------------------

#Constants
#Solar and planetary constants according to IAU 2015
# http://adsabs.harvard.edu/cgi-bin/bib_query?arXiv:1605.09788
#Sun
S_radius_SI    = 6.957e8       	  #m
S_radius_cgs   = S_radius_SI*1e2  #cm
S_GM_SI        = 1.3271244e20     #m^3 s^{-1} 
S_GM_cgs       = S_GM_SI*1e6      #cm^3 s^{-1} 
G_SI	       = 6.67408e-11      #m^3 kg^{-1} s^{-2}		
G_cgs	       = G_SI*1e3         #cm^3 g^{-1} s^{-2}
S_vol_SI       = 4./3.*np.pi*S_radius_SI**3  #m^3 
S_vol_cgs      = 4./3.*np.pi*S_radius_cgs**3 #cm^3
S_den_SI       = S_GM_SI/G_SI/S_vol_SI    #kg/m^3
S_den_cgs      = S_GM_cgs/G_cgs/S_vol_cgs #g/cm^3
#Earth
E_GM_SI        = 3.986004e14      #m^3 s^{-1} 
E_radius_e_SI  = 6.3781e6         # ecuatorial radius [m]
E_radius_p_SI  = 6.3568e6         # polar radius [m]
#Jupiter
J_GM_SI        = 1.2668653e17     #m^3 s^{-1} 
J_radius_e_SI  = 7.1492e7         # ecuatorial radius [m]
J_radius_p_SI  = 6.6854e7         # polar radius [m]
#Other constants
AU_SI = 1.4960e11 # m

#Plot parameters
units_ms = False
ylab = 'RV (km/s)'
ktom = 1.0
mstar_mean = 1.0
rstar_mean = 1.0
mstar_sigma = 0.0
rstar_sigma = 0.0

#Transit data cadence
n_cad = 10
t_cad = 29.425 / 60. / 24.

#No telescopes
telescopes = []

#MCMC controls
method = 'sm'
is_circular = False
ics = False
prec = 1.e-4
maxi = int(1e8)
thin_factor = int(5e3)
nconv = 100
errores='perc'
nwalkers = 100
unit_mass = 'solar'
scale_error_bars = True
s_factor = 1.0
a_factor = 2.0

columns_tr = [0,1]

#Default priors
P = 15.
e = 0.1
w = 3.1415926 / 2.0
ii = 3.1415026 / 2.0
inclination = ii
a = 13.0
q1 = 0.42
q2 = 0.25
pz = 0.5
k0 = 1.0
v0 = 0.0


columns_tr = [0,1,2]

#Transit fit
nbin = 16

#The defaul number of planets is 1
nplanets = 1

#Fit nothing
fit_rv = False
fit_tr = False

#All the parameters are fitted
#by default
fit_t0  = True
fit_P   = True
fit_e   = True
fit_w   = True
#transit fit
fit_i   = True
fit_a   = True
fit_q1  = True
fit_q2  = True
fit_pz  = True
#rv fit
fit_k   = True
fit_v0  = True


#flags
is_log_P     = False
is_ew        = False
is_sini      = False
is_log_a     = False
is_log_k     = False
is_log_rv0   = False

#Limits
min_t0  = 0.0          #days
max_t0  = 1e6          #days
min_P   = 0.1 	       #days
max_P   = 1e4 	       #days
min_e   = 1.e-10       #zero
max_e   = 0.999	       #one
min_w   = 0.0	       #rad
max_w   = 2*np.pi      #rad
#transit fit
min_i   = 1.22173      # 70 degrees
max_i   = np.pi / 2.0  # 90 degrees
min_a   = 1.5	       # The planet is outside the star
max_a   = 1.e8	       # The planet is really far
min_q1  = 0.0	       #
max_q1  = 1.0          #
min_q2  = 0.0	       #
max_q2  = 1.0	       #
min_pz  = 1.e-3	       # Earth size planet / sun
max_pz  = 0.99	       # a really big planet
#rv fit
min_k   = 5.e-4	       # m/s amplitudes
max_k   = 30.	       # a really big planet
min_rv0 = 1.	       #Systemic velocities
max_rv0 = 100.	       #systemic velocities

#Physical Limits
min_phys_t0  = 0.0          #days
max_phys_t0  = 1e6          #days
min_phys_P   = 0.1 	       #days
max_phys_P   = 1e4 	       #days
min_phys_e   = 0.0       #zero
max_phys_e   = 0.99999	       #one
min_phys_w   = 0.0	       #rad
max_phys_w   = 2*np.pi      #rad
#transit fit
min_phys_i   = 1.22173      # 70 degrees
max_phys_i   = np.pi / 2.0  # 90 degrees
min_phys_a   = 1.5	       # The planet is outside the star
max_phys_a   = 1.e4	       # The planet is really far
min_phys_q1  = 0.0	       #
max_phys_q1  = 1.0             #
min_phys_q2  = 0.0	       #
max_phys_q2  = 1.0	       #
min_phys_pz  = 1.e-3	       # Earth size planet / sun
max_phys_pz  = 0.99	       # a really big planet
#rv fit
min_phys_k   = 1.e-6           # m/s amplitudes
max_phys_k   = 30.	       # a really big planet
