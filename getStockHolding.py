
# Advanced Investments -- Trading Game
# @ Danjun Xu 13002775

import pandas as pd
import os
from InvestmentGame import backtest
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

def weekly_holding(rawdata_path,trade_date,initial_cap):
    df_sum = pd.DataFrame()
    Filename = os.listdir(rawdata_path)
    Filename.sort()
    for file in Filename:
        # print(file)
        stock_name = file.split('.')[0]
        df = pd.read_csv(rawdata_path + file, index_col=0)
        if df.empty:
            print(file, " is empty.")
            pass
        else:
            df['stockname'] = stock_name
            df['price_momentum']=backtest.price_momentum(df)
            df['low_volatility'] = backtest.low_volatility(df)

            df = df.dropna(axis=0)
            df=df[['stockname','Close','price_momentum','low_volatility']].dropna()
            df_sum = df_sum.append(df)

    df_sum=df_sum[df_sum.index==trade_date]
    df_sum=df_sum[df_sum.index==trade_date]
    df1 = df_sum['price_momentum'].groupby(df_sum.index).quantile(0.9).reset_index(). \
            rename({'price_momentum': 'top'}, axis=1).set_index('Date')
    df_sum = pd.merge(df_sum, df1, left_index=True, right_index=True)
    df2 = df_sum['low_volatility'].groupby(df_sum.index).quantile(0.1).reset_index(). \
            rename({'low_volatility': 'bottom'}, axis=1).set_index('Date')
    df_sum = pd.merge(df_sum, df2, left_index=True, right_index=True)
    df_sum = df_sum[(df_sum['price_momentum'] >= df_sum['top']) & (df_sum['low_volatility'] <= df_sum['bottom'])]

    df3 = df_sum['stockname'].groupby(df_sum.index).count().reset_index(). \
        rename({'stockname': 'num'}, axis=1).set_index('Date')
    df_sum = pd.merge(df_sum, df3, left_index=True, right_index=True)
    df_sum['quantity']=initial_cap/(df_sum['num']*df_sum['Close'])
    df_sum['quantity_absolute']=df_sum['quantity'].apply(lambda x: int(x))
    df_final=df_sum[['stockname','Close','num','quantity_absolute']]
    print(df_final)

    return df_final



if __name__ =='__main__':
    # getData().update_data()

    rawdata_path = '/Users/echo/PycharmProjects/EchoProject/sp500_data_1d/'

    #week2
    # df_final=weekly_holding(rawdata_path,trade_date='2021-11-05',initial_cap=1000000*1.15)
    # df_final = df_final[['stockname', 'quantity_absolute']].rename({'quantity_absolute': 'week2'}, axis=1).set_index(
    #     'stockname')
    # df_final.to_csv('stock_holding.csv')

    #week3
    # df_final=weekly_holding(rawdata_path,trade_date='2021-11-12',initial_cap=1005294.90*1.23)
    # df_final = df_final[['stockname', 'quantity_absolute']].rename({'quantity_absolute': 'week3'}, axis=1).set_index('stockname')

    # week4
    # df_final=weekly_holding(rawdata_path,trade_date='2021-11-19',initial_cap=1012315.65*1.23)
    # df_final = df_final[['stockname', 'quantity_absolute']].rename({'quantity_absolute': 'week4'}, axis=1).set_index('stockname')

    # week5
    df_final = weekly_holding(rawdata_path, trade_date='2021-11-26', initial_cap=1006493.65 / 0.8109)
    df_final = df_final[['stockname', 'quantity_absolute']].rename({'quantity_absolute': 'week5'}, axis=1).set_index(
        'stockname')

    df = pd.read_csv('stock_holding.csv', index_col=0)
    df = pd.concat([df, df_final], axis=1)
    df.to_csv('stock_holding.csv')








