#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  9 10:33:21 2019

@author: zhaoyuanyuan
"""

import requests
from bs4 import BeautifulSoup
import re
from database import Database

class JAVLIB:

    genre_URL = 'http://www.o23g.com/cn/genres.php'
    genre_av_URL = 'http://www.o23g.com/cn/vl_genre.php?list&mode=1&g={}&page={}'
    actor_av_URL = 'http://www.o23g.com/cn/vl_star.php?list&mode=1&s={}&page={}'
    best_av_URL = 'http://www.o23g.com/cn/vl_bestrated.php?list&mode=1&page={}'
    av_URL = 'http://www.o23g.com/cn/?v={}'

    agentList = 'ChromeAgent.txt'

    def __init__(self):
        pass

    def myGet(self, url):

        headers = {
               'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
               'Cache-Control': 'max-age=0',
               'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-CA) AppleWebKit/534.13 (KHTML like Gecko) Chrome/9.0.597.98 Safari/534.13',
               'Connection': 'keep-alive',
               }
        page = requests.get(url, headers=headers)
        return BeautifulSoup(page.content)


    # 获得分类与对应id
    def getGenres(self):
        self.genresList = {}
        soup = self.myGet(self.genre_URL)
        # structure: div->div->a href
        genreitems = soup.find_all('div', 'genreitem')
        for item in genreitems:
            genre = re.search('(?<=g=)\w+', str(item)).group(0)
            text =  item.get_text()
            self.genresList[text] = genre
        print('Found %d genres' % len(genreitems))
        return self.genresList

    
    def getAVinfo(self, avcode):
        # get av info by avcode
        soup = self.myGet(self.av_URL.format(avcode))
        avinfo = {'识别码': None, '发行日期': None, '使用者评价': None, '类别': None, '演员': None}
        for want in avinfo.keys():
            iget = soup.find_all('td', text=re.compile(want))
            if iget:
                cont = iget[0].parent.find('td', 'text').get_text('|', strip=True)
                avinfo[want] = cont
            else:
                print('[%s]%s信息未找到' % (avcode, want))

        # 拥看比
        _own = soup.find(href=re.compile('owned')).get_text()
        _look = soup.find(href=re.compile('watched')).get_text()
    
        rate_ol = 0
        if int(_look) != 0:
            rate_ol = int(_own) / int(_look)
        avinfo['拥看比'] = round(rate_ol, 2)

        # optimize
        if avinfo['使用者评价']:
            avinfo['使用者评价'] = eval(avinfo['使用者评价'])   # !maybe good way
        elif avinfo['使用者评价'] == '':
            avinfo['使用者评价'] = None
        return avinfo
        

    def getAVbyGenre(self, genre='b4', startpage=1, endpage=1):
        # get av info from genre page
        self.AVs = {}
        for page in range(startpage, endpage+1):
            soup = self.myGet(self.genre_av_URL.format(genre, page))
            avitems = soup.find_all('div', 'video')
            for item in avitems:
                avcode = item.get('id')[4:]
                print('正在获取INFO:[%s]' % avcode)
                info = self.getAVinfo(avcode)
                self.AVs[avcode] = info
        return self.AVs

    def getAVbyActor(self, actor='afgda', startpage=1, endpage=1):
        # get av info from actor page
        self.AVs = {}
        for page in range(startpage, endpage+1):
            soup = self.myGet(self.actor_av_URL.format(actor, page))
            avitems = soup.find_all('div', 'video')
            for item in avitems:
                avcode = item.get('id')[4:]
                print('正在获取INFO:[%s]' % avcode)
                info = self.getAVinfo(avcode)
                self.AVs[avcode] = info
        return self.AVs

    def getAVbyBest(self, startpage=1, endpage=1):
        # get av info from actor page
        self.AVs = {}
        for page in range(startpage, endpage+1):
            soup = self.myGet(self.best_av_URL.format(page))
            avitems = soup.find_all('div', 'video')
            for item in avitems:
                avcode = item.get('id')[4:]
                print('正在获取INFO:[%s]' % avcode)
                info = self.getAVinfo(avcode)
                self.AVs[avcode] = info
        return self.AVs

def main():
    rob = JAVLIB()
    # rob.getGenres()
    av = rob.getAVbyGenre('lm', 1, 25)  # which data you want?
    # SAVE
    db = Database()
    db.create()
    db.insertAll(av)
    #db.getAllRank()

main()