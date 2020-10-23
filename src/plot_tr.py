# -----------------------------------------------------------------
#       TRANSIT PARAMERS TO BE USED TO GENERATE PLOTS
# -----------------------------------------------------------------

# Create parameters vector
pars_tr = np.zeros(shape=(nplanets, 6))
for m in range(0, nplanets):
    pars_tr[m][0] = tp_val[m]
    pars_tr[m][1] = P_val[m]
    pars_tr[m][2] = e_val[m]
    pars_tr[m][3] = w_val[m]
    pars_tr[m][4] = i_val[m]
    pars_tr[m][5] = a_val[m]


# ===========================================================
# ===========================================================

def create_folded_tr_plots():

    for o in range(0, nplanets):

        if (fit_tr[o]):

            tr_vector = [None]*nbands

            for m in range(0, nbands):
                localx = []
                localy = []
                locale = []
                localt = []
                for n in range(0, len(megax)):
                    if (trlab[n] == m):
                        localx.append(megax[n])
                        localy.append(megay[n])
                        locale.append(megae[n])
                        localt.append(0)
                tr_vector[m] = create_tr_vector(
                    localx, localy, locale, localt, pars_tr, rp_val, o, m)

            transpose_tr = np.asarray(tr_vector)
            transpose_tr = transpose_tr.transpose()
            fancy_tr_plot(transpose_tr, o)


# Ntransit is the number of the transit that we want to plot
# tr_vector contains:
# xtime,yflux,eflux,xmodel,xmodel_res,fd_ub,res_res,fd_ub_unbinned
# these lists contains all the information for a given label
def fancy_tr_plot(tr_vector, pnumber):

    fname = outdir+'/'+star+plabels[pnumber]+'_tr.pdf'
    print('Creating ', fname)
    # Do the plot
    tfc = 24.  # time factor conversion to hours
    local_T0 = 0.

    # Extract the vectors to be plotted from tr_vector
    xtime = tr_vector[0]
    yflux = tr_vector[1]
    eflux = tr_vector[2]
    xmodel = tr_vector[3]
    xmodel_res = tr_vector[4]
    fd_ub = tr_vector[5]
    res_res = tr_vector[6]
    fd_ub_unbinned = tr_vector[7]

    # Do we want to plot a binned model?
    tvector = np.concatenate(xtime)
    rvector = np.concatenate(res_res)
    tbin = 5./60./24.
    fvector = np.concatenate(yflux)
    leftt = min(tvector)
    right = leftt + tbin
    xbined = []
    fbined = []
    rbined = []
    while (leftt < max(tvector)):
        fdummy = []
        rdummy = []
        for i in range(0, len(tvector)):
            if (tvector[i] > leftt and tvector[i] < right):
                fdummy.append(fvector[i])
                rdummy.append(rvector[i])
        fbined.append(np.mean(fdummy))
        rbined.append(np.mean(rdummy))
        xbined.append((leftt + tbin/2.)*24.)
        leftt = leftt + tbin
        right = right + tbin
    fbined = np.asarray(fbined)
    rbined = np.asarray(rbined)

    if plot_binned_data:
        for o in range(0, len(tr_colors)):
            tr_colors[o] = '#C0C0C0'

    # Start the plot
    plt.figure(1, figsize=(fsx, fsy+(nbands-1)*0.75*fsy))
    # Plot the transit light curve
    gs = gridspec.GridSpec(nrows=2, ncols=1, height_ratios=[
                           3.0, 1./(1+(nbands-1)*0.75)])
    gs.update(hspace=0.00)
    ax1 = plt.subplot(gs[0])
    plt.tick_params(labelsize=fos, direction='in')
    x_lim = (min(np.concatenate(xtime))-local_T0)*tfc
    plt.xlim(x_lim, -x_lim)
    if (select_y_tr):
        plt.ylim(y_lim_min, y_lim_max)
    min_val_model = max(np.concatenate(fd_ub)) - min(np.concatenate(fd_ub))
    deltay = 0.
    dy = 0.
    for m in range(0, nbands):
        if (plot_tr_errorbars):
            plt.errorbar((xtime-local_T0)*tfc, yflux, errors,
                         color=tr_colors[m], fmt='.', alpha=1.0)
        else:
            plt.plot((xtime[m]-local_T0)*tfc, yflux[m]-deltay, color=tr_colors[m],
                     ms=7, marker=mark_tr[m], alpha=0.75, linewidth=0.)
            plt.plot((xmodel[m]-local_T0)*tfc, fd_ub[m] -
                     deltay, 'k', linewidth=2.0, alpha=1.0)
            plt.errorbar(-x_lim*(0.95), min(yflux[m]-deltay), eflux[m]
                         [0], color=tr_colors[m], ms=7, fmt=mark_tr[m], alpha=1.0)
            plt.annotate(
                'Error bar '+bands[m], xy=(-x_lim*(0.70), min(yflux[m]-deltay)), fontsize=fos*0.7)
            if (m < nbands - 1):
                dy = max(yflux[m+1])-min(yflux[m+1])
            deltay = deltay + dy
            if plot_binned_data:
                plt.plot(xbined, fbined, 'ro')

        # save the data
        model_matrxi = np.asarray([(xmodel[m]-local_T0)*tfc, fd_ub[m]])
        np.savetxt(
            outdir+'/'+star+plabels[pnumber]+'-trmodel'+bands[m]+'.txt', model_matrxi.T)
        data_matrxi = np.asarray(
            [(xtime[m]-local_T0)*tfc, yflux[m], eflux[m], res_res[m]])
        np.savetxt(
            outdir+'/'+star+plabels[pnumber]+'-trdata'+bands[m]+'.txt', data_matrxi.T)

    if (nbands == 1):
        plt.ylabel('Flux', fontsize=fos)
    if (nbands > 1):
        plt.ylabel('Flux + offset', fontsize=fos)
    # Calculate the optimal step for the plot
    step_plot = int(abs(x_lim))  # the value of the x_axis
    # now we ensure the result is par
    step_plot = step_plot + int(step_plot % 2)
    step_plot = int(step_plot / 8.) + 1  # The size of the jump depends
    # let us get the new limit
    nuevo = np.arange(0, int(abs(x_lim)) + step_plot, step_plot)
    mxv = np.max(nuevo)
#  plt.xticks( np.arange(int(x_lim),int(-x_lim)+1,step_plot))
    plt.xticks(np.arange(-mxv, mxv+step_plot, step_plot))
    plt.minorticks_on()
    plt.ticklabel_format(useOffset=False, axis='y')
    plt.xlim(x_lim, -x_lim)
    plt.tick_params(axis='x', which='both', direction='in', labelbottom=False)
    plt.tick_params(axis='y', which='both', direction='in')
    # ------------------------------------------------------------
    # Plot the residuals
    # ------------------------------------------------------------
    ax0 = plt.subplot(gs[1])
    plt.tick_params(labelsize=fos, direction='in')
    for m in range(nbands):
        if (plot_tr_errorbars):
            plt.errorbar((xmodel_res[m]-local_T0)*tfc, res_res[m]
                         * 1e6, eflux[m]*1e6, fmt='.', alpha=0.5)
        else:
            plt.plot((xmodel_res[m]-local_T0)*tfc, res_res[m]*1e6, 'o',
                     color=tr_colors[m], ms=7, marker=mark_tr[m], alpha=0.5)
    plt.plot([x_lim, -x_lim], [0.0, 0.0], 'k--', linewidth=1.0, alpha=1.0)
    plt.xticks(np.arange(-mxv, mxv+step_plot, step_plot))
    plt.xlim(x_lim, -x_lim)
    yylims = ax0.get_ylim()
    miy = (max(abs(yylims[0]), abs(yylims[1])))
    plt.yticks(np.arange(-miy, miy, miy/2.))
    plt.ylim(-miy, miy*1.25)
    if plot_binned_data:
        plt.plot(xbined, rbined*1e6, 'ro')
    # Calcualte the rms
    if (is_plot_std_tr):
        trsigma = np.std(res_res*1e6, ddof=1)
        trsstr = ('%4.0f ppm' % (trsigma))
        y0, yyyy = ax0.get_ylim()
        plt.annotate('$\sigma = $'+trsstr, xy=(x_lim *
                                               (0.80), y0 + 1.8*miy), fontsize=fos*0.7)
#  if ( select_y_tr ):
#    plt.ylim( - ( y_lim_max - 1.0),y_lim_max - 1.0 )
    # Plot the residuals
    plt.minorticks_on()
    plt.tick_params(axis='x', which='both', direction='in')
    plt.tick_params(axis='y', which='both', direction='in')
    plt.ylabel('Residuals (ppm)', fontsize=fos*0.75)
    plt.xlabel("T - T0 (hours)", fontsize=fos)
    plt.savefig(fname, format='pdf', bbox_inches='tight')
    plt.savefig(fname[:-3]+'png', format='png', bbox_inches='tight', dpi=300)
    plt.close()


def create_tr_vector(time, flujo, eflujo, trlab, pars_tr, rp, plabel, bandlab):


    time = np.asarray(time)
    flujo = np.asarray(flujo)
    eflujo = np.asarray(eflujo)

    P = best_value(P_vec[plabel], maxloglike, get_value)
    T0 = best_value(T0_vec[plabel], maxloglike, get_value)
    tt = best_value(trt_vec[plabel], maxloglike, get_value)
    tt = tt/24.

    #span has to be given in units of days
    if (len(span_tr) < 1):
        span = 2*tt
    else:
        span = span_tr[plabel]

    span = 2*tt

    indices = []
    phase = abs(((time-T0)%P)/P)
    phase[phase>0.5] -= 1
    indices = abs(phase) <= span/P

    local_time = phase[indices]*P*24.0
    xtime = phase[indices]*P
    yflux = flujo[indices]
    eflux = eflujo[indices]

    xmodel_res = np.asarray(xtime)
    mimax = span
    xmodel = np.arange(-mimax, mimax, 1.0/60./24.)
    newtrlab = [0]*len(xmodel)

    # Let us create the model
    control = 1
    if nradius == 1:
        control = 0
    # The model has T0 = 0
    dumtp = pti.find_tp(0.0, e_val[plabel], w_val[plabel], P_val[plabel])
    dparstr = np.concatenate([[dumtp], pars_tr[plabel][1:]])
    #fd_ub = pti.flux_tr(xmodel,dparstr,my_ldc,n_cad,t_cad)
    fd_ub = pti.flux_tr(xmodel, newtrlab, dparstr, rp_val[plabel*nradius+bandlab*control],
                        my_ldc[bandlab*2:bandlab*2+2], n_cad[bandlab], t_cad[bandlab], nradius=1)
    # Let us create an unbinned model plot
    #fd_ub_unbinned = pti.flux_tr(xmodel,dparstr,my_ldc,1,t_cad)
    fd_ub_unbinned = pti.flux_tr(
        xmodel, newtrlab, dparstr, rp_val[plabel*nradius+bandlab*control], my_ldc[bandlab*2:bandlab*2+2], [1], t_cad[bandlab], nradius=1)
    # Calculate the flux to copute the residuals
    newtrlab = [0]*len(xmodel_res)
    fd_ub_res = pti.flux_tr(xmodel_res, newtrlab, dparstr, rp_val[plabel*nradius+bandlab*control],
                            my_ldc[bandlab*2:bandlab*2+2], n_cad[bandlab], t_cad[bandlab], nradius=1)

    # Define a vector which will contain the data of other planers for multi fits
    fd_ub_total = np.zeros(shape=len(fd_ub_res))

   #############################################################################
   # Let us calculate the flux caused by the other planets
    for p in range(nplanets):
        if (p != plabel):
            # fd_ub_total stores the flux of a star for each independent
            #fd_ub_total = fd_ub_total + pti.flux_tr(local_time,pars_tr[:,p],my_ldc,n_cad,t_cad)
            newtrlab = [0]*len(local_time)
            fd_ub_total = fd_ub_total + pti.flux_tr(local_time, newtrlab, pars_tr[p], rp_val[p*nradius+bandlab*control],
                                                    my_ldc[bandlab*2:bandlab*2+2], n_cad[bandlab], t_cad[bandlab], nradius=1)

    # Remove extra planets from the data
    yflux_local = yflux - fd_ub_total
    yflux_local = yflux_local - 1 + nplanets
    # The flux has been corrected for the other planets

    # Get the residuals
    res_res = yflux_local - fd_ub_res
    # are we plotting a GP together with the RV curve
    if kernel_tr[0:2] != 'No':
        xvec = local_time
        yvec = res_res
        evec = eflux
        m, C = pti.pred_gp(kernel_tr, pk_tr, xvec, yvec, evec,
                           xvec, jtr[bandlab], [0]*len(xvec))
        yflux_local = yflux_local - m
        res_res = res_res - m

    return xtime, yflux_local, eflux, xmodel, xmodel_res, fd_ub, res_res, fd_ub_unbinned

# ===========================================================
#              plot all transits
# ===========================================================

# Now this functions works only with one band


def plot_all_transits():
    global plot_tr_errorbars

    # Create the plot of the whole light
    model_flux = pti.flux_tr(
        megax, [0]*len(megax), pars_tr, rp_val, my_ldc, n_cad, t_cad)
    res_flux = megay - model_flux

    for i in range(0, nplanets):
        if (fit_tr[i]):
            if (m < nbands - 1):
                dy = max(yflux[m+1])-min(yflux[m+1])
            if (m < nbands - 1):
                dy = max(yflux[m+1])-min(yflux[m+1])

            xt, dt, yt, et = create_transit_data(
                megax, megay, megae, i, span_tr[i])
            xt2, dt2, yt2, et2 = create_transit_data(
                megax, res_flux, megae, i, span_tr[i])

            if (is_plot_all_tr[i]):
                for j in range(0, len(xt)):
                    xtm = np.arange(min(xt[j]), max(xt[j]), 1./20./24.)
                    ytm = pti.flux_tr(xtm, trlab, pars_tr,
                                      rp_val, my_ldc, n_cad, t_cad)

                    fname = outdir+'/'+star+plabels[i]+'_transit'+str(j)+'.pdf'
                    n = xt[j][len(xt[j])-1] - xt[0][0]
                    n = int(n/P_val[i])
                    #is_err = plot_tr_errorbars
                    #plot_tr_errorbars = True
                    fancy_tr_plot(t0_val[i]+P_val[i]*n, xt[j], yt[j], et[j],
                                  xtm, xt2[j], ytm, np.array(yt2[j]), ytm, fname)
                    #plot_tr_errorbars = is_err


def plot_lightcurve_timeseries():
    ''' This function creates a light curve time-series plot '''

    # Here I need to create a special trlab in order to separate the different colors
    # Now let us imagine that it works with 1-band
    xmodel = np.arange(min(megax), max(megax), 5./24.)
    my_trlab = [0]*len(xmodel)
    ymodel = pti.flux_tr(xmodel, my_trlab, pars_tr.transpose(),
                         rp_val, my_ldc, n_cad, t_cad, nradius)
    #ymodel = pti.flux_tr(xmodel,my_trlab,pars_tr,rp_val,my_ldc,n_cad,t_cad)

    # Calcualte the residuals
    trres = pti.flux_tr(megax, trlab, pars_tr.transpose(),
                        rp_val, my_ldc, n_cad, t_cad, nradius)
    trres = megay - trres

    # are we plotting a GP together with the RV curve
    if kernel_tr[0:2] != 'No':
        xvec = megax
        yvec = megay
        evec = megae
        m, C = pti.pred_gp(kernel_tr, pk_tr, xvec, trres,
                           evec, xmodel, jtr, jtrlab)
        tr_mvec = [xmodel, ymodel, 1.+m, (ymodel+m)]
        model_labels = ['Planetary signal', 'GP', 'P+GP']
        mcolors = ['r', 'b', 'k']
        malpha = [0.7, 0.7, 0.9]
    else:
        tr_mvec = [xmodel, ymodel]
        model_labels = ['Planetary signal']
        mcolors = ['k']
        malpha = [1.]

    # Call the sigma clipping functions
    #new_t, new_f = sigma_clip(megax,megay,trres,limit_sigma=sigma)

    # Recalculate the error bars
    #new_model_flux = pti.flux_tr(new_t,trlab,pars_tr,rps,my_ldc,n_cad,t_cad)
    # New residuals
    #new_res_flux = new_f - new_model_flux
    # Recompute the error bars from the std of the residuals
    #new_err = np.std(new_res_flux,ddof=1)

    # Name of plot file
    fname = outdir+'/'+star+'_lightcurve.pdf'

    tr_dvec = [megax, megay, megae, megae, trres, trlab]
    plot_labels_tr = [rv_xlabel, 'Flux', 'Residuals']
    # Create the RV timeseries plot
    create_nice_plot(tr_mvec, tr_dvec, plot_labels_tr, model_labels, bands, fname,
                     plot_residuals=False, fsx=2*fsx, model_colors=mcolors, model_alpha=malpha)
