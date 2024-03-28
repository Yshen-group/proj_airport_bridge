import mesa
import pandas as pd
import numpy as np
from task import *
from aviation import *

class Flights:
    ''' 
    单个航班类

    属性
    ----
    location: 位置
    planDate: 计划日期
    planTime: 计划时间
    actualDate: 实际日期
    actualTime: 实际时间
    ac: 航司信息
    boundType: 类型
    '''
    def __init__(self) -> None:
        self.location = 0
        self.planDate = 0
        self.planTime = 0
        self.actual_datetime = 0
        self.ac = None
        self.boundType = None
    
    def update(self,**kwargs):
        for key,value in kwargs.items():
            if hasattr(self,key):
                # hasattr(self,key) 判断是否有这个属性
                # setattr(self,key,value) 设置属性
                setattr(self,key,value)
            else:
                print('No such attribute')
    
    def update_from_row(self,row):
        self.location = row['机位']
        self.planDate = row['plan_date']
        self.planTime = row['plan_time']
        self.actual_datetime = row['actual_datetime']
        self.ac = row['航空公司']
        self.boundType = row['type']
    
class FlightsSet:
    ''' 
    航班集合类

    属性
    ----
    df_flights: 航班信息 DataFrame
    Margin: 时间间隔
    list_flights: 航班 list
    taskSet: 任务集合
    index: 索引

    方法
    ----
    login: 登录航班信息
    filterByAC: 根据航司信息筛选航班
    get_near_flights: 获取距离当前时间在 margin 间隔内的航班信息
    add_flight: 添加航班
    get_flights: 获取航班信息
    '''
    def __init__(self) -> None:
        self.df_flights = None
        self.Margin = 15
        self.index = 0
    
    def _fileter_from_origin(self,flights):
        flights['actual_time'] = pd.to_timedelta(flights['actual_time'])
        flights['actual_datetime'] = flights['actual_date'] + flights['actual_time']
        flights.sort_values(by='actual_datetime', inplace=True)
        flights.reset_index(drop=True, inplace=True)
        flights.drop(['actual_time', 'actual_date'], axis=1, inplace=True)
        flights.dropna(inplace=True)
        return flights
    
    def login(self,path):
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
        获取开始时间
        '''
        return self.df_flights['actual_datetime'][0]
    
    def get_near_flights(self,time,margin):
        ''' 
        获取距离当前 date、now ，在 margin 间隔内的航班信息，构造即将降落航班的属性
        创建任务到任务集合内
        '''
        res = []
        while not self.is_done() and self.df_flights['actual_datetime'][self.index] <= time+margin:
            flight = Flights()
            flight.update_from_row(self.df_flights.iloc[self.index])
            res.append(flight)
            self.index += 1
        return res
    
    def is_done(self):
        ''' 
        判断是否完成
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
    