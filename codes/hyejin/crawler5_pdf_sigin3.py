# step1.프로젝트에 필요한 패키지 불러오기
from  selenium  import  webdriver
from  selenium.webdriver.common.keys  import  Keys
from  selenium.webdriver.common.by  import  By
import  pandas  as  pd
import  math
import sys
import os
import re

import base64
import json
import logging
import time
from io import BytesIO
from typing import List

from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager

from PyPDF4 import PdfFileMerger  # Changed import


## 회사 리스트
from com_list import company_dict


print_options = {
        'landscape': False,
        'displayHeaderFooter': False,
        'printBackground': True,
        'preferCSSPageSize': True,
        'paperWidth': 8.27,   # A4 폭 (인치)
        'paperHeight': 11.69, # A4 높이 (인치)
    }


# step2.로그인 정보 및 검색할 회사 미리 정의
USR  =  "caley4@hansung.ac.kr"
PWD  =  "qkrcodnjs1234" 


# company_dict 사용 예시
for base_url in company_dict: 
    QUERY = company_dict[base_url]

    # 디렉토리 확인 후 없으면 생성
    directory = f"./{QUERY}"
    if not os.path.exists(directory):
        os.makedirs(directory)


    # 크롬 옵션 설정
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    options.add_experimental_option('prefs', {
        'printing.print_preview_sticky_settings.appState': '{"recentDestinations":[{"id":"Save as PDF","origin":"local","account":""}],"selectedDestinationId":"Save as PDF","version":2}',
        'savefile.default_directory': os.getcwd(),  # PDF 저장 경로
        'printing.default_destination_selection_rules': {
            'kind': 'Save as PDF'
        }
    })

    # 크롬 드라이버 실행
    driver = webdriver.Chrome(options=options)


    # step3.크롬드라이버 실행 및 잡플래닛 로그인
    driver.get("https://www.jobplanet.co.kr/users/sign_in?_nav=gb")
    time.sleep(4)

    # 아이디 입력
    login_id  =  driver.find_element(By.ID,  "user_email")
    login_id.send_keys(USR)

    # 비밀번호 입력
    login_pwd  =  driver.find_element(By.ID,  "user_password")
    login_pwd.send_keys(PWD)

    # 로그인 버튼 클릭
    login_id.send_keys(Keys.RETURN)
    time.sleep(3)


    # 마지막 페이지 찾기
    driver.get(base_url)
    time.sleep(3)  # 페이지 로드 대기

    # 페이지네이션 요소 찾기
    pagination = driver.find_element(By.CLASS_NAME, 'paginnation_new')

    # 'last' 버튼 찾기
    last_button = pagination.find_element(By.CLASS_NAME, 'btn_pglast')

    # 'href' 속성 값 추출
    last_page_href = last_button.get_attribute('href')

    # 'page=' 이후의 숫자를 추출하는 정규 표현식 사용
    last_page_number = int(re.search(r'page=(\d+)', last_page_href).group(1))
    print(company_dict[base_url]+" - "+str(last_page_number))


    # step4.원하는 회사의 리뷰 페이지까지 이동 함수
    # 각 페이지를 순차적으로 저장
    pdf_files = []
    for page in range(1, last_page_number + 1):
        url = f"{base_url}{page}"
        filename = f"/Users/hyejinpark/Desktop/면접질문/{QUERY}/page_{page}.pdf"

        driver.get(url)
        time.sleep(3) 
        

        resource = "/session/%s/chromium/send_command_and_get_result" % driver.session_id
        url = driver.command_executor._url + resource
        body = json.dumps({'cmd': 'Page.printToPDF', 'params': print_options})
        response = driver.command_executor._request('POST', url, body)
        result = response.get('value')
        result_2 = base64.b64decode(result['data'])

        file = BytesIO()
        file.write(result_2)
        pdf_files.append(file)
        with open(filename, "wb") as outfile:
            outfile.write(pdf_files[int(page-1)].getbuffer())
    
    # 크롬 드라이버 종료
    driver.quit ()
    
    print("================= "+company_dict[base_url]+"======= 끝")

    

    # 현재 폴더에서 PDF 파일 목록을 가져오기
    pdf_files = [f for f in os.listdir(directory) if f.endswith('.pdf')]

    # 파일 이름으로 정렬
    pdf_files.sort(key=lambda x: int(x.split('_')[1].split('.')[0]))

    # 병합할 PDF 파일 객체 생성
    merger = PdfFileMerger()

    # 정렬된 순서대로 파일을 병합
    for pdf_file in pdf_files:
        merger.append(f"{directory}/{pdf_file}")

    # 병합된 결과를 저장할 파일 이름
    output_filename = f"{directory}/{QUERY}_merged.pdf"

    # 병합된 PDF를 파일로 저장
    with open(output_filename, 'wb') as fout:
        merger.write(fout)

    # 메모리와 파일 핸들을 정리
    merger.close()

    print(f'병합이 완료되었습니다. {output_filename} 파일로 저장되었습니다.')

