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
  double precision :: wp, ws
  double precision :: si, new_t0, ttot
  double precision :: pi = 3.1415926535897932384626d0
  integer :: n, j
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
  ws  = w       !star periastron
  wp  = ws + pi !planet periastron
  if (flag(3)) a = 10.d0**a
  if (flag(2)) i = acos( i / a * ( 1.d0 + e * sin(wp) ) / ( 1.d0 - e*e ) )

  !Let us estimate the eclipse duration to rule out the no real recondary transits
  !For a planet with radius 0.0. This would not affect the method
  !and let us assume a central transit with i = 90 deg
  !ttot = (1.d0 + 0.d0)**2 - ( a * cos(i) * (1.0d0 - e*e) / ( 1.0d0 + e * sin(w)) )**2
  !ttot = asin( ttot / a / sin(i) )
  !ttot = P * ttot / pi * sqrt(1.0 - e*e) / ( 1.d0 + e*sin(w) )
  !ttot = 1.d0
  ttot = asin( 1.0 / a )
  ttot = P * ttot / pi

  !Obtain the eccentric anomaly by using find_anomaly
  call find_anomaly(t,t0,e,ws,P,ta,ts)
  swt = sin(wp+ta)

  si = sin(i)
  z = a * ( 1.d0 - e * e ) * sqrt( 1.d0 - swt * swt * si * si ) &
      / ( 1.d0 + e * cos(ta) ) 
  !z has been calculated

  !Let us remove the secondary transits
  do n = 0, ts - 1
    j = int( ( t(n) - t0 ) / P )
    new_t0 = t0 + j*P
    if ( t(n) > t0 + j*P + ttot .and. t(n) < t0 + (j+1)*P - ttot ) &
      z(n) = 1.d1
  end do
  
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
subroutine find_chi2_tr_trapezoidal(xd,yd,errs,plab_tr,pars,jitter,flag,ldc,&
           n_cad,t_cad,chi2,datas,npl)
implicit none

!In/Out variables
  integer, intent(in) :: datas, n_cad, npl
  double precision, intent(in), dimension(0:datas-1)  :: xd, yd, errs
  integer, intent(in), dimension(0:datas-1)  :: plab_tr
  double precision, intent(in), dimension(0:6,0:npl-1) :: pars
  !pars = T0, P, e, w, b, a/R*, Rp/R*
  double precision, intent(in) :: t_cad
  double precision, intent(in) :: jitter
  logical, intent(in), dimension(0:3) :: flag
  double precision, intent(in), dimension (0:1) :: ldc
  double precision, intent(out) :: chi2
!Local variables
  double precision, dimension(0:datas-1) :: muld_npl
  double precision, dimension(0:datas-1) :: res, muld, mu
  double precision :: npl_dbl, small, u1, u2, rp(0:npl-1)
  !double precision, dimension(0:datas-1,0:n_cad-1)  :: xd_ub, z, flux_ub
  double precision, dimension(0:n_cad)  :: xd_ub, z, fmultip
  double precision, dimension(0:n_cad,0:npl-1)  :: flux_ub
  double precision :: t_cad2, t_cadn
  integer :: n, j, k
  logical :: is_good
!External function
  external :: occultquad

  small = 1.d-5
  npl_dbl = dble(npl)

  t_cad2 = 0.5d0 * t_cad
  t_cadn = t_cad / n_cad

  !re-transform the parameters to u1 and u2
  u1 = sqrt(ldc(0))
  u2 = u1*( 1.d0 - 2.d0*ldc(1))
  u1 = 2.d0*u1*ldc(1)

  !Get planet radius
  rp(:) = pars(6,:)

  !are the u1 and u2 within a physical solution
  call check_us(u1,u2,is_good)
  if ( flag(1) ) then
    do n = 0, npl - 1
     call check_e(pars(2,n),pars(3,n),is_good)
     if ( .not. is_good ) exit
    end do
  end if

  if ( is_good ) then

  !Selective re-sampling
  muld_npl(:) = 0.d0
  !Restart flux_ub
  flux_ub(:,:) = 0.0
  do j = 0, datas - 1

    !The sime time stamps for all planets
    do k = 0, n_cad
      xd_ub(k) = xd(j) - t_cad2 + k*t_cadn
    end do

    do n = 0, npl - 1

      !Are we generating an eclipse?
      !Take care with the pars
      call find_z(xd_ub,pars(0:5,n),flag,z,n_cad+1)

      if ( ( ALL( z > 1.d0 + 2.d0*rp(n) ) ) .or. rp(n) < small ) then

        muld_npl(j) = muld_npl(j) + 1.d0 !This is not eclipse

      else

       !Each planet has a different orbit
       !Each planet generates a different eclipse
       call occultquad(z,u1,u2,rp(n),flux_ub(:,n),mu,n_cad+1)

     end if

    end do !planets

    fmultip(:) = 0.0
    !Get ready to rebin multiplanet flux
    do k = 0, n_cad
      fmultip(k) =  SUM(flux_ub(k,:))
    end do

    !Re-bin the model
    muld_npl(j) = muld_npl(j) + ( sum(fmultip) + sum(fmultip(1:n_cad-1)) ) &
                  / n_cad / 2.0d0

    muld(j) =  1.0d0 + muld_npl(j) - npl_dbl

  !Restart flux_ub
  flux_ub(:,:) = 0.0

  end do !datas

  !Let us calculate the residuals
  ! chi^2 = \Sum_i ( M - O )^2 / \sigma^2
  !Here I am assuming that we want limb darkening
  !If this is not true, use mu
 res(:) = ( muld(:) - yd(:) ) / sqrt( errs(:)**2 + jitter**2 )
  chi2 = dot_product(res,res)

  else

    chi2 = huge(0.d0)

  end if

end subroutine

subroutine find_chi2_tr(xd,yd,errs,plab_tr,pars,jitter,flag,ldc,&
           n_cad,t_cad,chi2,datas,npl)
implicit none

!In/Out variables
  integer, intent(in) :: datas, n_cad, npl
  double precision, intent(in), dimension(0:datas-1)  :: xd, yd, errs
  integer, intent(in), dimension(0:datas-1)  :: plab_tr
  double precision, intent(in), dimension(0:6,0:npl-1) :: pars
  !pars = T0, P, e, w, b, a/R*, Rp/R*
  double precision, intent(in) :: t_cad
  double precision, intent(in) :: jitter
  logical, intent(in), dimension(0:3) :: flag
  double precision, intent(in), dimension (0:1) :: ldc
  double precision, intent(out) :: chi2
!Local variables
  double precision, dimension(0:datas-1) :: muld_npl
  double precision, dimension(0:datas-1) :: res, muld, mu
  double precision :: npl_dbl, small, u1, u2, pz(0:npl-1), q1k, q2k

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
  pz(:) = pars(6,:)

!are the u1 and u2 within a physical solution
  call check_us(u1,u2,is_good)
  if ( flag(1) ) then
    do n = 0, npl - 1
     call check_e(pars(2,n),pars(3,n),is_good)
     if ( .not. is_good ) exit
    end do
  end if

  if ( is_good ) then

  !Selective re-sampling
  n = 0
  muld_npl(:) = 0.d0
  do j = 0, datas - 1

    !control the label of the planet
    do n = 0, npl - 1

    !Are we generating an eclipse?
    !Take care with the pars
    do k = 0, n_cad - 1
      xd_ub(k) = xd(j) + t_cad*((k+1.d0)-0.5d0*(n_cad+1.d0))/n_cad
    end do

    call find_z(xd_ub,pars(0:5,n),flag,z,n_cad)

    if ( ALL( z > 1.d0 + 2.0*pz(n) ) .or. pz(n) < small ) then

      muld_npl(j) = muld_npl(j) + 1.d0 !This is not eclipse

    else


      !Now we have z, let us use Agol's routines
      !call occultquad(z,u1,u2,pz,flux_ub,mu,n_cad)
      call occultquad(z,u1,u2,pz(n),flux_ub,mu,n_cad)

      !Re-bin the data
      muld_npl(j) = muld_npl(j) + sum(flux_ub) / n_cad


    end if

    end do !planets

    !The final flux is F = (F1 + F2 + ... + Fn ) / n
    muld(j) =  1.0d0 + muld_npl(j) - npl_dbl

  end do !datas
!print *, 'stop new tr chi2'
  !stop


  !Let us calculate the residuals
  ! chi^2 = \Sum_i ( M - O )^2 / \sigma^2
  !Here I am assuming that we want limb darkening
  !If this is not true, use mu
  res(:) = ( muld(:) - yd(:) ) / sqrt( errs(:)**2 + jitter**2 )
  chi2 = dot_product(res,res)

  else

    chi2 = huge(0.e0)

  end if

end subroutine

