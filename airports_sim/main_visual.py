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
    # ['isYiBan','isFangXing','isWeiXiu','isZhongWen','isYingWen']
    word_mapping = {
        'isYiBan':'一般勤务',
        'isFangXing':'放行机务',
        'isWeiXiu':'维修机务',
        'isZhongWen':'中文耳机',
        'isYingWen':'英文耳机',
        'default':'默认需求'
    }
    for key in name_list:
        show_text +='**'+ key+'**' + '被指派任务为' + '**'+word_mapping[name_list[key]]+'**'+'<br>'
    name_container.markdown(show_text,unsafe_allow_html=True)

def show_crew(df_crew,c_container,group):
    df_crew.sort_values(by='free',inplace=True,ascending=False)
    show_row = ['name','lounge','group','status','work_load','count','free']
    df_crew = df_crew[show_row]
    df_crew= df_crew[df_crew['group'] == group]
    df_crew['lounge'] = pd.to_numeric(df_crew['lounge'], errors='coerce')
    c_container.dataframe(df_crew)

def show_sub_crew(df_crew,c_container,group,lounge):
    df_crew.sort_values(by='free',inplace=True,ascending=False)
    show_row = ['name','lounge','group','status','work_load','count','free']
    df_crew = df_crew[show_row]
    df_crew= df_crew[df_crew['group'] == group]
    df_crew = df_crew[df_crew['lounge']==lounge]
    df_crew['lounge'] = pd.to_numeric(df_crew['lounge'], errors='coerce')
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

def show_result(col1,total_list,null_list):
    # col1中绘制 total_list
    col1.bar_chart(total_list)

def streamlit_html_div():
    ''' 
    设计整个网页的框架布局
    '''
    # 清空 crew 下的所有文件，'./dataset/crew/'
    st.title('系统仿真过程')
    time_container = st.empty() # 新建一个空白的容器
    st.markdown('## 控制参数')
    with st.container(height=100):
        global speed,min_work_time,max_work_time
        col1,col2,col3 = st.columns(3)
        speed = col1.slider('仿真速度',1,10,1)
        min_work_time = col2.number_input(label='最小工作时间，默认 30 分钟',value=30)
        max_work_time = col3.number_input(label='最大工作时间，默认 40 分钟',value=40)

    st.markdown('## 匹配过程')
    confirm_col = st.empty()
    with st.container(height=200):
        col1,col2= st.columns(2)
        col1.markdown('**需求航班信息**')
        col2.markdown('**保障人员信息**')
        col1,col2 = st.columns(2)
        flight_col = col1.empty() # 新建一个空白的容器
        name_col = col2.empty() # 新建一个空白的容器
    
    with st.container(height=400):
        # 候选池
        col1,col2= st.columns(2)
        col1.markdown('**同休息室人员(候选 1&2）**')
        col2.markdown('**所有工作人员（候选 3）**')

        col1,col2 = st.columns(2)
        sub_crew_container = col1.empty() # 新建一个空白的容器
        crew_container = col2.empty() # 新建一个空白的容器

    st.markdown('## 工作量展示')
    with st.container(height=400):
        col1,col2,col3 = st.columns([0.6,0.2,0.2])
        col1.markdown('**人员工作量**')
        col2.markdown('**休息室工作量**')
        col3.markdown('**单日派工数量**')
        col1,col2,col3 = st.columns([0.6,0.2,0.2])
        total_workload_col = col1.empty() # 新建一个空白的容器
        group_workload_col = col2.empty() # 新建一个空白的容器
        result_col = col3.empty()
    
    # with st.container(height=400):
    #     col1,col2 = st.columns(2)
    #     col1.markdown('**单日排列航班**')
    #     col2.markdown('**总排列航班数目**')
    #     col1,col2 = st.columns(2)
    #     record_single_col = col1.empty() # 新建一个空白的容器
    #     result_total_col = col2.empty() # 新建一个空白的容器
    return time_container,flight_col,name_col,sub_crew_container,crew_container,total_workload_col,group_workload_col,crew_container,result_col,confirm_col

def main():

    time_container,flight_col,name_col,sub_crew_container,crew_container,total_workload_col,group_workload_col,crew_container,result_col,confirm_col = streamlit_html_div()
    start_time = time.time()
    print('======   Clear the crew folder   =======')
    if os.path.exists('./dataset/crew/'):
        shutil.rmtree('./dataset/crew/')
    # 新建 crew 文件夹
    os.mkdir('./dataset/crew/')
    airport = airports()

    # Register the work time
    df_temp = pd.read_csv('./dataset/work_time.csv')
    df_temp['min'] = min_work_time
    df_temp['max'] = max_work_time
    df_temp.to_csv('./dataset/work_time.csv')

    flights_path = './dataset/flights_obs.xlsx'
    aviation_path =  './dataset/new_aviationCompany.xlsx'
    crew_zizhi_path = './dataset/人员资质证明.xlsx'
    crew_group_path = './dataset/人员组别.xlsx'
    gate_lounge_path = './dataset/Gate_lounge.xlsx'
    type_minNum_path = './dataset/机型最小人员数.xlsx'
    airport.login(aviation_path,flights_path,crew_zizhi_path,crew_group_path,gate_lounge_path,type_minNum_path)
    total_list = [0]
    null_list = [0]
    print('======   Start the simulation   =======')
    lounge = '60'

    while not airport.is_done():
        data = airport.step() # 获取数据接口
        now = data['time']
        flights = data['flights']
        tasks = data['tasks']
        crew = data['crew']
        name_list = data['name_list']
        group = data['group']
        if data['lounge'] != -1:
            lounge = data['lounge']
        
        single_total = data['single_total']
        single_null = data['single_null']
        if single_total!=total_list[-1] and single_total == -1:
            total_list.append(0)
            null_list.append(0)
        else:
            total_list[-1] = single_total
            null_list[-1] = single_null
        

    
        # crew_container.write('当前时间：{}'.format(now))
        time_container.write('当前时间：{}'.format(now))
        if flights:
            show_flights(flights,flight_col)
            if name_list:
                show_name_list(name_list,name_col)
        show_crew(crew,crew_container,group)
        show_sub_crew(crew,sub_crew_container,group,lounge)
        show_total_workload(crew,group,total_workload_col)
        show_group_workload(crew,group,group_workload_col)
        show_result(result_col,total_list,null_list)
        if speed != 1:
            time.sleep(speed/1000)


    print(airport.flightSet.index)

    end_time = time.time()
    airport.save_result()
    logger(start_time,end_time)

if __name__ == '__main__':
    main()