
# Advanced Investments -- Trading Game
# @ Danjun Xu 13002775

import pandas as pd
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

def plot_single(Trade,title=''):
    plt.rcParams['axes.unicode_minus'] = False
    Trade['Date_datetime'] = pd.to_datetime(Trade.index.astype(str), format='%Y-%m-%d')
    plt.figure(figsize=(16, 4))
    plt.plot(Trade['Date_datetime'], Trade['cumprod'])
    plt.title(title)
    plt.show()
    plt.close()

def plot_multi(Trade,colname,title=''):
    colorlist = ['slateblue', 'darkslateblue', 'mediumslateblue', 'blueviolet', 'indigo', 'darkorchid', 'violet']
    plt.rcParams['axes.unicode_minus'] = False
    Trade['Date_datetime'] = pd.to_datetime(Trade.index.astype(str), format='%Y-%m-%d')
    plt.figure(figsize=(16, 4))
    pos=0
    for subcolname in colname:
        plt.plot(Trade['Date_datetime'], Trade[subcolname],color=colorlist[pos], label=subcolname)
        plt.legend(loc='upper left')
        pos+=1
    plt.title(title)
    plt.show()
    plt.close()