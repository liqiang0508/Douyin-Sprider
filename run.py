#!/usr/bin/python
# -*- coding: UTF-8 -*-
import requests
import json
import os
import re
import time
from selenium import webdriver
import random
from prt_cmd_color import *
import sys

sys.setrecursionlimit(sys.maxint) #设置为一百万


headers1 = {'User-Agent':'Mozilla/6.0 (Windows; U; Windows NT 6.12; en-US; rv:1.9.1.7) Gecko/20091202 Firefox/3.5.6','Connection': 'close'} 

def getheaders():
    user_agent_list = ['Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1464.0 Safari/537.36',
                       'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.16 Safari/537.36',
                       'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.3319.102 Safari/537.36',
                       'Mozilla/5.0 (X11; CrOS i686 3912.101.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36',
                       'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36',
                       'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36',
                       'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:17.0) Gecko/20100101 Firefox/17.0.6',
                       'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1468.0 Safari/537.36',
                       'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2224.3 Safari/537.36',
                       'Mozilla/5.0 (X11; CrOS i686 3912.101.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36'
    
    ]
    UserAgent=random.choice(user_agent_list)
    return UserAgent


headers = {
    'content-type': 'application/json',
    'user-agent': getheaders()
}


opt = webdriver.ChromeOptions()
opt.headless = True
drive = webdriver.Chrome(options=opt)
# 86044891889
# 60144115810 me
uid = "86044891889"
uri = "https://www.iesdouyin.com/share/user/"+uid
dirname = "post"#
params = {
    'user_id':uid,
    'sec_uid': '',
    'count':'21',
    'max_cursor': 0,
    'aid':'1128',
    '_signature': '0M2EpxASjXXZgf6yrkCKktDNhL',
    'dytk':'3905df2f69a6a6561a9da86e08b69e20'
}
if not os.path.exists("video"):
    os.makedirs("video")

'''获取文件的大小,结果保留两位小数，单位为MB'''
def get_FileSize(filePath):
    # filePath = unicode(filePath,'utf8')
    fsize = os.path.getsize(filePath)
    fsize = fsize/float(1024*1024)
    return round(fsize,2)


def get_dytk():
    responce =  requests.get(uri, headers=headers,timeout = 5)
    data =responce.text
    dytkstart = data.find("dytk:")
    dytkend = data.find("\n", dytkstart)
    dytk = data[dytkstart:dytkend]
    # print("dytk=",dytk)
    dytks = dytk.split(":")
    print ("dytk===",dytks[1])
    params["dytk"] = dytks[1]
    

    
def getsign():
    try:

        responce =  requests.get(uri, headers=headers,timeout = 5)
        dy_src =responce.text
        tac_start = dy_src.find("tac=")
        tac_end = dy_src.find("</script>", tac_start)
        tac = dy_src[tac_start:tac_end]
            #print("获取到的tac:", tac)
        f = open("./tac.js", "w")
        f.write(tac)
        f.close()
        responce.close()
        drive.get("file:///E:/github/PythonStudy/douyin/get_sign.html")
        sign = drive.find_element_by_xpath("/html/body").text
        return sign
    except Exception as e:
        return None

def downFileFromDic(data,index):

    if index>len(data)-1:
        return 
    # print("downFileFromDic",data[index])
    name = data[index]["name"]
    url = data[index]["url"]
    aweme_id = data[index]["aweme_id"]
    name = name.replace("\n", "")
    # print("name=",name)
    if os.path.exists(name) and get_FileSize(name)!=0:
        printYellow("exists---"+aweme_id)
        index = index+1
        downFileFromDic(data,index)
        return
    print("StartDown--",url)
    with open(name,"wb") as f:
        try:
            # print("Start down===",url)
            responce = requests.get(url,headers = headers1, timeout = 5)
            f.write(responce.content)
            responce.close()
            s = requests.session()
            s.keep_alive = False
            index = index+1
            f.close()
            downFileFromDic(data,index)
            printGreen("Save Success---"+url)
        except Exception as e:
            f.close()
            printRed("downFile error---"+url)
            downFileFromDic(data,index)

def getPost(max_cursor,sign):
    with open(uid+"post_max_cursor","w") as f:
        f.write(str(max_cursor))
        f.close()
    params["max_cursor"] = max_cursor
    if sign==None:
        tempsign = getsign()
        if tempsign!=None:
            params["_signature"] = tempsign
    # print("getLike--",sign)
    try:
        response = requests.get('https://www.iesdouyin.com/web/api/v2/aweme/post/',timeout = 5, headers=headers, params=params)
    except Exception as e:
        getPost(max_cursor,None)
        return 
    # print("response===",response.text)
    jsonData = json.loads(response.text)
    Data = json.loads(response.text)
    DownDic = []
    aweme_list = Data["aweme_list"]
    has_more = Data["has_more"]
    
    if len(aweme_list)==0:
        getPost(max_cursor,getsign())
        return
    for data in aweme_list:
        desc = data["desc"]
        Id = data["aweme_id"]
        desc = re.sub('[\/:*?"<>|]','-',desc)#去掉非法字符   #只要字符串中的中文，字母，数字
        # print("id==",Id)
        path = "video/"+uid+"/"+dirname
        if not os.path.exists(path):
            os.makedirs(path)
        name = path+"/"+Id+desc+".mp4"#data["desc"]
        downurl = data["video"]["download_addr"]["url_list"][0]
        downurl = downurl.replace("play","playwm")

        DownDic.append({"name":name,"url":downurl,"aweme_id":Id})

    downFileFromDic(DownDic,0)
    print("has_more==",has_more)
    if has_more==True:
        time.sleep(0.5)
        getPost(Data["max_cursor"],sign)
    else:
        return

def getLike(max_cursor,sign):
    with open(uid+"like_max_cursor","w") as f:
        f.write(str(max_cursor))
        f.close()
    params["max_cursor"] = max_cursor
    if sign==None:
        tempsign = getsign()
        if tempsign!=None:
            params["_signature"] = tempsign

    try:
        response = requests.get('https://www.iesdouyin.com/web/api/v2/aweme/like/',timeout = 5, headers=headers, params=params)
    except Exception as e:
        getLike(max_cursor,None)
        return 

    jsonData = json.loads(response.text)
    Data = json.loads(response.text)
    DownDic = []
    aweme_list = Data["aweme_list"]
    has_more = Data["has_more"]
    # print("aweme_list-----",len(aweme_list))
    if len(aweme_list)==0:
        getLike(max_cursor,getsign())
        return
    for data in aweme_list:
        # print("data-----",data)
        desc = data["desc"]
        Id = data["aweme_id"]
        desc = re.sub('[\/:*?"<>|]','-',desc)#去掉非法字符   #只要字符串中的中文，字母，数字
       
        path = "video/"+uid+"/"+dirname
        if not os.path.exists(path):
            os.makedirs(path)

        name = path+"/"+Id+desc+".mp4"#data["desc"]
        downurl = data["video"]["download_addr"]["url_list"][0]
        downurl = downurl.replace("play","playwm")
        DownDic.append({"name":name,"url":downurl,"aweme_id":Id})
        
    downFileFromDic(DownDic,0)
    print("has_more==",has_more)
    if has_more==True:
        time.sleep(0.5)
        getLike(Data["max_cursor"],sign)
    else:
        getLike(Data["max_cursor"],None)
        return
# '''
get_dytk()
if len(sys.argv)==1:
    print("input douyin id")
else:
    uid = sys.argv[1]
    print("get douyin=="+uid)
    params["user_id"] = uid
    uri = "https://www.iesdouyin.com/share/user/"+uid
    # print uri
    # print sys.argv[2],type(sys.argv[2])
    if int(sys.argv[2]) == 1:#post
        dirname = "post"
        print("getPost")
        start = 0
        path = uid+"post_max_cursor"
        if os.path.exists(path):
            with open(path,"r") as f:
                start = f.read()
        getPost(start,None)
    else:
        dirname = "like"
        print("getlike")
        start = 0
        path = uid+"like_max_cursor"
        if os.path.exists(path):
            with open(path,"r") as f:
                start = f.read()
        getLike(start,None)
# '''
    


os.system("pause")

