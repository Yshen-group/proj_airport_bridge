from task import Task
import pandas as pd
import numpy as np

class AviationCompany():
    ''' 
    单独的航司信息类
    ----
    generated_time_task: 根据航司的基础属性生成任务
    update_from_row: 从行中更新航司信息
    ---
    '''
    def __init__(self):
        '''
        name: 名称
        codingId: 二字代码
        terminal: 停机坪
        is[任务]：属性
        '''
        self.name = None # 航司名称
        self.codingId = None # 航司二字代码
        self.terminal = 'T2' # set for T2 or S2

        self.isYiBan = False # 是否需要一般勤务
        self.isFangXing = False # 是否需要放行机务
        self.isWeiXiu = False # 是否需要维修机务
        self.isZhongwen = False # 是否需要中文耳机
        self.isYingwen = False # 是否需要英文耳机
    
    def generate_time_task(self):
        ''' 
        根据航司的基本属性生成任务

        PS: 任务的时间和地点, 在具体航班信息中确定
        '''
        newTask = Task()
        newTask.terminals = self.terminal
        newTask.taskList = [self.isYiBan,self.isFangXing,self.isWeiXiu,self.isZhongwen,self.isYingwen]
        return newTask
    
    def update_from_row(self,temp_row):
        self.name = temp_row['name'].values[0]
        self.codingId = temp_row['codingId'].values[0]
        self.terminal = temp_row['terminal'].values[0]
        self.isYiBan = temp_row['isYiBan'].values[0]
        self.isFangXing = temp_row['isFangXing'].values[0]
        self.isWeiXiu = temp_row['isWeiXiu'].values[0]
        self.isZhongwen = temp_row['isZhongWen'].values[0]
        self.isYingwen = temp_row['isYingWen'].values[0]


class ACsets():
    '''
    航司集合类: 用于管理航司信息

    方法
    ----
    login: 注册航司信息
    get_company_codingID: 获取所有航司二字代码
    get_aviation_from_id: 根据二字 id 获取特定航司信息
    create_task: 根据二字代码生成任务
    ----
    '''
    def __init__(self):
        '''
        dfCompany: 航司信息 pandas.DataFrame
        companySets: 航司二字代码集合 python.set 
        '''
        self.dfCompany = pd.DataFrame(columns=['name', 'codingId', 'terminal', 'isYiBan', 'isFangXing', 'isWeiXiu', 'isZhongWen', 'isYingWen'])
        self.companySets = set()
    
    def _filter_from_origin(self,df):
        ''' 
        过滤航班类型为空的列
        '''
        df.drop(['航班类型'], axis=1, inplace=True)
        df.rename(columns={'航空公司':'name', 
                           '二字代码':'codingId', 
                           '停机坪':'terminal',
                           '一般勤务':'isYiBan',
                           '放行机务':'isFangXing',
                           '维修机务':'isWeiXiu',
                           '英文耳机':'isYingWen',
                           '中文耳机':'isZhongWen'}, 
                           inplace=True)
        return df
    
    def login(self,path):
        '''
        注册航司信息

        path: 航司信息路径 
        '''
        df_com = pd.read_excel(path)
        self.dfCompany = self._filter_from_origin(df_com)
        self.companySets = set(df_com['codingId'])

    def get_company_codingID(self):
        '''
        获取航司二字代码集合
        '''
        return self.dfCompany['codingId']
    
    def get_aviation_from_id(self,codingID):
        ''' 
        根据二字代码获取航司信息
        '''
        avi = AviationCompany()
        temp_row = self.dfCompany[self.dfCompany['codingId'] == codingID]
        if temp_row.empty:
            raise 'The company is not in the list'
        else:
            avi.update_from_row(temp_row)
            return avi 

    def create_task(self,codingID):
        '''
        根据二字代码生成任务
        '''
        return self.get_aviation_from_id(codingID).generate_time_task()

    def add_aviation(self,aviation):
        ''' 
        暂时未用到
        '''
        self.dfCompany = self.dfCompany.append(aviation,ignore_index=True)
        self.companySets.add(aviation.codingId)
    
    def remove_aviation(self,aviation):
        '''
        暂时未用到
        '''
        self.dfCompany = self.dfCompany[self.dfCompany['codingId'] != aviation.codingId]
        self.companySets.remove(aviation.codingId)