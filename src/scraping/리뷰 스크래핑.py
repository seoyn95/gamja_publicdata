from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import math
import re


USR = " "
PWD = " "

# 로그인 함수
def login(driver, usr, pwd):
    driver.get("https://www.jobplanet.co.kr/users/sign_in?_nav=gb")
    time.sleep(3)
    driver.find_element(By.ID, "user_email").send_keys(usr)
    driver.find_element(By.ID, "user_password").send_keys(pwd)
    driver.find_element(By.ID, "user_password").send_keys(Keys.RETURN)
    time.sleep(5)

# 리뷰 페이지로 이동


def go_to_review_page(driver, query):
    try:
        # 검색페이지
        driver.get("https://www.jobplanet.co.kr/companies")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "search_bar_search_query"))
        )

        # 기업명입력
        search_box = driver.find_element(By.ID, "search_bar_search_query")
        search_box.clear()
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)
        time.sleep(3)

        # 기업명클릭
        company_results = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "h4.text-gray-800"))
        )

        target = None
        for result in company_results:
            if result.text.strip() == query.strip():
                target = result
                break

        if target:
            driver.execute_script("arguments[0].click();", target)
        else:
            print(f"[{query}] 정확한 기업명을 찾지 못했습니다.")
            return False
        time.sleep(2)

        # 새탭 
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(2)

        # 리뷰 
        try:
            review_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "viewReviews"))
            )
            review_button.click()
            time.sleep(2)
        except:
            print(f"[{query}] 리뷰 버튼 없음")

        return True

    except Exception as e:
        print(f"[{query}] 리뷰 페이지 이동 실패:", e)
        return False
    
# 별점 파싱
def parse_star_rating(element):
    try:
        rating_text = element.text.strip()
        return f"{rating_text}점"
    except:
        return "N/A"



# 리뷰 내용 파싱 함수
def parse_review_blob(blob):
    lines = blob.splitlines()
    date, summary = "", ""
    merit, disadvantage, opinion = "", "", ""

    for line in lines:
        if "작성" in line:
            date = line.strip().replace("작성", "").strip()

    try:
        idx_merit = lines.index("장점")
        idx_disadv = lines.index("단점")
        idx_opinion = lines.index("경영진에 바라는 점")
    except ValueError:
        idx_merit = idx_disadv = idx_opinion = -1

    if idx_merit > 0:
        summary = lines[idx_merit - 1].strip()
    if idx_merit != -1 and idx_disadv != -1:
        merit = "\n".join(lines[idx_merit + 1:idx_disadv]).strip()
    if idx_disadv != -1 and idx_opinion != -1:
        disadvantage = "\n".join(lines[idx_disadv + 1:idx_opinion]).strip()
    if idx_opinion != -1 and len(lines) > idx_opinion + 1:
        opinion = lines[idx_opinion + 1].strip()

    return date, summary, merit, disadvantage, opinion


def scrape_data(driver):
    list_div, list_cur = [], []
    list_date, list_summery = [], []
    list_merit, list_disadvantages, list_opinions = [], [], []

    try:
        review_count = driver.find_element(By.CSS_SELECTOR, "span.num.notranslate").text
        page = math.ceil(int(review_count.replace(",", "")) / 5)
    except:
        print("리뷰 수 파악 실패")
        return pd.DataFrame()

    for page_num in range(1, min(page + 1, 11)):  # 10
        try:
            # 페이지 로드 대기
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#viewReviewsList section"))
            )
            review_box = driver.find_elements(By.CSS_SELECTOR, "#viewReviewsList section")
        except Exception as e:
            print(f"{page_num}페이지 리뷰 로딩 실패: {e}")
            break

        # 중복 대비
        seen_reviews = set()  # 이미 본 리뷰 저장

        for i in review_box:
            try:
                user_info_area = i.find_elements(By.TAG_NAME, "div")[0]
                user_text_blob = user_info_area.text.strip()

                # 건너뛰기 
                if user_text_blob in seen_reviews:
                    continue

                seen_reviews.add(user_text_blob) 

                # 자동 파싱
                date, summary, merit, disadv, opinion = parse_review_blob(user_text_blob)

                list_div.append("분석불가" if not user_text_blob else user_text_blob.splitlines()[0])
                list_cur.append("")  
                list_date.append(date if date else "날짜 없음")
                list_summery.append(summary)
                list_merit.append(merit)
                list_disadvantages.append(disadv)
                list_opinions.append(opinion)
            except Exception as e:
                print(f"리뷰 파싱 실패: {e}")
                continue

        # 페이지 이동 
        if page_num < min(page, 10):  
            try:
                btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, f'//button[@title="{page_num + 1}"]'))
                )
                btn.click()
                time.sleep(4)  

                print(f"{page_num + 1}페이지로 이동 완료")
            except Exception as e:
                print(f"{page_num + 1}페이지로 이동 실패: {e}")
                break 

    df = pd.DataFrame({
        "구분": list_div,
        "고용형태": list_cur,
        "날짜": list_date,
        "요약": list_summery,
        "장점": list_merit,
        "단점": list_disadvantages,
        "경영진에게 바라는 점": list_opinions
    })
    return df


#지정 문자 제거
def clean_invalid_characters(text):
    clean_text = re.sub(r'[\x00-\x1F\x7F]', '', text)
    return clean_text

def main():
    df = pd.read_excel("filtered_list_.xlsx", header=None)
    company_list = df.iloc[:, 0].dropna().tolist()    # 기업명

    driver = webdriver.Chrome()
    login(driver, USR, PWD)

    for company in company_list:
        print(f">>{company} 리뷰 수집 중...")
        success = go_to_review_page(driver, company)
        if not success:
            continue
        data = scrape_data(driver)
        if not data.empty:
            cleaned_data = data.applymap(lambda x: clean_invalid_characters(str(x)))
            cleaned_data.to_excel(f"잡플래닛 리뷰_{company}.xlsx", index=False) #리뷰 파일 저장 
            print(f"{company} 저장 완료")
        
        driver.refresh()  #f5
        time.sleep(0.5) 

    driver.quit()

if __name__ == "__main__":
    main()