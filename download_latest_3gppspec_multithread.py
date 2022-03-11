# author : Hank Lee
# email: huiwu2068@gmail.com

import threading
import time
import requests
import zipfile
import queue as Queue
from pathlib import Path
import re
import os

url_prefix = "http://www.3gpp.org/ftp/Specs/latest"

releases = [ "Rel-16", "Rel-17", "Rel-18" ] # As they appear at url_prefix location

root = "D:\\xavier\\3gpp"

localheaders = {'User-Agent': 'Chrome/81.0.4044.138 Safari/537.36'}

class myThread (threading.Thread):
    def __init__(self, threadID, name, queue, where_to_save):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.queue = queue
        self.where_to_save = where_to_save
    def run(self):
        #print ("Thread started：" + self.name)
        while True:
            try:
                url = self.queue.get(timeout=1)   
                download_file(url, self.where_to_save)
            except:
                break
            
        #print ("Thread exited：" + self.name)

def download_file(file_link, where_to_save):
    if( ".zip" not in file_link) :
       return

    get_file = re.match(r'(.*)/(.*)/(.*)', file_link)

    where_to_save_dir  = where_to_save + get_file.group(2)
    where_to_save_file = where_to_save + get_file.group(2) + '\\' + get_file.group(3)
    zip_filename = get_file.group(3)

    get_dir  = Path(where_to_save_dir)
    get_file = Path(where_to_save_file)
    doc_file = Path(where_to_save_file.replace('.zip','.doc'))
    docx_file = Path(where_to_save_file.replace('.zip','.docx'))

    if not get_dir.is_dir():
        os.makedirs(where_to_save_dir)
        
    if not (doc_file.is_file() or docx_file.is_file()):
        print("download: ",file_link)

        r = requests.get(file_link, headers = localheaders)
        with open(where_to_save_file, 'wb') as outputfile:
            outputfile.write(r.content)

        with zipfile.ZipFile(where_to_save_file, 'r') as zip_ref:
            zip_ref.extractall(where_to_save_dir)
        os.remove(where_to_save_file)


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

def get_3gpp_url_list(latest_url):
    s = requests.session()

    spec_url_list = []

    response =s.get(latest_url,headers = localheaders)
        
    html = response.content.decode("utf-8")

    pattern = re.compile(r'<A HREF="(.*?)">(.*?)</A>',flags=re.I) 
    file_links_re = re.finditer(pattern,repr(html))

    for file_link_re in file_links_re:
        file = file_link_re.group(1)
        if re.match(r'.*\/latest\/Rel-.*',file):
            spec_url_list.append(file)
    return spec_url_list

for release in releases:

    print(f"Release: {release}: obtaining specs list...")
    spec_url_list = get_3gpp_url_list(f"{url_prefix}/{release}")
    file_list = get_file_list_url(spec_url_list)
    file_list = [f for f in file_list if ".zip" in f]
    print(f"Release: {release}: found {len(file_list)} specs")

    thread_num = 40
    # Sets the queue length
    workQueue = Queue.Queue(3000)

    #Populate the url into the queue
    #download_file(file_list[1], f"{root}\\{release}\\") # test...
    #workQueue.put(file_list[0]) # test...
    for url in file_list:
        workQueue.put(url)

    threads = []

    for i in range(thread_num):
        thread = myThread(i, 'Thread-%d'%(i), workQueue, f"{root}\\{release}\\")
        thread.start()
        threads.append(thread)

    for t in threads:
        t.join()

print ("End of main thread")