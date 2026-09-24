import numpy as np
import matplotlib.pyplot as plt
minWinChance=0.05
prob=[.5,.99,.9999999]

avgWinRate, percRanked = np.meshgrid(np.arange(minWinChance, 1+.000000001, .005), np.arange(0., 1+.000000001, .005))
avgAlphaChanceInc = ((0.03 * avgWinRate + 0.025 * (1 - avgWinRate)) * percRanked + (0.02 * avgWinRate + 0.015 * (1 - avgWinRate)) * (1 - percRanked)).ravel()
initialAlphaChance = (0.03 * percRanked + 0.02 * (1 - percRanked)).ravel()
maxGames=((1-initialAlphaChance)/avgAlphaChanceInc)

probval=max(prob)*.1+.9
matchNums=np.arange(0,1000)
winChance=(np.multiply(*np.meshgrid(avgAlphaChanceInc,matchNums))+initialAlphaChance)*avgWinRate.ravel()
prod_array=np.roll(np.cumprod(1 - winChance,0),1,0)
prod_array[0,:]=1
sum_array=np.cumsum(winChance*prod_array,0)
sum_array[np.arange(sum_array.shape[0])[:, None] >= np.argmax(sum_array > probval, axis=0)] = np.nan
games=[[*np.interp(prob,arr,matchNums,left=0,right=np.inf,),g] for arr,g in zip(np.transpose(sum_array),maxGames)]

probstr=[*[f'Probability {item*100}% Contour Plot' for item in prob],"Next Win After Game X Guarenteed"]
shape = (len(avgWinRate), len(avgWinRate[0]))
X = avgWinRate * 100
Y = percRanked * 100

def cur_fmt(x, y, Xflat, Yflat, Zflat):
    return f'x={x:.5f}  y={y:.5f}  z={Zflat[np.argmin(np.linalg.norm(np.vstack([Xflat - x, Yflat - y]), axis=0))]:.5f}'

for i,Zflat in enumerate(np.transpose(games,(1,0))):
    Zmax = np.max(Zflat[np.isfinite(Zflat)])
    Zmin = np.min(Zflat[np.isfinite(Zflat)])
    cp = plt.contourf(X, Y, Zflat.reshape(shape), levels=100)
    plt.colorbar(cp, ticks=[Zmin,*np.arange(np.ceil(Zmin), np.ceil(Zmax)),Zmax])
    plt.title(probstr[i])
    plt.xlabel('Average WinRate [%]')
    plt.ylabel('Percent Games are Ranked [%]')
    plt.gca().format_coord = lambda x, y: cur_fmt(x, y, X.flatten(), Y.flatten(), Zflat)
    plt.show()