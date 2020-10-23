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
subroutine find_z(t,pars,z,ts)
use constants
implicit none

!In/Out variables
  integer, intent(in) :: ts
  real(kind=mireal), intent(in), dimension(0:ts-1) :: t
  real(kind=mireal), intent(in), dimension(0:5) :: pars
  real(kind=mireal), intent(out), dimension(0:ts-1) :: z
!Local variables
  real(kind=mireal), dimension(0:ts-1) :: ta, swt
  real(kind=mireal) :: tp, P, e, w, i, a
  real(kind=mireal) :: si
!

  tp  = pars(0)
  P   = pars(1)
  e   = pars(2)
  w   = pars(3)
  i   = pars(4)
  a   = pars(5)

  !Obtain the true anomaly by using find_anomaly
  call find_anomaly_tp(t,tp,e,P,ta,ts)

  swt = sin(w+ta)
  si = sin(i)

  where (swt > 0.0 ) !We have the planet in front of the star -> transit
  !z has been calculated
    z = a * ( 1.d0 - e * e ) * sqrt( 1.d0 - swt * swt * si * si ) &
        / ( 1.d0 + e * cos(ta) )
  elsewhere !We have the planet behind the star -> occulation
  !z has avalue which gives flux = 1 in Mandel & Agol module
      z = 1.d1
  end where

end subroutine

subroutine flux_tr(xd,trlab,pars,rps,ldc,&
           n_cad,t_cad,nbands,nradius,n_data,npl,flux_out)
use constants
implicit none

!In/Out variables
  integer, intent(in) :: n_data, npl, nbands, nradius
  integer, intent(in) :: n_cad(0:nbands-1)
  real(kind=mireal), intent(in), dimension(0:n_data-1)  :: xd
  integer, intent(in), dimension(0:n_data-1)  :: trlab !this indicates the instrument label
  real(kind=mireal), intent(in), dimension(0:5,0:npl-1) :: pars
  real(kind=mireal), intent(in), dimension(0:nradius*npl-1) :: rps
!  real(kind=mireal), intent(in), dimension(0:nbands-1,0:npl-1) :: rps
  !pars = T0, P, e, w, b, a/R*, Rp/R*
  real(kind=mireal), intent(in) :: t_cad(0:nbands-1)
  real(kind=mireal), intent(in), dimension (0:2*nbands-1) :: ldc
  real(kind=mireal), intent(out), dimension(0:n_data-1) :: flux_out !output flux model
!Local variables
  real(kind=mireal), dimension(0:n_data-1) :: flux_per_planet
  real(kind=mireal), dimension(0:n_data-1) :: mu
  real(kind=mireal) :: npl_dbl, u1(0:nbands-1), u2(0:nbands-1)
  real(kind=mireal), allocatable, dimension(:,:)  :: flux_ub
  real(kind=mireal), allocatable, dimension(:)  :: xd_ub, z, fmultip
  integer :: n, j, control
  integer, allocatable :: k(:)

  !This flag controls the multi-radius fits
  control = 1
  if (nradius == 1) control = 0

  npl_dbl = dble(npl)


  do n = 0, nbands - 1
    u1(n) = ldc(2*n)
    u2(n) = ldc(2*n+1)
  end do


  flux_per_planet(:) = 0.d0
  do j = 0, n_data - 1

   allocate (flux_ub(0:n_cad(trlab(j))-1,0:npl-1))
   allocate (xd_ub(0:n_cad(trlab(j))-1),z(0:n_cad(trlab(j))-1),fmultip(0:n_cad(trlab(j))-1))
   allocate (k(0:n_cad(trlab(j))-1))

    k(:) = (/(n, n=0,n_cad(trlab(j))-1, 1)/)

    !Calculate the time-stamps for the binned model
    xd_ub(:) = xd(j) + t_cad(trlab(j))*((k(:)+1.d0)-0.5d0*(n_cad(trlab(j))+1.d0))/n_cad(trlab(j))

    !control the label of the planet
    do n = 0, npl - 1

      !Each z is independent for each planet
      call find_z(xd_ub,pars(0:5,n),z,n_cad(trlab(j)))



      if ( ALL( z > 1.d0 + rps(n*nradius+trlab(j)*control) ) .or. rps(n*nradius+trlab(j)*control) < small ) then


        flux_per_planet(j) = flux_per_planet(j) + 1.d0 !This is not eclipse
        flux_ub(:,n) = 0.d0

      else

        !Now we have z, let us use Agol's routines
        call occultquad(z,u1(trlab(j)),u2(trlab(j)),rps(n*nradius+trlab(j)*control),flux_ub(:,n),mu,n_cad(trlab(j)))
        !!!!!call qpower2(z,rp(n),u1,u2,flux_ub(:,n),n_cad)

      end if

    end do !planets

    fmultip(:) = 0.0
    !Sum the flux of all each sub-division of the model due to each planet
    do n = 0, n_cad(trlab(j)) - 1
      fmultip(n) =  SUM(flux_ub(n,:))
    end do

    !Re-bin the model
    flux_per_planet(j) = flux_per_planet(j) +  sum(fmultip) / n_cad(trlab(j))

    !Calcualte the flux received taking into account the transit of all planets
    flux_out(j) =  1.0d0 + flux_per_planet(j) - npl_dbl

    !Restart flux_ub
    flux_ub(:,:) = 0.0

    deallocate(flux_ub,xd_ub,z,fmultip,k)

  end do !n_data

end subroutine

!Flux for a single band fit
subroutine flux_tr_single(xd,pars,ldc,&
           n_cad,t_cad,n_data,npl,flux_out)
implicit none

!In/Out variables
  integer, intent(in) :: n_data, n_cad, npl
  double precision, intent(in), dimension(0:n_data-1)  :: xd
  double precision, intent(in), dimension(0:6,0:npl-1) :: pars
  !pars = T0, P, e, w, b, a/R*, Rp/R*
  double precision, intent(in) :: t_cad
  double precision, intent(in), dimension (0:1) :: ldc
  double precision, intent(out), dimension(0:n_data-1) :: flux_out
!Local variables
  double precision, dimension(0:n_data-1) :: flux_per_planet
  double precision, dimension(0:n_data-1) :: mu
  double precision :: npl_dbl, small, u1, u2, rp(0:npl-1)
  double precision, dimension(0:n_cad-1,0:npl-1)  :: flux_ub
  double precision, dimension(0:n_cad-1)  :: xd_ub, z, fmultip
  integer :: n, j, k(0:n_cad-1)
!External function
  external :: occultquad, find_z

  small = 1.d-5
  npl_dbl = dble(npl)

  u1 = ldc(0)
  u2 = ldc(1)

  !Get planet radius
  rp(:) = pars(6,:)

  ! k(:) = (/(n, n=0,n_cad(trlab(j))-1, 1)/)

  flux_per_planet(:) = 0.d0
  flux_ub(:,:) = 0.d0
  do j = 0, n_data - 1

    !Calculate the time-stamps for the binned model
    xd_ub(:) = xd(j) + t_cad*((k(:)+1.d0)-0.5d0*(n_cad+1.d0))/n_cad

    !control the label of the planet
    do n = 0, npl - 1

      !Each z is independent for each planet
      call find_z(xd_ub,pars(0:5,n),z,n_cad)

      if ( ALL( z > 1.d0 + rp(n) ) .or. rp(n) < small ) then

        flux_per_planet(j) = flux_per_planet(j) + 1.d0 !This is not eclipse
        flux_ub(:,n) = 0.d0

      else

        !Now we have z, let us use Agol's routines
        call occultquad(z,u1,u2,rp(n),flux_ub(:,n),mu,n_cad)
        !call qpower2(z,rp(n),u1,u2,flux_ub(:,n),n_cad)

      end if

    end do !planets

    fmultip(:) = 0.0
    !Sum the flux of all each sub-division of the model due to each planet
    do n = 0, n_cad - 1
      fmultip(n) =  SUM(flux_ub(n,:))
    end do

    !Re-bin the model
    flux_per_planet(j) = flux_per_planet(j) +  sum(fmultip) / n_cad

    !Calcualte the flux received taking into account the transit of all planets
    flux_out(j) =  1.0d0 + flux_per_planet(j) - npl_dbl

    !Restart flux_ub
    flux_ub(:,:) = 0.0

  end do !n_data

end subroutine

subroutine find_chi2_tr(xd,yd,errs,trlab,jtrlab,pars,rps,ldc,jtr,flag, &
           n_cad,t_cad,chi2,n_data,nbands,nradius,njtr,npl)
use constants
implicit none

!In/Out variables
  integer, intent(in) :: n_data, npl, nbands,nradius, njtr
  integer, intent(in) :: n_cad(0:nbands-1)
  real(kind=mireal), intent(in), dimension(0:n_data-1)  :: xd, yd, errs
  real(kind=mireal), intent(in), dimension(0:5,0:npl-1) :: pars
  real(kind=mireal), intent(in), dimension(0:nradius*npl-1) :: rps
!  real(kind=mireal), intent(in), dimension(0:nbands-1,0:npl-1) :: rps
  integer, intent(in), dimension(0:n_data-1)  :: trlab, jtrlab
  !pars = T0, P, e, w, b, a/R*
  real(kind=mireal), intent(in) :: t_cad(0:nbands-1)
  real(kind=mireal), dimension(0:njtr-1), intent(in) :: jtr
  logical, intent(in), dimension(0:3) :: flag
  real(kind=mireal), intent(in) :: ldc(0:2*nbands-1)
  real(kind=mireal), intent(out) :: chi2
!Local variables
  real(kind=mireal), dimension(0:n_data-1) :: res

    call find_res_tr(xd,yd,trlab,pars,rps,ldc,flag, &
           n_cad,t_cad,res,n_data,nbands,nradius,npl)
    res(:) = res(:) / sqrt( errs(:)**2 + jtr(jtrlab(:))**2 )
    chi2 = dot_product(res,res)


end subroutine

subroutine find_res_tr(xd,yd,trlab,pars,rps,ldc,flag, &
           n_cad,t_cad,res,n_data,nbands,nradius,npl)
use constants
implicit none

!In/Out variables
  integer, intent(in) :: n_data, npl, nbands, nradius
  integer, intent(in) :: n_cad(0:nbands-1)
  real(kind=mireal), intent(in), dimension(0:n_data-1)  :: xd, yd
  real(kind=mireal), intent(in), dimension(0:5,0:npl-1) :: pars
  real(kind=mireal), intent(in), dimension(0:nradius*npl-1) :: rps
!  real(kind=mireal), intent(in), dimension(0:nbands-1,0:npl-1) :: rps
  integer, intent(in), dimension(0:n_data-1)  :: trlab
  !pars = T0, P, e, w, b, a/R*
  real(kind=mireal), intent(in) :: t_cad(0:nbands-1)
  logical, intent(in), dimension(0:3) :: flag
  real(kind=mireal), intent(in) :: ldc(0:2*nbands-1)
  real(kind=mireal), intent(out) :: res(0:n_data-1)
!Local variables
  real(kind=mireal), dimension(0:n_data-1) :: flux_out
  real(kind=mireal), dimension(0:5,0:npl-1) :: up_pars !updated parameters
  real(kind=mireal), dimension(0:npl-1) :: t0, P, e, w, i, a, tp
  real(kind=mireal), dimension (0:2*nbands-1) :: up_ldc
  logical :: is_good
  integer :: n


  t0  = pars(0,:)
  P   = pars(1,:)
  e   = pars(2,:)
  w   = pars(3,:)
  i   = pars(4,:)
  a   = pars(5,:)

  if (flag(0)) P = 1.d0**pars(1,:)
  if (flag(1)) call ewto(e,w,e,w,npl)
  if (flag(3)) call rhotoa(a(0),P(:),a(:),npl)
  if (flag(2)) call btoi(i,a,e,w,i,npl)


  !Update limb darkening coefficients, pass from q's to u's
  is_good = .true.
  do n = 0, nbands - 1
    call get_us(ldc(2*n),ldc(2*n+1),up_ldc(2*n),up_ldc(2*n+1),1)
    call check_us(up_ldc(2*n),up_ldc(2*n+1),is_good)
    if ( .not. is_good ) exit
  end do

  if ( any( e > 1.d0 ) .or. any(e < 0.d0 ) ) is_good = .false.

  if ( is_good ) then

    do n = 0, npl - 1
      call find_tp(t0(n),e(n),w(n),P(n),tp(n))
    end do

    !At this point the parameters to fit are tp,P,e,w,i,a without parametrization
    up_pars(0,:) = tp
    up_pars(1,:) = P
    up_pars(2,:) = e
    up_pars(3,:) = w
    up_pars(4,:) = i
    up_pars(5,:) = a

    !Here we have a vector for the radius called rps

    call flux_tr(xd,trlab,up_pars,rps,up_ldc,&
           n_cad,t_cad,nbands,nradius,n_data,npl,flux_out)
    res(:) =  flux_out(:) - yd(:)

  else

    res(:) = huge(0.d0)

  end if

end subroutine