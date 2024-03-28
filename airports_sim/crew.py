import mesa
import pandas as pd
import numpy as np
from task import *

# class People:
#     def __init__(self) -> None:
#         self.name = None
#         self.id = None
#         self.terminal = None # 休息室
#         self.position = None 
#         self.group = None
#         self.isYiBan = False # 勤务
#         self.isFangXing = False # 桥载
#         self.isWeiXiu = False # 廊桥
#         self.isZhongwen = False # 中文
#         self.isYingwen = False # 英文

#     def update_from_row(self,temp_row):
#         self.name = temp_row['name'].values[0]
#         self.id = temp_row['id'].values[0]
#         self.terminal = temp_row['terminal'].values[0]
#         self.position = self.terminal
#         self.group = temp_row['group'].values[0]

#         self.isYiBan = temp_row['isYiBan'].values[0]
#         self.isFangXing = temp_row['isFangXing'].values[0]
#         self.isWeiXiu = temp_row['isWeiXiu'].values[0]
#         self.isZhongwen = temp_row['isZhongWen'].values[0]
#         self.isYingwen = temp_row['isYingWen'].values[0]

class Crew:
    def __init__(self) -> None:
        self.dfCrew = None
        self.index = 0
    
    def _fileter_from_origin(self,df):
        pass

    def login(self):
        df_zizhi = pd.read_excel('./dataset/人员资质证明.xlsx')
        df_group = pd.read_excel('./dataset/人员组别.xlsx')
        df_group.rename(columns={'人员':'姓名'}, inplace=True)
        df_group.fillna(0, inplace=True)
        df_new = pd.merge(df_group, df_zizhi[['姓名','机组通话']], on='姓名', how='left')
        # df_new = df_new[((df_new['耳机']==1) & (df_new['机组通话'].isnull())) | ((df_new['耳机']==0) & (df_new['机组通话'].notnull()))]
        df_new['机组通话'].unique()
        df_new['中文'] = df_new['机组通话'].notna()
        df_new['英文'] = df_new['机组通话'] == 'C/E'
        df_new.drop(columns=['机组通话','耳机'], inplace=True)
        df_new.rename(columns={'姓名':'name','桥载':'isFangXing','廊桥':'isWeiXiu','勤务':'isYiBan','中文':'isZhongWen','英文':'isYingWem','休息室':'terminal','组别':'group'}, inplace=True)
        df_new['status'] = 0 # 空闲
        df_new['work_load'] = 0 # 工作时长
        df_new['end_time'] = None # 结束时间
        df_new['position'] = None
        df_new['free'] = 0
        self.dfCrew = df_new
    
    def get_near1_people(self,position,group):
        assert position in [187,153,60,88]
        assert group in [1,2,3,4]
        # 找到对应 position 最近人员 并且 空闲状态 
        return self.dfCrew[(self.dfCrew['terminal'] == position) & (self.dfCrew['status'] == 0) & (self.dfCrew['group'] == group)]
    
    def get_near2_people(self,position,group):
        pass 

    def get_near3_people(self,position,group):
        pass
    
    def _update_people_status(self,name_dict,task:Task,now):
        # 所有人 free += 1
        self.dfCrew['free'] += 1

        # 如果 now > end_time+2, status = 0,position = terminal
        self.dfCrew.loc[(now > self.dfCrew['end_time'] + pd.Timedelta('2 min')) & (self.dfCrew['status'] == 1), 'status'] = 0
        self.dfCrew.loc[(now > self.dfCrew['end_time'] + pd.Timedelta('2 min')) & (self.dfCrew['status'] == 1), 'position'] = self.dfCrew.loc[(now > self.dfCrew['end_time'] + pd.Timedelta('2 min')) & (self.dfCrew['status'] == 1), 'terminal']

        # 任务
        for name in name_dict:
            self.dfCrew.loc[self.dfCrew['name'] == name, 'status'] = 1
            self.dfCrew.loc[self.dfCrew['name'] == name, 'work_load'] += 10
            self.dfCrew.loc[self.dfCrew['name'] == name, 'end_time'] = now + pd.Timedelta('10 min')
            self.dfCrew.loc[self.dfCrew['name'] == name, 'position'] = task.location
            self.dfCrew.loc[self.dfCrew['name'] == name, 'free'] = 0


