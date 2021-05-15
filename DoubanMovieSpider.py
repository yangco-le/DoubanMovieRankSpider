#!/usr/bin/env python
# coding: utf-8

# In[122]:


import sys
import importlib
import time
import urllib
import urllib.request as urllib2
import requests
import numpy as np
from bs4 import BeautifulSoup
from openpyxl import Workbook
import csv


# In[113]:


# 请求头，模拟浏览器请求
hds=[{'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'},{'User-Agent':'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.12 Safari/535.11'},{'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)'}]


# In[114]:


# 对于电影详细页的数据，多为原始文本信息，没有标签，因此转成列表的形式做处理
# 本函数从列表中提取query_text提示的信息
def getctx(list, query_text):
    # 查询信息在列表中的位置
    idx = list.index(query_text) + 1
    string = ""
    # \n表示结束，在结束之前所有信息拼接到string中
    while list[idx] != '\n':
        string += list[idx] + " "
        idx += 1
    return string


# In[115]:


# 对列表进行预处理，过滤列表中的无用字符
def preprocess(list):
    while ': ' in list:
        list.remove(': ')
    while ' / ' in list:
        list.remove(' / ')
    while ' ' in list:
        list.remove(' ')
    return list


# In[125]:


# 将数据保存至excel文件
def print_excel(list):
    wb=Workbook()
    ws=wb.active
    ws.title = "豆瓣电影榜单"
    ws.append(['电影名','评分','导演','类型','地区','语言', '上映时间'])
    count=1
    for item in list:
        ws.append(item)
        count+=1
    save_path = '豆瓣电影榜单.xlsx'
    wb.save(save_path)

# 将数据保存至csv文件
def print_csv(list):
    header = ['电影名','评分','导演','类型','地区','语言', '上映时间']

    with open('豆瓣电影榜单.csv','w')as f:
        f_csv = csv.writer(f)
        f_csv.writerow(header)
        f_csv.writerows(list)


# In[117]:


# 爬虫主函数
def movie_spider():
    page_num=0; # 页数
    movie_list=[] # 爬取的电影信息
    try_times=0 # 尝试次数
    
    while(True):
        # 形成每页的url
        url='https://movie.douban.com/top250?start=' + str(page_num * 25) + '&filter='
        # 防止请求太多频繁导致ip封禁
        time.sleep(np.random.rand()*5)
        
        # 获取url下的信息
        try:
            req = urllib2.Request(url, headers=hds[page_num%len(hds)])
            source_code = urllib2.urlopen(req).read().decode()
            plain_text=str(source_code)
        except (urllib2.HTTPError, urllib2.URLError) as e:
            print(e)
            continue
        
        # 查找指定标签下的数据
        soup = BeautifulSoup(plain_text)
        list_soup = soup.findAll('div', {'class': 'hd'})
        
        # 对访问情况进行管理控制
        try_times+=1;
        if list_soup==None and try_times<200:
            continue
        elif list_soup==None or len(list_soup)<=1:
            break
            
        # 对每一项查到的数据，获取其中包含的超链接，再次进行访问，再对第二个页面进行解析
        for movie_info in list_soup:
            # 找到该电影详细信息的url，获取详细信息
            url2 = movie_info.find('a').attrs['href']
            detailreq = urllib2.Request(url2, headers=hds[page_num%len(hds)])
            detail = urllib2.urlopen(detailreq).read().decode()
            detail_text=str(detail)
            detail_soup = BeautifulSoup(detail_text)

            # 找到需要信息的所在位置
            content = detail_soup.find('div', {'id': 'content'})
            info = content.find('div', {'id': 'info'})
            # 由于信息是纯文本信息，没有标签可以查找，整理成list做处理
            infolist = info.find_all(text=True)
            infolist = preprocess(infolist)
            rate = content.find('div', {'class': 'rating_self clearfix'})
            
            try:
                title = content.h1.span.string.strip() # 标题
            except:
                title = "暂无"
            try: 
                director = info.find('span', {'class': 'attrs'}).string.strip() # 导演
            except:
                director = "暂无"
            try:
                type = getctx(infolist, '类型:') # 类型
            except:
                type = "暂无"
            try:
                area = getctx(infolist, '制片国家/地区:') # 地区
            except:
                area = "暂无"
            try:
                lang = getctx(infolist, '语言:') # 语言
            except:
                lang = "暂无"
            try:
                releasetime = getctx(infolist, '上映日期:') # 上映日期
            except:
                releasetime = "暂无"
            try:
                rate = rate.strong.string # 评分
            except:
                rate = "暂无"
                
            # 添加到列表
            movie_list.append([title, rate, director, type, area, lang, releasetime])
            try_times=0
        
        page_num+=1 # 下一页
        if page_num >= 6:
            break
        # 提示信息
        print('Downloading Information From Page %d' % page_num)
    return movie_list


# In[118]:


# 启动爬虫
movie_list = movie_spider()


# In[89]:


# 保存数据形成csv
print_csv(movie_list)

