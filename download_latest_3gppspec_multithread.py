# author : Hank Lee
# email: huiwu2068@gmail.com

import threading
import time
import requests
import queue as Queue
from pathlib import Path
import re
import os


Specs_latest_url = "http://www.3gpp.org/ftp/Specs/latest/Rel-16/"

where_to_save = "D:\\3gppR16Latest\\"

localheaders = {'User-Agent': 'Chrome/81.0.4044.138 Safari/537.36'}

class myThread (threading.Thread):
    def __init__(self, threadID, name, queue):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.queue = queue
    def run(self):
        print ("开始线程：" + self.name)
        while True:
            try:
                url = self.queue.get(timeout=1)   
                download_file(url)
            except:
                break
            
        print ("退出线程：" + self.name)

def download_file(file_link):
    if( ".zip" not in file_link) :
       return

    get_file = re.match(r'(.*)/(.*)/(.*)', file_link)

    where_to_save_dir  = where_to_save + get_file.group(2)
    where_to_save_file = where_to_save + get_file.group(2) + '\\' + get_file.group(3)

    get_dir  = Path(where_to_save_dir)
    get_file = Path(where_to_save_file)

    if get_dir.is_dir() == False:
        os.makedirs(where_to_save_dir)
        
    if get_file.is_file() == False:
        print("download: ",file_link)

        r = requests.get(file_link, headers = localheaders)
        with open(where_to_save_file, 'wb') as outputfile:
            outputfile.write(r.content)

def get_file_list_url(spec_url_list):
    s = requests.session()

    file_list = []

    for spec_url in spec_url_list:
        response =s.get(spec_url,headers = localheaders)
        
        html = response.content.decode("utf-8")

        pattern = re.compile(r'<A HREF="(.*?)">(.*?)</A>',flags=re.I) 
        file_links_re = re.finditer(pattern,repr(html))

        for file_link_re in file_links_re:
            file = file_link_re.group(2)
            if re.match(r'.*\..*',file):
                file_list.append(spec_url+"/"+file)
    return file_list

def get_3gpp_url_list(Specs_latest_url):
    s = requests.session()

    spec_url_list = []

    response =s.get(Specs_latest_url,headers = localheaders)
        
    html = response.content.decode("utf-8")

    pattern = re.compile(r'<A HREF="(.*?)">(.*?)</A>',flags=re.I) 
    file_links_re = re.finditer(pattern,repr(html))

    for file_link_re in file_links_re:
        file = file_link_re.group(1)
        if re.match(r'.*\/latest\/Rel-.*',file):
            spec_url_list.append(file)
    return spec_url_list

spec_url_list = get_3gpp_url_list(Specs_latest_url)

file_list = get_file_list_url(spec_url_list)

print(file_list)
thread_num = 40
# 设置队列长度
workQueue = Queue.Queue(3000)

#将url填充到队列
for url in file_list:
    workQueue.put(url)

threads = []

for i in range(thread_num):
    thread = myThread(i, 'Thread-%d'%(i),workQueue)
    thread.start()
    threads.append(thread)

for t in threads:
    t.join()

print ("退出主线程")