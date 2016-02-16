!-------------------------------------------------------------------------
!Name of the program
!Here write a simple description of the program
!Date -->
!-------------------------------------------------------------------------

!----------------------------------------------------------
! This subroutine generates pseudo-random seeds
! Taken from
! https://gcc.gnu.org/onlinedocs/gfortran/RANDOM_005fSEED.html#RANDOM_005fSEED
!----------------------------------------------------------

subroutine init_random_seed()
use iso_fortran_env, only: int64
implicit none
integer, allocatable :: seed(:)
integer :: i, n, un, istat, dt(8), pid
integer(int64) :: t

call random_seed(size = n)
allocate(seed(n))
! First try if the OS provides a random number generator
open(newunit=un, file="/dev/urandom", access="stream", &
     form="unformatted", action="read", status="old", iostat=istat)
if (istat == 0) then
   read(un) seed
   close(un)
else
   ! Fallback to XOR:ing the current time and pid. The PID is
   ! useful in case one launches multiple instances of the same
   ! program in parallel.
   call system_clock(t)
   if (t == 0) then
      call date_and_time(values=dt)
      t = (dt(1) - 1970) * 365_int64 * 24 * 60 * 60 * 1000 &
           + dt(2) * 31_int64 * 24 * 60 * 60 * 1000 &
           + dt(3) * 24_int64 * 60 * 60 * 1000 &
           + dt(5) * 60 * 60 * 1000 &
           + dt(6) * 60 * 1000 + dt(7) * 1000 &
           + dt(8)
   end if
   pid = getpid()
   t = ieor(t, int(pid, kind(t)))
   do i = 1, n
      seed(i) = lcg(t)
   end do
end if
call random_seed(put=seed)

contains
! This simple PRNG might not be good enough for real work, but is
! sufficient for seeding a better PRNG.
function lcg(s)
  integer :: lcg
  integer(int64) :: s
  if (s == 0) then
     s = 104729
  else
     s = mod(s, 4294967296_int64)
  end if
  s = mod(s * 279470273_int64, 4294967291_int64)
  lcg = int(mod(s, int(huge(0), int64)), kind(0))
end function lcg
end subroutine init_random_seed

!-----------------------------------------------------------

subroutine find_anomaly(man,ta,ec,delta,imax,dman)
implicit none

integer, intent(in) :: dman
double precision, intent(in) , dimension(0:dman-1) :: man
double precision, intent(out), dimension(0:dman-1) :: ta
double precision, intent(in) :: ec, delta
integer, intent(in) :: imax

integer :: i,n
double precision, dimension(0:dman-1) :: f, df

  ta(:)  = 0.0
  f(:)   = ta(:) - ec * sin(ta(:)) - man(:)
  df(:)  =   1.0 - ec * cos(ta(:))
  n = 0

  do i = 0, dman-1
    do while ( abs(f(i)) >= delta .and. n <= imax )
      ta(i)  = ta(i) - f(i) / df(i)
      f(i)   = ta(i) - ec * sin(ta(i)) - man(i)
      df(i)  =   1.0 - ec * cos(ta(i))
      n = n + 1
    end do
  end do

  if ( n > imax ) then
    print *, 'I am tired, so much N-R'
    stop
  end if 

  ta(:) = sqrt( (1. + ec) / (1. -ec) ) * tan(ta(:)*0.5)
  ta(:) = 2. * atan(ta(:))

end subroutine

!-----------------------------------------------------------

subroutine rv_circular(t,rv0,t0,k,P,rv,ts)
implicit none

integer, intent(in) :: ts
double precision, intent(in), dimension(0:ts-1)  :: t
double precision, intent(out), dimension(0:ts-1) :: rv
double precision, intent(in) :: k, rv0, t0, P

double precision, parameter :: pi = 3.1415926535897932384626

  rv(:) = rv0 - k * sin( 2.*pi*( t(:) - t0) / P )

end subroutine

!-----------------------------------------------------------

subroutine rv_curve(t,rv0,t0,k,P,ec,w,rv,ts)
implicit none

integer, intent(in) :: ts
double precision, intent(in), dimension(0:ts-1)  :: t
double precision, intent(out), dimension(0:ts-1) :: rv
double precision, intent(in) :: k, rv0, t0, P, ec, w

double precision, parameter :: pi = 3.1415926535897932384626
double precision, dimension(0:ts-1) :: ma, ta
double precision :: delta = 1e-4
integer :: imax

external :: find_anomaly

  imax = int(1e5)

  ma(:) = 2.* pi * ( t(:) - t0 ) / P
  call find_anomaly(ma,ta,ec,delta,imax,ts)

  rv(:) = rv0 + k * ( cos(ta(:) + w ) + ec * cos(w) )
  
end subroutine

!-----------------------------------------------------------

subroutine find_chi2(xd,yd,errs,tlab,rv0,k,ec,w,t0,P,chi2,datas,nt)
implicit none

integer, intent(in) :: datas, nt
double precision, intent(in), dimension(0:datas-1)  :: xd, yd, errs, tlab
double precision, intent(in), dimension(0:nt-1)  :: rv0
double precision, intent(in)  :: k, t0, P, ec, w
double precision, intent(out) :: chi2

double precision, parameter :: pi = 3.1415926535897932384626
double precision, dimension(0:datas-1) :: model, res
integer :: i, tel

external :: rv_circular, rv_curve

  chi2 = 0.0

  !Here we could control what kind of fit we want to do

  tel = 0
  i = 0
  do i = 0, datas-1
  !call rv_circular(xd,rv0,t0,k,P,model,datas)
    if ( tel .ne. tlab(i)  ) tel = tel + 1 
    call rv_curve(xd(i),rv0(tel),t0,k,P,ec,w,model(i),1)
  end do

  !We will assume that the data is sorted, plese sort it!

  res(:) = ( yd(:) - model(:) ) / (errs(:)*errs(:))
  res(:) = res(:) * res(:)

  chi2 = sum(res)

end subroutine

!-----------------------------------------------------------

!subroutine mcmc_rv(xd,yd,errs,tlab,rv0,k,ec,w,t0,P,rv0mco,kmco,ecmco,wmco,t0mco,Pmco,prec,imcmc,ndata,chi_limit,datas,nt)
subroutine mcmc_rv(xd,yd,errs,tlab,rv0,k,ec,w,t0,P,prec,imcmc,ndata,chi_limit,datas,nt)
implicit none

integer, intent(in) :: imcmc, ndata, datas, nt
double precision, intent(in), dimension(0:datas-1)  :: xd, yd, errs, tlab
double precision, intent(in), dimension(0:nt-1)  :: rv0
double precision, intent(in)  :: k,t0, P, ec, w,prec,chi_limit
!double precision, intent(out), dimension(0:ndata-1)  :: kmco, ecmco, wmco, t0mco, Pmco
!double precision, intent(out), dimension(0:ndata-1, 0:nt-1) :: rv0mco
!double precision, intent(out), dimension(0:nt-1,0:ndata-1) :: rv0mco

double precision, parameter :: pi = 3.1415926535897932384626
double precision :: chi2_old, chi2_new
double precision, dimension(0:nt-1)  :: rv0mc, rv0mcn
double precision :: kmc, t0mc, Pmc, ecmc, wmc
double precision :: kmcn, t0mcn, Pmcn, ecmcn, wmcn
double precision  :: sk, srv0, st0, sP, sec, sw
double precision  :: q
integer :: i, j, check, n
real, dimension(0:5+nt) :: r

external :: init_random_seed, find_chi2

  check = imcmc / ndata

  if ( imcmc < ndata ) check = 1

  kmc    = k
  rv0mc  = rv0
  t0mc   = t0
  Pmc    = P
  ecmc   = ec
  wmc    = w

!rv0mco(:,0) = rv0mc(:)
!  kmco(0) = kmc
! ecmco(0) = ecmc
!  wmco(0) = wmc
! t0mco(0) = t0mc
!  Pmco(0) = Pmc

  sk = k * prec
  srv0 = k * prec
  st0 = t0 * prec
  sP = P * prec
  sec = 1. * prec
  sw = 2.*pi * prec

  call find_chi2(xd,yd,errs,tlab,rv0mc,kmc,ecmc,wmc,t0mc,Pmc,chi2_old,datas,nt)

  print *, 'Starting MCMC calculation'
  print *, 'Initial Chi_2: ', chi2_old

  call init_random_seed()
  !Let us create an array of random numbers to save time
  !Check the ram consumption

  open(unit=101,file='mcmc_rv.dat',status='unknown')
  write(101,*)'# i k ec w t0 P rv0mc(vector)'
  write(101,*) 0,rv0mc, kmc, ecmc, wmc, t0mc, Pmc

  n = 1
  i = 1
  do while ( chi2_old >= chi_limit .and. i <= imcmc - 1 )
    call random_number(r)
    r(1:5+nt) = ( r(1:5+nt) - 0.5) * 2.
    kmcn   =   kmc   + r(1) * sk
    ecmcn  =   ecmc  + r(2) * sec
    wmcn   =   wmc   + r(3) * sw
    t0mcn  =   t0mc  + r(4) * st0
    Pmcn   =   Pmc   + r(5) * sP
    do j = 0, nt-1
      rv0mcn(j) =   rv0mc(j) + r(6+j) * srv0
    end do
    call find_chi2(xd,yd,errs,tlab,rv0mcn,kmcn,ecmcn,wmcn,t0mcn,Pmcn,chi2_new,datas,nt)
    q = exp( ( chi2_old - chi2_new ) * 0.5  )
    if ( q > r(0) ) then
      chi2_old = chi2_new
       rv0mc = rv0mcn
         kmc = kmcn
        ecmc = ecmcn
         wmc = wmcn
        t0mc = t0mcn
         Pmc = Pmcn
    end if
    if ( mod(i,check) == 0 ) then
       print *, 'iter ',i,'  of ',imcmc,'chi2 = ',chi2_old
       write(101,*) i, kmc, ecmc, wmc, t0mc, Pmc, rv0mc
       !rv0mco(:,n) = rv0mc
       !  kmco(n) = kmc
       ! ecmco(n) = ecmc
       !  wmco(n) = wmc
       ! t0mco(n) = t0mc
       !  Pmco(n) = Pmc
               n = n + 1
    end if
    i = i + 1
  end do

  print *, 'Final Chi_2: ', chi2_old

  close(101)

end subroutine
