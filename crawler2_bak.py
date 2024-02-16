import time
import sys
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
from selenium.webdriver.common.by import By
import chromedriver_autoinstaller
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import html2md 

def save_file(md, title="bbbb", o='w'):
    with open(f'C:\work\lloydk\PSou\ia_crawler\pages_2\{title}.markdown', o, encoding='utf-8') as file:
        file.write(md)
        
chromedriver_autoinstaller.install()
driver = webdriver.Chrome()

soup_t = BeautifulSoup('', 'html.parser')

t2_urls={}
t2_urls['_']=' '

title="_"

for title in t2_urls:
    driver.get(t2_urls[title]); 
    driver.set_window_size(1300, 806)
    
    time.sleep(0.5)
    clicks1 = driver.find_elements(By.CSS_SELECTOR, '.left-menu-depth1-item a')
    num_clicks1 = len(clicks1)
    print(num_clicks1)
    for element in clicks1:
        print(f'Text: {element.text}, HREF: {element.get_attribute("href")}')

    soup_t = BeautifulSoup('', 'html.parser')

    for i in range(num_clicks1):
        try:
            click1 = driver.find_elements(By.CSS_SELECTOR, '.left-menu-depth1-item a')[i]
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", click1) 
            #창 크기 조절하거나 요소 보이게 스크롤 내리면 에러남... 
            time.sleep(0.3)  
            print(click1.text)
            click1.click()
            time.sleep(0.3)  
            html = driver.page_source
            soup_a = BeautifulSoup(html, 'html.parser')
            h3 = soup_a.find('h3')
            contents=soup_a.find(class_='sub-contents')
            soup_t.append(h3); soup_t.append(contents)
            
            if contents:
                nav_bar=contents.find('nav')
                if nav_bar:
                    a_tags=nav_bar.find_all('a')
                    del a_tags[0]
                    for a in a_tags:
                        if a['href'] != '#' :
                            driver.get('https://www.airport.kr/'+a['href'])
                            time.sleep(0.3)
                            html = driver.page_source
                            soup_aa = BeautifulSoup(html, 'html.parser').find(class_='sub-contents')
                            soup_aa.find('h4').decompose()
                            soup_aa.find('nav').decompose()
                            soup_t.append(soup_aa)
                            links=soup_aa.find_all('a', class_='tab-nav-list-link')
                            for link in links:
                                if link['href'] != '#' :
                                    driver.get('https://www.airport.kr/'+link['href'])
                                    time.sleep(0.5)
                                    html = driver.page_source
                                    soup_aaa = BeautifulSoup(html, 'html.parser').find(class_='sub-contents')
                                    dd=soup_aaa.find_all('nav')
                                    for d in dd:
                                        d.decompose()
                                    soup_t.append(soup_aaa)

        except Exception as e:
            print('err1', e)
            print(click1.text)

html2md.del_com_tags(soup_t)
html2md.parse_info(soup_t)
html2md.remove_href(soup_t)
html2md.parse_href(soup_t)
md=html2md.get_markdown(soup_t)
save_file(md)



