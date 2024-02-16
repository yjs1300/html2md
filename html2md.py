from bs4 import NavigableString
import html2text
import re

#질문 만들기 
def pp_faq(soup, title=None):
    
    # 새로운 제목 p 태그 추가
    div_tag1 = soup.find_all('div', class_='board-list-head')
    div_tag2= soup.select('.boxmodel2-list-item')

    if div_tag2:
        for div_tag in div_tag2:
            #제목 태그 추가
            new_p_tag = soup.new_tag("p")
            new_p_tag.string = '---'
            div_tag.append(new_p_tag)


    elif div_tag1:
        t1='';t2=''
        
        for div_tag in div_tag1:
            
            if title not in "제한물품 FAQ": # 고객센터 - FAQ
                t_category = div_tag.find('p', class_='board-list-category')
                
                # 요소 삭제 후 제목생성
                if t_category:
                    t1=t_category.get_text(strip=True)
                    t_category.decompose()
            
            t_inner = div_tag.find(['p','span'], class_='board-list-tit-inner')
            if t_inner:
                t2=t_inner.get_text(strip=True)
                t_inner.decompose()
            
            fre_q_title='질문: '+t1+' '+t2
            
            #제목 태그 추가
            new_p_tag = soup.new_tag("p")
            new_p_tag.string = '---'
            div_tag.append(new_p_tag)
            
            new_p_tag = soup.new_tag("p")
            new_p_tag.string = fre_q_title
            div_tag.append(new_p_tag)
            
            new_p_tag = soup.new_tag("p")
            new_p_tag.string = '답변: '
            div_tag.append(new_p_tag)

# 하위 페이지 -> header depth 추가
def add_depth(soup, t_step):
     
    if t_step > 0 :
        tags = soup.find_all(re.compile('^h[1-6]$'))
        if tags:
            for tag in tags:
                
                current_level = int(tag.name[1])
                new_level = current_level + t_step
                if new_level > 6:
                    new_tag=soup.new_tag('p')
                    if tag.text:
                        new_tag.string = f'**{tag.text.strip()}**'
                        tag.replace_with(new_tag)
                        #print(tag)
                    else :
                        tag.decompose()
                else :
                    new_tag = soup.new_tag(f'h{new_level}')
                    new_tag.string = tag.text.strip()
                    tag.replace_with(new_tag)
                        
# 공통 태그 제거
def del_com_tags(soup):
    for tag in soup.select('script, form, button, select, head, header, footer, input'):
        tag.decompose()
    
    ids=['#FindMyTermiWrap', '#managementPoll', '#address-layerWrap', '#FindMyTermiWrap', 
         '#airportOnMapWrap', '#terminalMoveWrap', '#baggage', 
         '.congestion', '.main-content','.main-banner-wrap footer-graft', '.loading'] 
    for id in ids:
        del_tags =soup.select(id)
        if del_tags:
            for d in del_tags :
                d.decompose()
 
#video -> string&url 처리
def make_md_vidio(soup):
    iframes = soup.find('div', class_='include-video')
    if iframes: 
        iframes.find_all('iframe')
        for iframe in iframes:
            # iframe의 src 속성 값 추출
            try:
                src = iframe['src'] 
                title=iframe['title'] 
                iframe.clear()
                iframe.string=title + ' | ' + src
            except :
                print()

# 테이블 처리
def make_md_tabel(soup):
    table_tags = soup.find_all(['tbody'])
    if table_tags : 
        for table in table_tags:
            #row 병합테이블 처리 변수
            td_i=0 #추가 td 위치
            rowspan_count=0 #병합된 셀에서 채운 줄 수
            make_row_span=None #row가 채워졌는지 확인 flag
            max_rowspan=0 #채워야할 줄 수
        
            tr_tags = table.find_all(['tr'])
            original_tr_tags = tr_tags[:] # 복사를 위한 원본 tr 태그 리스트 생성

            for tr in original_tr_tags: 
                if make_row_span is not None :
                    rowspan_count=rowspan_count+1 
                    
                for tt in tr.find_all(['td','th']):
                    #td, th 내 줄바꿈 제거 & bold체 삭제 ---
                    new_total_span = soup.new_tag('span')
                    div_tags = tt.find_all(['div','p'])
                    s_tags=tt.find_all('strong')
                    if s_tags:
                        for s in s_tags:
                            s_parent=s.parent
                            s.insert_after(s.text); s.decompose()
                        text = s_parent.get_text().strip()
                        s_parent.string = soup.new_string(text)

                    if div_tags : 
                        for div_tag in div_tags :
                            text = div_tag.get_text().strip()  # 모든 텍스트를 가져옴
                            new_total_span.append(soup.new_string(text))
                            div_tag.decompose()
                        tt.append(new_total_span)                       
                    br_tags=tt.find_all('br')
                    if br_tags:
                        string=''
                        for br_tag in br_tags:
                            br=br_tag.extract()
                            if br.find_parent('td'):
                                lines=br.find_parent('td').get_text().split()
                                string=' '.join(line.strip() for line in lines) 
                        br_tag.append(string)
                        
                    #td, th 내 ul 처리 ---
                    ul_tags = tt.find_all('ul')
                    if ul_tags:
                        for ul in ul_tags:
                            combined_text = ' * '.join(li.get_text().strip() for li in ul.find_all('li'))
                            # 각 li 항목 사이에 줄바꿈 문자 삽입
                            combined_text = combined_text.replace('\n', ' ')
                            combined_text = "* " + combined_text
                            new_content = soup.new_string(combined_text)
                            
                            # 새로운 내용을 ul 태그 바로 앞에 삽입
                            if ul.parent:
                                ul.insert_before(new_content)
                                ul.decompose()
                            else:
                                tt.append(new_content)
                    
                    #rowspan, colspan 처리---
                    if tt.has_attr('rowspan') and int(tt['rowspan']) > 1:
                        rowspan = int(tt['rowspan'])
                        del tt['rowspan']

                        #채울 row span 계산
                        if make_row_span == None :
                            make_row_span = rowspan-1
                            rowspan_count=0 #채운 row 수
                            td_i = td_i + 1
                            
                            #최대 rowspan 계산
                            if max_rowspan < rowspan:
                                max_rowspan = rowspan 
                                td_i = td_i - 1 #td_i 0부터 시작    
                            elif max_rowspan > 0 :
                                max_rowspan = max_rowspan - rowspan
                            
                            if max_rowspan <= rowspan_count :
                                td_i = td_i - 1

                        current_tr = tt.find_parent('tr')  # 현재 td의 부모 tr 태그 
                        next_tr = current_tr.find_next_sibling('tr')  # 다음 tr 태그 
                            
                        if next_tr: #rowspan 만큼 추가
                            for r in range(rowspan - 1):
                                rowspan_count = rowspan_count+1
                                # 다음 tr 태그의 td_i번째에 td 삽입
                                new_td = soup.new_tag('td')
                                if not tt.find('a') :
                                    new_td.string = tt.get_text().strip()
                                    next_tr.insert(td_i, new_td)  
                                    next_tr=next_tr.find_next_sibling('tr') 
                        else : 
                            new_td = soup.new_tag('td')
                            new_td.string = tt.get_text().strip()
                            current_tr.insert(0, new_td)  
                        
                        #row가 채워졌는지 확인 후 flag
                        if rowspan_count >= make_row_span:
                            #print('채워짐 플래그',td_i)
                            make_row_span=None
        
                    # colspan 속성이 있는지 확인하고, 값이 2 이상인지 검사
                    if tt.has_attr('colspan') and int(tt['colspan']) > 1:
                        colspan=int(tt['colspan'])
                        del tt['colspan']
                        # 필요한 수만큼 새로운 td 태그 추가
                        for _ in range(colspan - 1):
                            new_td = soup.new_tag('td')
                            new_td.string = tt.get_text()
                            tt.insert_after(new_td)
    
# step으로 끝나는 li태그 찾기
def match_class(tag):
    if tag.name == 'li' and 'class' in tag.attrs:
        for class_name in tag['class']:
            if re.search(r'^step[1-9]', class_name):
                return True
    return False

# < 태그들 전처리 >
def parse_info(soup, faq=False, title=None):
    
    #FAQ 형식 처리
    if faq:
        pp_faq(soup, title) 
    
    #표 등 설명 제거
    for caption in soup.find_all('caption'):
        caption.decompose()   
        
    # img 태그 제거 후 alt(설명)으로 대체 ---
    for img in soup.find_all('img'):
        if not re.search(r'로고\b|모습\b|\b전경', img.get('alt', '')):
            new_tag = soup.new_tag("p")  
            new_tag.string = img['alt']  
            img.replace_with(new_tag)
            #print(new_tag)
        else:
            img.decompose()
    
    #video -> string&url 처리
    make_md_vidio(soup)
    
    # 빈 div 태그 바로 위 제목 제거
    empty_divs = [div for div in soup.find_all('div') if not div.text.strip() and not div.contents]
    for div in empty_divs:
        parent_div_h = div.parent
        if parent_div_h and (parent_div_h.name == 'div' or parent_div_h.name[0] == 'h'):
            # 상위 div 태그 삭제
            print(f"삭제 : {parent_div_h}")
            parent_div_h.decompose()
           
    make_md_tabel(soup)
        
    # ".list-article" 요소 텍스트 처리
    list_articles = soup.find_all('div', class_='list-article')
    if list_articles :
        for article in list_articles:
            new_text=article.text.split()
            new_text=' '.join(new_text)
            article.clear()  
            article.append(new_text)

    #li 태그 뒤 step으로 끝나는 li태그를 ol 태그로 바꿈
    ol_tags = soup.find_all('ol')
    for ol in ol_tags:  
        brs = ol.find_all('br')
        for br in brs:
            br.decompose()
        li_tags = ol.find_all(match_class) #^step[1-9]
        for li in li_tags:
            if 'class' in li.attrs and len(li['class']) > 1 and re.search(r'step[1-9]$', li['class'][1]):
                new_ol = soup.new_tag("ol")
                new_ol.string = li.text.strip()
                li.parent.append(new_ol)
                li.decompose()

    # dl 태그 볼드 처리 
    dl_tags = soup.find_all('dl')
    for dl in dl_tags:
        dt_tag = dl.find('dt')
        if dt_tag:
            dt_strong = soup.new_tag('strong')  
            dt_strong.string = dt_tag.text 
            dt_tag.clear() 
            dt_tag.append(dt_strong)  

        # 각 <dl> 태그 내의 <dd> 태그 처리
        dd_tag = dl.find('dd')
        if dd_tag:
            strong_tag = dd_tag.find('strong')  
            if strong_tag:
                strong_text = strong_tag.extract() 
                dd_text = dd_tag.text.strip() 
                dd_tag.clear()  
                dd_tag.append(strong_text) 
                if dd_text: 
                    dd_tag.append(NavigableString(' ' + dd_text)) 
    
    # "inner-col" 클래스 <strong> 태그는 제거
    inner_col_elements = soup.find_all(class_="inner-col")
    if inner_col_elements:
        for element in inner_col_elements:
            strong_tags = element.find_all('strong')
            for strong_tag in strong_tags:
                strong_text = strong_tag.string
                strong_tag.replace_with(strong_text)

#-------------------------------------------------

# href 속성이 있으면서 class가 'tbl-logo-link'가 아닌 요소만 찾기
def filter_func(tag):
    return tag.has_attr('href') and \
           'tbl-logo-link' not in tag.get('class', []) and \
           not tag.find_parents(_class=re.compile(r'.*contents'))       

# 팝업, 히든태그 등의 바로가기 제거 
def remove_href(soup):
    tags_with_href = soup.find_all(filter_func)
    # 찾은 태그 제거
    for tag in tags_with_href:
        if tag.parent and tag.parent.name in ['td', 'th']:
            continue
        #태그 위 설명 제거
        guidebox_desc=tag.find_previous_sibling(lambda tag: tag.name == 'div' and 'guidebox-desc' in tag.get('class', []))
        if guidebox_desc:
            guidebox_desc.decompose()
        
        tag.decompose()

# 링크 전처리
def parse_href(soup):
    for link in soup.find_all('a'):
        href = link.get('href')  # 현재 링크의 href 속성 가져오기
        # href 속성이 '/'로 시작하면 http://pass.airport.kr 추가
        if href.startswith('/'):  
            new_href = f'http://pass.airport.kr{href}'  
            link['href'] = new_href  
   
# 빈 요소 삭제         
def delete_empty_tag(soup): 
    try:
        for tag in soup.find_all():
            if tag.name == 'td':
                continue
            if not tag.contents or not tag.text.strip():
                tag.decompose()
    except Exception as e:
        print('')

# < 마크다운으로 변환 >
def get_markdown(soup):
    
    #빈 태그 제거
    delete_empty_tag(soup)
    
    #링크 처리
    remove_href(soup)
    parse_href(soup)
        
    #마크다운 변환 ---
    text_maker = html2text.HTML2Text()
    text_maker.ignore_links = False
    text_maker.ignore_images = True
    text_maker.body_width = 0 # 자동 줄바꿈 비활성화

    # 1. \n이 2개 이상인 경우 \n로 대체
    markdown_content = text_maker.handle(soup.prettify())
    markdown_content = re.sub(r'\n\s*\n', '\n', markdown_content)
    
    # 2. 각 요소 앞에 줄바꿈 문자 추가
    # _로 시작하는 강조, **로 시작하는 볼드체, #로 시작하는 제목 앞에 줄바꿈 추가
    pattern = r'^(?=\s*(?:_|\*\*|#{1,}))'
    markdown_content = re.sub(pattern, '\n', markdown_content, flags=re.M)
    
    # 3. 줄바꿈 전처리
    text_lines = markdown_content.split('\n')  
    new_lines = []
    skip_indices = set()  # 빈 줄을 추가할 위치를 저장하기 위한 집합

    for i, line in enumerate(text_lines):
        if '---|' in line and i >= 1:
            # '---|'를 포함하는 줄의 앞앞줄에 빈 줄을 추가해야 함을 표시
            skip_indices.add(i-1)

    for i, line in enumerate(text_lines):
        if i in skip_indices:
            # 빈 줄 추가
            new_lines.append('')
        new_lines.append(line)

    # 수정된 라인들을 다시 하나의 문자열로 결합
    modified_text = '\n'.join(new_lines)

    return modified_text
