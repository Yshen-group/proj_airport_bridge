from flights import *
from task import *
from aviation import *
from airports import *
from crew import *
import os
import shutil
import time
import streamlit as st
st.set_page_config(layout="wide")

def logger(start,end):
    print('start:',start)
    print('end:',end)
    print('time:',end-start)
    print('=====================')
    path = './dataset/task_exec.xlsx'
    df = pd.read_excel(path)
    missing = df['People'].isnull().sum()
    print('缺失率', missing/len(df))

        # self.gate = 0 # 位置    
        # self.planDate = 0 # 计划日期
        # self.planTime = 0 # 计划时间
        # self.actual_datetime = 0 # 实际时间
        # self.ac = None # 航司信息
        # self.boundType = None # 类型,inbound or outbound
        # self.airType = None # 机型

def show_flights(flights,flight_container):
    df_list = [f.to_row() for f in flights]
    df = pd.concat(df_list)
    show_row = ['gate','actual_datetime','ac','boundType','airType']
    df = df[show_row]
    df.rename(columns={'gate':'登机口',
                          'actual_datetime':'实际时间',
                          'ac':'航司',
                          'boundType':'类型',
                          'airType':'机型'},inplace=True)
    flight_container.dataframe(df)


def show_task(tasks,task_container):
    df_list = [t.to_row() for t in tasks]
    df = pd.concat(df_list)
    show_row = ['gate','time','taskList']
    df = df[show_row]
    df.rename(columns={'gate':'登机口',
                            'time':'时间',
                            'taskList':'任务列表'},inplace=True)
    task_container.dataframe(df)

def convert_text(text):
    # '桥载':'isFangXing',
    # '廊桥':'isWeiXiu',
    # '勤务':'isYiBan',
    # '中文':'isZhongWen',
    # '英文':'isYingWen',
    NAME_SET = {'isFangXing':'桥载',
                'isWeiXiu':'廊桥',
                'isYiBan':'勤务',
                'isZhongWen':'中文',
                'isYingWen':'英文'}
    
    res = ''
    for i in text:
        res += f'{NAME_SET[i]} |'
    return res[:-1]

def show_name_list(name_list,name_container):
    show_text = ''
    for key,value in name_list.items():
        show_text += f'{key} : {convert_text(value)}<br>'
    name_container.markdown(show_text,unsafe_allow_html=True)

def show_crew(df_crew,c_container,group):
    df_crew.sort_values(by='free',inplace=True,ascending=False)
    show_row = ['name','lounge','group','status','work_load','count','free']
    df_crew = df_crew[show_row]
    df_crew= df_crew[df_crew['group'] == group]
    c_container.dataframe(df_crew)

def show_total_workload(df_crew,group,total_workload_col):
    df_crew = df_crew[df_crew['group'] == group]
    # 删除 workload 为 0 的人员
    df_crew = df_crew[df_crew['work_load'] != 0]
    df_crew = df_crew[['name','work_load']]
    df_crew.index = df_crew['name']
    # 排序条形图
    df_crew.sort_values(by='work_load',inplace=True)
    total_workload_col.bar_chart(df_crew['work_load'])

def show_group_workload(df_crew,group,group_workload_col):
    df_crew = df_crew[df_crew['group'] == group]
    # 删除 workload 为 0 的人员
    df_crew = df_crew[df_crew['work_load'] != 0]
    df_crew = df_crew[['lounge','work_load']]
    # 每个 lounge 的工作量
    df_crew = df_crew.groupby('lounge').sum()
    # 如果存60,88,153,187，没有 0
    df_crew = df_crew.reindex([60,88,153,187])
    lounge = ['60','88','153','187']
    for  key in lounge:
        if key not in df_crew.index:
            df_crew.loc[key] = 0
    group_workload_col.bar_chart(df_crew['work_load'])



def main():
    # 清空 crew 下的所有文件，'./dataset/crew/'
    st.title('系统仿真过程')
    speed = st.slider('仿真速度',0.1,1.0,0.5)
    time_container = st.empty() # 新建一个空白的容器
    col1,col2 = st.columns(2)
    col1.write('需求航班信息')
    col2.write('保障人员信息')
    col1,col2 = st.columns(2)
    flight_col = col1.empty() # 新建一个空白的容器
    name_col = col2.empty() # 新建一个空白的容器
    col1,col2 = st.columns(2)
    col1.write('人员工作量')
    col2.write('组别工作量')
    col1,col2 = st.columns(2)
    total_workload_col = col1.empty() # 新建一个空白的容器
    group_workload_col = col2.empty() # 新建一个空白的容器

    crew_container = st.empty() # 新建一个空白的容器

    start_time = time.time()
    print('======   Clear the crew folder   =======')
    if os.path.exists('./dataset/crew/'):
        shutil.rmtree('./dataset/crew/')
    # 新建 crew 文件夹
    os.mkdir('./dataset/crew/')
    airport = airports()
    flights_path = './dataset/flights_obs.xlsx'
    aviation_path =  './dataset/new_aviationCompany.xlsx'
    crew_zizhi_path = './dataset/人员资质证明.xlsx'
    crew_group_path = './dataset/人员组别.xlsx'
    gate_lounge_path = './dataset/Gate_lounge.xlsx'
    type_minNum_path = './dataset/机型最小人员数.xlsx'
    airport.login(aviation_path,flights_path,crew_zizhi_path,crew_group_path,gate_lounge_path,type_minNum_path)
    print('======   Start the simulation   =======')

    while not airport.is_done():
        data = airport.step() # 获取数据接口
        now = data['time']
        flights = data['flights']
        tasks = data['tasks']
        crew = data['crew']
        name_list = data['name_list']
        group = data['group']

        # crew_container.write('当前时间：{}'.format(now))
        time_container.write('当前时间：{}'.format(now))
        if flights:
            # show_task(tasks,flight_col)
            show_flights(flights,flight_col)
            if name_list:
                show_name_list(name_list,name_col)
        show_crew(crew,crew_container,group)
        show_total_workload(crew,group,total_workload_col)
        show_group_workload(crew,group,group_workload_col)
        


    print(airport.flightSet.index)

    end_time = time.time()
    airport.save_result()
    logger(start_time,end_time)

if __name__ == '__main__':
    main()