# 机场 廊桥人员派工项目

本项目主要面向浦东机场项目下廊桥人员派工项目，基于仿真和匹配优化完成实验结果

### 数据说明

浦东机场需要针对廊桥派工流程进行优化，现在面临的问题是派工人员需要反复在每次任务中寻找满足对应资质的空闲人员，是一项重复劳动的行为。可以采用的技术方案是采用仿真模拟的手段，然后利用一些简单的面向对象的方式建立 Python 脚本，之后利用简单的 FIFO 或者匈牙利匹配的方式来进行最优人员和任务之间的匹配。

### 算法说明
已经实现的功能包括

- AviationCompany() 航空公司
    - generate-time-task（time，location） 生成任务
    - update from row 更新航空公司
- ACSets() 航空公司集合
    - login 从数据中生成仿真
    - get_aviation from id 从代码获取航司信息
    - create task 根据代码生成航司对应的任务
    - get company coding ID 获取编码列表
- Crew 地勤人员集合
    - login 从数据中生成机组人员
    - **get near1 people 找到空闲的，同时处于对应1/4 terminal**
    - **get near2 people 找到空闲的，同时处于所有terminal的**
    - **get near3 people 找到即将完成任务的**
    - **_update people status 更新人员的状态**
- FlightsSet()
    - login 从数据中生成航班对应的任务
    - filter by id 根据航司信息获取航班id
    - get begin time 获取航班的开始时间
    - get near flights 获取最近的航班信息
    - is done 判断列表是否完成
- Task()
    - get-task-description 获取任务描述
    - get task duration 获取任务的持续时间
- Task set()
    - add task() 增加新的任务
- Airports（）
    - login() ，同时注册上述的机组人员、航班信息、terminal信息
    - get margin flights 获取最近的航班
    - generation task 从航班信息中获取time、location和id，由此生成任务
    - get terminal 获取登机口对应的terminal
    - step 更新函数，每一分钟更新
        - 获取需要添加的航班
        - **生成任务列表  # 应该是保留所有待办的任务清单，和对应的人员完成指派**
        - **获取对应的空闲人员 # 应该是获取所有空闲的人员，完成对应的任务的指派**
        - 完成人员和任务的指派问题
        - **更新任务和人员的状态 # 可能存在当前时间步骤没有完成任务**
    - is done 完成任务的更新
- Operator() 调度
    - match algorithm 完成任务集合和人员集合的匹配

![image](https://github.com/Yshen-group/proj_airport_bridge/assets/72689497/b499c788-4797-47c0-b1b3-2305e59e6025)


### 结果展示

暂无

### 如何参与开源项目

贡献使开源社区成为一个学习、激励和创造的绝佳场所。你所作的任何贡献都是**非常感谢**的。


1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### 版本控制

该项目使用Git进行版本管理。您可以在repository参看当前可用版本。

