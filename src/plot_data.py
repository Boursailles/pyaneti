#Let us do the plots here

from matplotlib import gridspec
from matplotlib.colors import LogNorm

#The size of our plots follow an aurea rectangle 
fsx = 6
fsy = 3.708

def plot_chains():
  plt.xlabel('iteration')
  plt.ylabel('$\chi^2$')
  if (nplanets == 1):
   plt.plot(vari,chi2red,'b.')
  else:
   plt.plot(vari[0],chi2red[0],'b.')
  plt.show()

def plot_rv_fancy(p_rv,rvy,p_all,rv_dum,errs_all,res,telescopes_labels,fname):
  plt.figure(3,figsize=(fsx,fsy))
  gs = gridspec.GridSpec(nrows=2, ncols=1, height_ratios=[3., 1.])
  gs.update(hspace=0.00) 
  ax0 = plt.subplot(gs[0])
  plt.minorticks_on()
  #plt.subplot(311)
  ax0 = plt.xlabel("")
  ax0 = plt.ylabel("RV (m/s)")
  ax0 = plt.plot([0.,1.],[0.,0.],'k--')
  ax0 = plt.plot(p_rv,rvy,'k',linewidth=1.0)
  mark = ['o', 'd', '^', '<', '>', '8', 's', 'p', '*']
  for j in range(0,nt):
    ax0 = plt.errorbar(p_all[j],rv_dum[j],errs_all[j],\
    label=telescopes_labels[j],fmt=mark[j],alpha=1.0)
  plt.legend(loc=0, ncol=1,scatterpoints=1,numpoints=1,frameon=False,fontsize='small')
  plt.xticks(np.arange(0.,1.01,0.1)) 
  plt.tick_params( axis='x',which='both',labelbottom='off') 
  #plt.subplot(312)
  ax1 = plt.subplot(gs[1])
  plt.xlabel("Orbital phase")
  plt.tick_params( axis='x',which='minor',bottom='on',left='on',right='on',top='on') 
  plt.xticks(np.arange(0.,1.01,0.1)) 
  plt.ylabel('Residuals (m/s)')
  plt.plot([0.,1.],[0.,0.],'k--',linewidth=1.0)
  for j in range(0,nt):
    plt.errorbar(p_all[j],res[j],errs_all[j],\
    label=telescopes_labels[j],fmt=mark[j],alpha=1.0)
  yylims = ax1.get_ylim()
  plt.yticks(np.arange(yylims[0],yylims[1],(yylims[1]-yylims[0])/4.))
  plt.minorticks_on()
  plt.savefig(fname,format='pdf',bbox_inches='tight')
  plt.show()

#===========================================================
#                   One planet plots
#===========================================================

if ( nplanets == 1 ):

	#=========================#
	#       Transit plot      #
	#=========================#
	def plot_transit():
		  #Move all the points to T0
	  for i in range(0,ntr):
	    xt[i] = xt[i] - P_val * i 

	  #Redefine megax with the new xt values
	  megax = np.concatenate(xt)
          flag = [False, False, False, False]
	  z_val = pti.find_z(megax,[t0_val,P_val,e_val,w_val
		  ,i_val,a_val],flag)
	  mud_val, mu0_val = pti.occultquad(z_val,q1_val,q2_val\
		  ,pz_val)
	  #Residuals
	  res = megay - mud_val

          #Let us plot the binned model 

	  #Redefine megax with the new xt values
	  megax = np.concatenate(xt)
	  smegax = sorted(megax)
          flag = [False, False, False, False]

          xd_ub = np.ndarray(shape=(n_cad,len(smegax)))
          xd_ub_res = np.ndarray(shape=(n_cad,len(smegax)))
          zd_ub = [None]*n_cad
          zd_ub_res = [None]*n_cad
          fd_ub = [None]*n_cad
          fd_ub_res = [None]*n_cad
          for m in range(0,n_cad):
            for n in range(0,len(smegax)):
                xd_ub[m][n] = smegax[n] + t_cad * ( (m+1) - 0.5 * (n_cad + 1 )  ) / n_cad
                xd_ub_res[m][n] = megax[n] + t_cad * ( (m+1) - 0.5 * (n_cad + 1 )  ) / n_cad

          for m in range(0,n_cad):
             zd_ub[m] = pti.find_z(xd_ub[m][:],[t0_val,P_val,e_val,w_val,i_val,a_val],flag)
	     fd_ub[m], dummm = pti.occultquad(zd_ub[m],q1_val,q2_val,pz_val)
             zd_ub_res[m] = pti.find_z(xd_ub_res[m][:],[t0_val,P_val,e_val,w_val,i_val,a_val],flag)
	     fd_ub_res[m], dummm = pti.occultquad(zd_ub_res[m],q1_val,q2_val,pz_val)

	  fd_reb = [0.0]*len(megax)
	  fd_reb_res = [0.0]*len(megax)
          for m in range(0,len(megax)):
	    for n in range(0,n_cad):
             fd_reb[m] = fd_reb[m] + fd_ub[n][m]/n_cad
             fd_reb_res[m] = fd_reb_res[m] + fd_ub_res[n][m]/n_cad

          res_res = megay - fd_reb_res

	  #Get the model data to do the plot
	  nvec = int(1e5)
	  dx = ( max(megax) - min(megax) ) / nvec
	  xvec = np.zeros(nvec)
	  xvec[0] = min(megax)
	  for i in range(1,nvec):
	    xvec[i] = xvec[i-1] + dx
	  zvec = pti.find_z(xvec,[t0_val,P_val,e_val,w_val,i_val,a_val],flag)
	  mud, mu0 = pti.occultquad(zvec,q1_val,q2_val,pz_val)
	  #Now we have data to plot a nice model

	  #Do the plot
          tfc = 24. # time factor conversion to hours
	  plt.figure(1,figsize=(fsx,fsy))
	  #Plot the transit light curve
	  gs = gridspec.GridSpec(nrows=2, ncols=1, height_ratios=[3.0, 1.])
          gs.update(hspace=0.00) 
	  ax1 = plt.subplot(gs[0])
	  x_lim = (min(xt[0])-T0)*tfc
	  plt.xlim(x_lim,-x_lim)
          min_val_model = max(fd_reb) -  min(fd_reb)
	  plt.errorbar((megax-T0)*tfc,megay,megae,fmt='r.',alpha=1.0)
	  plt.plot((smegax-T0)*tfc,fd_reb,'k',linewidth=1.0)
          plt.ylabel('Relative flux')
          plt.xticks( np.arange(int(x_lim),int(-x_lim)+1,1))
          plt.minorticks_on()
          plt.ticklabel_format(useOffset=False, axis='y')
          plt.tick_params( axis='x',which='both',labelbottom='off') 
	  #Plot the residuals
	  dplot = plt.subplot(gs[1])
	  plt.plot((smegax-T0)*tfc,np.zeros(len(smegax)),'k--',linewidth=1.0)
	  plt.errorbar((megax-T0)*tfc,res_res,megae,fmt='r.',alpha=1.0)
          yylims = dplot.get_ylim()
          plt.yticks(np.arange(yylims[0],yylims[1],(yylims[1]-yylims[0])/4.))
          plt.xticks( np.arange(int(x_lim),int(-x_lim)+1,1))
	  plt.xlim(x_lim,-x_lim)
	  #Plot the residuals
          plt.ylabel('Residuals')
          plt.xlabel("T - T0 (hours)")
          plt.minorticks_on()
	  plt.savefig(outdir+'/'+star+plabels[0]+'_tr.pdf',format='pdf',bbox_inches='tight')
	  plt.show()


	#=========================#
	#        RV plot          #
	#=========================#

       #Plot without fold the data
	def plot_rv_all_data():
		cfactor = np.float(1.e3)
                rv_datas = list(rv_all)
                errs_datas = list(errs_all)
		for i in range(0,nt):
			for j in range(0,len(rv_all[i])):
				#rv_all[i][j] = cfactor*rv_all[i][j]
				#errs_all[i][j] = cfactor*errs_all[i][j]
				rv_datas[i][j] = cfactor*rv_datas[i][j]
				errs_datas[i][j] = cfactor*errs_datas[i][j]

                #Let us save all the RV data in rv_dum
		n = 5000
		xmin = min(np.concatenate(time_all)) - 10
		xmax = max(np.concatenate(time_all)) + 10
		dn = (xmax - xmin) /  n
		rvx = np.empty([n])
		rvx[0] = xmin
		for j in range(1,n):
			rvx[j] = rvx[j-1] + dn

                #Model curve
		rvy = pti.rv_curve_mp(rvx,0.0,t0_val,\
	        k_val*cfactor,P_val,e_val,w_val,alpha_val*cfactor,beta_val*cfactor)
		rv_dum = [None]*nt
		for j in range(0,nt):
			#This is the model of the actual planet
			#the actual value, minus the systemic velocity
			rv_dum[j] = rv_datas[j] - v_val[j]*cfactor

                plt.figure(1,figsize=(7,6))
                plt.plot(rvx,rvy,'k')
                plt.minorticks_on()
                plt.xlabel("JD (days)")
                plt.ylabel('RV (m/s)')
	        plt.xlim(xmin,xmax)
                mark = ['o', 'd', '^', '<', '>', '8', 's', 'p', '*']
                for j in range(0,nt):
                  plt.errorbar(time_all[j],rv_dum[j],errs_datas[j],\
                  label=telescopes_labels[j],fmt=mark[j],alpha=1.0)
                plt.legend(loc=0, ncol=1,scatterpoints=1,numpoints=1,frameon=False,fontsize='small')
		fname = outdir+'/'+star+plabels[0]+'_rv_all.pdf'
                plt.savefig(fname,format='pdf',bbox_inches='tight')
                plt.show()


#===========================================================

  #Plot RV for one planet
	def plot_rv_one():
		cfactor = np.float(1.e3)
                rv_dat2 = list(rv_all)
                errs_dat2 = list(errs_all)
		for i in range(0,nt):
			for j in range(0,len(rv_all[i])):
				rv_dat2[i][j] = cfactor*rv_dat2[i][j]
				errs_dat2[i][j] = cfactor*errs_dat2[i][j]

                #Let us save all the RV data in rv_dum
		n = 5000
		xmin = t0_val
		xmax = t0_val + P_val
		dn = (xmax - xmin) /  n
		rvx = np.empty([n])
		rvx[0] = xmin
		for j in range(1,n):
			rvx[j] = rvx[j-1] + dn

                #Model curve
		rvy = pti.rv_curve_mp(rvx,0.0,t0_val,\
	        k_val*cfactor,P_val,e_val,w_val,0.0,0.0)
		res = [None]*nt
		rv_dum = [None]*nt
		for j in range(0,nt):
			#This is the model of the actual planet
			res[j] = pti.rv_curve_mp(time_all[j],0.0,t0_val,k_val*cfactor,\
	      	         P_val,e_val,w_val,0.0,0.0)
			#res[j] = pti.rv_curve_mp(time_all[j],v_val[j],t0_val,k_dum,\
	      	        # P_val,e_val,w_val,alpha_val,beta_val)
			#the actual value, minus the systemic velocity
                        alpha_time = [None]*len(time_all[j])
                        beta_time = [None]*len(time_all[j])
                        for m in range(0,len(time_all[j])):
                          alpha_time[m] = (time_all[j][m]-t0_val)**1 * alpha_val * cfactor
                          beta_time[m]  = (time_all[j][m]-t0_val)**2 * beta_val  * cfactor

			rv_dum[j] = rv_dat2[j] - v_val[j]*cfactor - alpha_time - beta_time 
			res[j] = rv_dum[j] - res[j]

			p_rv = scale_period(rvx,t0_val,P_val)
			p_all = [None]*nt
			for j in range(0,nt):
				p_all[j] = scale_period(time_all[j],t0_val,P_val)

		fname = outdir+'/'+star+plabels[0]+'_rv.pdf'
                plot_rv_fancy(p_rv,rvy,p_all,rv_dum,errs_dat2,res,telescopes_labels,fname)


#===========================================================
#                   Multi-planet plots
#===========================================================

else:
	#Plot RV for multiplanet
	def plot_rv_mp():
		cfactor = np.float(1.e3)
		rvy = [None]*nplanets
		p_rv = [None]*nplanets
		k_dum = [None]*nplanets
		for i in range(0,nplanets):
			k_dum[i] = cfactor*k_val[i]
		for i in range(0,nt):
			v_val[i] = cfactor*v_val[i]
			for j in range(0,len(rv_all[i])):
				rv_all[i][j] = cfactor*rv_all[i][j]
				errs_all[i][j] = cfactor*errs_all[i][j]


		for i in range(0,nplanets):
			rv_dum = []
			for j in range(0,nt):
				rv_dum.append(rv_all[j])
			#Create the RV fitted model for the planet i
			n = 5000
			xmin = t0_val[i]
			xmax = t0_val[i] + P_val[i]
			dn = (xmax - xmin) /  n
			rvx = np.empty([n])
			rvx[0] = xmin
			for j in range(1,n):
				rvx[j] = rvx[j-1] + dn
			rvy[i] = pti.rv_curve_mp(rvx,0.0,t0_val[i],\
				k_dum[i],P_val[i],e_val[i],w_val[i],alpha_val[i]*cfactor \
                                , beta_val[i]*cfactor)

			dt0_val = []
			dk_dum = []
			dP_val = []
			de_val = []
			dw_val = []

			j = 0
			while ( j < nplanets ):
				if ( j != i ):
					dt0_val.append(t0_val[j])
					dk_dum.append(k_dum[j])
					dP_val.append(P_val[j])
					de_val.append(e_val[j])
					dw_val.append(w_val[j])
				j = j + 1


			res = [None]*nt
			drvy = [None]*nt
			for j in range(0,nt):
				#This is the model of the actual planet
				res[j] = pti.rv_curve_mp(time_all[j],0.0,t0_val[i],k_dum[i],\
	      	         P_val[i],e_val[i],w_val[i], cfactor*alpha_val[i], cfactor*beta_val[i])

				#This variable has all the others planets 
				drvy[j] = pti.rv_curve_mp(time_all[j],0.0,dt0_val,dk_dum \
									,dP_val,de_val,dw_val,
                                          alpha_val[i]*cfactor \
                                          ,beta_val[i]*cfactor)

				#the actual value, minus the systemic velocity, minus the other planets
				rv_dum[j] = rv_dum[j] - v_val[j] - drvy[j]
				res[j] = rv_dum[j] - res[j]

			p_rv[i] = scale_period(rvx,t0_val[i],P_val[i])
			p_all = [None]*nt
			for j in range(0,nt):
				p_all[j] = scale_period(time_all[j],t0_val[i],P_val[i])

                        fname = outdir+'/'+star+plabels[i]+'_rv.pdf'
                        plot_rv_fancy(p_rv[i],rvy[i],p_all,rv_dum,errs_all,res,telescopes_labels,fname)

#===========================================================
#                   Histogram plots
#===========================================================

def create_plot_histogram(params,plabs,cbars='red',nb=50):
	n = len(params)
	plt.figure(1,figsize=(15,4*(n)/2))
	gs = gridspec.GridSpec(nrows=(n+1)/2,ncols=2)
	for i in range(0,n):
		plt.subplot(gs[i])
		vpar, lpar, rpar = find_vals_perc(params[i],1.0)
          #      minchi2_val = params[i][minchi2_index]
		plt.axvline(x=vpar,c=cbars)
#		plt.axvline(x=minchi2_val,c='yellow')
		plt.axvline(x=vpar-lpar,c=cbars,ls='--')
		plt.axvline(x=vpar+rpar,c=cbars,ls='--')
		plt.xlabel(plabs[i])
		plt.hist(params[i],normed=True,bins=nb)

	plt.savefig(outdir+'/'+star+plabels[0]+'_histogram.pdf',format='pdf',bbox_inches='tight')
	plt.show()

def plot_histogram(rf=1):

	if ( fit_tr and fit_rv ):
		dparams = [t0o[0::rf],Po[0::rf],eo[0::rf],wo[0::rf],io[0::rf],ao[0::rf],q1o[0::rf],q2o[0::rf],pzo[0::rf],ko[0::rf]]
		dplabs = ['$T0$','$P$','$e$','$\omega$','$i$','$a/R_*$','$q_1$','$q_2$','$R_p/R_*$','$k$']

		vlabs = [None]*nt
		dumvo = [None]*nt
		for i in range(0,nt):
			vlabs[i] = 'rv0 ' + telescopes_labels[i]
			dumvo[i] = vo[i][0::rf]


		params = np.concatenate([dparams,dumvo])
		labs = np.concatenate([dplabs,vlabs])
	
		create_plot_histogram(params,labs)


	if ( fit_tr and not fit_rv ):
		params = [t0o[0::rf],Po[0::rf],eo[0::rf],wo[0::rf],io[0::rf],ao[0::rf],q1o[0::rf],q2o[0::rf],pzo[0::rf]]
		labs = ['$T0$','$P$','$e$','$\omega$','$i$','$a/R_*$','$q_1$','$q_2$','$R_p/R_*$']
	
		create_plot_histogram(params,labs)

	if ( not fit_tr and fit_rv ):
		if (nplanets == 1 ):
			dparams = [t0o[0::rf],Po[0::rf],eo[0::rf],wo[0::rf],ko[0::rf],alphao[0::rf],betao[0::rf]]
			dplabs = ['$T0$','$P$','$e$','$\omega$','$k$','alpha','beta']
		else:
			dparams = [None]*(7*nplanets)
			dplabs = [None]*(7*nplanets)
			for i in range(0,nplanets):
				dparams[0+7*i] = t0o[i][0::rf]
				dparams[1+7*i] = Po[i][0::rf]
				dparams[2+7*i] = eo[i][0::rf]
				dparams[3+7*i] = wo[i][0::rf]
				dparams[4+7*i] = ko[i][0::rf]
				dparams[5+7*i] = alphao[i][0::rf]
				dparams[6+7*i] = betao[i][0::rf]
				dplabs[0+7*i] = 'T0'+plabels[i]
				dplabs[1+7*i] = 'P'+plabels[i]
				dplabs[2+7*i] = 'e'+plabels[i]
				dplabs[3+7*i] = '$\omega$'+plabels[i]
				dplabs[4+7*i] = 'k'+plabels[i]
				dplabs[5+7*i] = '$\\alpha$'+plabels[i]
				dplabs[6+7*i] = '$\\beta$'+plabels[i]

		vlabs = [None]*nt
		dvo = [None]*nt
		for i in range(0,nt):
			vlabs[i] = 'rv0 ' + telescopes_labels[i] + plabels[i]
			dvo[i] = vo[i][0::rf]


		params = np.concatenate([dparams,dvo])
		labs = np.concatenate([dplabs,vlabs])
	
		create_plot_histogram(params,labs)


#===========================================================
#                   Correlation plots
#===========================================================

def create_plot_correlation(params,plabs,col='red',mark='.'):
	n = len(params)
	plt.figure(1,figsize=(2*n,2*n))
	gs = gridspec.GridSpec(nrows=n,ncols=n)
	for i in range(0,n):
		for j in range(0,i):
			plt.subplot(gs[i*n+j])
			if ( j == 0 ):
				plt.ylabel(plabs[i])
			elif ( j == i - 1 ):
				#plt.colorbar() 
				plt.tick_params( axis='y',which='both',labelleft='off') 
			else:
				plt.tick_params( axis='y',which='both',labelleft='off') 
			if ( i == n-1):
				plt.xlabel(plabs[j])
			else:
				plt.tick_params( axis='x',which='both',labelbottom='off') 
			#plt.plot(params[j],params[i],c=col,marker=mark,ls='',alpha=0.5)

                        plt.hist2d(params[j],params[i],bins=100,norm=LogNorm())
	plt.savefig(outdir+'/'+star+plabels[0]+'_correlations.pdf',format='pdf',bbox_inches='tight')
	plt.show()

def plot_correlations(rf=1):

	if ( fit_tr and fit_rv ):
		dparams = [t0o[0::rf],Po[0::rf],eo[0::rf],wo[0::rf],io[0::rf],ao[0::rf],q1o[0::rf],q2o[0::rf],pzo[0::rf],ko[0::rf]]
		dplabs = ['$T0$','$P$','$e$','$\omega$','$i$','$a/R_*$','$q_1$','$q_2$','$R_p/R_*$','$k$']

		vlabs = [None]*nt
		dvo = [None]*nt
		for i in range(0,nt):
			vlabs[i] = 'rv0 ' + telescopes_labels[i]
			dvo[i] = vo[i][0::rf]

		params = np.concatenate([dparams,dvo])
		labs = np.concatenate([dplabs,vlabs])
	
		create_plot_correlation(params,labs,col='blue')


	if ( fit_tr and not fit_rv ):

		params = [t0o[1::rf],Po[1::rf],eo[1::rf],wo[1::rf],io[1::rf],ao[1::rf],q1o[1::rf],q2o[1::rf],pzo[1::rf]]
		labs = ['$T0$','$P$','$e$','$\omega$','$i$','$a/R_*$','$q_1$','$q_2$','$R_p/R_*$']
	
		create_plot_correlation(params,labs,col='blue')

	#Now it works only for RV fit	
	if ( not fit_tr and fit_rv ):
		if ( nplanets == 1 ):
			dparams = [t0o[1::rf],Po[1::rf],eo[1::rf],wo[1::rf],ko[1::rf],alphao[1::rf],betao[1::rf]]
			dplabs = ['$T0$','$P$','$e$','$\omega$','$k$','alpha','beta']
		else:
			dparams = [None]*(7*nplanets)
			dplabs = [None]*(7*nplanets)
			for i in range(0,nplanets):
				dparams[0+7*i] = t0o[i][1::rf]
				dparams[1+7*i] = Po[i][1::rf]
				dparams[2+7*i] = eo[i][1::rf]
				dparams[3+7*i] = wo[i][1::rf]
				dparams[4+7*i] = ko[i][1::rf]
				dparams[5+7*i] = alphao[i][1::rf]
				dparams[6+7*i] = betao[i][1::rf]
				dplabs[0+7*i] = 'T0'+ plabels[i]
				dplabs[1+7*i] = 'P'+ plabels[i]
				dplabs[2+7*i] = 'e'+ plabels[i]
				dplabs[3+7*i] = '$\omega$'+ plabels[i]
				dplabs[4+7*i] = '$k$'+ plabels[i]
				dplabs[5+7*i] = '$\\alpha$'+ plabels[i]
				dplabs[6+7*i] = '$\\beta$'+ plabels[i]

		vlabs = [None]*nt
		dvo = [None]*nt
		for i in range(0,nt):
			vlabs[i] = 'rv0 ' + telescopes_labels[i]
			dvo[i] = vo[i][1::rf]


		params = np.concatenate([dparams,dvo])
		labs = np.concatenate([dplabs,vlabs])
	
		create_plot_correlation(params,labs,col='blue')

