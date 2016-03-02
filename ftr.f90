!------------------------------------------------------------
!                         ftr.f90
! This file contains subroutines to calculate Marcov Chain 
! Monte Carlo simulations in order to obtain planet parameters
! from light curve fitting of transit planets
! The subroutines can be called from python by using f2py
! They also can be used in a fortran program
!              Date --> Feb  2016, Oscar Barragán
!------------------------------------------------------------

!-----------------------------------------------------------
!  Find z suborutine
!------------------------------------------------------------
subroutine find_z(t,t0,P,e,w,i,a,z,ts)
implicit none

!In/Out variables
  integer, intent(in) :: ts
  double precision, intent(in), dimension(0:ts-1) :: t
  double precision, intent(in) :: t0, P, e, w, i, a
  double precision, intent(out), dimension(0:ts-1) :: z
!Local variables
  double precision, parameter :: pi = 3.1415926535897932384626
  double precision, dimension(0:ts-1) :: ma, ta, swt
  double precision :: si, delta = 1e-7
  integer :: imax
!External function
  external :: find_anomaly
!

  si = sin(i)
  imax = int(1e7)
  ma = mod(2.*pi*(t-t0) / P, 2.*pi)
  !Obtain the eccentric anomaly by using find_anomaly
  call find_anomaly(ma,ta,e,delta,imax,ts)
  swt = sin(w+ta)
  z = a * ( 1. - e * e ) / (1. + e * cos(ta) ) * &
      sqrt( 1. - swt * swt * si * si ) 
  !z has been calculated
  
end subroutine

!-----------------------------------------------------------
! This routine calculates the chi square for a RV curve
! given a set of xd-yd data points
! It takes into acount the possible difference in systematic
! velocities for different telescopes.
!Input parameters are:
! xd, yd, errs -> set of data to fit (array(datas))
! tlab -> Telescope labels (array of integers number)
! rv0  -> array for the different systemic velocities,
!         its size is the number of telescopes
! k, ec, w, t0, P -> typical planet parameters
! ics -> is circular flag, True or False.
! datas, nt -> sizes of xd,yd, errs (datas) and rv0(nt)  
!Output parameter:
! chi2 -> a double precision value with the chi2 value
!-----------------------------------------------------------
!subroutine find_chi2_tr(xd,yd,errs,t0,P,e,w,i,a,u1,u2,pz,chi2,isc,datas)
subroutine find_chi2_tr(xd,yd,errs,params,chi2,isc,datas)
implicit none

!In/Out variables
  integer, intent(in) :: datas
  double precision, intent(in), dimension(0:datas-1)  :: xd, yd, errs
  !double precision, intent(in) :: t0, P,e, w, i, a, u1, u2, pz
  double precision, intent(in), dimension (0:8) :: params
  logical, intent(in)  :: isc
  double precision, intent(out) :: chi2
!Local variables
  double precision, parameter :: pi = 3.1415926535897932384626
  double precision, dimension(0:datas-1) :: z, res, muld, mu
  double precision :: t0, P, e, w, i, a, u1, u2, pz
!External function
  external :: occultquad, find_z

  t0  = params(0)
  P   = params(1)
  e   = params(2)
  w   = params(3)
  i   = params(4)
  a   = params(5)
  u1  = params(6)
  u2  = params(7)
  pz  = params(8) 

  !Let us find the projected distance z
  call find_z(xd,t0,P,e,w,i,a,z,datas)
  !Now we have z, let us use Agol's routines
  call occultquad(z,u1,u2,pz,muld,mu,datas)

  !Let us calculate the residuals
  ! chi^2 = \Sum_i ( M - O )^2 / \sigma^2
  !Here I am assuming that we want limb darkening
  !If this is not true, use mu 
  res(:) = ( muld(:) - yd(:) ) / errs(:) 
  chi2 = dot_product(res,res)

end subroutine
!-----------------------------------------------------------
! This routine calculates a MCMC chain by using metropolis-
! hasting algorithm
! given a set of xd-yd data points
!Input parameters are:
! xd, yd, errs -> set of data to fit (array(datas))
! tlab -> Telescope labels (array of integers number)
! rv0  -> array for the different systemic velocities,
!         its size is the number of telescopes
! k, ec, w, t0, P -> typical planet parameters
! prec -> precision of the step size
! maxi -> maximum number of iterations
! thin factor -> number of steps between each output
! chi2_toler -> tolerance of the reduced chi^2 (1 + chi2_toler)
! ics -> is circular flag, True or False.
! datas, nt -> sizes of xd,yd, errs (datas) and rv0(nt)  
!Output parameter:
! This functions outputs a file called mh_rvfit.dat
!-----------------------------------------------------------
subroutine metropolis_hastings_tr_improved(xd,yd,errs,params,prec,maxi,thin_factor,ics,wtf,nconv,datas)
implicit none

!In/Out variables
  integer, intent(in) :: maxi, thin_factor, nconv, datas
  integer, intent(in),dimension(0:8) :: wtf
  double precision, intent(in), dimension(0:datas-1) :: xd, yd, errs
  double precision, intent(in)  :: prec
  !Params vector contains all the parameters
  !t0,P,e,w,i,a,u1,u2,pz
  double precision, intent(inout), dimension(0:8) :: params
  !f2py intent(in,out)  :: params
  logical, intent(in) :: ics
!Local variables
  double precision, parameter :: pi = 3.1415926535897932384626
  double precision :: chi2_old, chi2_new, chi2_red
  double precision, dimension(0:8) :: params_new
  double precision, dimension(0:nconv-1) :: chi2_vec, x_vec
  double precision  :: q, chi2_y, chi2_slope, toler_slope
  integer :: j, nu, n
  real, dimension(0:9) :: r
  logical :: get_out
!external calls
  external :: init_random_seed, find_chi2_tr
 
  !Let us estimate our fist chi_2 value
  !call find_chi2_tr(xd,yd,errs,t0,P,e,w,i,a,u1,u2,pz,chi2_old,ics,datas)
  call find_chi2_tr(xd,yd,errs,params,chi2_old,ics,datas)
  !Calculate the degrees of freedom
  nu = datas - size(params)
  chi2_red = chi2_old / nu
  !Print the initial cofiguration
  print *, ''
  print *, 'Starting MCMC calculation'
  print *, 'Initial Chi2_red= ',chi2_red,'nu =',nu

  !Call a random seed 
  call init_random_seed()

  !Let us start the otput file
  open(unit=101,file='mh_trfit.dat',status='unknown')

  !Initialize the values
  toler_slope = prec 
  j = 1
  n = 0
  get_out = .TRUE.

  !The infinite cycle starts!
  do while ( get_out )
    !r will contain random numbers for each variable
    !Let us add a random shift to each parameter
    call random_number(r)
    r(1:9) = ( r(1:9) - 0.5) * 2.
    params_new = params + r(1:9) * prec * wtf
    !Let us calculate our new chi2
    call find_chi2_tr(xd,yd,errs,params_new,chi2_new,ics,datas)
    !Ratio between the models
    q = exp( ( chi2_old - chi2_new ) * 0.5  )
    !If the new model is better, let us save it
    if ( q > r(0) ) then
      chi2_old = chi2_new
      params = params_new
    end if
    !Calculate the reduced chi square
    chi2_red = chi2_old / nu
    !Save the data each thin_factor iteration
    if ( mod(j,thin_factor) == 0 ) then
      print *, 'iter ',j,', Chi2_red =', chi2_red
      write(101,*) j, chi2_old, chi2_red, params
      !Check convergence here
      chi2_vec(n) = chi2_red
      x_vec(n) = n
      n = n + 1
      if ( n == size(chi2_vec) ) then
        call fit_a_line(x_vec,chi2_vec,chi2_y,chi2_slope,nconv)        
        n = 0
        !If chi2_red has not changed the last nconv iterations
        print *, abs(chi2_slope), toler_slope
        if ( abs(chi2_slope) < toler_slope ) then
          print *, 'I did my best to converge, chi2_red =', &
                    chi2_y
          get_out = .FALSE.
        end if
      end if
      !I checked covergence
    end if
    j = j + 1
  end do

  close(101)

end subroutine
!

subroutine metropolis_hastings(xd_rv,yd_rv,errs_rv,xd_tr,yd_tr,errs_tr,params,prec,maxi,thin_factor,ics,wtf,nconv,drv,dtr,ntl)
implicit none

!In/Out variables
  integer, intent(in) :: maxi, thin_factor, nconv, drv, dtr, ntl
  integer, intent(in),dimension(0:9+ntl) :: wtf
  double precision, intent(in), dimension(0:drv-1) :: xd_rv, yd_rv, errs_rv
  double precision, intent(in), dimension(0:dtr-1) :: xd_tr, yd_tr, errs_tr
  double precision, intent(in)  :: prec
  !Params vector contains all the parameters
  !t0,P,e,w,i,a,u1,u2,pz
  double precision, intent(inout), dimension(0:9+ntl) :: params
  !f2py intent(in,out)  :: params
  logical, intent(in) :: ics
!Local variables
  double precision, parameter :: pi = 3.1415926535897932384626
  double precision :: chi2_rv_old, chi2_tr_old, chi2_rv_new, chi2_tr_new, chi2_red
  double precision :: chi2_old_total, chi2_new_total
  double precision, dimension(0:4+ntl) :: params_rv, params_rv_new
  double precision, dimension(0:8) :: params_tr, params_tr_new
  double precision, dimension(0:9+ntl) :: params_new
  double precision, dimension(0:nconv-1) :: chi2_vec, x_vec
  double precision  :: q, chi2_y, chi2_slope, toler_slope
  integer :: j, nu, n
  real, dimension(0:10+ntl) :: r
  logical :: get_out
!external calls
  external :: init_random_seed, find_chi2_tr

  params_tr = params(0:8)
  params_rv(0:3) = params(0:3)
  params_rv(4:4+ntl) = params(9:9+ntl)

  !Let us estimate our fist chi_2 value
  call find_chi2_tr(xd_tr,yd_tr,errs_tr,params_tr,chi2_tr_old,ics,dtr)
  call find_chi2_rv(xd_rv,yd_rv,errs_rv,params_rv,chi2_rv_old,ics,drv)
  chi2_old_total = chi2_tr_old + chi2_rv_old
  !Calculate the degrees of freedom
  nu = dtr + drv - size(params)
  chi2_red = ( chi2_old_total ) / nu
  !Print the initial cofiguration
  print *, ''
  print *, 'Starting MCMC calculation'
  print *, 'Initial Chi2_red= ',chi2_red,'nu =',nu

  !Call a random seed 
  call init_random_seed()

  !Let us start the otput file
  open(unit=101,file='mh_fit.dat',status='unknown')

  !Initialize the values
  toler_slope = prec 
  j = 1
  n = 0
  get_out = .TRUE.

  !The infinite cycle starts!
  do while ( get_out )
    !r will contain random numbers for each variable
    !Let us add a random shift to each parameter
    call random_number(r)
    r(1:10+ntl) = ( r(1:10+ntl) - 0.5) * 2.
    params_new = params + r(1:10+ntl) * prec * wtf
    !Let us calculate our new chi2
    params_tr_new = params_new(0:8)
    params_rv_new(0:3) = params_new(0:3)
    params_rv_new(4:4+ntl) = params_new(9:9+ntl)
    !Let us estimate our fist chi_2 value
    call find_chi2_tr(xd_tr,yd_tr,errs_tr,params_tr_new,chi2_tr_new,ics,dtr)
    call find_chi2_rv(xd_rv,yd_rv,errs_rv,params_rv_new,chi2_rv_new,ics,drv)
    chi2_new_total = chi2_tr_new + chi2_rv_new
    !Ratio between the models
    q = exp( ( chi2_old_total - chi2_new_total ) * 0.5  )
    !If the new model is better, let us save it
    if ( q > r(0) ) then
      chi2_old_total = chi2_new_total
      params = params_new
    end if
    !Calculate the reduced chi square
    chi2_red = chi2_old_total / nu
    !Save the data each thin_factor iteration
    if ( mod(j,thin_factor) == 0 ) then
      print *, 'iter ',j,', Chi2_red =', chi2_red
      write(101,*) j, chi2_old_total, chi2_red, params
      !Check convergence here
      chi2_vec(n) = chi2_red
      x_vec(n) = n
      n = n + 1
      if ( n == size(chi2_vec) ) then
        call fit_a_line(x_vec,chi2_vec,chi2_y,chi2_slope,nconv)        
        n = 0
        !If chi2_red has not changed the last nconv iterations
        print *, abs(chi2_slope), toler_slope
        if ( abs(chi2_slope) < toler_slope ) then
          print *, 'I did my best to converge, chi2_red =', &
                    chi2_y
          get_out = .FALSE.
        end if
      end if
      !I checked covergence
    end if
    j = j + 1
  end do

  close(101)

end subroutine


