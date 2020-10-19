# coding = utf-8
#with open('text.log', 'w') as f:
 #   f.write('b')
import json
import requests
import os
import psutil
import time


class Process_manage():
    def __init__(self):
        pass

    def read_task_pid(self, file_name):
        # 读取程序的pid
        try:
            with open(file_name, 'r') as f:
                task_pid = f.read()
            return task_pid
        except:
            return None

    def check_process(self, task_pid):
        # 检查程序是否在运行
        if task_pid != None:
            try:
                proc = psutil.Process(int(task_pid))  # 读取到进程号之后检验程序是否在运行
                return True
            except:
                return False
        else:
            return False

    def star_process(self, task_name, num=0):
        # 根据指令启动相应的爬虫程序
        if num == 0:
            task = self.read_task_pid(task_name)
            result = self.check_process(task)
            if result == False:
                if task_name == 'create_token':
                    os.system(
                        'nohup /opt/module/miniconda3/envs/python3/bin/python -u create_token.py >create_token.log 2>&1 & echo $! > create_token')
                else:
                    os.system(
                        # '(/opt/module/miniconda3/envs/python3/bin/scrapy crawl %s --logfile=%s.log --pidfile=%s &) >/dev/null  2>&1' % (
                        #     task_name, task_name, task_name))
                        '(/root/opt/software/miniconda3/envs/python3/bin/scrapy crawl %s --logfile=%s.log --pidfile=%s &) >/dev/null  2>&1' % (
                            task_name, task_name, task_name))
        else:
            for index in range(1, num+1):
                if task_name == 'detail_parse':
                    time.sleep(120)
                new_task = task_name + str(index)
                task = self.read_task_pid(new_task)
                result = self.check_process(task)
                if result == False:
                    if new_task == 'create_token':
                        os.system(
                            'nohup /opt/module/miniconda3/envs/python3/bin/python -u create_token.py >create_token.log 2>&1 & echo $! > create_token')
                    else:
                        os.system(
                            '(/root/opt/software/miniconda3/envs/python3/bin/scrapy crawl %s --logfile=%s.log --pidfile=%s &) >/dev/null  2>&1' % (
                                task_name, new_task, new_task))

    def kill_process(self, task_name):
        # 根据pid kill进程
        task_pid = self.read_task_pid(task_name)
        if task_pid != None:
            try:
                os.system('kill -9 %d' % (int(task_pid)))
            except:
                pass
        if task_name == 'creak_token':
            os.system('killall -9 chrome')
            os.system('killall -9 chromedriver')


class Task_status():
    def __init__(self):
        self.url = ''

    def get_task(self):
        response = requests.get(url=self.url)
        data = json.loads(response.text)


if __name__ == '__main__':
    p = Process_manage()
    p.star_process('keywords')
    p.star_process('seller_info')
    p.star_process('profile_parse')
    p.star_process('reviews')
    p.star_process('sellersprite_parse')
    p.star_process('detail_parse', 2)
