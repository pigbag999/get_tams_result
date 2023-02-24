#coding=gbk
# [project]:
# [timeout]: 300 (单位s)
# [test_case_name]:获取任务结果
# [test_case_id]:获取任务结果
# [test_case_author]:lichanghe
# [test_case_description]:
# [test_case_time]:2022/10/31 下午1:55
# -*- coding: utf-8 -*-
import os
import subprocess
import re
import json
# try:
#     import yaml
# except ModuleNotFoundError as err_msg:
#     print("Missing yaml, start to download")
#     subprocess.run("pip install yaml", shell=True)
#     import yaml

try:
    import requests
except ModuleNotFoundError as err_msg:
    print("Missing requests, start to download")
    subprocess.run("pip install requests", shell=True)
    import requests
import urllib.request


max_download_num = 10#输入下载logcat文件的最大个数
now_path = os.getcwd()
task_id = input('请输入任务id：')
host = "http://tams.thundersoft.com/"
download_host = 'http://tams.thundersoft.com/api/storage/download/'
all_device_id_list = set()
merge_dict = {}
case_merge_dict = {}
download_merge_dict = {}
time_merge_dict = {}

with open('precise_package_blacklist.txt', 'r') as f:
    black_package_name = f.read()
    black_package_name_list = black_package_name.split(',')

with open('fuzzy_name_blacklist.txt','r') as f:
    fuzzy_name = f.read()
    fuzzy_name_list = fuzzy_name.split(',')

def remove_result_from_blacklist(self):

    for i in range(len(self.all_device_result['exceptions']) - 1, -1, -1):
        package_name = self.all_device_result['exceptions'][i]['package_name']
        type = self.all_device_result['exceptions'][i]['type']

        for black_name in black_package_name_list:
            if package_name == black_name:
                del self.all_device_result['exceptions'][i]
        for fuzzy in fuzzy_name_list:
            if fuzzy in package_name:
                del self.all_device_result['exceptions'][i]



def due_tams_result_to_dict(self,device_id):

    for i in range(len(self.all_device_result['exceptions']) - 1, -1, -1):
        package_name = self.all_device_result['exceptions'][i]['package_name']
        type = self.all_device_result['exceptions'][i]['type']

        if '{0}_{1}_{2}'.format(device_id, package_name, type) in self.result_dict.keys():
            self.result_dict['{0}_{1}_{2}'.format(device_id, package_name, type)] += 1
        else:
            self.result_dict['{0}_{1}_{2}'.format(device_id, package_name, type)] = 1
    due_result_dict = {}
    for i in self.result_dict.keys():

        if '{}'.format(device_id) in i:
            # print(i.split('{}'.format(device_id))[1])

            due_result_dict[i.split('{}'.format(device_id))[1].strip('_')] = self.result_dict[i]

            self.result_dict_dict[f'{device_id}'] = due_result_dict





def due_tams_result_to_download_dict(self):
    for i in range(len(self.all_device_result['exceptions']) - 1, -1, -1):
        package_name = self.all_device_result['exceptions'][i]['package_name']
        type = self.all_device_result['exceptions'][i]['type']
        download_device_id = self.all_device_result['exceptions'][i]['device_id']
        try:
            for first_key in self.all_device_result['exceptions'][i]['log'].keys():
            # for first_key in self.all_device_result.get('exceptions')[i].get('log').keys():
                download_path = self.all_device_result['exceptions'][i]['log'][first_key]['path']
                download_name = self.all_device_result['exceptions'][i]['log'][first_key]['filename']
                due_download_dict = {}

                if '{0}_{1}_{2}'.format(download_device_id,package_name, type) in self.download_dict.keys():
                    self.download_dict['{0}_{1}_{2}'.format(download_device_id,package_name, type)]['{}'.format(download_name)] = download_path
                else:
                    due_download_dict['{}'.format(download_name)] = download_path
                    self.download_dict['{0}_{1}_{2}'.format(download_device_id,package_name, type)] = due_download_dict
        except KeyError as e:
            del self.all_device_result['exceptions'][i]

def  due_tams_result_to_case_dict(self,device_id):
    for i in range(len(self.all_device_result['exceptions']) - 1, -1, -1):
        package_name = self.all_device_result['exceptions'][i]['package_name']
        type = self.all_device_result['exceptions'][i]['type']
        case_name = self.all_device_result['exceptions'][i]['case_name']

        if '{0}_{1}_{2}_{3}'.format(device_id, package_name, type,case_name) in self.case_dict.keys():
            self.case_dict['{0}_{1}_{2}_{3}'.format(device_id, package_name, type,case_name)] += 1
        else:
            self.case_dict['{0}_{1}_{2}_{3}'.format(device_id, package_name, type,case_name)] = 1
    due_case_dict = {}
    for i in self.case_dict.keys():

        if '{}'.format(device_id) in i:
            # print(i.split('{}'.format(device_id))[1])

            due_case_dict[i.split('{}'.format(device_id))[1].strip('_')] = self.case_dict[i]

            self.case_dict_dict[f'{device_id}'] = due_case_dict

def  due_tams_result_to_time_merge_dict(self):
    time_result = self.all_device_data['summary']

    total_result = time_result['total']
    for device_id in all_device_id_list:
        if device_id in time_result.keys():
            if device_id in time_merge_dict.keys():
                time_merge_dict[device_id] += time_result[device_id]['test_time']
            else:
                time_merge_dict[device_id] = time_result[device_id]['test_time']
    if 'total' in time_merge_dict.keys():
        time_merge_dict['total'] += total_result['test_time']
    else:
        time_merge_dict['total'] = total_result['test_time']

def due_tams_result_to_pass_rate_dict(self):
    pass
    # for device_id in time_merge_dict.keys():
    #     time_merge_dict[device_id] = time_merge_dict[device_id] / 3600


class TaskResult():
    def __init__(self,task_id):
        self.task_id = task_id
        self.device_id_list = []
        self.all_device_result = {}
        self.result_dict = {}
        self.result_dict_dict = {}
        self.case_dict = {}
        self.case_dict_dict = {}
        self.download_dict = {}
        self.all_device_data = {}

    def get_tams_device_id(self):
        api = 'api/result/get/{}'.format(self.task_id)
        url = os.path.join(host, api)
        all_device_data = requests.get(url)
        all_device_data = all_device_data.text
        # with open('{}_device_info.txt'.format(task_id),'a+') as f:
        #     f.write(all_device_data)
        all_device_data = json.loads(all_device_data)
        self.all_device_data = all_device_data
        for i in range(len(all_device_data['config']['dut_list'])):
            device_name = all_device_data['config']['dut_list'][i]['DUT']
            self.device_id_list.append(device_name)
            all_device_id_list.add(device_name)
        print(self.device_id_list)

    def get_tams_result(self):
        self.get_tams_device_id()
        print('开始获取{}的数据:'.format(self.task_id))

        for device_id in self.device_id_list:
            try:
                    # device_id = device_id.replace(':','')
                api = 'api/result/get_exception/{0}/{1}?limit=100000000'.format(self.task_id,device_id)
                url = os.path.join(host,api)
                all_device_result = requests.get(url)
                all_device_result = all_device_result.text
                all_device_result = json.loads(all_device_result)
                self.all_device_result = all_device_result
                #对数据进行处理
                remove_result_from_blacklist(self)
                due_tams_result_to_dict(self,device_id)
                due_tams_result_to_download_dict(self)
                due_tams_result_to_case_dict(self,device_id)

                for download_id in self.download_dict.keys():
                    if download_id in download_merge_dict.keys():
                        for logcat in self.download_dict[download_id].keys():
                            download_merge_dict[download_id][logcat] = self.download_dict[download_id][logcat]
                    else:
                        download_merge_dict[download_id] = self.download_dict[download_id]
            except KeyError as e:
                print('task {0} {1} have no result!'.format(self.task_id,device_id))

        try:
            due_tams_result_to_time_merge_dict(self)
        except KeyError as e:
            pass


        with open(os.path.join(now_path, 'result_path', '{}_result.txt'.format(self.task_id)), 'a+') as f:
            f.write('--'*20 +"↓↓↓测试设备id如下↓↓↓" + '--'*20 + '\n')

            f.write(str(self.device_id_list) + '\n')
            f.write('\n')
            f.write('--'*20+'↓↓↓任务结果如下↓↓↓' + '--'*20 + '\n')
            json.dump(self.result_dict_dict, f, indent=True)
            f.write('\n')
            f.write('--'*20 + '↓↓↓bug所在的case分布如下↓↓↓' + '--'*20)
            f.write('\n')
            json.dump(self.case_dict_dict, f, indent=True)
        # with open('{}_download_result.txt'.format(self.task_id), 'a+') as f:
        #     json.dump(self.download_dict,f,indent=True)

    def merge(self):
        self.get_tams_result()
        '''合并bug数目结果'''
        for id in self.result_dict_dict.keys():
            if id in merge_dict.keys():
                for package in self.result_dict_dict[id]:
                    if package in merge_dict[id]:
                        merge_dict[id][package] += self.result_dict_dict[id][package]
                    else:
                        merge_dict[id][package] = self.result_dict_dict[id][package]
            else:
                merge_dict[id] = self.result_dict_dict[id]
        '''合并case数目结果'''
        for id in self.case_dict_dict.keys():
            if id in case_merge_dict.keys():
                for package in self.case_dict_dict[id]:
                    if package in case_merge_dict[id]:
                        case_merge_dict[id][package] += self.case_dict_dict[id][package]
                    else:
                        case_merge_dict[id][package] = self.case_dict_dict[id][package]
            else:
                case_merge_dict[id] = self.case_dict_dict[id]

        '''合并下载path'''
        for download_id in self.download_dict.keys():
            if download_id in download_merge_dict.keys():
                for logcat in self.download_dict[download_id].keys():
                    download_merge_dict[download_id][logcat] = self.download_dict[download_id][logcat]
            else:
                download_merge_dict[download_id] = self.download_dict[download_id]


def download_log(task_id):
    print(f'开始下载任务{task_id}的文件')
    for key in download_merge_dict.keys():
        device_id = key.split('_')[0]
        package_name = key.split('_')[1].strip()
        type = key.split('_')[-1]
        if type == 'CRASH':
            type = 'APP_CRASH'

        count_num = 0
        for key2 in download_merge_dict[key].keys():
            if count_num >= max_download_num:
                break
            else:
                file_name = key2
                download_local_path = os.path.join(now_path, 'log_path', f'{task_id}', device_id.replace(":",""), type, package_name)
                if not os.path.exists(download_local_path):
                    os.makedirs(download_local_path)
                download_path = download_merge_dict[key][key2]
                print(f'开始下载{device_id}_{package_name}_{type}')

                urllib.request.urlretrieve(download_host + download_path, os.path.join(download_local_path, file_name))
                count_num += 1

def download_type_log(task_id):
    print(f'开始下载任务{task_id}的文件')
    for key in download_merge_dict.keys():
        device_id = key.split('_')[0]
        package_name = key.split('_')[1].strip()
        type = key.split('_')[-1]
        count_num = 0
        if type == 'CRASH':
            type = 'APP_CRASH'


            for key2 in download_merge_dict[key].keys():
                if count_num >= max_download_num:
                    break
                else:
                    file_name = key2
                    download_local_path = os.path.join(now_path, 'log_path', f'{task_id}_type', package_name,device_id.replace(":",""), type, package_name)
                    if not os.path.exists(download_local_path):
                        os.makedirs(download_local_path)
                    download_path = download_merge_dict[key][key2]
                    print(f'开始下载{device_id}_{package_name}_{type}')

                    urllib.request.urlretrieve(download_host + download_path, os.path.join(download_local_path, file_name))
                    count_num += 1
        if type == 'ANR':



            for key2 in download_merge_dict[key].keys():
                if count_num >= max_download_num:
                    break
                else:
                    file_name = key2
                    download_local_path = os.path.join(now_path, 'log_path', f'{task_id}_type', f'{package_name}_ANR',
                                                       device_id.replace(":", ""), type, package_name)
                    if not os.path.exists(download_local_path):
                        os.makedirs(download_local_path)
                    download_path = download_merge_dict[key][key2]
                    print(f'开始下载{device_id}_{package_name}_{type}')

                    urllib.request.urlretrieve(download_host + download_path,
                                               os.path.join(download_local_path, file_name))
                    count_num += 1












if __name__ == '__main__':
    if '-m' in task_id:
        task_id = task_id.split('-m')[0]
        task_id = task_id.split(',')
        # print(task_id)
        new_task_id = []
        for id in task_id:
            id = id.strip()
            new_task_id.append(id)
        for id in new_task_id:
            task = TaskResult(id)
            task.merge()
            if os.path.exists(os.path.join(now_path,'result_path','{}_result.txt'.format(id))):
                os.remove(os.path.join(now_path,'result_path','{}_result.txt'.format(id)))
            else:
                pass
        #常规下载：
        # download_log(f'{new_task_id[0]}_merge')
        #格式化下载:
        # download_type_log(f'{new_task_id[0]}_merge')
        print('任务结果合并完毕!')
        for device_id in time_merge_dict.keys():
            time_merge_dict[device_id] = f'{time_merge_dict[device_id] / 3600}h'
        with open(os.path.join(now_path,'result_path',f'{new_task_id[0]}_merge.txt'), 'a+') as f:
            # f.write(str(merge_dict))
            f.write('--' * 20 + "↓↓↓测试设备id如下↓↓↓" + '--' * 20 + '\n')
            f.write(str(all_device_id_list)+'\n')
            f.write('--' * 20 + '↓↓↓各设备挂测时间如下↓↓↓' + '--' * 20 + '\n')
            json.dump(time_merge_dict, f, indent=True)
            f.write('\n')
            f.write('\n')
            f.write('--' * 20 + '↓↓↓任务结果如下↓↓↓' + '--' * 20 + '\n')

            json.dump(merge_dict, f, indent=True)
            f.write('\n')
            f.write('--' * 20 + '↓↓↓bug所在的case分布如下↓↓↓' + '--' * 20)
            f.write('\n')
            json.dump(case_merge_dict, f, indent=True)





    else:

            task = TaskResult(task_id)
            task.get_tams_result()
            #常规下载：
            # download_log(task_id)
            #格式化下载：
            # download_type_log(task_id)
            for device_id in time_merge_dict.keys():
                time_merge_dict[device_id] = f'{time_merge_dict[device_id] / 3600}h'
            with open(os.path.join(now_path, 'result_path', '{}_result.txt'.format(task_id)), 'a+') as f:
                f.write('--' * 20 + '↓↓↓各设备挂测时间如下↓↓↓' + '--' * 20 + '\n')
                json.dump(time_merge_dict, f, indent=True)









