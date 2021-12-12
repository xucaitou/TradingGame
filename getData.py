
# Advanced Investments -- Trading Game
# @ Danjun Xu 13002775
from bs4 import BeautifulSoup as bs
import requests
import yfinance as yf
import os
import pandas as pd
import time

def get_html(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/81.0.4044.138 Safari/537.36',
        'accept-language': 'zh-CN,zh;q=0.9'
    }
    print("--> Obtaining web site information")
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        html = response.text
        return html
    else:
        print("Fail to get website information!")

def get_SD():
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    html = get_html(url=url)
    soup = bs(html, 'lxml')
    table = soup.find('table',{'class':'wikitable sortable'})
    SD = dict()
    for row in table.findAll('tr'):
        col = row.findAll('td')
        if len(col) > 0:
            ticker = str(col[0].a.contents[0].string.strip())
            sector = str(col[3].contents[0].string.strip()).lower()
            SD[ticker] = sector
    return SD

def get_UpdateDay(UpdateDay='Now'):
    if UpdateDay == 'Now':
        UpdateDay = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        UpdateDay = str(UpdateDay)
    else:
        UpdateDay = str(UpdateDay)
    return UpdateDay

# get 4-year historical data for backtesting
class getData:
    def __init__(self):
        self.rawdata_path='/Users/echo/PycharmProjects/EchoProject/sp500_data_1d/'
        self.start='2018-01-01'
        self.end='2021-10-29'
        self.interval='1d'

    def download_stock_data(self,stock_name):
        data = yf.download(stock_name, start=self.start, end=self.end, interval=self.interval)
        path = self.rawdata_path + stock_name + '.csv'
        data.to_csv(path)

    def get_historical_data(self):
        SD = get_SD()
        for stock_name in list(SD):
            self.download_stock_data(stock_name)
            print(stock_name)

    def update_data(self):
        update_date=get_UpdateDay(UpdateDay='Now')
        Filename=os.listdir(self.rawdata_path)
        Filename.sort()
        for file in Filename:
            print(file)
            stock_name=file.split('.')[0]
            df = pd.read_csv(self.rawdata_path+file,index_col=0)
            if df.empty:
                print(file," is empty.")
                pass
            else:
                last_update_date=df.index[-1]
                if last_update_date==update_date:
                    pass
                else:
                    print(last_update_date,update_date)
                    data = yf.download(stock_name, start=last_update_date, end=update_date, interval=self.interval)
                    if data.empty:
                        print("Already updated.")
                        pass
                    elif len(data)==1:
                        print("Already updated.")
                        pass
                    else:
                        data.index=data.index.map(lambda x: str(x)[:10])
                        for date in data.index:
                            if date in df.index:
                                pass
                            else:
                                df=df.append(data[data.index==date])
                        df.to_csv(self.rawdata_path+file)


if __name__ =='__main__':
    getdata=getData()
    # getdata.get_historical_data()
    getdata.update_data()

    # ds = web.DataReader('F-F_Research_Data_Factors_weekly', 'famafrench')
    # get_available_datasets()
    print(ds)


