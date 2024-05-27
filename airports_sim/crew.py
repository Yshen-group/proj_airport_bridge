import mesa
import pandas as pd
import numpy as np
from task import *
class Crew:
    ''' 
    机组人员管理

    方法
    ----
    login: 注册人员信息
    get_near1_people: 获取附近 1/4 的人员
    get_near2_people: 获取附近 1/4 即将空闲人员
    get_near3_people: 获取附近 1/2 空闲人员
    _update_people_status: 根据分配的任务更新人员状态
    '''
    def __init__(self) -> None:
        ''' 
        dfCrew: 人员数据库  pandas.DataFrame
        index: 索引
        '''
        self.dfCrew = None
        self.index = 0
    
    def _fileter_from_origin(self,df):
        pass

    def login(self,crew_zizhi_path,crew_group_path):
        '''
        登录人员信息, 融合资质证明和组别信息
        '''
        df_zizhi = pd.read_excel(crew_zizhi_path) #'./dataset/人员资质证明.xlsx'
        df_group = pd.read_excel(crew_group_path) #'./dataset/人员组别.xlsx'
        df_group.rename(columns={'人员':'姓名'}, inplace=True)
        df_group.fillna(0, inplace=True)
        df_new = pd.merge(df_group, df_zizhi[['姓名','机组通话']], on='姓名', how='left')
        # df_new = df_new[((df_new['耳机']==1) & (df_new['机组通话'].isnull())) | ((df_new['耳机']==0) & (df_new['机组通话'].notnull()))]
        df_new['机组通话'].unique()
        df_new['中文'] = df_new['机组通话'].notna()
        df_new['英文'] = df_new['机组通话'] == 'C/E'
        df_new.drop(columns=['机组通话','耳机'], inplace=True)

        df_new.rename(columns={'姓名':'name',
                               '桥载':'isFangXing',
                               '廊桥':'isWeiXiu',
                               '勤务':'isYiBan',
                               '中文':'isZhongWen',
                               '英文':'isYingWen',
                               '休息室':'lounge',
                               '组别':'group'}, inplace=True)
        df_new['status'] = 0 # 空闲
        df_new['work_load'] = 0 # 工作时长
        df_new['end_time'] = None # 结束时间
        df_new['gate'] = None
        df_new['free'] = 0
        self.dfCrew = df_new
    
    def get_near1_people(self,lounge,group):
        ''' 
        获取附近 1/4的人员
        '''
        assert lounge in [187,153,60,88]
        assert group in [1,2,3,4]
        # 找到对应 position 最近人员 并且 空闲状态 
        return self.dfCrew[(self.dfCrew['lounge'] == lounge) & (self.dfCrew['status'] == 0) & (self.dfCrew['group'] == group)]
    
    def get_near2_people(self,lounge,group,now,df_can):
        ''' 
        获取附近 1/4 即将空闲人员
        '''
        # 应该是在 near1 的基础上进行

        df_can_add =  self.dfCrew[(self.dfCrew['lounge'] == lounge) & (self.dfCrew['status'] == 1) & (self.dfCrew['group'] == group) & (self.dfCrew['end_time'] < now+pd.Timedelta('15 min'))]
        return pd.concat([df_can,df_can_add])

    def get_near3_people(self,lounge,group,df_can):
        '''
        获取附近 1/2 空闲人员
        '''
        # 187航站楼与 153 航站楼连接
        # 60航站楼与 88 航站楼连接
        if lounge == 187:
            df_can_add = self.dfCrew[(self.dfCrew['lounge'] == 153) & (self.dfCrew['status'] == 0) & (self.dfCrew['group'] == group)]
        elif lounge == 153:
            df_can_add = self.dfCrew[(self.dfCrew['lounge'] == 187) & (self.dfCrew['status'] == 0) & (self.dfCrew['group'] == group)]
        elif lounge == 60:
            df_can_add = self.dfCrew[(self.dfCrew['lounge'] == 88) & (self.dfCrew['status'] == 0) & (self.dfCrew['group'] == group)]
        else:
            df_can_add = self.dfCrew[(self.dfCrew['lounge'] == 60) & (self.dfCrew['status'] == 0) & (self.dfCrew['group'] == group)]
        return pd.concat([df_can,df_can_add])
    
    def _update_people_status(self,name_dict,task:Task,now):
        '''
        根据分配的任务更新人员状态
        '''
        # 任务
        for name in name_dict:
            self.dfCrew.loc[self.dfCrew['name'] == name, 'status'] = 1
            self.dfCrew.loc[self.dfCrew['name'] == name, 'work_load'] += 10
            self.dfCrew.loc[self.dfCrew['name'] == name, 'end_time'] = now + pd.Timedelta('10 min')
            self.dfCrew.loc[self.dfCrew['name'] == name, 'gate'] = task.gate
            self.dfCrew.loc[self.dfCrew['name'] == name, 'free'] = 0
    
    def update_status(self,now):
        ''' 
        根据当前的时间恢复状态
        '''
        # 空闲均+1
        self.dfCrew.loc[self.dfCrew['status'] == 0, 'free'] += 1
        self.dfCrew.loc[(now > self.dfCrew['end_time'] + pd.Timedelta('2 min')) & (self.dfCrew['status'] == 1), 'status'] = 0
        self.dfCrew.loc[(now > self.dfCrew['end_time'] + pd.Timedelta('2 min')) & (self.dfCrew['status'] == 1), 'gate'] = self.dfCrew.loc[(now > self.dfCrew['end_time'] + pd.Timedelta('2 min')) & (self.dfCrew['status'] == 1), 'gate']


