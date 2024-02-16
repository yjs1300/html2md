# @ des: gpts rag data 
# @ created by: 윤지수
# @ updated: 2024.02

# 시스템 메모리 확인
# import psutil
# mem = psutil.virtual_memory()
# print(f"Total memory: {mem.total / (1024 ** 3):.2f} GB") #Total memory: 15.72 GB
# print(f"Available memory: {mem.available / (1024 ** 3):.2f} GB") #Available memory: 7.16 GB

import time
import sys

from selenium import webdriver
from selenium.webdriver.common.by import By
import chromedriver_autoinstaller
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re

from html2md import *
    
def save_file(soup, title, o='w'):
    with open(f'C:\work\lloydk\PSou\ia_crawler\pages_2\{title}.markdown', o, encoding='utf-8') as file:
        file.write(get_markdown(soup))

#depth2인 카테고리 페이지 저장
def scrap_d2(soup, title, m_t_step, ajax=False):
    
    #depth가 2인 페이지 내의 ajax/javascript 요소 {상위제목 : 요소}
    ajax_css1={"취항 도시":'.local-list-item'}; ajax_css2={"취항 도시":'.local-town-item'}
    #depth가 2인 페이지 내의 하위 페이지 
    depth3_t={"-":["제2여객터미널"], "-":["검역"]} #{상위페이지 제목:[{페이지 제목},...]}
 
    #하위 페이지 포함한 제목 생성, url 가져오기
    t2_urls=parse_d2_title(soup, title, 3) 

    print(len(t2_urls))
    print(t2_urls)

    #하하위 페이지 있으면 url&제목 반환
    t3_urls=[]
    
    #하위 페이지 붙이기---
    if ajax : #요소가 ajax 
        soup_a=crawl_ajax(t2_urls, ajax_css1, ajax_css2)
        #depth 추가
        add_depth(soup_a, m_t_step)
        for title2 in t2_urls :
            soup.select_one(".m_title_1").append(soup_a)  
    
    else : #요소가 page
        for title2 in t2_urls :
            print(t2_urls[title2])
            #페이지 이동 후 스크래핑
            driver.get(t2_urls[title2])
            html=driver.page_source
            soup_d2=BeautifulSoup(html, 'html.parser')
            
            #추가할 페이지 depth 추가
            add_depth(soup_d2, m_t_step)
            print(title2)
            #하위 페이지가 더 있으면 url 반환 
            for i, title3 in enumerate(depth3_t):
                if title3 in title2 :
                    print(depth3_t[title3][0])
                    t3_urls.append(parse_d3_title(soup_d2, depth3_t[title3][0], 4))

            #.m_title_i_j 밑에 내용 붙이기
            i, j = re.findall(r'_(\d+)', title2)
            soup.select_one(f".m_title_{i}_{j}").append(soup_d2) #append 후 soup_d2 제거됨
        
    del_com_tags(soup)
    return t3_urls


#하위 페이지 포함할 제목 생성
def parse_d2_title(soup, title, t_size=3):
    # 상위 페이지의 제목 요소
    d2_title_css={"터미널 안내":r'^boxmodel-list-head.*', "맞춤형 서비스":r'^boxmodel-list-item-inner.*'}
    #하위페이지 제목:링크
    t2_urls = {}

    title_tags = soup.find_all('div', class_=re.compile(d2_title_css[title]))
    print(title_tags)

    if title == '터미널 안내' :
        for i, t in enumerate(title_tags): 
            #기존 제목 삭제 후 새 제목 추가
            new_tag1=soup.new_tag('p')
            new_tag1['class'] = f'm_title_{i}'
            #div1=t.find('div').extract() ; span1=t.find('span').extract() 
            new_tag1.string='#'*t_size + ' '+ t.get_text(strip=True)

            #하위 url 가져오기
            d2_urls = t.parent.find_all('a', href=True)
            for j, url in enumerate(d2_urls):
                new_tag=soup.new_tag('p')
                new_tag['class'] = f'm_title_{i}_{j}'
                t2_urls[t.get_text(strip=True) +'_'+ url.get_text(strip=True)+f"_{i}_{j}"]='https://www.airport.kr'+url['href']
                url.insert_before(new_tag)
                
            t.string=new_tag1.string
        
            # del t2_urls["교통약자 주차 서비스_자세히 보기_4_0"]
            # t2_urls['주차장 안내_예약주차장_0_2']= 'https://parking.airport.kr/reserve'
            # t2_urls["주차장 혼잡도_제1여객터미널_2_0"]="https://www.airport.kr/ap/ko/tpt/parkingPlaceInfo.do"
            # t2_urls["주차장 혼잡도_제2여객터미널_2_1"]="https://www.airport.kr/ap/ko/tpt/getParkingPlaceInfoT2Short.do"
          
    elif title == '맞춤형 서비스' :
        for i, t in enumerate(title_tags): 
            #기존 제목 삭제 후 새 제목 추가
            new_tag=soup.new_tag('p')
            new_tag['class'] = f'm_title_{i}'
            #div1=t.find('div').extract() ; span1=t.find('span').extract()
            div1=t.find('div') ; span1=t.find('span')
            new_tag.string='#'*t_size + ' ' + span1.get_text(strip=True) + ' '+ div1.get_text(strip=True)
            t.insert(0, new_tag)

            #하위 url 가져오기
            d2_urls = t.find_all('a', href=True)
            for j, url in enumerate(d2_urls):
                new_tag=soup.new_tag('p')
                new_tag['class'] = f'm_title_{i}_{j}'
                t2_urls[div1.get_text(strip=True) +'_'+ url.get_text(strip=True)+f"_{i}_{j}"]='https://www.airport.kr'+url['href']
                # print('parent',url.parent)
                url.insert_before(new_tag)
                # print('----',url.parent)
        
            div1.decompose(); span1.decompose(); 

    return t2_urls

def crawl_ajax(t2_urls, title, ajax_css1={}, ajax_css2={}):
    
    #ajax 요소 클릭, 가져와 붙이기
    driver.get(t2_urls[title])

    clicks1 = driver.find_elements(By.CSS_SELECTOR, ajax_css1)
    
    soup_t=BeautifulSoup('','html.parser')
    
    for click1 in clicks1:
        id=click1.get_attribute('id')
        pattern = re.compile(r'([A-Z])')
        match = pattern.search(id).group()
        
        # print(id, match)
        click1.click(); time.sleep(0.2)
        clicks2 = driver.find_elements(By.CSS_SELECTOR,f'[id^="s_{match}"]')
        # print(len(clicks2))
        for click2 in clicks2:
            click2.click(); time.sleep(0.2)
            html=driver.page_source
            soup_a=BeautifulSoup(html, 'html.parser')
            soup_t.append(soup_a)
  
    return soup_t

def scrap_d3(soup2, soup3, t3):
    if '제2여객터미널' in t3:
        i= re.findall(r'_(\d+)', t3)

        #상위 페이지에 추가할 내용
        select_content='.article'

        soup3='\n'.join([str(tag) for tag in soup3.select(select_content)[-3:]])
        soup3=BeautifulSoup(soup3,'html.parser')

        add_depth(soup3,4)
        
        #추가할 페이지 depth 추가
        soup2.select_one(f".s_title_{i[0]}").append(soup3)  
        del_com_tags(soup2)
    elif '검역' in t3:
        i= re.findall(r'_(\d+)', t3)

        #상위 페이지에 추가할 내용
        select_content='.article'

        soup3='\n'.join([str(tag) for tag in soup3.select(select_content)])
        soup3=BeautifulSoup(soup3,'html.parser')

        add_depth(soup3,4)
        
        #추가할 페이지 depth 추가
        soup2.select_one(f".s_title_{i[0]}").append(soup3)  
        del_com_tags(soup2)

def parse_d3_title(soup, title, t_size=4):
    # 상위 페이지의 제목 요소
    d3_title_css={"제2여객터미널":'.tab-nav-list-item', 
                  "서울 심야버스":'.btn-type-tab'}
    t3_urls = {}

    if title in '제2여객터미널' :
        title_tags = soup.select(d3_title_css['제2여객터미널'])
        for i, t in enumerate(title_tags): 
            #기존 소제목 삭제 후 추가
            new_tag=soup.new_tag('p')
            a1=t.find('a')
            new_tag.string='#'*t_size + ' ' + a1.get_text(strip=True)

            if i == 0: #제1여객터미널
                #소제목과 하위 내용 같은 상위태그로
                new_tag['class'] = f's_title'
                t.insert(0, new_tag) 
                a1.decompose()
                contents=t.find("div", id_="top-contents").extract()
                t.insert(1, contents) 
            elif i == 1 : #하위 링크 #제2여객터미널
                new_tag['class'] = f's_title_1'
                t.insert(0, new_tag) 
                t3_urls[a1.get_text(strip=True)+'_1']='https://www.airport.kr'+a1['href']
                a1.decompose()
    #검역안내
    elif title in '검역' :
        print()
        title_tags = soup.select(d3_title_css['검역'])
        for i, t in enumerate(title_tags): 
            #기존 소제목 삭제 후 추가
            new_tag=soup.new_tag('p')
            a1=t.find('a')
            new_tag.string='#'*t_size + ' ' + a1.get_text(strip=True)

            if i == 0: 
                #소제목과 하위 내용 같은 상위태그로
                new_tag['class'] = f's_title'
                t.insert(0, new_tag) 
                a1.decompose()
                contents=t.parent.parent.parent.find_all("article", class_=re.compile(r"article *"))
                print('*'*30)
                for c in contents: 
                    content=c.extract()
                    print(content)
                    t.insert(1, content) 
            elif i == 1 : #하위 링크 
                new_tag['class'] = f's_title_2'
                t.insert(0, new_tag) 
                t3_urls[a1.get_text(strip=True)+'_2']='https://www.airport.kr'+a1['href']
                a1.decompose()           
            elif i == 2 : #하위 링크 
                new_tag['class'] = f's_title_3'
                t.insert(0, new_tag) 
                t3_urls[a1.get_text(strip=True)+'_3']='https://www.airport.kr'+a1['href']
                a1.decompose()       
    return t3_urls

                
if __name__ == '__main__':
    
    #페이지 정보---
    category=["출발", "도착", "환승," "교통·주차", "쇼핑·식당","안내·서비스"]
    
    depth1_p=["안내·편의시설","전시·공연·체험"] #depth1인 카테고리
    depth2_p= ["맞춤형 서비스","환승투어"] # #depth2인 카테고리
    ajax_or_js=["취항정보"] #ajax/js 상위 제목
    remove_p = ["도착시간"] #삭제 하위 카테고리
    
    #nav bar 가져오기---
    chromedriver_autoinstaller.install() #크롬 버전에 맞게 크롬 드라이버 자동 다은

    url = '' #메인페이지 
    driver = webdriver.Chrome()
    driver.get(url)  

    #Driver wait
    selector="nav .gnb-depth1 a.gnb-depth2-link"
    try: 
        WebDriverWait(driver, 2).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector)))
        # 찾고자하는 요소가 나올 때까지 최대 2초 대기
    except Exception as e:
        print("페이지 로딩 실패 \n", e)
        
    nav=driver.find_elements(By.CSS_SELECTOR, selector)
    nav_ctg={}

    #테스트 ==============
    for i in range(21, 26):
        nav_ctg[nav[i].get_attribute('text')]=nav[i].get_attribute('href')
    
    # for ctg in remove_p:
    #     del nav_ctg[ctg]

    for nav_c in nav_ctg:
        print(nav_c)
        ajax=False 
        if nav_c in ajax_or_js:
            ajax=True

        if nav_c in depth1_p: #depth 1 인 페이지 저장
            #print(nav_c)
            driver.get(nav_ctg[nav_c])
            time.sleep(2)
            html=driver.page_source
            soup1=BeautifulSoup(html,"html.parser"); 
            del_com_tags(soup1)
            parse_info(soup1, faq=True)
            del_search=soup1.find_all('div',class_=re.compile(r".*search.*"))
            for d in del_search:
                d.decompose()
            #remove_href(soup1) 
            save_file(soup1, nav_c, o='w')

        if nav_c in depth2_p: #depth 2 인 페이지 저장
            driver.get(nav_ctg[nav_c])
            html=driver.page_source
            soup2=BeautifulSoup(html,"html.parser"); #parse_info(soup2, faq=True) 
            t3_urls = scrap_d2(soup2, nav_c, 3, ajax)
                
            #depth 2 soup에 depth3 soup 붙이기
            if len(t3_urls) > 0 : 
                print(t3_urls)
                for i in range(len(t3_urls)):
                    for t3 in t3_urls[i]:
                        driver.get(t3_urls[i][t3])
                        html=driver.page_source
                        soup3=BeautifulSoup(html,"html.parser")
                        scrap_d3(soup2, soup3, t3)
                    
            #pp_faq(soup2, t3)        
            parse_info(soup2) 
            remove_href(soup2)         
            save_file(soup2, nav_c, o='w')
            
    print('끝~~~~~~')
    driver.quit()
    sys.exit()


  
