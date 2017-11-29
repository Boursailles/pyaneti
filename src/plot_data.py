#Let us do the plots here
from matplotlib import gridspec
from matplotlib.colors import LogNorm

if ( is_seaborn_plot ):
  import seaborn as sns
  sns.set(style='ticks')
  sns.set_color_codes(seaborn_palette)

fsx = figure_size_x
fsy = figure_size_y
fos = font_size_label

vari = params[0]
chi2 = params[2] + params[3]


#===========================================================
#              plot chains
#===========================================================

def plot_chains():
  plt.xlabel('iteration')
  plt.ylabel('Reduced $\chi^2$')
  plt.hist2d(vari,chi2/(ndata-npars),bins=50)
  fname = outdir+'/'+star+'_chains.pdf'
  print 'Creating ', fname
  plt.savefig(fname,bbox_inches='tight')
  plt.close()

def plot_likelihood():
  plt.xlabel('iteration')
  plt.ylabel('$\ln \mathcal{L}$')
  plt.hist2d(vari,par_likelihood,bins=50)
  fname = outdir+'/'+star+'_likelihood.pdf'
  print 'Creating ', fname
  plt.savefig(fname,bbox_inches='tight')
  plt.close()
##===========================================================
#              plot tr fancy function
#===========================================================

#Ntransit is the number of the transit that we want to plot
def fancy_tr_plot(t0_val,xtime,yflux,errors,xmodel,xmodel_res,fd_reb,res_res,fname):

  print 'Creating ', fname
  #Do the plot
  tfc = 24. # time factor conversion to hours
  local_T0 = t0_val
  plt.figure(1,figsize=(fsx,fsy))
  #Plot the transit light curve
  gs = gridspec.GridSpec(nrows=2, ncols=1, height_ratios=[3.0, 1.])
  gs.update(hspace=0.00)
  ax1 = plt.subplot(gs[0])
  plt.tick_params(labelsize=fos,direction='in')
  x_lim = (min(xtime)-local_T0)*tfc
  plt.xlim(x_lim,-x_lim)
  if ( select_y_tr ):
    plt.ylim(y_lim_min,y_lim_max)
  min_val_model = max(fd_reb) -  min(fd_reb)
  if ( plot_tr_errorbars ):
    plt.errorbar((xtime-local_T0)*tfc,yflux,errors,color=tr_colors,fmt='.',alpha=1.0)
  else:
    plt.plot((xtime-local_T0)*tfc,yflux,'o',color=tr_colors,ms=8,alpha=0.8)
    y0,yyyy = ax1.get_ylim()
    plt.errorbar(-x_lim*(0.95),y0 +errors[0]*2,errors[0],color=tr_colors,fmt='o',alpha=1.0)
    plt.annotate('Error bar',xy=(-x_lim*(0.70),y0 +errors[0]*1.75),fontsize=fos*0.7)
  plt.plot((xmodel-local_T0)*tfc,fd_reb,'k',linewidth=2.0,alpha=1.0)
  plt.ylabel('Relative flux',fontsize=fos)
  #Calculate the optimal step for the plot
  step_plot = int(abs(x_lim)) #the value of the x_axis
  step_plot = step_plot + int( step_plot % 2 ) # now we ensure the result is par
  step_plot = int ( step_plot / 8. ) + 1 #The size of the jump depends
  #let us get the new limit
  nuevo = np.arange(0,int(abs(x_lim)) + step_plot ,step_plot)
  mxv = np.max(nuevo)
#  plt.xticks( np.arange(int(x_lim),int(-x_lim)+1,step_plot))
  plt.xticks( np.arange(-mxv,mxv+step_plot,step_plot))
  plt.minorticks_on()
  plt.ticklabel_format(useOffset=False, axis='y')
  plt.xlim(x_lim,-x_lim)
  plt.tick_params( axis='x',which='both',direction='in',labelbottom='off')
  plt.tick_params( axis='y',which='both',direction='in')
  #Plot the residuals
  ax0 = plt.subplot(gs[1])
  plt.tick_params(labelsize=fos,direction='in')
  if ( plot_tr_errorbars ):
    plt.errorbar((xmodel_res-local_T0)*tfc,res_res*1e6,errors,color=tr_colors,fmt='.',alpha=1.0)
  else:
    plt.plot((xmodel_res-local_T0)*tfc,res_res*1e6,'o',color=tr_colors,ms=8,alpha=0.8)
  plt.plot([x_lim,-x_lim],[0.0,0.0],'k--',linewidth=1.0,alpha=1.0)
  plt.xticks( np.arange(-mxv,mxv+step_plot,step_plot))
  plt.xlim(x_lim,-x_lim)
  yylims = ax0.get_ylim()
  miy = (max(abs(yylims[0]),abs(yylims[1])))
  plt.yticks(np.arange(-miy,miy,miy/2.))
  plt.ylim(-miy,miy*1.25)
  #Calcualte the rms
  if ( is_plot_std_tr ):
    trsigma = np.std(res_res*1e6,ddof=1)
    trsstr = ('%4.0f ppm'%(trsigma))
    y0,yyyy = ax0.get_ylim()
    plt.annotate('$\sigma = $'+trsstr,xy=(x_lim*(0.80),y0 + 1.8*miy),fontsize=fos*0.7)
#  if ( select_y_tr ):
#    plt.ylim( - ( y_lim_max - 1.0),y_lim_max - 1.0 )
  #Plot the residuals
  plt.minorticks_on()
  plt.tick_params( axis='x',which='both',direction='in')
  plt.tick_params( axis='y',which='both',direction='in')
  plt.ylabel('Residuals (ppm)',fontsize=fos*0.75)
  plt.xlabel("T - T0 (hours)",fontsize=fos)
  plt.savefig(fname,format='pdf',bbox_inches='tight')
  plt.savefig(fname[:-3]+'png',format='png',bbox_inches='tight',dpi=300)
  plt.close()

#-----------------------------------------------------------------
#       TRANSIT PARAMERS TO BE USED TO GENERATE PLOTS
#-----------------------------------------------------------------

ldc = [ best_value(params[4+8*nplanets],maxloglike,get_value), best_value(params[5+8*nplanets],maxloglike,get_value) ]
q1_val = ldc[0]
q2_val = ldc[1]
u1_val = np.sqrt(q1_val)
u2_val = u1_val * (1.0 -2.0*q2_val)
u1_val = 2.0*u1_val*q2_val
flag = [False]*4
my_ldc = [u1_val,u2_val]

t0_val = [None]*nplanets
tp_val = [None]*nplanets
P_val  = [None]*nplanets
e_val  = [None]*nplanets
w_val  = [None]*nplanets
i_val  = [None]*nplanets
a_val  = [None]*nplanets
rp_val = [None]*nplanets

base = 4
for m in range(0,nplanets):
  t0_val[m] = best_value(params[base + 0],maxloglike,get_value)
  P_val[m]  = best_value(params[base + 1],maxloglike,get_value)
  e_val[m]  = best_value(params[base + 2],maxloglike,get_value)
  w_val[m]  = best_value(params[base + 3],maxloglike,get_value)
  i_val[m]  = best_value(params[base + 4],maxloglike,get_value)
  a_val[m]  = best_value(params[base + 5],maxloglike,get_value)
  rp_val[m] = best_value(params[base + 6],maxloglike,get_value)
  base = base + 8


  if ( is_den_a ):
    a_val[m] = a_val[0]*(P_val[m]*P_val[m]*7464960000.*G_cgs/3.0/np.pi)**(1./3.)
    if ( m > 0):
      a_val[m] = (P_val[m]/P_val[0])**(2./3.)*a_val[0]

  #Check flags
  #Change between b and i
  if ( is_b_factor ):
    i_val[m] = np.arccos( i_val[m] / a_val[m] * \
            ( 1.0 + e_val[m] * np.sin(w_val[m] + np.pi) / ( 1.0 - e_val[m]**2 ) ) )

  if ( is_ew ):
    e_dum = e_val[m]
    w_dum = w_val[m]
    e_val[m] = e_val[m]**2 + w_val[m]**2
    w_val[m] = np.arctan2(e_dum,w_val[m])
    w_val[m] = w_val[m] % (2*np.pi)

  tp_val[m] = pti.find_tp(t0_val[m],e_val[m],w_val[m],P_val[m])

  #Create parameters vector
  pars_tr = np.zeros(shape=(7,nplanets))
  for m in range(0,nplanets):
      pars_tr[0,m] = tp_val[m]
      pars_tr[1,m] = P_val[m]
      pars_tr[2,m] = e_val[m]
      pars_tr[3,m] = w_val[m]
      pars_tr[4,m] = i_val[m]
      pars_tr[5,m] = a_val[m]
      pars_tr[6,m] = rp_val[m]

#===========================================================
#              plot the folded data for each transit
#===========================================================
def plot_transit_nice():

  for o in range(0,nplanets):

    if ( fit_tr[o] ):


      if ( len(span_tr) < 1 ):
          local_span = 0.0
      else:
          local_span = span_tr[o]

      local_time_d, xtime_d, yflux_d, eflux_d = create_transit_data(megax,megay,megae,o,local_span)

      local_time = np.concatenate(local_time_d)
      xtime = np.concatenate(xtime_d)
      yflux = np.concatenate(yflux_d)
      eflux = np.concatenate(eflux_d)

      xmodel_res = xtime
      xmodel = np.arange(min(xtime), max(xtime),1.0/20./24.)
      #Let us create the model

      #The model has T0 = 0
      dumtp = pti.find_tp(0.0,e_val[o],w_val[o],P_val[o])
      dparstr = np.concatenate([[dumtp],pars_tr[1:,o]])
      fd_ub = pti.flux_tr(xmodel,dparstr,flag,my_ldc,n_cad,t_cad)
      #Calculate the flux to copute the residuals
      fd_ub_res = pti.flux_tr(xmodel_res,dparstr,flag,my_ldc,n_cad,t_cad)

      #Define a vector which will contain the data of other planers for multi fits
      fd_ub_total = list(fd_ub_res)
      fd_ub_total = np.zeros(shape=len(fd_ub_res))

     #############################################################################
     # Let us calculate the flux caused by the other planets
      for p in range(0,nplanets):
        if ( p != o ):
          #fd_ub_total stores the flux of a star for each independent
          fd_ub_total = fd_ub_total + pti.flux_tr(local_time,pars_tr[:,p],flag,my_ldc,n_cad,t_cad)

      #Remove extra planets from the data
      yflux_local = yflux - fd_ub_total
      yflux_local = yflux_local - 1 + nplanets
      #The flux has been corrected for the other planets

      #Get the residuals
      res_res = yflux_local - fd_ub_res

     #############################################################################

      fname = outdir+'/'+star+plabels[o]+'_tr.pdf'
      #xtime is the folded time
      #yflux_local is the data flux
      #eflux is the error related to yflux
      #xmodel is the light curve model timestamps
      #xmodel_res is the residuals time_stamps
      #fd_reb is the modeled light cuve
      #res_res are the residuals
      fancy_tr_plot(0.0,xtime,yflux_local,eflux,xmodel,xmodel_res,fd_ub,res_res,fname)

#===========================================================
#              plot all transits
#===========================================================

def plot_all_transits():

  #Create the plot of the whole light
  model_flux = pti.flux_tr(megax,pars_tr,flag,my_ldc,n_cad,t_cad)
  res_flux = megay - model_flux

  for i in range(0,nplanets):
    if ( fit_tr[i] ):

      xt, dt, yt, et = create_transit_data(megax,megay,megae,i,span_tr[i])
      xt2, dt2, yt2, et2 = create_transit_data(megax,res_flux,megae,i,span_tr[i])

      if ( is_plot_all_tr[i] ):
        for j in range(0,len(xt)):
          xtm = np.arange(min(xt[j]),max(xt[j]),1./20./24.)
          ytm = pti.flux_tr(xtm,pars_tr,flag,my_ldc,n_cad,t_cad)

          fname = outdir+'/'+star+plabels[i]+'_transit'+str(j)+'.pdf'
          n = xt[j][len(xt[j])-1] - xt[0][0]
          n = int(n/P_val[i])
          fancy_tr_plot(t0_val[i]+P_val[i]*n,xt[j],yt[j],et[j],xtm,xt2[j],ytm,np.array(yt2[j]),fname)


#===========================================================
#              clean transits
#  This function cleans the light curve with a N-sigma aogorithm
#===========================================================

def clean_transits(sigma=10):

    #Now we are ready to call the function in fortran
    #All the data is in megax, megay and megae
    model_flux = pti.flux_tr(megax,pars_tr,flag,my_ldc,n_cad,t_cad)
    xvec_model = np.arange(min(megax),max(megax),1./20./24.)
    solution_flux = pti.flux_tr(xvec_model,pars_tr,flag,my_ldc,n_cad,t_cad)

    #Calcualte the residuals
    res_flux = megay - model_flux

    #Call the sigma clipping functions
    new_t, new_f = sigma_clip(megax,megay,res_flux,limit_sigma=sigma)

    #Recalculate the error bars
    new_model_flux = pti.flux_tr(new_t,pars_tr,flag,my_ldc,n_cad,t_cad)
    #New residuals
    new_res_flux = new_f - new_model_flux
    #Recompute the error bars from the std of the residuals
    new_err = np.std(new_res_flux,ddof=1)


    plt.figure(3,figsize=(5*fsx,fsy))
    fname = outdir+'/'+star+'_lightcurve.pdf'
    print 'Creating ', fname
    plt.plot(megax,megay,'ro')
    plt.plot(xvec_model,solution_flux,'k-')
    plt.plot(new_t,new_f,'bo')
    plt.ylabel('Flux',fontsize=fos*0.75)
    plt.xlabel(tr_xlabel,fontsize=fos)
    plt.xlim(min(megax),max(megax))
    plt.minorticks_on()
    plt.savefig(fname,format='pdf',bbox_inches='tight')
    plt.savefig(fname[:-3]+'png',format='png',bbox_inches='tight',dpi=300)
    plt.close()

    #Write the cleaned light curve into a file
    #Let us create or detrended file
    out_f = outdir+'/'+star+'_new_lc.dat'
    of = open(out_f,'w')
    for i in range(0,len(new_t)):
      of.write(' %8.8f   %8.8f  %8.8f \n'%(new_t[i],new_f[i],new_err))

    of.close()


#===========================================================
#              plot rv fancy function
#===========================================================

def plot_rv_fancy(p_rv,rvy,p_all,rv_dum,errs_all,res,telescopes_labels,fname):
  print 'Creating ', fname
  plt.figure(3,figsize=(fsx,fsy))
  gs = gridspec.GridSpec(nrows=2, ncols=1, height_ratios=[3., 1.])
  gs.update(hspace=0.00)
  ax0 = plt.subplot(gs[0])
  plt.tick_params(labelsize=fos,direction='in')
  plt.minorticks_on()
  #plt.subplot(311)
  plt.xlabel("")
  plt.ylabel("RV (m/s)",fontsize=fos)
  #plt.plot([0.,1.],[0.,0.],'k--')
  plt.plot(p_rv,rvy,'k',linewidth=1.0)
  for j in range(0,nt):
    #
    plt.errorbar(p_all[j],rv_dum[j],new_errs_all[j],\
    fmt=mark[j],\
    alpha=1.0 ,color='#C0C0C0',\
    markersize=rv_markersize,fillstyle=rv_fillstyle)
    #
    plt.errorbar(p_all[j],rv_dum[j],errs_all[j],\
    label=telescopes_labels[j],\
    fmt=mark[j],\
    alpha=1.0 ,color=rv_colors[j],\
    markersize=rv_markersize,fillstyle=rv_fillstyle)
  if ( is_rv_legend ): plt.legend(loc=2, ncol=1,scatterpoints=1,numpoints=1,frameon=True,fontsize=fos*0.7)
  plt.xticks(np.arange(0.,1.01,0.1))
  plt.tick_params( axis='x',which='both',direction='in',labelbottom='off')
  plt.tick_params( axis='y',which='both',direction='in')
  yylims = ax0.get_ylim()
  miy = int(max(abs(yylims[0]),abs(yylims[1])))
  if ( miy == 0): #To avoid errors for really small RV variations
    miy = max(abs(yylims[0]),abs(yylims[1]))
  plt.ylim(-miy,miy)
  plt.xlim(0.,1.)
  #plt.yticks(np.arange(-miy,miy,2.*miy/8.))
#  plt.yticks(np.arange(yylims[0],yylims[1],(yylims[1]-yylims[0])/7.))
  #NEW SUBPLOT
  ax1 = plt.subplot(gs[1])
  plt.tick_params(labelsize=fos,direction='in')
  plt.xlabel("Orbital phase",fontsize=fos)
  plt.tick_params( axis='x',which='minor',direction='in',bottom='on',left='on',right='on',top='on')
  plt.tick_params( axis='y',which='both',direction='in')
  plt.xticks(np.arange(0.,1.01,0.1))
  plt.ylabel('Residuals (m/s)',fontsize=fos*0.75)
  plt.plot([0.,1.],[0.,0.],'k--',linewidth=1.0)
  for j in range(0,nt):
    #
    plt.errorbar(p_all[j],res[j],new_errs_all[j],\
    fmt=mark[j],\
    alpha=1.0 ,color='#C0C0C0',\
    markersize=rv_markersize,fillstyle=rv_fillstyle)
    #
    plt.errorbar(p_all[j],res[j],errs_all[j],\
    label=telescopes_labels[j],fmt=mark[j],color=rv_colors[j], \
    alpha=1.0,markersize=rv_markersize,fillstyle=rv_fillstyle)
  yylims = ax1.get_ylim()
  miy = int(max(abs(yylims[0]),abs(yylims[1])))
  if ( miy == 0): #To avoid errors for really small RV variations
    miy = max(abs(yylims[0]),abs(yylims[1]))
  plt.yticks(np.arange(-miy,miy,2.*miy/4.))
  plt.ylim(-miy,miy)
  plt.minorticks_on()
  plt.xlim(0.,1.)
  plt.savefig(fname,format='pdf',bbox_inches='tight')
  plt.savefig(fname[:-3]+'png',format='png',bbox_inches='tight',dpi=300)
  plt.close()


#===========================================================
#                   RV PLOTS
#===========================================================

v_vec_val = [None]*nt
v_val = [None]*nt
#3 + npars + ldc
v_vec_val[:] = params[4+8*nplanets+2:4+8*nplanets+2+nt]
for o in range(0,nt):
  v_val[o] = best_value(v_vec_val[o],maxloglike,get_value)
  if ( is_log_rv0 ):
    v_val[o] = 10.0**(v_val[o])


alpha_val = 0.0
beta_val = 0.0
if ( is_linear_trend != 'f' or is_quadratic_trend != 'f' ):
  alpha_val = best_value(params_trends[0],maxloglike,get_value)
  beta_val  = best_value(params_trends[1],maxloglike,get_value)


base = 4
t0_val = np.ndarray(nplanets)
P_val  = np.ndarray(nplanets)
e_val  = np.ndarray(nplanets)
w_val  = np.ndarray(nplanets)
k_val  = np.ndarray(nplanets)

for o in range(0,nplanets):
  t0_val[o] = best_value(params[base + 0],maxloglike,get_value)
  P_val[o]  = best_value(params[base + 1],maxloglike,get_value)
  e_val[o]  = best_value(params[base + 2],maxloglike,get_value)
  w_val[o]  = best_value(params[base + 3],maxloglike,get_value)
  k_val[o]  = best_value(params[base + 7],maxloglike,get_value)
  if ( is_log_P ):
    P_val[o] = 10.0**(P_val[o])
  if ( is_log_k ):
    k_val[o] = 10.0**(k_val[o])
  if ( is_ew ):
    edum_val = e_val[o]
    e_val[o] = e_val[o]**2 + w_val[o]**2
    w_val[o] = np.arctan2(edum_val,w_val[o])

  base = base + 8

if ( nplanets > 0 ):
  #Plot without fold the data
  #===========================================================
  #      Plot the light curve with all the parameters
  #===========================================================
  def plot_rv_all_data():
    cfactor = np.float(1.e3)
    rv_datas = [None]*nt
    errs_datas = [None]*nt
    for i in range(0,nt):
      rv_datas[i] = list(rv_all[i])
      errs_datas[i] = list(errs_all[i])
    for i in range(0,nt):
      for j in range(0,len(rv_all[i])):
        rv_datas[i][j] = cfactor*rv_datas[i][j]
        errs_datas[i][j] = cfactor*errs_datas[i][j]

    #Let us save all the RV data in rv_dum
    n = 5000
    xmin = min(np.concatenate(time_all))
    xmax = max(np.concatenate(time_all))
    total_tt = xmax - xmin
    agregar = total_tt*0.1
    xmax = xmax + agregar
    xmin = xmin - agregar
    dn = (xmax - xmin) /  n
    rvx = np.empty([n])
    rvx[0] = xmin
    for j in range(1,n):
      rvx[j] = rvx[j-1] + dn

    #Model curve
    rvy = pti.rv_curve_mp(rvx,0.0,t0_val,\
    k_val*cfactor,P_val,e_val,w_val,alpha_val*cfactor,beta_val*cfactor)
    rv_dum = [None]*nt
    res_dum_all = [None]*nt
    for j in range(0,nt):
      res_dum_all[j] = pti.rv_curve_mp(time_all[j],0.0,t0_val,\
      k_val*cfactor,P_val,e_val,w_val,alpha_val*cfactor,beta_val*cfactor)
      #This is the model of the actual planet
      #the actual value, minus the systemic velocity
      rv_dum[j] = rv_datas[j] - v_val[j]*cfactor
      res_dum_all[j] = rv_dum[j] - res_dum_all[j]

    plt.figure(1,figsize=(2*fsx,fsy))
    plt.plot(rvx,rvy,'k')

    plt.minorticks_on()
    plt.xlabel(rv_xlabel,fontsize=fos)
    plt.ylabel('RV (m/s)',fontsize=fos)
    plt.xlim(xmin,xmax)
    plt.tick_params(labelsize=fos,direction='in')
    for j in range(0,nt):
      plt.errorbar(time_all[j],rv_dum[j],new_errs_all[j],color='#C0C0C0',\
      fmt=mark[j],alpha=1.0,markersize=rv_markersize)
      #
      plt.errorbar(time_all[j],rv_dum[j],errs_datas[j],color=rv_colors[j],\
      label=telescopes_labels[j],fmt=mark[j],alpha=1.0,markersize=rv_markersize)
    plt.legend(loc=2, ncol=1,scatterpoints=1,numpoints=1,frameon=True,fontsize=fos*0.8)
    fname = outdir+'/'+star+'_rv_all.pdf'
    print 'Creating ', fname
    plt.savefig(fname,format='pdf',bbox_inches='tight')
    plt.savefig(fname[:-3]+'png',format='png',bbox_inches='tight',dpi=300)
    plt.close()

    #Let us create or detrended file
    out_f = outdir+'/'+star+'_rv_residuals.dat'
    vec_x = np.concatenate(time_all)
    vec_y = np.concatenate(res_dum_all)
    vec_z = np.concatenate(errs_all)
    of = open(out_f,'w')
    #of.write('#This detrended light curve was created with pyaneti/lunas\n')
    for i in range(0,len(vec_x)):
      of.write(' %8.8f   %8.8f  %8.8f \n'%(vec_x[i],vec_y[i],vec_z[i]*cfactor))

    of.close()


    return res_dum_all

#===========================================================
#                RV multi-planet fit
#===========================================================
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
        rv_dum.append(list(rv_all[j]))
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
      k_dum[i],P_val[i],e_val[i],w_val[i],0.0 \
      ,0.0)

      dt0_val = []
      dk_dum = []
      dP_val = []
      de_val = []
      dw_val = []

      j = 0
      while ( j < nplanets ):
        if ( j != i and nplanets>1 ):
          dt0_val.append(t0_val[j])
          dk_dum.append(k_dum[j])
          dP_val.append(P_val[j])
          de_val.append(e_val[j])
          dw_val.append(w_val[j])
        j = j + 1

      res = [None]*nt
      drvy = [None]*nt
      for j in range(0,nt): #Remove the signal for each telescope
        #This is the model of the actual planet
        res[j] = pti.rv_curve_mp(time_all[j],0.0,t0_val[i],k_dum[i],\
        P_val[i],e_val[i],w_val[i], 0.0, 0.0)

        #This variable has all the others planets
        if ( nplanets > 1 ):
          drvy[j] = pti.rv_curve_mp(time_all[j],0.0,dt0_val,dk_dum \
          ,dP_val,de_val,dw_val, 0.0 \
          ,0.0)
        else:
          drvy[j] = 0.0

        alpha_time = [0.0]*len(time_all[j])
        beta_time = [0.0]*len(time_all[j])
        if ( is_linear_trend or is_quadratic_trend ):
          for m in range(0,len(time_all[j])):
              alpha_time[m] = (time_all[j][m]-t0_val[0])**1 * alpha_val * cfactor
              beta_time[m]  = (time_all[j][m]-t0_val[0])**2 * beta_val  * cfactor

        #the actual value, minus the systemic velocity, minus the other planets
        for o in range(len(time_all[j])):
          if ( nplanets > 1 ):
            rv_dum[j][o] = rv_dum[j][o] - v_val[j] - drvy[j][o] - alpha_time[o] - beta_time[o]
          else:
            rv_dum[j][o] = rv_dum[j][o] - v_val[j] - drvy[j] - alpha_time[o] - beta_time[o]
          res[j][o] = rv_dum[j][o] - res[j][o]

      p_rv[i] = scale_period(rvx,t0_val[i],P_val[i])
      p_all = [None]*nt
      for j in range(0,nt):
        p_all[j] = scale_period(time_all[j],t0_val[i],P_val[i])

      fname = outdir+'/'+star+plabels[i]+'_rv.pdf'
      plot_rv_fancy(p_rv[i],rvy[i],p_all,rv_dum,errs_all,res,telescopes_labels,fname)

#===========================================================
#                   Histogram plots
#===========================================================

#Define the labels to be used in the plots

labs = []
elab = '$e$'
wlab = '$\omega$'
ilab = '$i$ (deg)'
klab = '$K$'
alab = '$a/R_\star$'
if ( is_ew ):
    elab = '$\sqrt{e} \sin \omega$'
    wlab = '$\sqrt{e} \cos \omega$'
if ( is_b_factor ):
    ilab = 'b'
if ( is_log_k ):
    klab = '$\log_{10} K$'
if ( is_den_a ):
    alab = '$\\rho_{\star}^{-3}$'
for o in range(0,nplanets):
  etiquetas = ['$T0$'+plabels[o],'$P$'+plabels[o],elab+plabels[o], \
               wlab+plabels[o],ilab+plabels[o],alab+plabels[o], \
               '$R_{\mathrm{p}}/R_\star$'+plabels[o],klab+plabels[o]]
  labs.append(etiquetas)
labs.append(['$q_1$','$q_2$'])
labs.append(telescopes_labels)
labels = np.concatenate(labs)

def plot_correlations():
  create_plot_correlation(params[4:],labels,col='blue',num=plot_parameters)

def plot_posterior():
    create_plot_posterior(params[4:],labels, cbars='red', nb=50, num=plot_parameters)

def create_plot_posterior(params,plabs,cbars='red',nb=50,num=[]):
  if ( len(num) < 2 ):
    n = range(0,len(params))
  else:
    n = num
  plt.figure(1,figsize=(12,4*(len(n))/2))
  gs = gridspec.GridSpec(nrows=(len(n)+1)/2,ncols=2)
  j = 0
  for i in n:
    plt.subplot(gs[j])
    vpar, lpar, rpar = find_vals_perc(params[i],1.0)
    moda = my_mode(params[i])
    #best_val = params[i][minchi2_index]
    #plt.axvline(x=best_val,c='yellow')
    plt.axvline(x=vpar,c=cbars)
    plt.axvline(x=moda,c='y',ls='-.')
    plt.axvline(x=vpar-lpar,c=cbars,ls='--')
    plt.axvline(x=vpar+rpar,c=cbars,ls='--')
    plt.xlabel(plabs[i])
    plt.tick_params( axis='y',which='both',direction='in')
    plt.tick_params( axis='x',which='both',direction='in')
    if ( is_seaborn_plot ):
      sns.kdeplot(params[i], shade=True)
    else:
      plt.hist(params[i],normed=True,bins=nb)
    j = j + 1

  fname = outdir+'/'+star+'_posterior.pdf'
  print 'Creating ', fname
  plt.savefig(fname,format='pdf',bbox_inches='tight')
  plt.close()


def create_plot_correlation(params,plabs,col='red',mark='.',num=[]):
  if ( len(num) < 1 ):
    n = range(0,len(params))
  else:
    n = num
  plt.figure(1,figsize=(4*len(n),4*len(n)))
  gs = gridspec.GridSpec(nrows=len(n),ncols=len(n))
  o = 0
  for i in n:
    p = 0
    for j in n:
      if ( j < i ):
        plt.subplot(gs[o*len(n)+p])
        plt.tick_params( axis='y',which='both',direction='in',labelleft='off')
        plt.tick_params( axis='x',which='both',direction='in',labelbottom='off')
        plt.ticklabel_format(useOffset=False, axis='both')
        if ( j == n[0] ):
           plt.ylabel(plabs[i],fontsize=25)
        elif ( j == i - 1 ):
          plt.tick_params( axis='y',which='both',direction='in',labelleft='off')
          plt.tick_params( axis='x',which='both',direction='in',labelbottom='off')
        else:
          plt.tick_params( axis='y',which='both',direction='in',labelleft='off')
          plt.tick_params( axis='x',which='both',direction='in',labelbottom='off')
        if ( i == n[len(n)-1]):
          plt.xlabel(plabs[j],fontsize=25)
        else:
          plt.tick_params( axis='y',which='both',direction='in',labelleft='off')
          plt.tick_params( axis='x',which='both',direction='in',labelbottom='off')
        plt.hist2d(params[j],params[i],bins=100,norm=LogNorm())
        p = p + 1
    o = o + 1

  fname = outdir+'/'+star+'_correlations.pdf'
  print 'Creating ', fname
  plt.savefig(fname,format='pdf',bbox_inches='tight')
  plt.close()

def create_corner_plot():
  import corner

  #update plot_parameters vector
  npp = list(plot_parameters)
  for o in range(0,len(plot_parameters)):
      npp[o] = 4 + plot_parameters[o]

  #Let us take only the values to be plotted
  newpars = [0.0]*len(npp)
  newlabs = [0.0]*len(npp)
  for o in range(0,len(npp)):
      newpars[o] = params[npp[o]]
      newlabs[o] = labels[plot_parameters[o]]

  #Let us prepare the vector for corner
  data = np.zeros(shape=(len(newpars[0]),len(npp)))
  for o in range(0,len(newpars[0])):
      dumvec = []
      for m in range(0,len(npp)):
          dumvec.append(newpars[m][o])
      data[o] = dumvec

  figure = corner.corner(data, labels=newlabs, \
                       quantiles=[0.16, 0.5, 0.84], \
                        show_titles=True )
  fname = outdir+'/'+star+'_corner.pdf'
  print 'Creating ', fname
  plt.savefig(fname,format='pdf',bbox_inches='tight')
  figure.savefig(fname,format='pdf')
  plt.close()
