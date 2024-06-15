import numpy as np
import pandas as pd    
class Task():
    ''' 
    单次执行的任务
    '''
    def __init__(self) -> None:
        ''' 
        gate: 登机口位置
        time: 执行时间
        taskList: 子任务分解 list
        '''
        self.terminal = None # 航站楼
        self.lounge = None # 休息室
        self.gate = None # 登机口
        self.time = None # 时间

        self.minNum = 1 # 最小人数，由机型和进出港类型决定

        self.taskList = [] # 勤务需求
        self.taskDuration = [] # 勤务需求持续时间
        self.type = 'inbound' # 类型, inbound or outbound
        self.airtype = 'L' # 机型
        self.lifetime = 15 # 可被观察的时间为 15 分钟
        self.isdone = False # 是否完成
    
    def get_task_description(self):
        ''' 
        描述任务的地点、时间和任务列表
        '''
        return f'Boarding gate: {self.gate}, Time: {self.time}, TaskList: {self.taskList}'
    
    def get_task_duration(self):
        '''
        获取任务持续时间
        '''
        # 根据任务的时间生成持续时间，20～40 分钟,pd.Timedelta 格式
        # TODO 后续修改为 self.time 开启的时间
        duration = np.random.randint(30,40)
        return duration 
    
    def __len__(self):
        return len(self.taskList)
    
    def update_status(self,flag = False):
        '''
        更新任务状态
        '''
        
        self.lifetime -= 1
    
    def isdead(self):
        '''
        判断任务是否可以执行
        '''
        return self.lifetime == 0
    
    def to_row(self):
        '''
        转换成行
        '''
        return pd.DataFrame([self.__dict__])

class TaskSet:
    '''
    任务集合
    '''
    def __init__(self) -> None:
        ''' 
        tasks: 任务列表
        '''
        self.tasks = []
    
    def add_task(self,task):
        '''
        添加任务
        '''
        self.tasks.append(task)
    
    def get_tasks(self):
        '''
        获取现有的任务列表
        '''
        return self.tasks
    
    def update_task_status(self,name_list,task):
        '''
        更新任务状态, 标记任务完成
        '''
        for name in name_list:
            print(f'{name} finish the task: {task.get_task_description()}')
    
    def isnotnull(self):
        '''
        判断是否为空
        '''
        return len(self.tasks) > 0
    
    # 遍历
    def __iter__(self):
        return iter(self.tasks)