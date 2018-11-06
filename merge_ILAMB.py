from ILAMB.Variable import Variable
from ILAMB.Confrontation import Confrontation
from ILAMB.ModelResult import ModelResult
import ILAMB.Post as post
import ILAMB.ilamblib as il
from taylorDiagram import plot_Taylor_graph
import numpy as np
import waipy
import matplotlib.pyplot as plt
from PyEMD import EEMD
from hht import hht
from hht import plot_imfs
from hht import plot_frequency

def change_x_tick(mod, site_id, ax0):
    tmask = np.where(mod.data.mask[:, site_id] == False)[0]
    if tmask.size > 0:
        tmin, tmax = tmask[[0, -1]]
    else:
        tmin = 0;
        tmax = mod.time.size - 1
    t = mod.time[tmin:(tmax + 1)]
    ind = np.where(t % 365 < 30.)[0]
    ticks= t[ind] - (t[ind] % 365)
    ticklabels = (ticks / 365. + 1850.).astype(int)
    ax0.set_xticks(ticks)
    ax0.set_xticklabels(ticklabels)

def Plot_TimeSeries(obs,mod,site_id):
    print('Process on TimeSeries ' + 'No.' + str(site_id) + '!')
    t = mod.time
    print(len(t))

    x = obs.data[:, site_id]
    y = mod.data[:, site_id]
    xx = x.compressed()
    yy = y[~x.mask]
    mods = []
    mods.append(yy)
    fig0 = plt.figure(figsize=(5, 5))
    plt.suptitle('Time series')
    ax0 = fig0.add_subplot(2,1,1)
    fig0, samples0 = plot_Taylor_graph(xx, mods, fig0, 212, bbox_to_anchor=(1, 0.45), datamask=None)
    ax0.plot(t[~x.mask], xx, 'k')
    ax0.plot(t[~x.mask], yy)
    ax0.set_xlabel('Time')
    ax0.set_ylabel(obs.unit)
    change_x_tick(mod, site_id, ax0)


def Plot_PDF_CDF(obs,mod,site_id):
    print('Process on PDF&CDF ' + 'No.' + str(site_id) + '!')
    t = mod.time
    x = obs.data[:, site_id]
    y = mod.data[:, site_id]
    # xx = x.compressed()
    # yy = y[~x.mask]

    fig0 = plt.figure(figsize=(5, 5))
    plt.suptitle('PDF and CDF')
    ax0 = fig0.add_subplot(2, 1, 1)
    ax1 = fig0.add_subplot(2, 1, 2)

    h_obs_sorted = np.ma.sort(x).compressed()
    p1_data = 1. * np.arange(len(h_obs_sorted)) / (len(h_obs_sorted) - 1)
    p_h, x_h = np.histogram(h_obs_sorted, bins=np.int(len(h_obs_sorted)))  # bin it into n = N/10 bins
    x_h = x_h[:-1] + (x_h[1] - x_h[0]) / 2  # convert bin edges to centers
    ax0.plot(x_h, p_h / float(sum(p_h)), 'k-', label='Observed')
    ax1.plot(h_obs_sorted, p1_data, 'k-', label='Observed')

    h_obs_sorted = np.ma.sort(y).compressed()
    p1_data = 1. * np.arange(len(h_obs_sorted)) / (len(h_obs_sorted) - 1)
    p_h, x_h = np.histogram(h_obs_sorted, bins=np.int(len(h_obs_sorted)))  # bin it into n = N/10 bins
    x_h = x_h[:-1] + (x_h[1] - x_h[0]) / 2  # convert bin edges to centers
    ax0.plot(x_h, p_h / float(sum(p_h)))
    ax1.plot(h_obs_sorted, p1_data)

def Plot_Wavelet(obs,mod,site_id):
    print('Process on Wavelet ' + 'No.' + str(site_id) + '!')
    time_data = mod.time
    data = obs.data[:, site_id]
    y = mod.data[:, site_id]
    fig3 = plt.figure(figsize=(8, 8))
    result = waipy.cwt(data, 1, 1, 0.125, 2, 4 / 0.125, 0.72, 6, mother='Morlet', name='Obs')
    ax1,ax2,ax3,ax5 =waipy.wavelet_plot('Obs', time_data, data, 0.03125, result, fig3, unit=obs.unit)
    change_x_tick(mod, site_id, ax2)

def Plot_IMF(obs,mod,site_id):
    print('Process on IMF ' + 'No.' + str(site_id) + '!')
    data = obs.data[:, site_id]
    time = mod.time[~data.mask]
    y = mod.data[:, site_id]
    time_y = mod.time[~y.mask]
    d_mod = []
    d_mod.append(y)
    fig1 = plt.figure(figsize=(4 * (len(d_mod) + 1), 8))
    fig2 = plt.figure(figsize=(4 * (len(d_mod) + 1), 8))
    fig3 = plt.figure(figsize=(5, 5))
    fig4 = plt.figure(figsize=(5, 5))

    fig1.subplots_adjust(wspace=0.5, hspace=0.3)
    fig2.subplots_adjust(wspace=0.5, hspace=0.3)

    eemd = EEMD(trials=5)
    imfs = eemd.eemd(data.compressed())
    fig3, freq = hht(data.compressed(), imfs, time, 1, fig3)
    if len(imfs) >= 1:
        fig1 = plot_imfs(data.compressed(), imfs, time_samples=time, fig=fig1, no=1, m=len(d_mod))
        fig2 = plot_frequency(data.compressed(), freq.T, time_samples=time, fig=fig2, no=1, m=len(d_mod))
    imfs2 = eemd.eemd(y.compressed())
    fig4, freq2 = hht(y.compressed(), imfs2, time_y, 1, fig4)
    if len(imfs) >= 1:
        fig1 = plot_imfs(y.compressed(), imfs2, time_samples=time_y, fig=fig1, no=2, m=len(d_mod))
        fig2 = plot_frequency(y.compressed(), freq2.T, time_samples=time_y, fig=fig2, no=2, m=len(d_mod))

def Plot_response2(obs1, mod1, obs2, mod2, site_id):
    print('Process on Response ' + 'No.' + str(site_id) + '!')
    x1 = obs1.data[:, site_id]
    y1 = mod1.data[:, site_id]
    xx1 = x1.compressed()
    yy1 = y1[~x1.mask]

    x2 = obs2.data[:, site_id]
    y2 = mod2.data[:, site_id]
    xx2 = x2.compressed()
    yy2 = y2[~x2.mask]

    fig0 = plt.figure(figsize=(5, 5))
    plt.suptitle('Response 2 variables')
    ax0 = fig0.add_subplot(1, 1, 1)
    ax0.plot(xx1, xx2, 'k')
    ax0.plot(yy1, yy2)
    ax0.set_xlabel(obs1.unit)
    ax0.set_ylabel(obs2.unit)

def CycleReshape(var, cycle_length=None):  # cycle_length [days]
    if cycle_length == None:
        cycle_length = 1.
    dt = int((var.time_bnds[:, 1] - var.time_bnds[:, 0]).mean())
    spd = int(round(cycle_length / dt))
    if spd <= 0:
        print('The cycle number is smaller than the given data cycle')
    elif spd == 1:
        begin = 0
    else:
        begin = np.argmin(var.time[:(spd - 1)] % spd) # begin starts from 8?
    end = begin + int(var.time[begin:].size / float(spd)) * spd
    shp = (-1, spd) + var.data.shape[1:]  # reshape (-1, spd, lat, lon)
    cycle = var.data[begin:end].reshape(shp)  # reshape (time, cycle, lat, lon)
    # what is the meaning of tbnd? var.time_bnds[begin:end, :].shape  (time, 2)
    tbnd = var.time_bnds[begin:end, :].reshape((-1, spd, 2)) # % cycle_length
    tbnd = tbnd[:, 0, :]
    # tbnd[-1, 1] = 1.
    t = tbnd.mean(axis=1)
    return cycle, t, tbnd  # bounds on time

        # fig0, samples0 = plot_Taylor_graph(xx, mods, fig0, 212, bbox_to_anchor=(1, 0.45), datamask=None)
def Plot_TimeSeries_cycle(obs, mod, site_id, cycle_length):

    odata, ot, otb = CycleReshape(obs, cycle_length=cycle_length)
    mdata, mt, mtb = CycleReshape(mod, cycle_length=cycle_length)
    print('Process on Cycle TimeSeries ' + 'No.' + str(site_id) + '!')
    t = ot
    x = odata[:, :, site_id]
    y = mdata[:, :, site_id]
    fig0 = plt.figure(figsize=(8, 8))
    plt.suptitle('Time series')
    for i in range(len(x[0,:])):
        xx = x[:, i].compressed()
        yy = y[:, i][~x[:, i].mask]
        mods = []
        mods.append(yy)
        ax0 = fig0.add_subplot(len(x[0,:]), 2, i*2+1)
        num = len(x[0,:])*100 +2*10+i*2+2
        print(num)
        fig0, samples0 = plot_Taylor_graph(xx, mods, fig0, num, bbox_to_anchor=(1, 0.45), datamask=None)
        ax0.plot(t[~x[:, i].mask], xx, 'k')
        ax0.plot(t[~x[:, i].mask], yy)
        ax0.set_xlabel('Time')
        ax0.set_ylabel(obs.unit+'(Cycle '+str(i)+')')
        change_x_tick(mod, site_id, ax0)

def Plot_TimeSeries_cycle_reshape(obs, mod, site_id, cycle_length):

    odata, ot, otb = CycleReshape(obs, cycle_length=cycle_length)
    mdata, mt, mtb = CycleReshape(mod, cycle_length=cycle_length)
    print('Process on Cycle TimeSeries ' + 'No.' + str(site_id) + '!')
    t = ot
    x = odata[:, :, site_id]
    y = mdata[:, :, site_id]
    xx = x.mean(axis=0)
    yy = y.mean(axis=0)
    mods = []
    mods.append(yy)
    fig0 = plt.figure(figsize=(5, 5))
    plt.suptitle('Time series')
    ax0 = fig0.add_subplot(2, 1, 1)
    fig0, samples0 = plot_Taylor_graph(xx, mods, fig0, 212, bbox_to_anchor=(1, 0.45), datamask=None)
    ax0.plot(range(len(x.mean(axis=0))), x.mean(axis=0), 'k')
    ax0.fill_between(range(len(x.mean(axis=0))), x.mean(axis=0) - x.std(axis=0),
                     x.mean(axis=0) + x.std(axis=0), alpha=0.2, edgecolor='#1B2ACC',
                     facecolor='gray',
                     linewidth=0.5, linestyle='dashdot', antialiased=True)
    ax0.plot(range(len(y.mean(axis=0))), y.mean(axis=0))
    ax0.fill_between(range(len(y.mean(axis=0))), y.mean(axis=0) - y.std(axis=0),
                     y.mean(axis=0) + y.std(axis=0), alpha=0.2, edgecolor='#1B2ACC',
                     facecolor='blue',
                     linewidth=0.5, linestyle='dashdot', antialiased=True)
    # ax0.set_xlabel(obs.unit+'(Cycle)')
    ax0.set_ylabel('Mean')


def GetSeasonMask(obs, mod, site_id, season_kind):
    print('This function is used to mask seasons!')
    # The input data is annual data
    odata, ot, otb = CycleReshape(obs, cycle_length=365.)
    mdata, mt, mtb = CycleReshape(mod, cycle_length=365.)
    print('Process on mask Seasonal ' + 'No.' + str(site_id) + '!')
    x = odata[:, :, site_id]
    y = mdata[:, :, site_id]
    begin = 0
    end = 0 + int(x[0, :].size / float(4)) * 4
    mask = np.ones_like(x)
    if season_kind == 1:
        mask[:,begin:end/4]=0
        xx = np.ma.masked_where(mask, x)
        yy = np.ma.masked_where(mask, x)
    elif season_kind == 2:
        mask[:,end/4:2*end/4]=0
        xx = np.ma.masked_where(mask, x)
        yy = np.ma.masked_where(mask, x)
    elif season_kind == 3:
        mask[:,2*end/4:3*end/4]=0
        xx = np.ma.masked_where(mask, x)
        yy = np.ma.masked_where(mask, x)
    else:
        mask[:, 3 * end / 4:end] = 0
        xx = np.ma.masked_where(mask, x)
        yy = np.ma.masked_where(mask, x)
    return xx.reshape(1,-1), yy.reshape(1,-1)



# model = '/Users/lli51/Downloads/allfiles/171206_ELMv0_CN_NEE_model.nc4'
# model = '/Users/lli51/Downloads/ILAMB_sample/MODELS/CLM40cn/rsus/rsus_Amon_CLM40cn_historical_r1i1p1_185001-201012.nc'

data_file = '/Users/lli51/Downloads/ILAMB_sample/DATA/rsus/CERES/rsus_0.5x0.5.nc'
m = ModelResult('/Users/lli51/Downloads/ILAMB_sample/MODELS/CLM40cn/', modelname='CLM40cn')
c1 = Confrontation(source=data_file, name='CERES', variable='rsus')


# data_file = '/Users/lli51/Downloads/alldata/obs_FSH_model_ilamb.nc4'
# m = ModelResult('/Users/lli51/Downloads/ILAMB_sample/MODELS/CLM40cn/', modelname='CLM40cn')
# c1 = Confrontation(source=data_file, name='CERES', variable='FSH')

obs1, mod1 = c1.stageData(m)
# obs1=Variable(filename='/Users/lli51/Downloads/alldata/obs_FSH_model_ilamb.nc4', variable_name='FSH')
# mod1=Variable(filename='/Users/lli51/Downloads/ILAMB_sample/MODELS/CLM40cn/FSH/171206_ELMv0_CN_FSH_model_ilamb.nc4', variable_name='FSH')


data_o = (obs1.extractDatasites(lat=obs1.lat, lon=obs1.lat))
data_m = (mod1.extractDatasites(lat=obs1.lat, lon=obs1.lat))

print(data_o)

hello
Plot_TimeSeries(data_o, data_m, 0)
Plot_PDF_CDF(data_o, data_m, 0)
Plot_Wavelet(data_o, data_m, 0)
Plot_IMF(data_o, data_m, 0)
Plot_response2(data_o, data_m, data_o, data_m, 0)
# odata, ot, otb = CycleReshape(data_o, cycle_length=62.)
# mdata, mt, mtb = CycleReshape(data_m, cycle_length=93.)
# Plot_TimeSeries_cycle(data_o, data_m, 0, 365.)
# Plot_TimeSeries_cycle_reshape(data_o, data_m, 0, 365.)
GetSeasonMask(data_o, data_m, 0, 1)

# obs2=Variable(filename='/Users/lli51/Downloads/ILAMB_sample/DATA/albedo/CERES/albedo_0.5x0.5.nc', variable_name='albedo')
# obs2=Variable(filename='/Users/lli51/Downloads/ILAMB_sample/MODELS/CLM40cn/rsds/rsds_Amon_CLM40cn_historical_r1i1p1_185001-201012.nc', variable_name='rsds')
# mod2=Variable(filename='/Users/lli51/Downloads/ILAMB_sample/MODELS/CLM40cn/rsds/rsds_Amon_CLM40cn_historical_r1i1p1_185001-201012.nc', variable_name='rsds')
#
# data = '/Users/lli51/Downloads/allfiles/ER_obs_daily.nc4'
# m = ModelResult('/Users/lli51/Downloads/ILAMB_sample/MODELS/CLM40cn2/', modelname='CLM40cn2')
# c = Confrontation(source=data, name='ER', variable='ER')
# print(obs1.time_bnds)
# print(obs1.time_bnds[0, 0], obs1.time_bnds[-1, 1])


# mod2 = m.extractTimeSeries('rsus', initial_time = obs1.time_bnds[0, 0],
#                                   final_time = obs1.time_bnds[-1, 1],
#                                   lats = None if obs1.spatial else obs1.lat,
#                                   lons = None if obs1.spatial else obs1.lon)
#
# import ILAMB.ilamblib as il
# obs2, mod2= il.MakeComparable(obs1,mod2,
#                                     mask_ref  = True,
#                                     clip_ref  = True,
#                                     )



# print((obs1.time_bnds[:,1]-obs1.time_bnds[:,0]).mean())
# print(mod2)

# fig3 = plt.figure(figsize=(5, 5))
# ax = fig3.add_subplot(1,1,1)
# obs2.plot(ax)
plt.show()
