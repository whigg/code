"""
Make full-ice-shelf area-average time series

"""
import sys
import numpy as np
import pandas as pd
import tables as tb
import statsmodels.api as sm
import matplotlib.pyplot as plt
import altimpy as ap
from scipy.signal import detrend
from patsy import dmatrix
from sklearn.linear_model import LassoCV

PLOT = True
DIR = '/Users/fpaolo/data/shelves/' 
#FILE_IN = 'all_19920716_20111015_shelf_tide_grids_mts.h5.ice_oce'
FILE_IN = 'h_raw4.h5'
UNITS = 'm/yr'

#plt.rcParams['font.family'] = 'arial'
plt.rcParams['font.size'] = 11
plt.rcParams['grid.linestyle'] = '-'
plt.rcParams['grid.linewidth'] = 0.2
plt.rcParams['grid.color'] = '0.5'
'''
plt.rcParams['xtick.direction'] = 'out'
plt.rcParams['xtick.major.size'] = 0
#plt.rcParams['ytick.major.size'] = 0
plt.rcParams['xtick.labelsize'] = 12 # 18
#plt.rcParams['ytick.labelsize'] = 12 # 18
#plt.rcParams['xtick.major.pad'] = 6
#plt.rcParams['ytick.major.pad'] = 6
'''

def gradient(y, dt=0.25):
    return np.gradient(y.values, dt)


shelves = [
    ap.fimbulw,
    ap.fimbule,
    ap.lazarev,
    ap.amery,
    ap.west,
    ap.shackleton,
    #ap.conger,
    ap.totten,
    ap.moscow,
    ap.rosse,
    ap.rossw,
    ap.sulzberger,
    ap.getz,
    ap.dotson,
    ap.crosson,
    ap.thwaites,
    ap.pig,
    ap.abbot,
    ap.stange,
    ap.bach,
    ap.wilkins,
    ap.georges,
    ap.georgen,
    #ap.larsena,
    ap.larsenb,
    ap.larsenc,
    ap.larsend,
    ap.ronne,
    ap.filchner,
    ap.brunt,
    ap.riiser,
    ap.ais,
    ]

names = [
    'Fimbul W',
    'Fimbul E',
    'Lazarev',
    'Amery',
    'West',
    'Shacklet.',
    #'con',
    'Totten',
    'Moscow',
    'Ross E',
    'Ross W',
    'Sulzberg.',
    'Getz',
    'Dotson',
    'Crosson',
    'Thwaites',
    'PIG',
    'Abbot',
    'Stange',
    'Bach',
    'Wilkins',
    'George S',
    'George N',
    #'laa',
    'Larsen B',
    'Larsen C',
    'Larsen D',
    'Ronne',
    'Filchner',
    'Brunt',
    'Riiser',
    'All',
    ]

print 'loading data...'
fin = tb.openFile(DIR + FILE_IN)
try:
    time = ap.num2year(fin.root.time[:])
except:
    time = fin.root.time[:]
lon = fin.root.lon[:]
lat = fin.root.lat[:]
d = fin.root.dh_mean_mixed_const_xcal[:]
#d = fin.root.dg_mean_xcal[:]
#e = fin.root.dh_error_xcal[:]
#d = fin.root.n_ad_xcal[:]
nz, ny, nx = d.shape
dt = ap.year2date(time)


if 0:
    reg = ap.west
    d, lon, lat = ap.get_subset(reg, d, lon, lat)
    plt.figure()
    plt.imshow(d[10], extent=(lon.min(), lon.max(), lat.min(), lat.max()), 
               origin='lower', interpolation='nearest', aspect='auto')
    plt.grid(True)
    plt.show()
    sys.exit()

if 1:
    time, d = ap.time_filt(time, d, from_time=1994, to_time=2013)
    #time, e = time_filt(time, e, from_time=1992, to_time=20013)


# area-average time series
df = pd.DataFrame(index=time)
df2 = pd.DataFrame(index=time)
for k, s in zip(names, shelves):
    shelf, x, y = ap.get_subset(s, d, lon, lat)
    #error, x, y = ap.get_subset(s, e, lon, lat)
    A = ap.get_area_cells(shelf[10], x, y)
    ts, _ = ap.area_weighted_mean(shelf, A)
    #ts2, _ = ap.area_weighted_mean(error, A)
    df[k] = ts
    #df2[k] = ts2
    if 0:
        print k
        plt.imshow(shelf[10], extent=(x.min(), x.max(), y.min(), y.max()), 
                   origin='lower', interpolation='nearest', aspect='auto')
        plt.show()

df.fillna(0, inplace=True)  # leave this!!!

if 0:
    df = df.apply(ap.hp_filt, lamb=7)

if 0:
    df = df.apply(detrend)

if 0:
    df = df.apply(gradient, dt=0.25)

if 1:
    df = df.apply(ap.referenced, to='mean')

ncols = 3
nrows = int(np.ceil(len(df.columns) / float(ncols)))

# plot
fig, axs = plt.subplots(nrows, ncols, sharex=False, sharey=False, figsize=(16.5,14))
fig.patch.set_facecolor('white')

# calculate trends
zeros = np.zeros_like(time)
n = 0
for j in range(ncols):
    for i in range(nrows):

        #------------------------- plot -----------------------------

        print n, k
        k = df.columns[n]
        s = df[k]
        m, c = ap.linear_fit_robust(time, s.values, return_coef=True)
        x, y = ap.linear_fit_robust(time, s.values, return_coef=False)
        pol = np.polyfit(time, s.values, 2)
        yy = np.polyval(pol, time)
        #axs[i,j].fill_between(time, s.values+2*r, s.values-2*r, facecolor='0.5',
        #                      edgecolor='w', alpha=0.2)
        #axs[i,j].plot(time, zeros, ':', c='0.5', linewidth=0.5)
        axs[i,j].plot(time, y, c='0.2', linewidth=0.75, zorder=2)
        axs[i,j].plot(time, s.values, 's', c='0.5', markersize=4, zorder=1)
        if 0:
            axs[i,j].plot(time, yy, c='b', linewidth=1.5, zorder=2)
        if 1:
            axs[i,j].plot(time, ap.lasso_cv(time, s, max_deg=3), c='b',
                          linewidth=1.75)
        if 1:
            axs[i,j].plot(time, ap.polyfit_cv(time, s.values, cv=10,
                          max_deg=3, randomise=True), c='r', linewidth=1.5)

        #----------------------- settings ---------------------------

        if i == 0:
            ap.intitle('%s %.2f %s' % (k, m, UNITS), ax=axs[i,j],  loc=8,
                       pad=-1, borderalpha=0.7)
        else:
            ap.intitle('%s %.2f' % (k, m), ax=axs[i,j], loc=8,
                       pad=-1, borderalpha=0.7)

        if i != nrows-1:
            ap.adjust_spines(axs[i,j], ['left'], pad=15)
        else:
            ap.adjust_spines(axs[i,j], ['left', 'bottom'], pad=15)
            axs[i,j].set_xticks([1994, 1997, 2000, 2003, 2006, 2009, 2012])
        mn, mx = ap.get_limits(s)
        axs[i,j].set_yticks([mn, 0, mx])
        axs[i,j].set_ylim(mn, mx)
        axs[i,j].set_xlim(1994, 2012)
        axs[i,j].tick_params(axis='both', direction='out', length=6, width=1,
                        labelsize=12)
        n += 1

fig.subplots_adjust(left=0.07, right=0.95, bottom=0.01, top=0.95, wspace=0.25, hspace=0.28)
axs[5,0].set_ylabel('Elevation change (m)', fontsize='large')
fig.autofmt_xdate()
#plt.savefig('g_old_ann.png', dpi=150)
#plt.savefig('backscatter_ts2.png', dpi=150)
plt.show()

#---------------------------------------------------------------------
# save data 
#---------------------------------------------------------------------

if 0:
    print 'saving data...'
    fout = tb.openFile(DIR + FILE_OUT, 'a')
    try:
        fout.createArray('/', 'time', time)
    except:
        pass
    try:
        fout.createArray('/', 'xyz_nodes', xyz)
    except:
        pass
    try:
        fout.createArray('/', 'xx', xx)
        fout.createArray('/', 'yy', yy)
    except:
        pass
    #write_slabs(fout, 'dh_mean_xcal_short_const', data)
    #write_slabs(fout, 'dh_mean_short_const_xcal', data)
    #write_slabs(fout, 'dh_mean_xcal', data)
    #write_slabs(fout, 'dh_error_xcal', data)
    write_slabs(fout, 'nobs_xcal', data)
    fout.flush()
    fout.close()
    fin.close()

    print 'out ->', DIR + FILE_OUT


