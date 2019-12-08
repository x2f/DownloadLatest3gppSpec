# author : Hank Lee
# email: huiwu2068@gmail.com

import threading
import time
import requests
import queue as Queue
from pathlib import Path
import re


spec_url_list = ["http://www.3gpp.org/ftp/Specs/latest/Rel-15/23_series/",
"http://www.3gpp.org/ftp/Specs/latest/Rel-15/24_series/",
"http://www.3gpp.org/ftp/Specs/latest/Rel-15/29_series/",
"http://www.3gpp.org/ftp/Specs/latest/Rel-15/32_series/",
"http://www.3gpp.org/ftp/Specs/latest/Rel-15/33_series/",
"http://www.3gpp.org/ftp/Specs/latest/Rel-15/35_series/",
"http://www.3gpp.org/ftp/Specs/latest/Rel-15/37_series/",
"http://www.3gpp.org/ftp/Specs/latest/Rel-15/38_series/"]

where_to_save = "C:\\3gppLatest\\"

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}

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
    get_file = re.match(r'(.*)/(.*)', file_link)

    where_to_save_file = where_to_save + get_file.group(2)

    get_file = Path(where_to_save_file)

    if get_file.is_file() == False:
        print("download: ",file_link)

        r = requests.get(file_link, headers = headers)
        with open(where_to_save_file, 'wb') as outputfile:
            outputfile.write(r.content)

def get_file_list_url(spec_url_list):
    s = requests.session()

    file_list = []

    for spec_url in spec_url_list:
        response =s.get(spec_url,headers = headers)
        
        html = response.content.decode("utf-8")

        pattern = re.compile(r'<A HREF="(.*?)">(.*?)</A>') 
        file_links_re = re.finditer(pattern,repr(html))

        for file_link_re in file_links_re:
            file = file_link_re.group(2)
            if re.match(r'.*\..*',file):
                file_list.append(spec_url+file)
    return file_list

file_list = get_file_list_url(spec_url_list)

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