from flights import *
from task import *
from aviation import *
import mesa

class airports(mesa.Model):
    def __init__(self):
        super().__init__()
        self.aviationSet = ACsets()
        self.flightSet = FlightsSet()
        self.taskSet = TaskSet()

        self.margin = pd.Timedelta('15 min') # 时间间隔
        self.begin = None
        self.now = None
    
    def login(self,aviation_path,flights_path):
        self.aviationSet.login(aviation_path)
        self.flightSet.login(flights_path)
        self.flightSet.filter_by_id(self.aviationSet.get_company_codingID())
        self.begin = self.flightSet.get_begin_time()
        self.now = self.begin # 初始化最早时间
    
    def get_margin_flights(self):
        return self.flightSet.get_near_flights(self.now,self.margin)
    
    def generation_task(self,flight):
        ''' 
        从航班信息中获取 time 和 id 信息
        配合航司信息生成任务
        '''
        return self.aviationSet.create_task(flight.ac,flight.actual_datetime,flight.location)
    
    def step(self):
        self.now += pd.Timedelta('1min')
        flights_list = self.get_margin_flights()
        if flights_list:
            for flight in flights_list:
                task = self.generation_task(flight)
                self.taskSet.add_task(task)
                print(task.get_task_description())
            print(f'Now time: {self.now}')
    
    def is_done(self):
        return self.flightSet.is_done()


    
