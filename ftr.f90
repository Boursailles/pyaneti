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
  double precision, dimension(0:ts-1) :: ta, swt
  double precision :: si, delta = 1.e-7
  integer :: imax = int(1e7)
!External function
  external :: find_anomaly
!

  !Obtain the eccentric anomaly by using find_anomaly
  call find_anomaly(t,t0,e,w,P,ta,delta,imax,ts)
  swt = sin(w+ta)

  !do imax = 0, ts-1
  !  print *, t(imax), ta(imax), swt(imax)
  !end do

  !stop

  si = sin(i)
  z = a * ( 1. - e * e ) * sqrt( 1. - swt * swt * si * si ) &
      / ( 1. + e * cos(ta) ) 
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
subroutine find_chi2_tr(xd,yd,errs,params,flag,chi2,isc,datas)
implicit none

!In/Out variables
  integer, intent(in) :: datas
  double precision, intent(in), dimension(0:datas-1)  :: xd, yd, errs
  double precision, intent(in), dimension (0:8) :: params
  logical, intent(in)  :: isc
  double precision, intent(out) :: chi2
!Local variables
  double precision, parameter :: pi = 3.1415926535897932384626
  double precision, dimension(0:datas-1) :: z, res, muld, mu
  double precision :: t0, P, e, w, i, a, u1, u2, pz
  logical :: flag(0:3)
!  integer :: n
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

  if ( flag(0) ) P = 10**params(1)
  if ( flag(1) ) then
    e = params(2) * params(2) + params(3) * params(3)
    w = atan2(params(2),params(3))
  end if
  if (flag(2)) i = asin(params(4))
  if (flag(3)) a = 10**params(5)

  !print *, params
  if ( isc ) then !The orbit is circular
    e = dble(0.0)
    w = pi / 2.0
  end if

!  do n = 0, datas-1
!    print *, xd(n)
!  end do
!  stop

  !Let us find the projected distance z
  call find_z(xd,t0,P,e,w,i,a,z,datas)

  !print *, z(0), z(10), z(100)
  !print *, z
  !print *, minval(z)

  !Now we have z, let us use Agol's routines
  call occultquad(z,u1,u2,pz,muld,mu,datas)

  !print *,muld

  !stop

  !print *, muld
  !Let us calculate the residuals
  ! chi^2 = \Sum_i ( M - O )^2 / \sigma^2
  !Here I am assuming that we want limb darkening
  !If this is not true, use mu 
  res(:) = ( muld(:) - yd(:) ) / errs(:) 
  chi2 = dot_product(res,res)
  
  !print *, chi2


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
subroutine metropolis_hastings_tr(xd,yd,errs,params,prec,maxi,thin_factor,ics,wtf,flag,nconv,datas)
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
  logical, intent(in) :: ics, flag(0:3)
!Local variables
  double precision, parameter :: pi = 3.1415926535897932384626
  double precision :: chi2_old, chi2_new, chi2_red
  double precision, dimension(0:8) :: params_new
  double precision, dimension(0:nconv-1) :: chi2_vec, x_vec
  double precision  :: q, chi2_y, chi2_slope, toler_slope
  double precision :: ecos, esin, prec_init
  integer :: j, nu, n
  double precision, dimension(0:9) :: r
  logical :: get_out
!external calls
  external :: init_random_seed, find_chi2_tr

  !Period
  if ( flag(0) ) params(1) = log10(params(1))
  !eccentricity and periastron
  if ( flag(1) ) then
    esin = sqrt(params(2)) * sin(params(3))
    ecos = sqrt(params(2)) * cos(params(3))
    params(2) = esin
    params(3) = ecos
  end if
  if (flag(2) ) params(4) = sin(params(4))
  if (flag(3) ) params(5) = log10(params(5))

  !Let us estimate our fist chi_2 value
  !call find_chi2_tr(xd,yd,errs,t0,P,e,w,i,a,u1,u2,pz,chi2_old,ics,datas)
  call find_chi2_tr(xd,yd,errs,params,flag,chi2_old,ics,datas)
  !Calculate the degrees of freedom
  nu = datas - size(params)
  chi2_red = chi2_old / nu
  !Print the initial cofiguration
  print *, ''
  print *, 'Starting MCMC calculation'
  print *, 'Initial Chi2_red= ',chi2_red,'nu =',nu


  !Let us start the otput file
  open(unit=101,file='mh_trfit.dat',status='unknown')

  !Initialize the values
  toler_slope = prec 
  j = 1
  n = 0
  get_out = .TRUE.

  call init_random_seed()

  !The infinite cycle starts!
  do while ( get_out )
    !r will contain random numbers for each variable
    !Let us add a random shift to each parameter
    !Call a random seed 
    call random_number(r)
    !prec_init = prec * sqrt(chi2_red)
    prec_init = prec
    r(1:9) = ( r(1:9) - 0.5) * 2.
    params_new = params + r(1:9) * prec_init * wtf
    !print *, ''
    !print *, params
    !print *, params_new
    !Let us calculate our new chi2
    call find_chi2_tr(xd,yd,errs,params_new,flag,chi2_new,ics,datas)
    !print *, prec, wtf
    !print *, chi2_old, chi2_new
    !Ratio between the models
    q = exp( ( chi2_old - chi2_new ) * 0.5  )
    !If the new model is better, let us save it
    if ( q > r(0) ) then
      chi2_old = chi2_new
      params = params_new
    end if
    !Calculate the reduced chi square
    chi2_red = chi2_old / nu
    !stop
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
      if ( j > maxi ) then
        print *, 'Maximum number of iteration reached!'
        get_out = .FALSE.
      end if
    end if
    !I checked covergence

    j = j + 1
  end do

  close(101)

end subroutine
!

subroutine metropolis_hastings(xd_rv,yd_rv,errs_rv,tlab,xd_tr,yd_tr,errs_tr,params,prec,maxi,thin_factor, &
           ics,wtf,flag,nconv,drv,dtr,ntl)
implicit none

!In/Out variables
  integer, intent(in) :: maxi, thin_factor, nconv, drv, dtr, ntl
  integer, intent(in),dimension(0:10) :: wtf
  double precision, intent(in), dimension(0:drv-1)::xd_rv,yd_rv,errs_rv
  integer, intent(in), dimension(0:drv-1):: tlab
  double precision, intent(in), dimension(0:dtr-1) :: xd_tr, yd_tr, errs_tr
  double precision, intent(in)  :: prec
  !Params vector contains all the parameters
  !t0,P,e,w,i,a,u1,u2,pz
  double precision, intent(inout), dimension(0:9+ntl) :: params
  !f2py intent(in,out)  :: params
  logical, intent(in) :: ics, flag(0:5)
!Local variables
  double precision, parameter :: pi = 3.1415926535897932384626
  double precision :: chi2_rv_old, chi2_tr_old, chi2_rv_new, chi2_tr_new, chi2_red
  double precision :: chi2_old_total, chi2_new_total
  double precision, dimension(0:4+ntl) :: params_rv, params_rv_new
  double precision, dimension(0:8) :: params_tr, params_tr_new
  double precision, dimension(0:9+ntl) :: params_new
  double precision, dimension(0:nconv-1) :: chi2_vec, x_vec
  double precision  :: q, chi2_y, chi2_slope, toler_slope
  double precision  :: esin, ecos, prec_init
  integer :: j, nu, n
  double precision, dimension(0:10+ntl) :: r
  logical :: get_out, flag_rv(0:3), flag_tr(0:3)
!external calls
  external :: init_random_seed, find_chi2_tr


  if ( flag(0) ) params(1) = log10(params(1))
  if ( flag(1) ) then
    esin = sqrt(params(2)) * sin(params(3))
    ecos = sqrt(params(2)) * cos(params(3))
    params(2) = esin
    params(3) = ecos
  end if
  if ( flag(2) ) params(4) = sin(params(4))
  if ( flag(3) ) params(5) = log10(params(5))
  if ( flag(4) ) params(9) = log10(params(9))
  if ( flag(5) ) params(10:9+ntl) = log10(params(10:9+ntl))

  flag_tr = flag(0:3)
  flag_rv(0:1) = flag(0:1)
  flag_rv(2:3) = flag(4:5)

  params_tr = params(0:8)
  params_rv(0:3) = params(0:3)
  params_rv(4:4+ntl) = params(9:9+ntl)

  !Let us estimate our fist chi_2 value
  call find_chi2_tr(xd_tr,yd_tr,errs_tr,params_tr,flag_tr,chi2_tr_old,ics,dtr)
  call find_chi2_rv(xd_rv,yd_rv,errs_rv,tlab,params_rv,flag_rv,chi2_rv_old,ics,drv,ntl)
  print *, chi2_rv_old, chi2_tr_old
  chi2_old_total = chi2_tr_old + chi2_rv_old
  !Calculate the degrees of freedom
  nu = dtr + drv - size(params)
  chi2_red = ( chi2_old_total ) / nu
  !Print the initial cofiguration
  print *, ''
  print *, 'Starting MCMC calculation'
  print *, 'Initial Chi2_red= ',chi2_red,'nu =',nu


  !Let us start the otput file
  open(unit=101,file='mh_fit.dat',status='unknown')

  !Initialize the values
  toler_slope = prec 
  j = 1
  n = 0
  get_out = .TRUE.

  !Call a random seed 
  call init_random_seed()

  !The infinite cycle starts!
  do while ( get_out )
    !r will contain random numbers for each variable
    !Let us add a random shift to each parameter
    call random_number(r)
    prec_init = prec * sqrt(chi2_old_total) * r(10)
    !prec_init = prec 
    r(1:10+ntl) = ( r(1:10+ntl) - 0.5) * 2.
    params_new(0:9)      = params(0:9)      + r(1:10)     * prec_init * wtf(0:9)
    params_new(10:9+ntl) = params(10:9+ntl) + r(11:10+ntl) * prec_init * wtf(10)
    !Let us calculate our new chi2
    params_tr_new = params_new(0:8)
    params_rv_new(0:3) = params_new(0:3)
    params_rv_new(4:4+ntl) = params_new(9:9+ntl)
    call find_chi2_tr(xd_tr,yd_tr,errs_tr,params_tr_new,flag_tr,chi2_tr_new,ics,dtr)
    call find_chi2_rv(xd_rv,yd_rv,errs_rv,tlab,params_rv_new,flag_rv,chi2_rv_new,ics,drv,ntl)
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
      print *, 'c2 tr =', chi2_tr_new, 'c2 rv =', chi2_rv_new
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

      if ( j > maxi ) then
        print *, 'Maximum number of iteration reached!'
        get_out = .FALSE.
      end if

      end if
      !I checked covergence
    end if
    j = j + 1
  end do

  close(101)

end subroutine

!-----------------------------------------------------------
subroutine stretch_move_tr(xd,yd,errs,params,limits,nwalks,prec,maxi,thin_factor,ics,wtf,flag,nconv,datas)
implicit none

!In/Out variables
  integer, intent(in) :: nwalks, maxi, thin_factor, datas, nconv
  double precision, intent(in), dimension(0:datas-1)  :: xd, yd, errs
  double precision, intent(inout), dimension(0:8) :: params
  !f2py intent(in,out)  :: params
  double precision, intent(inout), dimension(0:2*(9)-1) :: limits
  !f2py intent(in,out)  :: limits
  integer, intent(in), dimension(0:8) :: wtf
  double precision, intent(in)  :: prec
  logical, intent(in) :: ics, flag(0:3)
!Local variables
  double precision, parameter :: pi = 3.1415926535897932384626
  double precision, dimension(0:nwalks-1) :: chi2_old, chi2_new, chi2_red
  double precision, dimension(0:8,0:nwalks-1) :: params_old, params_new
  double precision, dimension(0:nconv-1) :: chi2_vec, x_vec
  double precision  :: q, chi2_y, chi2_slope, toler_slope
  double precision  :: esin, ecos, nu, aa, chi2_red_min
  integer :: j, n, nk, n_burn, spar, new_thin_factor,good_chain
  logical :: get_out, is_burn, is_limit_good
  !Let us add a plus random generator
  double precision, dimension(0:nwalks-1) :: r_rand, z_rand
  integer, dimension(0:nwalks-1) :: r_int
  integer, dimension(0:8) :: wtf_all 
  real :: r_real
!external calls
  external :: init_random_seed, find_chi2_rv

  !What are we going to fit?
  wtf_all(0:8) = wtf(0:8)

  spar = size(params)

  print *, flag

  !Period
  if ( flag(0) )  then
    params(1) = log10(params(1))
    limits(2) = log10(limits(2))
    limits(3) = log10(limits(3))
  end if
  ! e and w
  if ( flag(1) ) then
    esin = sqrt(params(2)) * dsin(params(3))
    ecos = sqrt(params(2)) * dcos(params(3))
    params(2) = esin
    params(3) = ecos
    limits(4) = -1.0
    limits(5) = 1.0
    limits(6) = -1.0
    limits(7) = 1.0
  end if
  !i
  if ( flag(2) ) then
    params(4) = sin(params(4))
    limits(8:9) = sin(limits(8:9))
  end if
  !a = rp/r*
  if ( flag(3) ) then
    params(5) = log10(params(5))
    limits(10:11) = log10(limits(10:11))
  end if

  !Call a random seed 
  print *, 'CREATING RANDOM SEED'
  call init_random_seed()

  call random_number(r_rand)
  !Let us initinate all the walkers with the priors
  !I am not sure it this works, it is just a test
  r_rand = ( r_rand - 0.5 ) * 2.0

  !Let us create uniformative random priors

  print *, 'CREATING RANDOM UNIFORMATIVE PRIORS'
  do nk = 0, nwalks - 1
    !params_old(:,j) = params * ( 1. + (real(j)/nwalks) * r_rand(j)*0.01 ) 

    j = 0
    do n = 0, 8
      if ( wtf_all(n) == 0 ) then
        params_old(n,nk) = params(n)
      else
        call random_number(r_real)
        params_old(n,nk) = limits(j+1) - limits(j)
        params_old(n,nk) = limits(j) + r_real*params_old(n,nk) 
      end if
      print *, params_old(n,nk), limits(j), limits(j+1)
      j = j + 2
    end do

    !Let us estimate our first chi_2 value
    call find_chi2_tr(xd,yd,errs,params_old(:,nk),flag,chi2_old(nk),ics,datas)

  end do
  

  !Calculate the degrees of freedom
  nu = dble(datas - spar)
  !If we are fixing a circular orbit, ec and w are not used 
  if ( ics ) nu = nu + 2 
  chi2_red = chi2_old / nu
  !Print the initial cofiguration
  print *, ''
  print *, 'Starting stretch move MCMC calculation'
  print *, 'Initial Chi2_red= ', minval(chi2_red),'nu =', nu

  !Let us start the otput file
  open(unit=101,file='mh_trfit.dat',status='unknown')
  !Initialize the values

  toler_slope = prec
  j = 1
  n = 0
  get_out = .TRUE.
  is_burn = .FALSE.

  aa = 2.0
  n_burn = 1

  !The infinite cycle starts!
  print *, 'STARTING INFINITE LOOP!'

  do while ( get_out )

    !Do the work for all the walkers
    call random_number(z_rand)
    call random_number(r_rand)
    call random_int(r_int,nwalks)

    do nk = 0, nwalks - 1
    !Draw the random walker nk, from the complemetary walkers
    !This definition does not avoid to copy the same k walker
      params_new(:,nk) = params_old(:,r_int(nk))
      !Let us generate a random step
      z_rand(nk) = z_rand(nk) * aa ! a = 2 as suggested by emcee paper
      call find_gz(z_rand(nk),aa) 
    
      !Now we can have the evolved walker
      params_new(:,nk) = params_new(:,nk) + wtf_all(:) * z_rand(nk) * &
                       ( params_old(:,nk) - params_new(:,nk) )

      !Let us check the limits
      call check_limits(params_new(:,nk),limits, &
      is_limit_good,9)
      if ( is_limit_good ) then !evaluate chi2
        !Obtain the new chi square 
        call find_chi2_tr(xd,yd,errs,params_new(:,nk),flag,chi2_new(nk),ics,datas)
      else !we do not have a good model
        chi2_new(nk) = huge(dble(0.0))
        !print *, 'I almost collapse!'
      end if

      !Is the new model better? 
      q = z_rand(nk)**( spar - 1.) * &
          exp( ( chi2_old(nk) - chi2_new(nk) ) * 0.5  )

      if ( q >= r_rand(nk) ) then
        chi2_old(nk) = chi2_new(nk)
        params_old(:,nk) = params_new(:,nk)
      end if

      chi2_red(nk) = chi2_old(nk) / nu

      !Start to burn-in 
      if ( is_burn ) then
        if ( mod(j,new_thin_factor) == 0 ) then
          if ( nk == good_chain ) write(101,*) n_burn, chi2_old(nk), chi2_red(nk), params_old(:,nk)
        end if
      end if
      !End burn-in

    end do

     if ( is_burn ) then
        if ( mod(j,new_thin_factor) == 0 ) n_burn = n_burn + 1
        if ( n_burn > nconv ) get_out = .false.
     end if

    chi2_red_min = minval(chi2_red)

    !Save the data each thin_factor iteration
    if ( .not. is_burn ) then
      if ( mod(j,thin_factor) == 0 ) then

        print *, 'iter ',j,', Chi2_red =', chi2_red_min
        !Check convergence here
        chi2_vec(n) = chi2_red_min
        x_vec(n) = n
        n = n + 1

        if ( n == size(chi2_vec) ) then

          call fit_a_line(x_vec,chi2_vec,chi2_y,chi2_slope,nconv)
          n = 0
          !If chi2_red has not changed the last nconv iterations
          print *, abs(chi2_slope), toler_slope / (chi2_y)
          if ( abs(chi2_slope) < ( toler_slope / (chi2_y) ) ) then
            print *, 'THE CHAIN HAS CONVERGED'
            print *, 'Starting burning-in phase'
            is_burn = .True.
            new_thin_factor = 10
            good_chain = minloc(chi2_red,dim=1) - 1
            print *, 'The best chain is', good_chain, &
            'with chi2_red =', chi2_red(good_chain)
          end if

          if ( j > maxi ) then
            print *, 'Maximum number of iteration reached!'
            get_out = .FALSE.
          end if

        end if
      !I checked covergence
      end if

    end if

  j = j + 1

  end do

  close(101)

end subroutine


