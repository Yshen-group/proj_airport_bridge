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
    ''' 
    记录起止时间
    '''
    print('start:',start)
    print('end:',end)
    print('time:',end-start)
    print('=====================')
    path = './dataset/task_exec.xlsx'
    df = pd.read_excel(path)
    missing = df['People'].isnull().sum()
    print('缺失率', missing/len(df))

def show_flights(flights,flight_container):
    ''' 
    input:
    flights: list, 航班列表
    flight_container: streamlit容器

    output:
    展示航班信息
    '''
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
    ''' 
    inputs
    tasks: list, 任务列表
    task_container: streamlit容器

    output:
    展示任务信息
    '''
    df_list = [t.to_row() for t in tasks]
    df = pd.concat(df_list)
    show_row = ['gate','time','taskList']
    df = df[show_row]
    df.rename(columns={'gate':'登机口',
                            'time':'时间',
                            'taskList':'任务列表'},inplace=True)
    task_container.dataframe(df)

def convert_text(text):
    '''
    input:
    text: list, 文本列表
    '''
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
    ''' 
    input:
    name_list: dict, 名称列表
    name_container: streamlit容器

    output:
    展示名称列表
    '''
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
    '''
    展示完整的机组信息

    input:
    df_crew: DataFrame, 机组信息
    c_container: streamlit容器
    group: str, 机组类型
    '''
    df_crew.sort_values(by='free',inplace=True,ascending=False)
    show_row = ['name','lounge','group','status','work_load','count','free']
    df_crew = df_crew[show_row]
    df_crew= df_crew[df_crew['group'] == group]
    df_crew['lounge'] = pd.to_numeric(df_crew['lounge'], errors='coerce')
    c_container.dataframe(df_crew)

def show_sub_crew(df_crew,c_container,group,lounge):
    '''
    展示特定休息室对应的机组人员信息

    input:
    df_crew: DataFrame, 机组信息    
    c_container: streamlit容器
    group: str, 机组类型
    lounge: str, 休息室
    '''
    df_crew.sort_values(by='free',inplace=True,ascending=False)
    show_row = ['name','lounge','group','status','work_load','count','free']
    df_crew = df_crew[show_row]
    df_crew= df_crew[df_crew['group'] == group]
    df_crew = df_crew[df_crew['lounge']==lounge]
    df_crew['lounge'] = pd.to_numeric(df_crew['lounge'], errors='coerce')
    c_container.dataframe(df_crew)

def show_total_workload(df_crew,group,total_workload_col):
    '''
    展示整体的工作量

    input:
    df_crew: DataFrame, 机组信息
    group: str, 机组类型
    total_workload_col: streamlit容器
    '''
    df_crew = df_crew[df_crew['group'] == group]
    # 删除 workload 为 0 的人员
    df_crew = df_crew[df_crew['work_load'] != 0]
    df_crew = df_crew[['name','work_load']]
    df_crew.index = df_crew['name']
    # 排序条形图
    df_crew.sort_values(by='work_load',inplace=True)
    total_workload_col.bar_chart(df_crew['work_load'])

def show_group_workload(df_crew,group,group_workload_col):
    '''
    展示每个组别的工作量

    input:
    df_crew: DataFrame, 机组信息
    group: str, 机组类型
    group_workload_col: streamlit容器
    '''
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

def layout_init():
    ''' 
    初始化网络的所有布局
    '''
    # 清空 crew 下的所有文件，'./dataset/crew/'
    st.title('系统仿真过程')
    time_container = st.empty() # 新建一个空白的容器

    st.sidebar.markdown('## 控制按钮')
    if 'start' not in st.session_state:
        # 开始执行的标志
        st.session_state.start = False
    if 'pause' not in st.session_state:
        # 暂停循环
        st.session_state.pause = False
    if 'reset' not in st.session_state:
        # 回到上一次派工状态
        st.session_state.reset = False
    if 'reset_response' not in st.session_state:
        # 重新排列上次数据
        st.session_state.reset_response = True  # 默认是不需要重新排列

    # 新增按钮来改变 session_state 的值
    def on_start():
        st.session_state.start = True
        st.session_state.pause = False
        st.session_state.reset = False
        st.session_state.reset_response = True
    st.sidebar.button('开始/继续', on_click=on_start)

    # def on_pause():
    #     st.session_state.start = False
    #     st.session_state.pause = True
    #     st.session_state.reset = False
    #     st.session_state.reset_response = True # 暂停的时候不需要响应上次的数据
    # st.sidebar.button('暂停', on_click=on_pause)

    # 新增一个重新排列上次数据的按钮
    def on_reset():
        st.session_state.start = False
        st.session_state.pause = False
        st.session_state.reset = True 
        st.session_state.reset_response = True

    st.sidebar.button('暂停任务', on_click=on_reset)

    def on_reset_response():
        # 只有点击才需要重新排列
        st.session_state.reset_response = False
    st.sidebar.button('重新排列', on_click=on_reset_response)

    st.markdown('## 控制参数')
    global speed,min_work_time,max_work_time
    with st.container(height=100):
        col1,col2,col3 = st.columns(3)
        st.session_state['speed'] = col1.slider('仿真速度',1,10,1)
        st.session_state['min_work_time'] = col2.number_input(label='最小工作时间，默认 30 分钟',value=30)
        st.session_state['max_work_time'] = col3.number_input(label='最大工作时间，默认 40 分钟',value=40)

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

def data_init():
    '''
    初始化数据
    '''
    print('======   Clear the crew folder   =======')
    if os.path.exists('./dataset/crew/'):
        shutil.rmtree('./dataset/crew/')
    # 新建 crew 文件夹
    os.mkdir('./dataset/crew/')
    airport = airports()
    # Register the work time
    df_temp = pd.read_csv('./dataset/work_time.csv')
    df_temp['min'] = st.session_state.min_work_time
    df_temp['max'] = st.session_state.max_work_time
    df_temp.to_csv('./dataset/work_time.csv')

    flights_path = './dataset/flights_obs.xlsx'
    aviation_path =  './dataset/new_aviationCompany.xlsx'
    crew_zizhi_path = './dataset/人员资质证明.xlsx'
    crew_group_path = './dataset/人员组别.xlsx'
    gate_lounge_path = './dataset/Gate_lounge.xlsx'
    type_minNum_path = './dataset/机型最小人员数.xlsx'
    airport.login(aviation_path,flights_path,crew_zizhi_path,crew_group_path,gate_lounge_path,type_minNum_path)
    return airport

def total_result_pre(time_container,flight_col,name_col,sub_crew_container,crew_container,total_workload_col,group_workload_col,result_col,confirm_col):
    '''
    在页面数据上展示每次 airports 更新的 step 的数据
    data 每次实时更新的数据
    last_data 上一次排列更新的数据
    '''
    data = st.session_state['data']
    now = st.session_state['data']['time'] # 输出当前时间
    flights = st.session_state['data']['flights'] # 输出当前的航班任务
    tasks = st.session_state['data']['tasks'] # 输出当前的任务集合
    crew = st.session_state['data']['crew'] # 输出当前的机组信息
    name_list = st.session_state['data']['name_list'] # 输出当前的任务名称代表
    group = st.session_state['data']['group'] # 输出当前的机组内类型

    if data['lounge'] != -1:
        st.session_state.lounge = data['lounge']
    single_total = data['single_total'] # 这是什么意思
    single_null = data['single_null'] # 这是什么意思
    if single_total!=st.session_state['total_list'][-1] and single_total == -1: # 这是什么意思
        st.session_state['total_list'].append(0)
        st.session_state['null_list'].append(0)
    else:
        st.session_state['total_list'][-1] = single_total
        st.session_state['null_list'][-1] = single_null

    # crew_container.write('当前时间：{}'.format(now))
    time_container.write('当前时间：{}'.format(now)) # 展示当前的时间
    # 如果有航班信息，展示航班信息
    if  flights: # 上一次航班的信息
        show_flights(flights,flight_col) # 展示过去的航班信息
    
    if name_list:
        show_name_list(name_list,name_col) # 展示过去的任务名称代表
    else:
        show_name_list(st.session_state.last_data['name_list'],name_col) # 展示过去的任务名称代表

    show_crew(crew,crew_container,group)
    show_sub_crew(crew,sub_crew_container,group,st.session_state.lounge)
    show_total_workload(crew,group,total_workload_col)
    show_group_workload(crew,group,group_workload_col)
    show_result(result_col,st.session_state.total_list,st.session_state.null_list)
    if st.session_state.speed != 1:
        time.sleep(st.session_state.speed/1000)

@st.fragment(run_every=0.001)
def step(time_container,flight_col,name_col,sub_crew_container,crew_container,total_workload_col,group_workload_col,result_col,confirm_col):
    '''
    运行仿真的每一步
    '''
    before_air = copy.deepcopy(st.session_state['airport'])
    if st.session_state.done:
        st.stop()
    # 同时需要保存排列任务的航班数据
    data = st.session_state['airport'].step() # 获取数据接口']
    st.session_state['done'] = st.session_state['airport'].is_done()

    st.session_state['data'] = data # 每次要求更新数据

    # 如何判断是否应该记录上次历史派工的数据
    if 'last_data' not in st.session_state or  data['name_list'] != None:
        st.session_state['last_data'] = copy.deepcopy(data) # 保留最新的data数据,这个数据是无所谓的
        st.session_state['last_airports'] = copy.deepcopy(before_air) # 保留最新的airports数据
    total_result_pre(time_container,flight_col,name_col,sub_crew_container,crew_container,total_workload_col,group_workload_col,result_col,confirm_col)

time_container,flight_col,name_col,sub_crew_container,crew_container,total_workload_col,group_workload_col,crew_container,result_col,confirm_col = layout_init()
if 'confirm' not in st.session_state:
    print('======   Start the simulation   =======')
    # 初始化一些信息
    total_list = [0]
    null_list = [0]
    lounge = '60'
    st.session_state['lounge'] = lounge
    st.session_state['total_list'] = total_list
    st.session_state['null_list'] = null_list
    airport = data_init()
    st.session_state['airport'] = airport
    st.session_state['confirm'] = 1
    st.session_state['done'] = False
    st.session_state['reset_response'] = True

if 'data' in st.session_state:
    if st.session_state['reset']: # 重置阶段
        if st.session_state['reset_response']:
            #  True 表示不需要更新响应，直接使用之前数据展示即可
            st.session_state['data'] = copy.deepcopy(st.session_state['last_data'])
            # st.session_state['airport'] = copy.deepcopy(st.session_state['last_airports'])
        else:
            #  False 需要更新响应，应该回退到之前的数据，进行 cover 的迭代
            name_list = st.session_state['last_data']['name_list']
            # 更新重新的数据
            st.session_state['airport'] = copy.deepcopy(st.session_state['last_airports']) # 之前机场的信息 
            st.session_state['data'] = st.session_state['airport'].step_cover(name_list) # 最新机场的信息
            st.session_state['reset_response'] = True
            st.session_state['last_data'] = copy.deepcopy(st.session_state['data']) # 保留最新的数据
    total_result_pre(time_container,flight_col,name_col,sub_crew_container,crew_container,total_workload_col,group_workload_col,result_col,confirm_col)

if st.session_state.start: # 点击 start之后，开始运行 step，此时的 airports 理论上响应之后的数据
    step(time_container,flight_col,name_col,sub_crew_container,crew_container,total_workload_col,group_workload_col,result_col,confirm_col)
