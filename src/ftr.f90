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
!                     find_z
!  This suborutine finds the projected distance between
!  the star and planet centers. Eq. (5), ( z = r_sky) from
!  Winn, 2010, Transit and Occultations.
!------------------------------------------------------------
subroutine find_z(t,pars,flag,z,ts)
implicit none

!In/Out variables
  integer, intent(in) :: ts
  double precision, intent(in), dimension(0:ts-1) :: t
  double precision, intent(in), dimension(0:5) :: pars
  double precision, intent(out), dimension(0:ts-1) :: z
  logical, intent(in), dimension(0:3) :: flag 
!Local variables
  double precision, dimension(0:ts-1) :: ta, swt
  double precision :: t0, P, e, w, i, a
  double precision :: si
  double precision :: pi = 3.1415926535897932384626d0
!External function
  external :: find_anomaly
!

  t0  = pars(0)
  P   = pars(1)
  e   = pars(2)
  w   = pars(3)
  i   = pars(4)
  a   = pars(5)

  if ( flag(0) ) P = 1.d0**pars(1)
  if ( flag(1) ) then
    e = pars(2) * pars(2) + pars(3) * pars(3)
    w = atan2(pars(2),pars(3))
  end if
  !Let us get the w of the planet
  w = w + pi
  if (flag(3)) a = 10.0**a
  if (flag(2)) i = acos( i / a * ( 1.d0 + e * sin(w) ) / ( 1.d0 - e*e ) )

  !Obtain the eccentric anomaly by using find_anomaly
  call find_anomaly(t,t0,e,w,P,ta,ts)
  swt = sin(w+ta)

  si = sin(i)
  z = a * ( 1.d0 - e * e ) * sqrt( 1.d0 - swt * swt * si * si ) &
      / ( 1.d0 + e * cos(ta) ) 
  !z has been calculated
  
end subroutine

subroutine check_eclipse(z,pz,is_good,sizez)
implicit none

!In/Out variables
  integer, intent(in) :: sizez
  double precision, intent(in), dimension(0:sizez) :: z
  double precision, intent(in) :: pz
  logical, intent(out) :: is_good
!Local variables
  integer :: i
  double precision :: limit

  limit = 1.d0 + pz
  is_good = .false.
  !At least we have to have one eclipse condition
  do i = 1, sizez - 2
    if ( z(i) < limit ) then
      is_good = .true.
      exit
    end if
  end do

  !if ( z(0) < limit .and. z(sizez-1) < limit ) is_good = .false.

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
subroutine find_chi2_tr(xd,yd,errs,pars,jitter,flag,params,n_cad,t_cad,chi2,datas)
!subroutine find_chi2_tr(yd,errs,z,params,chi2,datas)
implicit none

!In/Out variables
  integer, intent(in) :: datas, n_cad
  double precision, intent(in), dimension(0:datas-1)  :: xd, yd, errs
  double precision, intent(in), dimension(0:5) :: pars
  double precision, intent(in) :: t_cad
  double precision, intent(in) :: jitter
  logical, intent(in), dimension(0:3) :: flag 
  double precision, intent(in), dimension (0:2) :: params
  double precision, intent(out) :: chi2
!Local variables
  double precision, dimension(0:datas-1) :: res, muld, mu
  double precision :: u1, u2, pz, q1k, q2k, zdum(0:0)
  !double precision, dimension(0:datas-1,0:n_cad-1)  :: xd_ub, z, flux_ub
  double precision, dimension(0:n_cad-1)  :: xd_ub, z, flux_ub
  integer ::  j, k
  logical :: is_good
!External function
  external :: occultquad

  q1k = params(0)
  q2k = params(1)
  pz  = params(2) 
  !re-transform the parameters to u1 and u2
  u1 = sqrt(q1k)
  u2 = u1*( 1.d0 - 2.d0*q2k)
  u1 = 2.d0*u1*q2k

  !are the u1 and u2 within a physical solution
  call check_us(u1,u2,is_good)

  if ( is_good ) then

  !Selective re-sampling
  do j = 0, datas - 1

    !Are we generating an eclipse?
    call find_z(xd(j),pars,flag,zdum,1) 

    if ( zdum(0) > 1.0 + 2*pz ) then

      muld(j) = 1.d0 !This is not eclipse

    else   

      do k = 0, n_cad - 1
        xd_ub(k) = xd(j) + t_cad*((k+1.d0)-0.5*(n_cad+1.d0))/n_cad 
      end do

      call find_z(xd_ub,pars,flag,z,n_cad) 
      !Now we have z, let us use Agol's routines
      call occultquad(z,u1,u2,pz,flux_ub,mu,n_cad)

      !Re-bin the data
      muld(j) = sum(flux_ub) / n_cad

    end if

  end do

  !Let us calculate the residuals
  ! chi^2 = \Sum_i ( M - O )^2 / \sigma^2
  !Here I am assuming that we want limb darkening
  !If this is not true, use mu 
  res(:) = ( muld(:) - yd(:) ) / sqrt( errs(:)**2 + jitter**2 )
  chi2 = dot_product(res,res)

  else

    chi2 = huge(dble(0.d0))

  end if

end subroutine
!-----------------------------------------------------------

subroutine find_chi2_tr_new(xd,yd,errs,pars,jitter,flag,ldc,&
           n_cad,t_cad,chi2,datas,npl)
implicit none

!In/Out variables
  integer, intent(in) :: datas, n_cad, npl
  double precision, intent(in), dimension(0:datas-1)  :: xd, yd, errs
  double precision, intent(in), dimension(0:6,npl-1) :: pars
  !pars = T0, P, e, w, b, a/R*, Rp/R*
  double precision, intent(in) :: t_cad
  double precision, intent(in) :: jitter
  logical, intent(in), dimension(0:3) :: flag
  double precision, intent(in), dimension (0:1) :: ldc
  double precision, intent(out) :: chi2
!Local variables
  double precision, dimension(0:datas-1,0:npl-1) :: muld_npl
  double precision, dimension(0:datas-1) :: res, muld, mu
  double precision :: npl_dbl, small, dbl, u1, u2, pz(0:npl-1), q1k, q2k, zdum(0:0)
  !double precision, dimension(0:datas-1,0:n_cad-1)  :: xd_ub, z, flux_ub
  double precision, dimension(0:n_cad-1)  :: xd_ub, z, flux_ub
  integer :: n, j, k
  logical :: is_good
!External function
  external :: occultquad

  small = 1.d-5
  npl_dbl = dble(npl)

  q1k = ldc(0)
  q2k = ldc(1)
  !re-transform the parameters to u1 and u2
  u1 = sqrt(q1k)
  u2 = u1*( 1.d0 - 2.d0*q2k)
  u1 = 2.d0*u1*q2k

  !Get planet radius
  pz = pars(6,:)

  !are the u1 and u2 within a physical solution
  call check_us(u1,u2,is_good)

  if ( is_good ) then

  !Selective re-sampling
  do j = 0, datas - 1

    do n = 0, npl - 1

    !Are we generating an eclipse?
    !Take care with the pars
    call find_z(xd(j),pars(:,n),flag,zdum,1)

    if ( zdum(0) > 1.0 + 2*pz(n) .or. pz(n) < small ) then

      muld_npl(j,n) = 1.d0 !This is not eclipse

    else

      do k = 0, n_cad - 1
        xd_ub(k) = xd(j) + t_cad*((k+1.d0)-0.5*(n_cad+1.d0))/n_cad
      end do

      call find_z(xd_ub,pars,flag,z,n_cad)
      !Now we have z, let us use Agol's routines
      call occultquad(z,u1,u2,pz,flux_ub,mu,n_cad)

      !Re-bin the data
      muld_npl(j,n) = sum(flux_ub) / n_cad

    end if

    end do !planets

    !The final flux is F = (F1 + F2 + ... + Fn ) / n
    muld(:) = 0.d0
    do n = 0, npl - 1
      muld(:) = muld(:) +  muld_npl(:,n)
    end do
    !This is the final flux for all the planets
    muld(:) = muld / npl_dbl

  end do

  !Let us calculate the residuals
  ! chi^2 = \Sum_i ( M - O )^2 / \sigma^2
  !Here I am assuming that we want limb darkening
  !If this is not true, use mu
  res(:) = ( muld(:) - yd(:) ) / sqrt( errs(:)**2 + jitter**2 )
  chi2 = dot_product(res,res)

  else

    chi2 = huge(dble(0.d0))

  end if

end subroutine

!
!-----------------------------------------------------------
subroutine stretch_move_tr(xd,yd,errs,pars,pstar, lpstar,lims,limits_physical, &
nwalks,a_factor,maxi,thin_factor,n_cad,t_cad,wtf,flag,afk,nconv,datas)
implicit none

!In/Out variables
  integer, intent(in) :: nwalks, maxi, thin_factor, n_cad, datas, nconv
  double precision, intent(in), dimension(0:datas-1)  :: xd, yd, errs
  double precision, intent(in), dimension(0:8) :: pars
  double precision, intent(in), dimension(0:1)  :: pstar, lpstar
  double precision, intent(in), dimension(0:(2*9)-1) :: lims
  double precision, intent(in) :: a_factor, t_cad
  integer, intent(in), dimension(0:8) :: wtf
  logical, intent(in) :: flag(0:3)
  logical, intent(in) :: afk
!Local variables
  double precision, dimension(0:8) :: params
  double precision, dimension(0:datas-1) :: zr
  double precision, dimension(0:2*(9)-1) :: limits, limits_physical
  double precision, dimension(0:nwalks-1) :: chi2_old, chi2_new, chi2_red
  double precision, dimension(0:8,0:nwalks-1) :: params_old, params_new
  double precision, dimension(0:8,0:nwalks-1,0:nconv-1) :: params_chains
  double precision, dimension(0:nwalks-1) :: mstar, rstar
  double precision, dimension(0:nwalks-1) :: jitter_old, jitter_new
  double precision, dimension(0:nwalks-1,0:datas-1) :: mult_old, mult_new, mult_total
  double precision  :: q, esin, ecos, aa, chi2_red_min
  integer :: o, j, n, m, nu, nk, n_burn, spar, new_thin_factor
  logical :: continua, is_burn, is_limit_good, is_cvg, is_eclipse
  double precision :: r_rand(0:nwalks-1), z_rand(0:nwalks-1)
  integer, dimension(0:nwalks-1) :: r_int
  integer, dimension(0:8) :: wtf_all 
  double precision :: r_real
  character(len=15) :: output_files
!external calls
  external :: init_random_seed, find_chi2_tr

  output_files = 'mh_trfit.dat'

  params(:) = pars(:)
  limits(:) = lims(:)
  wtf_all(:) = wtf(:)

  !size of parameters (only parameters to fit!)
  !what parameters are we fitting?
  spar = sum(wtf_all(:))

  !Check if there are flags to evolve modified parameters

  !Period
  if ( flag(0) )  then
    params(1)   = log10(params(1))
    limits(2:3) = log10(limits(2:3))
    limits_physical(2:3) = log10(limits_physical(2:3))
  end if
  ! e and w
  if ( flag(1) ) then
    esin = sqrt(params(2)) * sin(params(3))
    ecos = sqrt(params(2)) * cos(params(3))
    params(2) = esin
    params(3) = ecos
    limits(4) = - sqrt(limits(5))
    limits(5) =   sqrt(limits(5))
    limits(6) = limits(4)
    limits(7) = limits(5)
    limits_physical(4) = - sqrt(limits_physical(5))
    limits_physical(5) =   sqrt(limits_physical(5))
    limits_physical(6) = limits_physical(4)
    limits_physical(7) = limits_physical(5)
  end if
  !a = rp/r*
  if ( flag(3) ) then
    params(5) = log10(params(5))
    limits(10:11) = log10(limits(10:11))
    limits_physical(10:11) = log10(limits_physical(10:11))
  end if
  !i
  if ( flag(2) ) then
    params(4) = params(5) * cos(params(4))
    limits(8) = 0.0
    limits(9) = 1.0
    limits_physical(8) = 0.d0
    limits_physical(9) = 1.d0
  end if


  !Let us create the jitter from the error bars
  call gauss_random_bm(errs(0)*1.d-2,errs(0)*1.d-3,jitter_old,nwalks)
  !call gauss_random_bm(0.0d0,0.0d0,jitter_old,nwalks)
  mult_old(:,:) = 1.0d0
  mult_new(:,:) = 1.0d0
  do nk = 0, nwalks - 1
    do j = 0, datas-1
      mult_old(nk,j) = 1.0d0/sqrt( errs(j)**2 + jitter_old(nk)**2  )
    end do
  end do


  print *, 'CREATING RANDOM SEED'
  call init_random_seed()

  print *, 'CREATING RANDOM (UNIFORM) UNIFORMATIVE PRIORS'
  !Let us create uniformative uniform random priors

  nk = 0
  do while (nk < nwalks )

      !Counter for the limits
      j = 0

      do n = 0, 8
        if ( wtf_all(n) == 0 ) then
          !this parameter does not change
          params_old(n,nk) = params(n)
        else
          call random_number(r_real)
          params_old(n,nk) = limits(j+1) - limits(j)
          params_old(n,nk) = limits(j) + r_real*params_old(n,nk) 
        end if
        j = j + 2 !two limits for each parameter

      end do

    !Check that e < 1 for ew
   if ( flag(1) ) then
     is_limit_good = .false.
     do while ( .not. is_limit_good )
      call check_e(params_old(2,nk),params_old(3,nk),limits(5)**2,is_limit_good)
      if ( .not. is_limit_good  ) then
        params_old(2,nk) = params_old(2,nk) * params_old(2,nk)
        params_old(3,nk) = params_old(3,nk) * params_old(3,nk)
       end if
     end do
   end if

    !Let us find z
    call find_z(xd,params_old(0:5,nk),flag,zr,datas)

    !Let us check if there is an eclipse
    call check_eclipse(zr,params_old(8,nk),is_eclipse,datas)
    !if we do not have an eclipse, let us recalculate this wlaker
    if ( .not. is_eclipse ) then
      nk = nk
    else
    !Each walker is a point in a parameter space
    !Let us estimate our first chi_2 value for each walker
    call find_chi2_tr(xd,yd,errs,params_old(0:5,nk),jitter_old(nk),flag,params_old(6:8,nk), &
                      n_cad, t_cad, chi2_old(nk),datas)
      nk = nk + 1
    end if

  end do
!  stop
  
  !Calculate the degrees of freedom
  nu = datas - spar
  if ( nu <= 0 ) then
    print *, 'Your number of parameters is larger than your datapoints!'
    print *, 'I cannot fit that!'
    stop
  end if
  chi2_red = chi2_old / nu
  !Print the initial cofiguration
  print *, ''
  print *, 'Starting stretch move MCMC calculation'
  print *, 'DOF =', nu

  call print_chain_data(chi2_red,nwalks)

  !Initialize the values
  j = 1
  n = 0
  continua = .TRUE.
  is_burn = .FALSE.
  aa = a_factor 
  n_burn = 1

  !The infinite cycle starts!
  print *, 'STARTING INFINITE LOOP!'
  do while ( continua )

    !Do the work for all the walkers
    call random_number(z_rand)
    call random_number(r_rand)
    !Create random integers to be the index of the walks
    !Note that r_ink(i) != i (avoid copy the same walker)
    call random_int(r_int,nwalks)

    do nk = 0, nwalks - 1 !walkers
        params_new(:,nk) = params_old(:,r_int(nk))
        jitter_new(nk) = jitter_old(r_int(nk))
    end do


   !Let us set a gaussian distribution for the limb darkening coefficents
   if( wtf_all(6) == 0 ) then !q1
     call gauss_random_bm(params(6),0.05d0,params_old(6,:),nwalks)
   end if
   if( wtf_all(7) == 0 ) then !q2
     call gauss_random_bm(params(7),0.05d0,params_old(7,:),nwalks)
   end if


    if ( afk ) then
      wtf_all(5) = 0
      !Fill mass and radius 
      call gauss_random_bm(pstar(0),lpstar(0),mstar,nwalks)
      call gauss_random_bm(pstar(1),lpstar(1),rstar,nwalks)
      !The a parameter comes from 3rd kepler law
      !params_old(1) is the period
      call get_a_scaled(mstar,rstar,params_old(1,:),params_old(5,:),nwalks)
    end if

    !$OMP PARALLEL &
    !$OMP PRIVATE(is_limit_good,q,m)
    !$OMP DO SCHEDULE(DYNAMIC)
    do nk = 0, nwalks - 1 !walkers

    !Draw the random walker nk, from the complemetary walkers
      z_rand(nk) = z_rand(nk) * aa

      !The gz function to mantain the affine variance codition in the walks
      call find_gz(z_rand(nk),aa)

      !Evolve for all the planets for all the parameters
      params_new(:,nk) = params_new(:,nk) + wtf_all(:) * z_rand(nk) * &
                           ( params_old(:,nk) - params_new(:,nk) )
      jitter_new(nk) = jitter_new(nk) + z_rand(nk) * &
                           ( jitter_old(nk) - jitter_new(nk) )

        !Let us check the limits
        call check_limits(params_new(:,nk),limits_physical(:), &
                          is_limit_good,9)
        if ( is_limit_good ) then
            !Check that e < 1 for ew
          if ( flag(1) ) then
            call check_e(params_new(2,nk),params_new(3,nk),1.0d0,is_limit_good)
          end if
        end if

      if ( is_limit_good ) then !evaluate chi2
        !Let us find z
        !call find_z(xd,params_new(0:5,nk),flag,zr,datas)
        !call check_eclipse(zr,params_new(8,nk),is_eclipse,datas)
        !find chi2
        !if ( is_eclipse ) then
          call find_chi2_tr(xd,yd,errs,params_new(0:5,nk),jitter_new(nk), &
               flag,params_new(6:8,nk),n_cad,t_cad,chi2_new(nk),datas)
        !else
        !  chi2_new(nk) = huge(0.0d0)
        !end if
      else !we do not have a good model
        chi2_new(nk) = huge(dble(0.0)) !a really big number
      end if


     mult_new(nk,:) = 1.0d0
     do m = 0, datas-1
       mult_new(nk,m) = 1.0d0/sqrt( errs(m)**2 + jitter_new(nk)**2  )
     end do

     mult_total(nk,:) = mult_new(nk,:) / mult_old(nk,:)

     q = 1.0d0
     do m = 0, datas-1
       q = q * mult_total(nk,m)
     end do

      !Compare the models
      q = q * z_rand(nk)**(spar - 1) * &
          exp( ( chi2_old(nk) - chi2_new(nk) ) * 0.5  )

      if ( q >= r_rand(nk) ) then !is the new model better?
          chi2_old(nk) = chi2_new(nk)
          params_old(:,nk) = params_new(:,nk)
          jitter_old(nk) = jitter_new(nk)
          mult_old(nk,:) = mult_new(nk,:)
      end if

      chi2_red(nk) = chi2_old(nk) / nu

      !Start to burn-in 
      if ( is_burn ) then
        if ( mod(j,new_thin_factor) == 0 ) then
            !$OMP CRITICAL
            write(123,*) j, nk, chi2_old(nk), jitter_old(nk), params_old(:,nk)
            !$OMP END CRITICAL
        end if
      end if
      !End burn-in

    end do !walkers
    !$OMP END PARALLEL

     if ( is_burn ) then

        if ( mod(j,new_thin_factor) == 0 ) then
          n_burn = n_burn + 1
        end if
        if ( n_burn > nconv ) continua = .false.

     else

      if ( mod(j,thin_factor) == 0 ) then

        !Obtain the chi2 mean of all the variables
        chi2_red_min = sum(chi2_red) / nwalks

        !Create the 3D array to use the Gelman-Rubin test
        !The first elemets are the parameters for transit fit
        !second is the information of all chains
        !third is the chains each iteration
        params_chains(:,:,n) = params_old(:,:)
        
        n = n + 1

        if ( n == nconv ) then !Perform GR test

          n = 0

          call print_chain_data(chi2_red,nwalks)
          print *, '==========================='
          print *, '  PERFOMING GELMAN-RUBIN'
          print *, '   TEST FOR CONVERGENCE'
          print *, '==========================='

          !Let us check convergence for all the parameters
          is_cvg = .true.
          do o = 0, 8 !For all parameters 
              !Do the test to the parameters that we are fitting
              if ( wtf_all(o) == 1 ) then
                !do the Gelman and Rubin statistics
                call gr_test(params_chains(o,:,:),nwalks,nconv,is_cvg)
                ! If only a chain for a given parameter does
                ! not converge is enoug to keep iterating
              end if
            if ( .not. is_cvg ) exit
          end do

          if ( .not. is_cvg  ) then
            print *, '=================================='
            print *, 'CHAINS HAVE NOT CONVERGED YET!'
            print *,  nconv*thin_factor,' ITERATIONS MORE!'
            print *, '=================================='
          else
            print *, '==========================='
            print *, '  CHAINS HAVE CONVERGED'
            print *, '==========================='
            print *, 'STARTING BURNING-IN PHASE'
            print *, '==========================='
            is_burn = .True.
            new_thin_factor = thin_factor
            print *, 'Creating ', output_files
            open(unit=123,file=output_files,status='unknown')
          end if

          if ( j > maxi ) then
            print *, 'Maximum number of iteration reached!'
            continua = .FALSE.
          end if

        end if
      !I checked covergence

      end if

    end if

  j = j + 1

  end do

  !Close all the files
  close(123)

end subroutine

