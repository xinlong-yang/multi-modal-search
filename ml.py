# -*- coding: utf-8 -*-
from distutils.command.build_scripts import first_line_re
from warnings import catch_warnings
import webbrowser
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import json
import requests
from selenium import webdriver  
from lxml import etree
import time
from fake_useragent import UserAgent
import random
from datetime import datetime
import bs4
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
from selenium.common.exceptions import StaleElementReferenceException

class ML:
    def __init__(self):
        self.option = webdriver.ChromeOptions()
        self.option.add_argument('--headless')  
        self.option.add_argument('--no-sandbox')
        self.option.add_argument('window-size=1920x1080')
        self.option.add_argument('--start-maximized')
        self.option.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36")
        # self.driver = webdriver.Chrome(options=self.option)
        self.top20 = ['Carnegie Mellon University', 'Stanford University', 'University of California, San Diego','University of Illinois, Urbana Champaign','University of California, Berkeley',
                        'University of Washington', 'Massachusetts Institute of Technology', 'Cornell University', 'University of Maryland, College Park',
                        'University of Pennsylvania', 'University of Texas at Austin', 'Johns Hopkins University','Columbia University',
                        'University of Michigan', 'University of Massachusetts Amherst', 'University of California, Los Angeles',
                        'Georgia Institute of Technology','New York University','Princeton University','University of Southern California', 'CMU', 'MIT',
                        "GIT", "UIUC", 'UCSD', 'UW', 'UC San Diego', 'AWS', 'Facebook', 'Google', 'Salesforce', 'ETH Zürich', 'Meta'
        ]

        self.prompts = ['multimodal','multi-modal', 'vision-language', 'VQA', 'cross-modal', 'cross modal', 'visual question answering', 'modal',  'modal alignment',  'text-to-image', 'visual-textual', 'unimodal']

    def Check_Top20(self, school1, school2):
        for top in self.top20:
            if top == school1 or top in school1:
                return True
        for top in self.top20:
            if top == school2 or top in school2:
                return True
        return False

    def check_multimodal(self, para):
        f = False
        for key_words in self.prompts:
            if para.find(key_words) != -1:
                f = True
                break
        return f

    def Get_NIPS(self, year = 2022):
        '''
            NIPS/ICML/ICLR官网内容一致，可以直接复用，year是需要爬取的年份
        '''
        url = 'https://nips.cc/Conferences/' + str(year) + '/Schedule?type=Poster'
        driver_main = webdriver.Chrome(options=self.option)
        Data = []
        driver_main.get(url)
        element = WebDriverWait(driver_main, 20).until(EC.visibility_of_all_elements_located((By.CLASS_NAME, "maincard")))

        # 循环检测
        for i in range(len(element)):
            driver_tmp = webdriver.Chrome(options=self.option)
            paper_id = element[i].get_attribute("id")[9:]
            main_url = 'https://nips.cc/Conferences/2022/Schedule?showEvent=' + str(paper_id)
            driver_tmp.get(main_url)
            main_info = WebDriverWait(driver_tmp, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'maincard')))
            # paper的主要信息
            paper_name = main_info.text.split('\n')[2].encode('latin-1').decode('unicode_escape')
            paper_author = main_info.text.split('\n')[3].encode('latin-1').decode('unicode_escape')

            # BUG 修复bug：有些poster多了一些字段，需要单独处理
            if 'Session' in paper_author:
                paper_author = main_info.text.split('\n')[4].encode('latin-1').decode('unicode_escape')

            author_cnt = len(paper_author.split('·'))
            abstract = WebDriverWait(driver_tmp, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "abstractContainer"))).text.encode('latin-1').decode('unicode_escape')
            # 获取作者编号
            author_id = driver_tmp.find_elements_by_class_name("btn")
            first_author = author_id[-1-author_cnt].get_attribute("onclick")
            last_author = author_id[-2].get_attribute("onclick")
            first_author = first_author[first_author.find('(') + 2:first_author.find(')') - 1]
            last_author = last_author[last_author.find('(') + 2:last_author.find(')') - 1]

            # 接下来获取作者单位，主要是一作和通讯的单位
            address_url1 = 'https://nips.cc/Conferences/2022/Schedule?showSpeaker=' + str(first_author)
            driver_tmp.get(address_url1)
            school1 = driver_tmp.find_element_by_class_name("maincard").text.split('\n')

            # BUG 修复bug：有些作者没有单位，则直接跳过下一个循环
            if len(school1) == 1: # 没写单位，直接跳过
                continue
            else:
                school1 = school1[1].encode('latin-1').decode('unicode_escape')
            address_url2 = 'https://nips.cc/Conferences/2022/Schedule?showSpeaker=' + str(last_author)
            driver_tmp.get(address_url2)
            school2 = driver_tmp.find_element_by_class_name("maincard").text.split('\n')

            if len(school2) == 1:
                continue
            else:
                school2 = school2[1].encode('latin-1').decode('unicode_escape')

            print(i, paper_name, school1, school2)
            
            # 仅仅保存符合要求的paper
            if self.check_multimodal(abstract) and self.Check_Top20(school1, school2):
                print(i, paper_name)
                Data.append({'Conference':"NIPS",'Name':paper_name, 'Author':paper_author, 'School':school2, 'abstract':abstract})
            # 关闭
            driver_tmp.quit()
        df = pd.DataFrame(Data,columns=['Conference','Name','Author','School','abstract'])
        path = '/root/spider_yxl/multi-modal-search/nips2022.csv'
        driver_main.quit()
        df.to_csv(path)

    def Get_ICML(self, year = 2022):
        '''
            NIPS/ICML/ICLR官网内容一致，可以直接复用，year是需要爬取的年份
        '''
        url = 'https://icml.cc/Conferences/' + str(year) + '/Schedule?type=Poster'
        driver_main = webdriver.Chrome(options=self.option)
        Data = []
        driver_main.get(url)
        element = WebDriverWait(driver_main, 20).until(EC.visibility_of_all_elements_located((By.CLASS_NAME, "maincard")))

        # 循环检测
        print("paper number: ", len(element))
        for i in range(len(element)):
            driver_tmp = webdriver.Chrome(options=self.option)
            paper_id = element[i].get_attribute("id")[9:]
            main_url = 'https://icml.cc/Conferences/2022/Schedule?showEvent=' + str(paper_id)
            driver_tmp.get(main_url)
            main_info = WebDriverWait(driver_tmp, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'maincard')))
            # paper的主要信息
            paper_name = main_info.text.split('\n')[2]
            paper_author = main_info.text.split('\n')[3]

            # BUG 修复bug：有些poster多了一些字段，需要单独处理
            if 'Session' in paper_author:
                paper_author = main_info.text.split('\n')[4]

            author_cnt = len(paper_author.split('·'))
            abstract = WebDriverWait(driver_tmp, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "abstractContainer"))).text
            # 获取作者编号
            author_id = driver_tmp.find_elements_by_class_name("btn")
            first_author = author_id[-1-author_cnt].get_attribute("onclick")
            last_author = author_id[-2].get_attribute("onclick")
            first_author = first_author[first_author.find('(') + 2:first_author.find(')') - 1]
            last_author = last_author[last_author.find('(') + 2:last_author.find(')') - 1]

            # 接下来获取作者单位，主要是一作和通讯的单位
            address_url1 = 'https://icml.cc/Conferences/2022/Schedule?showSpeaker=' + str(first_author)
            driver_tmp.get(address_url1)
            school1 = driver_tmp.find_element_by_class_name("maincard").text.split('\n')

            # BUG 修复bug：有些作者没有单位，则直接跳过下一个循环
            if len(school1) == 1: # 没写单位，直接跳过
                continue
            else:
                school1 = school1[1]
            address_url2 = 'https://icml.cc/Conferences/2022/Schedule?showSpeaker=' + str(last_author)
            driver_tmp.get(address_url2)
            school2 = driver_tmp.find_element_by_class_name("maincard").text.split('\n')
            
            if len(school2) == 1:
                continue
            else:
                school2 = school2[1]

            print(i, paper_name, school1, school2)
            
            # 仅仅保存符合要求的paper
            if self.check_multimodal(abstract) and self.Check_Top20(school1, school2):
                print(i, paper_name)
                Data.append({'Conference':"ICML",'Name':paper_name, 'Author':paper_author, 'School':school2, 'abstract':abstract})
            # 关闭
            driver_tmp.quit()
        df = pd.DataFrame(Data,columns=['Conference','Name','Author','School','abstract'])
        path = '/root/spider_yxl/multi-modal-search/icml2022.csv'
        driver_main.quit()
        df.to_csv(path)


    def Get_ICLR(self, year = 2022):
        '''
            NIPS/ICML/ICLR官网内容一致，可以直接复用，year是需要爬取的年份
        '''
        url = 'https://iclr.cc/Conferences/' + str(year) + '/Schedule?type=Poster'
        driver_main = webdriver.Chrome(options=self.option)
        Data = []
        driver_main.get(url)
        element = WebDriverWait(driver_main, 20).until(EC.visibility_of_all_elements_located((By.CLASS_NAME, "maincard")))

        # 循环检测
        print("paper number: ", len(element))
        for i in range(len(element)):
            driver_tmp = webdriver.Chrome(options=self.option)
            paper_id = element[i].get_attribute("id")[9:]
            main_url = 'https://iclr.cc/Conferences/2022/Schedule?showEvent=' + str(paper_id)
            driver_tmp.get(main_url)
            main_info = WebDriverWait(driver_tmp, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'maincard')))
            # paper的主要信息
            paper_name = main_info.text.split('\n')[2]
            paper_author = main_info.text.split('\n')[3]

            # BUG 修复bug：有些poster多了一些字段，需要单独处理
            if 'Session' in paper_author:
                paper_author = main_info.text.split('\n')[4]

            author_cnt = len(paper_author.split('·'))
            abstract = WebDriverWait(driver_tmp, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "abstractContainer"))).text
            # 获取作者编号
            author_id = driver_tmp.find_elements_by_class_name("btn")
            first_author = author_id[-1-author_cnt].get_attribute("onclick")
            last_author = author_id[-2].get_attribute("onclick")
            first_author = first_author[first_author.find('(') + 2:first_author.find(')') - 1]
            last_author = last_author[last_author.find('(') + 2:last_author.find(')') - 1]

            # 接下来获取作者单位，主要是一作和通讯的单位
            address_url1 = 'https://iclr.cc/Conferences/2022/Schedule?showSpeaker=' + str(first_author)
            driver_tmp.get(address_url1)
            school1 = driver_tmp.find_element_by_class_name("maincard").text.split('\n')

            # BUG 修复bug：有些作者没有单位，则直接跳过下一个循环
            if len(school1) == 1: # 没写单位，直接跳过
                continue
            else:
                school1 = school1[1]
            address_url2 = 'https://iclr.cc/Conferences/2022/Schedule?showSpeaker=' + str(last_author)
            driver_tmp.get(address_url2)
            school2 = driver_tmp.find_element_by_class_name("maincard").text.split('\n')
            
            if len(school2) == 1:
                continue
            else:
                school2 = school2[1]

            print(i, paper_name, school1, school2)
            
            # 仅仅保存符合要求的paper
            if self.check_multimodal(abstract) and self.Check_Top20(school1, school2):
                print(i, paper_name)
                Data.append({'Conference':"ICLR",'Name':paper_name, 'Author':paper_author, 'School':school2, 'abstract':abstract})
            # 关闭
            driver_tmp.quit()
        df = pd.DataFrame(Data,columns=['Conference','Name','Author','School','abstract'])
        path = '/root/spider_yxl/multi-modal-search/iclr2022.csv'
        driver_main.quit()
        df.to_csv(path)


class ACL:
    def __init__(self):
        self.option = webdriver.ChromeOptions()
        self.option.add_argument('--headless')  
        self.option.add_argument('--no-sandbox')
        self.option.add_argument('window-size=1920x1080')
        self.option.add_argument('--start-maximized')
        self.option.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36")
        # self.driver = webdriver.Chrome(options=self.option)
        self.top20 = ['Carnegie Mellon University', 'Stanford University', 'University of California, San Diego','University of Illinois, Urbana Champaign','University of California, Berkeley',
                        'University of Washington', 'Massachusetts Institute of Technology', 'Cornell University', 'University of Maryland, College Park',
                        'University of Pennsylvania', 'University of Texas at Austin', 'Johns Hopkins University','Columbia University',
                        'University of Michigan', 'University of Massachusetts Amherst', 'University of California, Los Angeles',
                        'Georgia Institute of Technology','New York University','Princeton University','University of Southern California', 'CMU', 'MIT',
                        "GIT", "UIUC", 'UCSD', 'UW', 'UC San Diego', 'AWS', 'Facebook', 'Google', 'Salesforce', 'ETH Zürich', 'Meta'
        ]

        self.prompts = ['multimodal','multi-modal', 'vision-language', 'VQA', 'cross-modal', 'cross modal', 'visual question answering', 'modal',  'modal alignment',  'text-to-image', 'visual-textual', 'unimodal']

    def Check_Top20(self, school1, school2):
        for top in self.top20:
            if top == school1 or top in school1:
                return True
        for top in self.top20:
            if top == school2 or top in school2:
                return True
        return False

    def check_multimodal(self, para):
        f = False
        for key_words in self.prompts:
            if para.find(key_words) != -1:
                f = True
                break
        return f

    def Get_ACL(self, year = 2022):
        long_paper_num = 604
        Data = []
        web_driver = webdriver.Chrome(options=self.option)
        for i in range(1,long_paper_num):
            url = 'https://aclanthology.org/2022.acl-long.' + str(i) + '/'
            # print(url)
            web_driver.get(url)
            paper_author = web_driver.find_element_by_class_name("lead").text
            abstract = web_driver.find_element_by_class_name("card-body").text.split('\n')[1]
            paper_name = web_driver.find_element_by_id('citeRichText').text
            print(i, paper_name)
            if self.check_multimodal(abstract):
                Data.append({'Conference':"ACL",'Name':paper_name, 'Author':paper_author, 'abstract':abstract})
            # 关闭
        df = pd.DataFrame(Data,columns=['Conference','Name','Author','abstract'])
        path = '/root/spider_yxl/multi-modal-search/acl2022.csv'
        df.to_csv(path)




class CVPR:
    def __init__(self):
        self.option = webdriver.ChromeOptions()
        self.option.add_argument('--headless')  
        self.option.add_argument('--no-sandbox')
        self.option.add_argument('window-size=1920x1080')
        self.option.add_argument('--start-maximized')
        self.option.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36")
        # self.driver = webdriver.Chrome(options=self.option)

        self.top20 = ['Carnegie Mellon University', 'Stanford University', 'University of California, San Diego','University of Illinois, Urbana Champaign','University of California, Berkeley',
                        'University of Washington', 'Massachusetts Institute of Technology', 'Cornell University', 'University of Maryland, College Park',
                        'University of Pennsylvania', 'University of Texas at Austin', 'Johns Hopkins University','Columbia University',
                        'University of Michigan', 'University of Massachusetts Amherst', 'University of California, Los Angeles',
                        'Georgia Institute of Technology','New York University','Princeton University','University of Southern California', 'CMU', 'MIT',
                        "GIT", "UIUC", 'UCSD', 'UW', 'UC San Diego', 'AWS', 'Facebook', 'Google', 'Salesforce', 'ETH Zürich', 'Meta'
        ]

        self.prompts = ['multimodal','multi-modal', 'vision-language', 'VQA', 'cross-modal', 'cross modal', 'visual question answering', 'modal',  'modal alignment',  'text-to-image', 'visual-textual', 'unimodal']


    def Check_Top20(self, school1, school2):
        for top in self.top20:
            if top == school1 or top in school1:
                return True
        for top in self.top20:
            if top == school2 or top in school2:
                return True
        return False


    def check_multimodal(self, para):
        f = False
        for key_words in self.prompts:
            if para.find(key_words) != -1:
                f = True
                break
        return f

    def Get_CVPR(self, year = 2022):
        # 先爬作者信息，如果是top20的再去详细页面爬abstract
        main_url = 'https://cvpr2023.thecvf.com/Conferences/2023/AcceptedPapers'
        web_driver = webdriver.Chrome(options=self.option)
        web_driver.get(main_url)
        Table_info = web_driver.find_elements_by_tag_name("td")
        Data = []
        # print(len(Table_info))
        for i in range(2,len(Table_info),3):
            driver_tmp = webdriver.Chrome(options=self.option)
            td = Table_info[i]
            paper_name = td.text.split('\n')[0]
            paper_name = paper_name[:paper_name.find('Poster Session')]
            paper_author = td.text.split('\n')[1].split('·')
            school1 = str(paper_author[0])
            school1 = school1[school1.find('(') + 1: school1.find(')')]
            school2 = str(paper_author[-1])
            school2 = school2[school2.find('(') + 1: school2.find(')')]

            if self.Check_Top20(school1,school2):
                print(paper_name)
                atr = str(paper_name).replace(":", '').strip().split(' ')
                process_papername = atr[0]
                for i in range(1,len(atr)):
                    process_papername = process_papername + '_' + atr[i]
                author_tmp = str(paper_author[0])
                author_tmp = author_tmp[:author_tmp.find('(')].strip()
                abstact_url = 'https://openaccess.thecvf.com/content/CVPR2023/html/' + author_tmp.split(' ')[-1] + '_' + process_papername + '_CVPR_2023_paper.html'
                print(paper_name, school1, school2, abstact_url)
                abstact_url = abstact_url.replace('&','')
                try:
                    driver_tmp.get(abstact_url)
                    abstract = str(driver_tmp.find_element_by_id('abstract').text)
                    if self.check_multimodal(abstract):
                        Data.append({'Conference':"CVPR",'Name':paper_name, 'Author':paper_author, 'School':school2, 'abstract':abstract})
                except:
                    continue
                # 获取abstract
            # 关闭
            driver_tmp.quit()
        df = pd.DataFrame(Data,columns=['Conference','Name','Author','School','abstract'])
        path = '/root/spider_yxl/multi-modal-search/cvpr2022.csv'
        df.to_csv(path)
        web_driver.quit()







if __name__ == '__main__':
    # setting encoding
    reload(sys)
    sys.setdefaultencoding('utf-8')

    # ml = ML()
    # ml.Get_ICML()
    cvpr = CVPR()
    cvpr.Get_CVPR()
