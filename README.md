### html2md.py
---
홈페이지 크롤링 및 마크다운 전처리 반자동화

- 풍부하고 정확한 답변 생성을 위해 홈페이지를 참조 데이터로 활용

- 전처리
  - gpt model이 빠르고 정확하게 프롬프트를 생성시키기 위함
      - 최대한 사람이 만든 마크다운과 비슷하게 처리
  - 데이터 선택&정제
      1. 제거할 태그와 요소들 추출 후 삭제 (19개)
      2. 질의응답형식 전처리
          - —-
          질문 : ㅇㅇㅇ
          답변 : ㅇㅇㅇ
      3. html 테이블 md로 변환
          - rowspan, colspan 처리
          - 셀 내 줄바꿈, list, bold체 처리
      4. 이미지 및 기타 요소들로 인해 불필요하게 추가되는 넘버링, 줄바꿈, 제목 정제
      5. 볼드체 해야할 부분, 안 해야 할 부분 처리 (dt, dl, 일부 class)
      6. 줄바꿈 처리
          - 태그가 마크다운으로 변환되면서 중첩태그가 줄바꿈으로 변함 → 카트다운을 \n으로 이어붙인 후 테이블, 강조, 제목 앞에서 줄바꿈 처리
  - 최대한 많은 내용 포함
      - 링크가 /'로 시작하면 메인링크 추가
      - video -> string&url 처리
      - 이미지 : 설명(alt attr)으로 대체 ('로고'가 포함된 것 등 제거)
  - 긴 문맥 안에서 gpt가 상위 항목을 어떻게 인식할 것인가?
      - header(#)수로 상하관계 조절, 6 이 넘어가면 볼드처리

### crawler.py
---
main module 아키텍쳐

depth1=[] #depth1 인 최상위 카테고리

depth2=[] #depth2 인 최상위 카테고리

ajax_or_js=[] #ajax/js 상위 제목

nav_ctg = 크롤링후 네비게이션 바 url dict로 저장()

for nav_c in nav_ctg:

  if nav_c in depth1:
  
    크롤링()
    
    전처리()
    
    마크다운 저장()
    
  if nav_c in depth2:
  
    depth3인 페이지 = 크롤링(페이지이동/클릭)() # 제목(#) 추가 후 하위 페이지 붙이기(class: m_title_)
    
     if depth3인 페이지 :
     
        크롤링(페이지이동/클릭) # 상위 페이지에 붙이기 (class: s_title_)
        
    전처리()
    
    마크다운 저장()
