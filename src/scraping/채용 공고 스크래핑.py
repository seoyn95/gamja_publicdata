import time
import pandas as pd
import os
import re
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service 


# 데이터 추출 함수
def extract_job_details(driver):
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # 회사 이름
    company_name_element = soup.select_one('.company_info .company_name a')
    company_name_text = company_name_element.text.strip() if company_name_element else ""
    company_name_text = company_name_text.replace("기업 랭킹", "").strip()
    

    # 요약 정보 추출
    summary_items = soup.select('.recruitment-summary__dd')
    job_details = {
        "회사명": company_name_text,
        "날짜": soup.select_one('.recruitment-summary__end').text.strip(),
        "마감일": summary_items[0].text.strip() if len(summary_items) > 0 else "",
        "직무": summary_items[1].text.strip() if len(summary_items) > 1 else "",
        "경력": summary_items[2].text.strip() if len(summary_items) > 2 else "",
        "근무지역": soup.select_one('.recruitment-summary__location').text.strip() if soup.select_one('.recruitment-summary__location') else "",
        "고용형태": summary_items[3].text.strip() if len(summary_items) > 3 else "",
    }

    # 섹션별 내용 추출
    sections = soup.select('.recruitment-detail__box')
    for section in sections:
        title_tag = section.select_one('.recruitment-detail__tit')
        content_tag = section.select_one('.recruitment-detail__txt')
        if title_tag and content_tag:
            job_details[title_tag.text.strip()] = content_tag.get_text(separator="\n", strip=True)

    return job_details

# 엑셀로 저장하는 함수
def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', '', name)

def save_to_excel(job_info):
    company_name = job_info.get("회사명", "unknown_company") 
    sanitized_name = sanitize_filename(company_name)
    
    # 파일명
    base_filename = f"{sanitized_name}.xlsx"
    filename = base_filename

    # 중복 번호
    counter = 1
    while os.path.exists(filename):
        filename = f"{sanitized_name}_{counter}.xlsx"
        counter += 1

    # 저장
    df = pd.DataFrame([job_info])
    df.to_excel(filename, index=False)
    print(f"Saved to: {filename}")



# 크롤링 
def crawl_and_save_job_posting(url):
    driver_path = r"C:\Users\Seo Yeon\OneDrive\바탕 화면\chromedriver.exe"
    service = Service(executable_path=driver_path) 
    driver = webdriver.Chrome(service=service)  
    driver.get(url)
    time.sleep(0.5) 

    # 채용 공고 정보 추출
    job_info = extract_job_details(driver)
    driver.quit() #드라이버 종료 
    save_to_excel(job_info)    # 엑셀로 저장



# 실행
df = pd.read_excel("filtered_company_list.xlsx")
for idx, row in df.iterrows():
    url = row[1]  
    print(f"({idx + 1}) 크롤링 중: {url}")
    crawl_and_save_job_posting(url)
