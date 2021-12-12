
# Advanced Investments -- Trading Game
# @ Danjun Xu 13002775

import pandas as pd
import numpy as np
import os
import datetime
import InvestmentGame.tool as tool
import warnings
warnings.filterwarnings('ignore')

def sum_data(rawdata_path):
    df_sum=pd.DataFrame()
    Filename=os.listdir(rawdata_path)
    Filename.sort()
    count=1
    for file in Filename:
        print(count)
        print(file)
        stock_name=file.split('.')[0]
        df = pd.read_csv(rawdata_path+file,index_col=0)
        if df.empty:
            print(file," is empty.")
            pass
        else:
            df['stockname']=stock_name
            df['todayreturn']=df['Adj Close']/df['Adj Close'].shift(1)-1
            df['dateint']=df.index
            df['dateint']=df['dateint'].apply(lambda x:x[:4]+x[5:7]+x[8:])
            df['weekday']=df['dateint'].apply(lambda x:datetime.date(int(x[:4]),int(x[4:6]),int(x[6:])).weekday()+1)
            df=df.dropna(axis=0)
            df_sum=df_sum.append(df)
        count+=1
    df_sum.to_hdf('data_backtest_week1.hdf',key='data')

# T-month: formation period (usually T=12)
# S-month: skip period (usually S=1)
# factor 1: momentum factor
def price_momentum(temp,T=12,S=1,par=False):
    kargs={'T':T,'S':S}

    temp['monthly_return'] = temp['Adj Close'].shift(1) / temp['Adj Close'].shift(22) - 1
    temp['cum_return'] = temp['Adj Close'].shift(1) / temp['Adj Close'].shift(T * 21+1) - 1
    temp['cum_return_skip'] = temp['cum_return'].shift(S * 21)
    temp['mean_monthly_return'] = temp['cum_return_skip'] / T
    temp['return_gap'] = temp['monthly_return'] - temp['mean_monthly_return']
    temp['return_gap2'] = temp['return_gap'] * temp['return_gap']
    temp['monthly_volatility'] = temp['return_gap2']
    for t in range(T - 1):
        temp['monthly_volatility'] += temp['return_gap2'].shift((t + 1) * 21)
    temp['monthly_volatility'] = temp['monthly_volatility'] / (T - 1)
    temp['price_momentum'] = temp['mean_monthly_return'] / temp['monthly_volatility']
    if par==False:
        return temp['price_momentum']
    else:
        return temp['price_momentum'],kargs

# factor 2: momentum factor
def low_volatility(temp,T=12,par=False):
    kargs={'T':T}

    temp['monthly_return'] = temp['Adj Close'].shift(1) / temp['Adj Close'].shift(22) - 1
    temp['cum_return'] = temp['Adj Close'].shift(1) / temp['Adj Close'].shift(T * 21 + 1) - 1
    temp['mean_monthly_return'] = temp['cum_return'] / T
    temp['return_gap'] = temp['monthly_return'] - temp['mean_monthly_return']
    temp['return_gap2'] = temp['return_gap'] * temp['return_gap']
    temp['monthly_volatility'] = temp['return_gap2']
    for t in range(T - 1):
        temp['monthly_volatility'] += temp['return_gap2'].shift((t + 1) * 21)
    temp['low_volatility'] = temp['monthly_volatility'] / (T - 1)

    if par==False:
        return temp['low_volatility']
    else:
        return temp['low_volatility'], kargs

def strategy(factor,**kargs):
    df = pd.read_hdf('data_backtest_week1.hdf')
    df['dateint']=df['dateint'].astype(int)
    df2=pd.DataFrame()
    for stock in df['stockname'].unique():
        temp=df[df['stockname']==stock]

        if factor=='price_momentum':
            temp['factor'],kargs=price_momentum(temp,**kargs,par=True)
        elif factor=='low_volatility':
            temp['factor'], kargs = low_volatility(temp, **kargs,par=True)

        temp=temp[temp['weekday']==1] # every week trade on Monday
        temp['nextweekreturn']=temp['Adj Close'].shift(-1)/temp['Adj Close']-1

        temp=temp[['stockname','nextweekreturn','factor']].dropna()

        df2=df2.append(temp)

    if factor=='price_momentum':
        df3 = df2['factor'].groupby(df2.index).quantile(0.9).reset_index(). \
            rename({'factor': 'top'}, axis=1).set_index('Date')
        df2 = pd.merge(df2, df3, left_index=True, right_index=True)
        df4 = df2[df2['factor'] >= df2['top']]
    elif factor=='low_volatility':
        df3 = df2['factor'].groupby(df2.index).quantile(0.1).reset_index(). \
            rename({'factor': 'bottom'}, axis=1).set_index('Date')
        df2 = pd.merge(df2, df3, left_index=True, right_index=True)
        df4 = df2[df2['factor'] <= df2['bottom']]

    df5 = df4['stockname'].groupby(df4.index).count().reset_index(). \
        rename({'stockname': 'num'}, axis=1).set_index('Date')
    DataTableSum = pd.merge(df4, df5, left_index=True, right_index=True)
    DataTableSum['return'] = DataTableSum['nextweekreturn'] / DataTableSum['num']
    print(DataTableSum['num'])

    Trade = DataTableSum['return'].groupby(DataTableSum.index).sum().reset_index().set_index('Date')
    Trade.index = pd.to_datetime(Trade.index.astype(str), format='%Y-%m-%d')
    Trade = Trade[Trade.index>=pd.datetime(2021,1,1)]
    Trade['cumprod'] = (Trade['return'] + 1).cumprod()
    Trade['DD'] = Trade['cumprod'] / Trade['cumprod'].cummax() - 1

    AnualReturn = np.mean(Trade.loc[:, 'return']) * 52
    AnualStd = np.std(Trade.loc[:, 'return']) * np.sqrt(52)
    MMD = Trade['DD'].min()
    s = pd.Series(
        {'factor':factor,
         'kargs':kargs,
         'AnnualReturn': format(AnualReturn, '.4f'),
         'Sharpe': format((AnualReturn / AnualStd), '.2f'),
         'MMD': format(MMD, '.4f'),
         'Calmar': format((-AnualReturn / MMD), '.2f'),
         })
    print(s)

    tool.plot_single(Trade,kargs)

    return Trade[['cumprod']]

if __name__ =='__main__':
    rawdata_path = '/Users/echo/PycharmProjects/EchoProject/sp500_data_1d/'
    # sum_data(rawdata_path) #(481870, 10)

    # kargs = {'T': 12}
    # strategy(factor='low_volatility', **kargs)

    kargs = {'T': 12, 'S': 1}
    strategy(factor='price_momentum', **kargs)

    # par={5:'1 week',20:'1 month',125:'6 months',250:'1 year'}
    # Trade=pd.DataFrame()
    # for n in par.keys():
    #     Temp=strategy(12,1)
    #     Temp=Temp.rename({'cumprod':par[n]},axis=1)
    #     if Trade.empty:
    #         Trade=Temp.copy()
    #     else:
    #         Trade = pd.merge(Trade, Temp, left_index=True, right_index=True)
    #
    # tool.plot_multi(Trade,colname=['1 week','1 month','6 months','1 year'],title='Momentum')







