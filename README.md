# 机场 廊桥人员派工项目

本项目主要面向浦东机场项目廊桥派工仿真项目，基于仿真技术配合匹配算法完成勤务人员的匹配工作，主要参考沈老师的《0317 机场派工逻辑》
![沈老师派工逻辑梳理示意图](https://chenxia31blog.oss-cn-hangzhou.aliyuncs.com/img/20240527110732.png)

### 仿真数据说明

位于项目根目录下 /dataset 文件夹中，主要包括：

固定数据
1. 人员组别
2. 人员资质说明
3. Gate_lounge 航站楼和登机口
4. new_aviationComnpany 航司对应的勤务需求

运营数据
1. 机务维修中心出港 2 月
2. 机务维修中心进港 2 月
3. 观测航班信息.xlsx; 在上述信息上提取的规则数据

### 仿真流程说明

仿真过程的类整理在根目录 /airports_sim 文件夹中，其中文件作用包括

aviation.py
1. aviationCompany 航司公司类
2. ACSets 航司集合类

flights.py
1. fligths 单个航班类
2. flights set 集合航班类

crew.py
1. crew 主要是面向勤务人员操作

task.py
1. task 任务类，用于描述任务的时间、地点和任务属性,包括任务的持续时间
2. taskSet 任务集合类，方便后续操作

airports.py
1. operator 根据观察的勤务需求和空闲人员完成匹配
2. airports 函数仿真的主要逻辑，通过调用上述的类别，在时间线的步骤下，按照 flights 生成对应的航班，并根据 aviation 产生对应的 task，并调用 crew 的召回算法来获取当前的空闲人员，引入 operator 后完成两者的最优匹配。根据识别的结果来完成状态更新。

![仿真算法流程](https://chenxia31blog.oss-cn-hangzhou.aliyuncs.com/img/20240527112840.png)

### 待办事项
1. 将现实任务的时间替换现有的随机时间


### 匹配算法思路
这部分主要由 zp 复杂，期望主导引入 TRB 论文，前期调研可行的匹配算法包括：
1. 基于规则的FIFO规则算法
2. 匈牙利匹配算法
3. 更优秀的二分图匹配算法，KM 匹配、GS 匹配等
4. MDP 动态时空价值匹配，基于未来状态的匹配算法

![可能的匹配算法思路](https://chenxia31blog.oss-cn-hangzhou.aliyuncs.com/img/20240527112739.png)

### 结果输出

生成的可行执行过程存储在 task-exec 文件中，后续会增加可视化输出模块,增加多路人员召回模块最终结果实现0%缺失
![匹配算法缺失](https://chenxia31blog.oss-cn-hangzhou.aliyuncs.com/img/20240527192737.png)

### 如何修改本项目

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
4. Save the modfied(`'git add .'`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### 版本控制

该项目使用Git进行版本管理。您可以在repository参看当前可用版本。

