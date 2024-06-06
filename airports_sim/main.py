from flights import *
from task import *
from aviation import *
from airports import *
from crew import *
import os
import shutil

def main():
    # 清空 crew 下的所有文件，'./dataset/crew/'
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
    airport.login(aviation_path,flights_path,crew_zizhi_path,crew_group_path,gate_lounge_path)
    print('======   Start the simulation   =======')

    while not airport.is_done():
        airport.step()
    print(airport.flightSet.index)
    airport.save_result()

if __name__ == '__main__':
    main()