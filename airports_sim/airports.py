from flights import *
from task import *
from aviation import *
from crew import *
class operator():
    ''' 
    调度人员类抽象
    '''
    def __init__(self) -> None:
        pass 

    def match_algorithm(self,task,candidate):
        ''' 
        匹配算法，按照沈老师整理的过程撰写匹配逻辑
        1. 宽窄机型
        2. 进港、离港
        3. 勤务保障需求
        taskList: 任务列表
        candidate: 候选人员

        return: 匹配的人员名单
        '''
        # 贪心选择，空闲时间最长排序的人员，第一具有 task 的人员

        taskList = task.taskList
        boundType = task.type # 飞机进出港
        airType = task.airtype # 机型

        print(f'boundType: {boundType}, airType: {airType}')
        df_can = candidate.sort_values(by='free',ascending=False)

        # 如果没有人员
        if df_can.shape[0] == 0:
            return None
        
        name_task_dict = {}
        trans = ['isYiBan','isFangXing','isWeiXiu','isZhongWen','isYingWen']
        # taskList 代表的是五种任务的属性，[self.isYiBan,self.isFangXing,self.isWeiXiu,self.isZhongwen,self.isYingwen]
        for i in range(len(taskList)):
            if taskList[i] == 1:
                # 选择第一个具有该属性的人员
                for index,row in df_can.iterrows():
                    if row[trans[i]] == 1 and row['name'] not in name_task_dict:
                        # 同时更新 taskList
                        name_task_dict[row['name']] = set()
                        for j in range(len(taskList)):
                            if row[trans[j]] == 1:
                                name_task_dict[row['name']].add(trans[j])
                                taskList[j] -= row[trans[j]]
                        break
        if taskList==[0,0,0,0,0]:
            # 选择 free 时间长的人
            name = df_can.iloc[0]['name']
            name_task_dict[name] = set()
            for i in range(len(taskList)):
                if df_can.iloc[0,:][trans[i]] == 1:
                    name_task_dict[name].add(trans[i])
        return name_task_dict

class airports():
    ''' 
    机场仿真过程类
    '''
    def __init__(self):
        super().__init__()
        # Fixed datatype
        self.aviationSet = ACsets()  # 航司信息
        self.flightSet = FlightsSet() # 航班信息
        self.crew = Crew() # 地勤人员信息
        self.operator = operator() # 调度算法
        self.gate_lounge = None

        # Dynamic datatype
        self.taskSet = TaskSet() # 任务集合
        self.margin = pd.Timedelta('15 min') # 可观察未来航班的时间间隔
        self.begin = None
        self.now = None
        self.days = 0
        self.df_task_exec = pd.DataFrame(columns=['Time',
                                                  'Lounge',
                                                  'Gate',
                                                  'Duration',
                                                  'People']) # 任务执行记录
    
    def record_process(self,gate,time,terminals,duration,name_list):
        '''
        记录每次任务和对应的人员名单
        task_list: 任务列表
        name_list: 人员名单
        '''
        print('======   Record the process   =======')
        duration = duration[0]
        if name_list:
            name_list = ''.join(list(name_list.keys()))
        # 为 df_task_exec 添加一行记录
        new_row = {'Time':time,'Gate':gate,'Lounge':terminals,'Duration':duration,'People':name_list}
        # 没有 row
        df_new_row = pd.DataFrame(new_row,index=[0])
        # 合并 df
        self.df_task_exec = pd.concat([self.df_task_exec,df_new_row],ignore_index=True)
    
    def save_result(self):
        ''' 
        保存完整运行结果
        '''
        self.df_task_exec.to_excel('./dataset/task_exec.xlsx',index=False)

    def login(self,aviation_path,flights_path,crew_zizhi_path,crew_group_path,gate_lounge_path):
        '''
        注册静态数据
        aviation_path: 航司信息路径
        flights_path: 航班信息路径
        crew_zizhi_path: 人员资质证明路径
        crew_group_path: 人员组别路径
        gate_lounge_path: 休息室路径
        '''
        self.aviationSet.login(aviation_path)
        self.flightSet.login(flights_path)
        print('Flights login success,len is ',self.flightSet.df_flights.shape[0])
        self.flightSet.filter_by_id(self.aviationSet.get_company_codingID())
        self.crew.login(crew_zizhi_path,crew_group_path)
        self.gate_terminal = pd.read_excel(gate_lounge_path) # ./dataset/Gate_lounge.xlsx'
        self.gate_terminal.rename(columns={'停机口':'gate',
                                           '休息室':'lounge'}, inplace=True)
        self.begin = self.flightSet.get_begin_time()
        self.now = self.begin # 初始化最早时间

    def get_margin_flights(self):
        '''
        获取可观察的航班的集合
        '''
        return self.flightSet.get_near_flights(self.now,self.margin)

    def generation_task(self,flight):
        ''' 
        从航班中生成任务,任务的时间和地点与航班一致
        '''
        newTask = self.aviationSet.create_task(flight.ac)
        newTask.time = flight.actual_datetime  # 任务执行时刻
        newTask.lounge = self.get_lounge(flight.gate) # 任务执行休息室
        newTask.gate = flight.gate # 任务执行登机口
        newTask.type = flight.boundType # 任务类型
        newTask.airtype = flight.airType # 任务飞机类型
        newTask.taskDuration = [newTask.get_task_duration() for _ in range(len(newTask.taskList))] # 任务持续时间,这部分需要做数据分析
        return newTask
    
    def get_lounge(self,gate):
        '''
        根据停机口获取休息室,根据 gate 明确对应的 terminal
        '''
        gate = int(gate)
        try:
            return self.gate_lounge[self.gate_lounge['gate'] == gate]['lounge'].values[0]
        except:
            lounges = [187,153,60,88]
            # 返回最近的休息室
            fix = [abs(gate - i) for i in lounges]
            return lounges[fix.index(min(fix))]
    
    def step(self):
        '''
        每次仿真的前进步骤s
        '''
        data = {} # 想清楚 data 需要有什么数据
        # 1. time，当前时间
        self.now += pd.Timedelta('1min') # 每分钟仿真一次
        data['time'] = self.now
        # 2. crew，人员信息
        self.crew.update_status(self.now) # 更新人员的 status 状态
        data['crew'] = self.crew.dfCrew
        # 3. task，任务信息
        flights_list = self.get_margin_flights() # 获取能够观察到的航班
        data['flights'] = flights_list

        if flights_list: 
            for flight in flights_list:
                task = self.generation_task(flight) # 根据航班信息生成任务
                self.taskSet.add_task(task) # 向任务集合中添加任务
        data['tasks'] = self.taskSet.tasks
        group = (self.now - self.begin).days % 4 + 1 # 每一天同时只有一个 Group 工作
        data['group'] = group
        name_list = None
        if self.taskSet.isnotnull():   # 这里应该是获取所有需要解决的任务列表，然后匹配所有的任务
            for task in self.taskSet:
                
                df_can =self.crew.get_near1_people(self.get_lounge(task.gate),group) # 获取附近 1/4 的人员
                name_list = self.operator.match_algorithm(task,df_can) # 第一次任务匹配
                if not name_list: # 第一次找不到人
                    print('No enough people, try to find the near2 people')
                    df_can = self.crew.get_near2_people(self.get_lounge(task.gate),group,self.now,df_can) # 第二次任务匹配
                    name_list = self.operator.match_algorithm(task,df_can)
                if not name_list:
                    # 除非没有人员，否则不会执行
                    print('No enough people, try to find the near3 people')
                    df_can = self.crew.get_near3_people(self.get_lounge(task.gate),group,df_can) # 第三次任务匹配
                    name_list = self.operator.match_algorithm(task,df_can)
    
                # 保存 namelist
                if name_list:
                    self.taskSet.tasks.remove(task)
                    self.record_process(task.gate,task.time,task.lounge,task.taskDuration,name_list)
                    self.crew._update_people_status(name_list,task,self.now)
                    self.taskSet.update_task_status(name_list,task)
                else:
                    if task.isdead():
                        self.taskSet.tasks.remove(task)
                        name_list = None
                        self.record_process(task.gate,task.time,task.lounge,task.taskDuration,name_list)
                task.update_status()
        data['name_list'] = name_list

        # 每增加一天
        if (self.now-self.begin).days != self.days:
            self.crew.record_single_day(str(self.now.month)+'-'+str(self.now.day))
            self.days = (self.now-self.begin).days # 更新天数
        
        return data

    def is_done(self):
        # return self.flightSet.index == 10
        return self.flightSet.is_done()


    
