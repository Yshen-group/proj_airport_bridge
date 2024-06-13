import pandas as pd
import numpy as np
from task import *
from aviation import *

class Flights:
    ''' 
    单个航班类
    '''
    def __init__(self) -> None:
        '''
        gate: d登机口
        planDate: 计划日期
        planTime: 计划时间
        actualDate: 实际日期
        actualTime: 实际时间
        ac: 航司信息
        boundType: 类型
        '''
        self.gate = 0 # 位置    
        self.planDate = 0 # 计划日期
        self.planTime = 0 # 计划时间
        self.actual_datetime = 0 # 实际时间
        self.ac = None # 航司信息
        self.boundType = None # 类型,inbound or outbound
        self.airType = None # 机型
    
    def update(self,**kwargs):
        for key,value in kwargs.items():
            if hasattr(self,key):
                # hasattr(self,key) 判断是否有这个属性
                # setattr(self,key,value) 设置属性
                setattr(self,key,value)
            else:
                print('No such attribute')
    
    def update_from_row(self,row):
        '''
        从行中更新航班信息
        '''
        self.gate = row['机位']
        self.planDate = row['plan_date']
        self.planTime = row['plan_time']
        self.actual_datetime = row['actual_datetime']
        self.ac = row['航空公司']
        self.boundType = row['type']
        self.airType = row['机型']
        
class FlightsSet:
    ''' 
    航班集合类

    方法
    ----
    login: 注册航班信息
    filter_by_id: 根据航司信息筛选航班
    get_begin_time: 获取最早出发时间
    get_near_flights: 按照规则获取可观察的航班, 用于生成任务
    is_done: 判断所有航班是否完全排列
    '''
    def __init__(self) -> None:
        '''
        ----
        df_flights: 所有的航班信息 pandas.DataFrame
        Margin: 时间间隔
        index: 索引
        '''
        self.df_flights = None # 所有的航班信息
        self.Margin = 15 # TODO 时间间隔
        self.index = 0 # 索引   
    
    def _fileter_from_origin(self,df_flights):
        '''
        内部方法
        '''
        df_flights['actual_time'] = pd.to_timedelta(df_flights['actual_time'])
        df_flights['actual_datetime'] = df_flights['actual_date'] + df_flights['actual_time']
        df_flights.sort_values(by='actual_datetime', inplace=True)
        df_flights.reset_index(drop=True, inplace=True)
        df_flights.drop(['actual_time', 'actual_date'], axis=1, inplace=True)
        df_flights.dropna(inplace=True)
        return df_flights
    
    def login(self,path):
        ''' 
        根据历史观察数据, 注册航班信息
        '''
        # path = '../dataset/flights_obs.xlsx'
        flights = pd.read_excel(path)
        self.df_flights = self._fileter_from_origin(flights)
    
    def filter_by_id(self,codingId):
        ''' 
        根据航司信息筛选航班
        '''
        self.df_flights = self.df_flights[self.df_flights['航空公司'].isin(codingId)]
        self.df_flights.reset_index(drop=True, inplace=True)
    
    def get_begin_time(self):
        ''' 
        获取最早出发时间
        '''
        return self.df_flights['actual_datetime'][0]
    
    def get_near_flights(self,time,margin):
        ''' 
        按照规则获取可观察的航班, 用于生成任务
        '''
        res = []
        while not self.is_done() and self.df_flights['actual_datetime'][self.index] <= time+margin:
            flight = Flights()
            flight.update_from_row(self.df_flights.iloc[self.index]) # 从行中转换成为航班
            res.append(flight)
            self.index += 1
        return res
    
    def is_done(self):
        ''' 
        判断所有航班是否完成
        '''
        return self.index >= len(self.df_flights)
    
    def add_flight(self,flight):
        ''' 
        暂时未开发
        '''
        self.flights.append(flight)
    
    def get_flights(self,idx):
        ''' 
        暂时未开发
        '''
        return Flights().from_row(self.df_flights.iloc[idx])
    