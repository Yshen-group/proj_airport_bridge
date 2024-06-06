import mesa
import pandas as pd
import numpy as np
from task import *
import copy
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
        df_new['status'] = 0 # 0-1 标识，0 标识空闲；1 标识被占用
        df_new['work_load'] = 0 # 工作时长， 标识总工作时间
        df_new['end_time'] = None # 期望工作结束时间，begin_time + task_duration
        df_new['gate'] = None # 工作登机口
        df_new['count'] = 0 # 被派工次数
        df_new['free'] = 0 # 空闲时间：距离上次运行工作时间
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
        # 任务指派之后，对应人员的数值得到更新
        for name in name_dict:
            self.dfCrew.loc[self.dfCrew['name'] == name, 'status'] = 1 # 将其状态设置为被占用
            self.dfCrew.loc[self.dfCrew['name'] == name, 'work_load'] += task.get_task_duration() # 增加工作时长
            time = task.taskDuration[0] # int type
            self.dfCrew.loc[self.dfCrew['name'] == name, 'end_time'] = now + pd.Timedelta(f'{time}minute')# 设置期望工作时间
            self.dfCrew.loc[self.dfCrew['name'] == name, 'gate'] = task.gate # 工作登机口
            self.dfCrew.loc[self.dfCrew['name'] == name, 'free'] = 0 # 重置空闲时间
            self.dfCrew.loc[self.dfCrew['name'] == name, 'count'] += 1
    
    def record_single_day(self,day):
        '''
        记录单天的工作情况,保留用户的信息
        '''
        temp_df = copy.deepcopy(self.dfCrew) # 清空数据
        temp_df['date'] = day # 新增日期
        temp_df = temp_df[temp_df['work_load'] > 0] # 只保留工作过的人员
        temp_df.to_csv(f'./dataset/crew/crew_{day}.csv') # 每天保存到对应的结果

               
        self.dfCrew['status'] = 0  # 状态不需要更新
        self.dfCrew['work_load'] = 0 # 工作时间清零
        self.dfCrew['end_time'] = None # 不需要更新期望工作时间
        self.dfCrew['gate'] = None # 不需要更新等级时间
        self.dfCrew['count'] = 0 # 排班次数清零
        self.dfCrew['free'] = 0  # 空闲时间等待最后更新

        
    
    def update_status(self,now):
        ''' 
        根据当前的时间恢复状态
        '''
        self.dfCrew.loc[self.dfCrew['status'] == 0, 'free'] += 1 # 空闲状态用户的空闲时间增加
        self.dfCrew.loc[(now > self.dfCrew['end_time'] + pd.Timedelta('2 min')) & (self.dfCrew['status'] == 1), 'status'] = 0
        self.dfCrew.loc[(now > self.dfCrew['end_time'] + pd.Timedelta('2 min')) & (self.dfCrew['status'] == 1), 'gate'] = self.dfCrew.loc[(now > self.dfCrew['end_time'] + pd.Timedelta('2 min')) & (self.dfCrew['status'] == 1), 'gate']


