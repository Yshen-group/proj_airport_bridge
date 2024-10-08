# 利用streamlit的session state、fragment、dialog等功能，实现了仿真过程的暂停、继续、重置等功能。

import streamlit as st
# 含有 sleep now 的代码
import time 
from datetime import datetime

# dialog 的功能介绍
# 用于产出一个独立当前页面的弹窗用于收集用户的信息

# fragment 用于并行的信息

# 希望实现功能，可以点击某个按钮，重新运行某个状态的输出
# 现在实现的逻辑是不断的输出一个循环的输出
# 但是希望在循环的过程中，可以点击某个按钮，运行暂停这个循环，然后再次点击按钮，继续这个循环

# 1. 点击按钮，开始循环
# 2. 在循环的过程中，点击按钮，暂停循环
# 3. 再次点击按钮

# 技术思路包括

# layout:
# 1. 固定的按钮，左边包括开始、暂停、继续、重置的按钮
if 'start' not in st.session_state:
    st.session_state.start = False

if 'pause' not in st.session_state:
    st.session_state.pause = False

if 'reset' not in st.session_state:
    st.session_state.reset = False\


# 2. 左边是 sidebar 用户布置按钮，右边是输出容器，用于输出循环的内容
# 3. 按钮的功能，每次点击会改变对应的 session_state 的值
def on_start():
    st.session_state.start = True
    st.session_state.pause = False
    st.session_state.reset = False

def on_pause():
    st.session_state.start = False
    st.session_state.pause = True
    st.session_state.reset = False

def on_continue():
    st.session_state.start = True
    st.session_state.pause = False
    st.session_state.reset = False
st.sidebar.button('开始', on_click=on_start)
st.sidebar.button('暂停', on_click=on_pause)
st.sidebar.button('继续', on_click=on_continue)

# # 4. 输出容器，用于输出循环的内容
# if st.session_state.start:
#     st.write('开始循环')
# if st.session_state.pause:
#     st.write('暂停循环')

# 用一个 session state 用于存储当前的信息
if 'current_time' not in st.session_state:
    st.session_state.current_time = datetime.now()

# 循环的状态，当到达某个点的时候自动暂停
if 'current_count' not in st.session_state:
    st.session_state.current_count = 0


# 5. 循环的内容
@st.fragment(run_every=1)
def loop(card):
    if st.session_state.current_count % 10:
        st.session_state.pause = True
        st.session_state.start = False
    if st.session_state.start:
        st.session_state.current_time = datetime.now()
        card.write('当前时间：{}'.format(st.session_state.current_time))
    if st.session_state.pause:
        card.write('当前时间：{}'.format(st.session_state.current_time))
    st.session_state.current_count += 1
    time.sleep(1)

# 新建一个布局，用于展示输出的文字
card  = st.empty()
loop(card)