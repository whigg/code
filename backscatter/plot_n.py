import sys
import numpy as np
import tables as tb
import netCDF4 as nc
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import scipy.ndimage as img
from mpl_toolkits.basemap import interp

sys.path.append('/Users/fpaolo/code/misc')
import util
import viz

# input
#---------------------------------------------------------------------

fname = sys.argv[1]

# HDF5
f = tb.openFile(fname)
year = f.root.year[:]
n_ad = f.root.n_ad[:]
n_da = f.root.n_da[:]
lon = f.root.lon[:]
lat = f.root.lat[:]

'''
k, = np.where((year > 2003.1) & (year < 2009))
year = year[k]
dh = dh[k,...]
'''

# parameters
ABS_VAL = 0.12  # for trend
#ABS_VAL = 1.5  # for difference
GRID_CELL = (1, 5)
#width = 0.9  # gaussian width
width = 1.5  # gaussian width

BBOX_REG = (-82, -76.2, -26, -79.5)  # FRIS
#BBOX_REG = (-156, -76, 154, -81.2)   # ROSS
#BBOX_REG = (68, -74.5, 70, -67.5)   # AMERY

MFILE = '/Users/fpaolo/data/masks/scripps_antarctica_masks/scripps_antarctica_mask1km_v1.tif'

#CMAP = cm.jet_r # cm.gist_rainbow #cm.spectral_r # cm.RdBu_r # cm.jet_r
CMAP = viz.colormap('rgb')
LABEL = 'm/yr'

title = 'FRIS 1992-2012\n(ERS1, ERS2, ENVI)'
legend = 'Elevation change rate m/yr'
ticklabels = '0', '4', '8 m/yr'
ticks = -ABS_VAL, 0, ABS_VAL 
colormap = [
    (0, 0.001, 2, 3), # value
    (1, 1, 1, 1), # red
    (0, 0, 1, 1), # green
    (0, 0, 0, 1), # blue
    (0, 1, 1, 1), # alpha
]
colorexp = 1.0
colorlim = ticks[0], ticks[-1]
inches = 6.4, 3.6
extent = (-121.1, -113.8), (32.1, 35.5)
ylim = 150.0
xlim = ylim * inches[0] / inches[1]
axis = -xlim, xlim, -ylim, ylim

print 'lon/lat:', lon[GRID_CELL[1]], lat[GRID_CELL[0]]
#---------------------------------------------------------------------

def linear_fit(x, y, return_coef=False):
    """
    Fit a straight-line by Ordinary Least Squares.

    If `return_coef=True` returns the slope (m) and intercept (c).
    """
    x, y = np.asarray(x), np.asarray(y)
    ind, = np.where((~np.isnan(x)) & (~np.isnan(y) & (y!=0))) #<<<<<<<<<<<<<<< check the 0!!!!!
    if len(ind) < 2:
        return (np.nan, np.nan)
    x, y = x[ind], y[ind]
    A = np.ones((len(x), 2))
    A[:,0] = x
    m, c = np.linalg.lstsq(A, y)[0]
    if return_coef:
        return (m, c)
    else:
        x_pol = np.linspace(x.min(), x.max(), 200)
        y_pol = m*x_pol + c
        return (x_pol, y_pol)


def gaussian_filter(grid, width):
    """Gaussian smoothing."""
    k = np.where((np.isnan(grid)) | (grid == 0))
    grid[k] = 0
    grid = img.gaussian_filter(grid, width, order=0, output=None, mode='reflect', cval=0.0)
    grid[k] = np.nan
    return grid


def filter_npts(X, npts=10):
    _, ny, nx = X.shape
    for i in range(ny):
        for j in range(nx):
            ii, = np.where(~np.isnan(X[:,i,j]))
            if len(ii) < npts:
                X[:,i,j] = np.nan
    return X


def filter_abs(X, abs_val=2):
    X[np.abs(X)>abs_val] = np.nan
    return X


def area_grid_cells(X, x_edges, y_edges):
    """
    X is a 2D grid.
    """
    deg2rad = lambda x: (x*np.pi)/180.
    R = 6378    # Earth's radius in m
    c = (np.pi/180) * R**2
    A = np.empty_like(X)
    ny, nx = X.shape
    for i in range(ny):
        for j in range(nx):
            lat1, lat2 = deg2rad(y_edges[i]), deg2rad(y_edges[i+1])
            lon1, lon2 = deg2rad(x_edges[j]), deg2rad(x_edges[j+1])
            A[i,j] = c * np.abs(np.sin(lat1) - np.sin(lat2)) * np.abs(lon1 - lon2)
    '''
    plt.imshow(A, origin='lower')
    plt.colorbar()
    plt.show()
    sys.exit()
    '''
    return A


def area_weighted_mean_ts(X, A):
    """
    X is 3D with one ts at every grid-cell
    A is 2D with area of every grid-cell
    """
    nt, _, _ = X.shape
    ts = np.zeros(nt, 'f8')
    X[X==0] = np.nan
    X = np.ma.masked_invalid(X)
    for k in range(nt):
        G = X[k,...]
        W = A.copy()
        W[np.isnan(G)] = 0
        s = W.sum()
        if s != 0:
            W /= s 
        else:
            W[:] = 0 
        ts[k] = np.sum(W*G)  # area-weighted average
    '''
    plt.imshow(G, origin='lower')
    plt.colorbar()
    plt.show()
    sys.exit()
    '''
    return ts


def plot_grid(lon, lat, dhdt, cell=None, plot_cell=False, contourf=True):
    fig = plt.figure()
    m = viz.make_proj_stere(BBOX_REG)
    plon, plat = lon[GRID_CELL[1]], lat[GRID_CELL[0]]
    lon, lat = np.meshgrid(lon, lat)
    xx, yy = m(lon, lat)
    x, y = m(plon, plat)
    print 'point cell (lon lat x y):', plon, plat, x, y
    dhdt = np.ma.masked_invalid(dhdt)
    m.pcolormesh(xx, yy, dhdt, cmap=CMAP, vmin=-ABS_VAL, vmax=ABS_VAL, alpha=1)
    m.plot(x, y, 'mo', markersize=8)
    if plot_cell:
        lon, lat = util.box(cell)
        x, y = m(lon, lat)
        m.plot(x, y, 'k', linewidth=2)
    if contourf:
        fig2 = plt.figure()
        m.contourf(xx, yy, dhdt, 25, cmap=CMAP)

    #plt.colorbar().set_label(LABEL)
    viz.colorbar(fig, CMAP, (-ABS_VAL,ABS_VAL))

    '''
    w = 50.0 / (axis[1] - axis[0])
    rect = 0.142 - w, 0.08, 2 * w, 0.02
    cmap = CMAP
    viz.colorbar(fig, cmap, colorlim, legend, rect, ticks, ticklabels, 
        size=7, weight='bold', color='k', edgecolor='w')
    leg = fig.add_axes([0, 0, 1, 1])
    leg.set_axis_off()
    viz.text(leg, 0.70, 0.90, title, ha='center', va='top', size=10,
        weight='bold', color='k', edgecolor='w')
    '''
    return fig


def plot_ts(x, y):
    x_pol, y_pol = util.poly_fit(x, y, order=3)
    x_lin, y_lin = linear_fit(x, y)
    m, c = linear_fit(x, y, return_coef=True)
    
    fig = plt.figure()
    ax = fig.add_subplot((111))

    x = x.round(2)
    n = y_lin[0]  # reference to zero
    plt.plot(x, y-n, linewidth=2)
    plt.plot(x_pol, y_pol-n)
    plt.plot(x_lin, y_lin-n)

    viz.add_inner_title(ax, 'linear trend = %.1f cm/yr' % (m*100), loc=2)
    #plt.ylim(-0.8, 0.8)
    plt.xlabel('time')
    plt.ylabel('dh (m)')
    plt.show()
    return fig


def plot_ts_mean(t, Y):
    y = np.ma.masked_invalid(Y)
    ts = np.mean(np.mean(y, axis=1), axis=1)

    #x_pol, y_pol = spline_interp(t, ts, smooth=0.1)
    x_pol, y_pol = util.poly_fit(t, ts, order=3)
    x_lin, y_lin = linear_fit(t, ts)
    m, c = linear_fit(t, ts, return_coef=True)

    fig = plt.figure()
    ax = fig.add_subplot((111))

    n = y_lin[0]  # shift
    plt.plot(t, ts-n, linewidth=2)
    plt.plot(x_pol, y_pol-n)
    plt.plot(x_lin, y_lin-n)

    viz.add_inner_title(ax, 'linear trend = %.1f cm/yr' % (m*100), loc=2)
    #plt.ylim(ts.min(), ts.max())
    plt.xlabel('time')
    plt.ylabel('dh (m)')
    plt.title('Mean TS')
    plt.show()
    return fig


def plot_ts_full(t, Y, (i,j)):
    y = np.ma.masked_invalid(Y)
    mean_t = np.mean(np.mean(y, axis=1), axis=1)
    mean_xy = np.mean(y, axis=0)
    ts = mean_t + mean_xy[i,j] + Y[:,i,j]

    #x_pol, y_pol = spline_interp(t, ts, smooth=0.1)
    x_pol, y_pol = util.poly_fit(t, ts, order=3)
    x_lin, y_lin = linear_fit(t, ts)
    m, c = linear_fit(t, ts, return_coef=True)

    fig = plt.figure()
    ax = fig.add_subplot((111))

    n = y_lin[0]  # shift
    plt.plot(t, ts-n, linewidth=2)
    plt.plot(x_pol, y_pol-n)
    plt.plot(x_lin, y_lin-n)

    viz.add_inner_title(ax, 'linear trend = %.1f cm/yr' % (m*100), loc=2)
    #plt.ylim(ts.min(), ts.max())
    plt.xlabel('time')
    plt.ylabel('dh (m)')
    plt.title('Mean TS')
    plt.show()
    return fig


def plot_grid_and_ts(lon, lat, dhdt, t, dh, (i,j), **kw):
    cell = (lon[j], lon[j+1], lat[i], lat[i+1])
    plot_grid(lon, lat, dhdt, cell, **kw)
    plt.show()


def plot_map(lon, lat, grid, bbox, mfile, mres=1, **kw):
    fig1 = plt.figure()
    ax = fig1.add_subplot(111)
    m = viz.make_proj_stere(bbox)
    m = viz.plot_grid_proj(m, lon, lat, grid, contourf=False, shift=True, **kw)
    plt.colorbar(orientation='vertical', shrink=.7)
    x, y, mask = viz.get_gtif_subreg(m, mfile, mres)
    mask = np.ma.masked_values(mask, 4)
    m.imshow(mask, zorder=1, cmap=plt.cm.gray_r)
    #m = plot_boundaries(m, (lon.min(),lon.max(),lat.min()-10,lat.max()+3))
    p_ = m.drawparallels(np.arange(-90.,-70.,3), labels=[0,0,0,1], color='0.6')
    m_ = m.drawmeridians(np.arange(-80.,-20.,5), labels=[1,0,0,0], color='0.6')
    #viz.colorbar(fig1, CMAP, (-ABS_VAL,ABS_VAL))
    return fig1 


def regrid(lon, lat, dhdt, factor=10):
    m, n = len(lon), len(lat)
    lon2 = np.linspace(lon[0], lon[-1], m*factor)
    lat2 = np.linspace(lat[0], lat[-1], n*factor)
    xx, yy = np.meshgrid(lon2, lat2)
    dhdt2 = interp(dhdt, lon, lat, xx, yy, order=1)                          # good!!!
    return lon2, lat2, dhdt2

#---------------------------------------------------------------------

t = np.asarray(year)

# remember to take off a piece of the grid (land) !!!!!!!!
#dh[:,:,:int(dh.shape[2]/1.5)] = np.nan  # for FRIS
#dh[:,25:,120:] = np.nan  # for FRIS_3
#dh[:,:,50:] = np.nan  # for FRIS_2
#dh[:,:,:39] = np.nan  # for FRIS_2
#dh[:,:16,:] = np.nan  # for FRIS_2
#dh[:,10:,48:] = np.nan  # for ROSS
#dh[:,12:,57:] = np.nan  # for ROSS_2 (land)
#dh[:,:,:55] = np.nan  # for ROSS_2
#dh[:,:,60:] = np.nan  # for ROSS_2
#dh[:,7:,:] = np.nan  # for ROSS_2

k, = np.where((year > 2000) & (year < 2000.1))
print 'year:', year[k], 'k:', k
plot_map(lon, lat, n_ad[k[0],...]+n_da[d[0],...], BBOX_REG, MFILE, mres=1, cmap=cm.jet)
plt.title('Crossover density after averaging TS (2011.3)')
plt.show()

for fid in tb.file._open_files.values():
    fid.close()
