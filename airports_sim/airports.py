from flights import *
from task import *
from aviation import *
from crew import *
import mesa

class operator():
    def __init__(self) -> None:
        pass 

    def match_algorithm(self,taskList,candidate):
        ''' 
        任务匹配算法
        '''
        # 贪心选择，空闲时间最长排序的人员，第一具有 task 的人员
        df_can = candidate.sort_values(by='free',ascending=False)
        df_can = df_can[df_can['status'] == 0]
        print(df_can)
        name_task_dict = {}
        trans = ['isYiBan','isFangXing','isWeiXiu','isZhongWen','isYingWem']
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
        return name_task_dict


class airports(mesa.Model):
    def __init__(self):
        super().__init__()
        self.aviationSet = ACsets()
        self.flightSet = FlightsSet()
        self.taskSet = TaskSet()
        self.crew = Crew()
        self.operator = operator()

        self.margin = pd.Timedelta('15 min') # 时间间隔
        self.begin = None
        self.now = None
        self.gate_terminal = None
    
    def login(self,aviation_path,flights_path):
        self.aviationSet.login(aviation_path)
        self.flightSet.login(flights_path)
        self.flightSet.filter_by_id(self.aviationSet.get_company_codingID())
        self.begin = self.flightSet.get_begin_time()
        self.now = self.begin # 初始化最早时间
        self.crew.login()
        self.gate_terminal = pd.read_excel('./dataset/Gate_lounge.xlsx')
        self.gate_terminal.rename(columns={'停机口':'gate','休息室':'terminal'}, inplace=True)
    
    def get_margin_flights(self):
        return self.flightSet.get_near_flights(self.now,self.margin)

    def generation_task(self,flight):
        ''' 
        从航班信息中获取 time 和 id 信息
        配合航司信息生成任务
        '''
        newTask = self.aviationSet.create_task(flight.ac,flight.actual_datetime,flight.location)
            # update newTask duration list
        newTask.taskDuration = [pd.Timedelta('10 min') for _ in range(len(newTask))]
        return newTask
    def get_terminal(self,terminal):
        terminal = int(terminal)
        try:
            return self.gate_terminal[self.gate_terminal['gate'] == terminal]['terminal'].values[0]
        except:
            terminals = [187,153,60,88]
            # 返回最近的休息室
            fix = [abs(terminal - i) for i in terminals]
            return terminals[fix.index(min(fix))]
    
    def step(self):
        self.now += pd.Timedelta('1min')
        flights_list = self.get_margin_flights()
        if flights_list:
            for flight in flights_list:
                task = self.generation_task(flight)
                self.taskSet.add_task(task)
                print('=========Task Description=========')
                print(task.get_task_description())
                df_can =self.crew.get_near1_people(self.get_terminal(task.location),1)
                print('=========Match Algorithm=========')
                name_list = self.operator.match_algorithm(task.taskList,df_can)
                print(name_list)
                self.crew._update_people_status(name_list,task,self.now)
                self.taskSet.update_task_status(name_list,task)

            print(f'Now time: {self.now}')
    
    
    def is_done(self):
        return self.flightSet.index == 10
        # return self.flightSet.is_done()


    
