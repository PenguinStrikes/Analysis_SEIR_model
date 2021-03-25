# Import relevant libraries
import numpy as np
import math
import random
import glob
import os
import sys
import imageio
import scipy.stats as stats
from scipy import integrate, optimize
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
from matplotlib import colors
import seaborn as sns

PROJ_ROOT = os.path.abspath(os.path.join(os.pardir))
sys.path.append(os.path.join(PROJ_ROOT, 'fig'))

class SEIR_modelling():
    
    def __init__(self, N, beta=0.5, sigma=0.1, gamma=0.1):
        self.N  = N # Define our total population (N)
        self.I0 = 0
        self.E0 = 1
        self.R0 = 0
        self.S0 = self.N - self.I0 - self.E0 - self.R0
        self.beta = beta
        self.sigma = sigma
        self.gamma = gamma
        self.t = np.linspace(0, 120, 120)  # Create a grid of space in time
        self.S,self.E,self.I,self.R = 0,0,0,0
        
    def SEIR_model(self, z, t, beta, sigma, gamma):
        S,E,I,R = z                           # Given population size
        N = S + E + I + R                     # Rate of change of the susceptible group (S)
        dSdt = -beta * S * I / N              # Rate of change of the exposed group (E)
        dEdt = beta * S * I / N - sigma * E   # Rate of change of the infectious group (I)
        dIdt = sigma * E - gamma * I          # Rate of change of the recovered group (R)
        dRdt = gamma * I
        return dSdt, dEdt, dIdt, dRdt
    
    def SEIR_solver(self):
        ret = integrate.odeint(self.SEIR_model, 
                               [self.S0,self.E0,self.I0,self.R0], 
                               self.t, 
                               args=(self.beta, self.sigma, self.gamma))
        self.S, self.E, self.I, self.R = ret.T
        
    def plot_animation(self, skip_frames=False):
        path = '../fig/animation_files/'
        for f in glob.glob(path+"*"):
            os.remove(f)
        
        for i in range(0, 101):
            if skip_frames == True:
                if (i % 2) == 0:
                    self.plot_model(i, save=path + str(i).zfill(3), show=False)
            else:
                self.plot_model(i, save=path + str(i).zfill(3), show=False)
            
        images = []
        for f in sorted(glob.glob(path + '*png')):
            images.append(imageio.imread(f))
            imageio.mimsave('../fig/output/animation.gif', images, duration=0.05)
        
    def plot_model(self, i, save=False, show=True):
        aE = [1] * int(self.E[i])
        aI = [2] * int(self.I[i])
        aR = [3] * int(self.R[i])
        aS = [0] * (100 - len(aE + aI + aR))
        li = aS + aE + aI + aR
        my_lst = random.sample(li, len(li))
        my_lst = np.reshape(my_lst, (-1, 10))

        # Plot our data on three separate curves
        fig, ax = plt.subplots(1,2, figsize=(20, 5), gridspec_kw={'width_ratios': [5,2]})

        ax[0].plot(self.t[0:i], self.S[0:i], 'grey', ls='--', alpha=0.8, lw=4, label='Susceptible')
        ax[0].plot(self.t[0:i], self.E[0:i], '#C56FE6', alpha=0.8, lw=4, label='Exposed')
        ax[0].plot(self.t[0:i], self.I[0:i], '#F35162', alpha=0.8, lw=4, label='Infected')
        ax[0].plot(self.t[0:i], self.R[0:i], '#2FCB8F', alpha=0.8, lw=4, label='Recovered')
        ax[0].set_xlabel('Time', fontsize=16)
        ax[0].set_ylabel('% of Population', fontsize=20)
        ax[0].set_ylim(0,self.N * 1.01)
        
        cmap = colors.ListedColormap(['grey','#C56FE6','#F35162','#2FCB8F'])
        ax[1].pcolor(my_lst[::-1], cmap=cmap, edgecolors='k', linewidths=2, alpha=0.8)
        ax[1].axis('off')
        
        ax[0].legend(frameon=False, fontsize=20, loc='center left', bbox_to_anchor=(-0.35, 0.5))
        sns.despine()
        if save != False:
            try:
                fig.savefig(save + '.png', bbox_inches='tight', dpi=70)
            except:
                pass
        if show == True:
            plt.show()
        else:
            plt.close()