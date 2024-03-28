from task import Task
import pandas as pd
import numpy as np

class AviationCompany():
    ''' 
    单独的航司信息类

    属性
    ----
    name: 名称
    codingId: 二字代码
    terminal: 停机坪
    is 任务：属性

    方法
    ----
    create_task: 创建任务
    '''
    def __init__(self):
        ''' 
        
        name: 名称
        codingId: 二字代码
        terminal: 停机坪
        is 任务：属性
        '''
        self.name = None
        self.codingId = None
        self.terminal = 'T2' # set for T2 or S2
        self.isYiBan = False
        self.isFangXing = False
        self.isWeiXiu = False
        self.isZhongwen = False
        self.isYingwen = False
    
    def generate_time_task(self,time = None,location = None):
        newTask = Task()
        newTask.terminals = self.terminal
        newTask.time = time
        newTask.location = location
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
    航司集合类

    属性
    ----
    dfCompany: 航司信息 DataFrame
    companySets: 航司代码集合

    方法
    ----
    login: 登录航司信息
    get_company: 根据二字编号获取航司信息

    '''
    def __init__(self):
        self.dfCompany = pd.DataFrame(columns=['name', 'codingId', 'terminal', 'isYiBan', 'isFangXing', 'isWeiXiu', 'isZhongWen', 'isYingWen'])
        self.companySets = set()
    
    def _filter_from_origin(self,df):
        # 过滤掉不需要的列
        df.drop(['航班类型'], axis=1, inplace=True)
        df.rename(columns={'航空公司':'name', '二字代码':'codingId', '停机坪':'terminal','一般勤务':'isYiBan','放行机务':'isFangXing','维修机务':'isWeiXiu','英文耳机':'isYingWen','中文耳机':'isZhongWen'}, inplace=True)
        return df
    
    def login(self,path):
        # 根据 path 提供的航司资质来注册航司列表
        df_com = pd.read_excel(path)
        self.dfCompany = self._filter_from_origin(df_com)
        self.companySets = set(df_com['codingId'])
    
    def get_aviation_from_id(self,codingID):
        # 根据二字代码获取航司信息
        avi = AviationCompany()
        temp_row = self.dfCompany[self.dfCompany['codingId'] == codingID]
        if temp_row.empty:
            raise 'The company is not in the list'
        else:
            avi.update_from_row(temp_row)
            return avi 

    def create_task(self,codingID,time = None,location = None):
        # 根据二字代码生成任务
        return self.get_aviation_from_id(codingID).generate_time_task(time,location)
    

    def get_company_codingID(self):
        return self.dfCompany['codingId']

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