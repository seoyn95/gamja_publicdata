import pandas as pd
import re
import os

# 입력값 예시: "123 631 222 7 1"
user_input = input("pid 산업 직무 이직사유 지역 (띄어쓰기로 입력): ")
pid, industry_code, job_code, reason_code, region_code = map(int, user_input.strip().split())

user_pid = pid
user_industry_code = str(industry_code)
user_job_code = job_code
user_reason_code = reason_code
user_region_codes = [region_code]

# <1> 업종명 추출
industry_df = pd.read_excel("업종코드.xlsx")
industry_df['숫자'] = industry_df['숫자'].astype(str).str.zfill(2)
mid_code = user_industry_code[:2]
result = industry_df[industry_df['숫자'] == mid_code]

if result.empty:
    print("해당하는 업종 코드가 없습니다.")
    exit()

업종명 = result.iloc[0]['업종']
print(f"업종명: {업종명}")

# <2> 채용공고 필터링 (지역 기반)
location_name_to_code = {
    "서울": 1, "부산": 2, "대구": 3, "대전": 4, "인천": 5, "광주": 6, "울산": 7,
    "경기": 8, "강원": 9, "충북": 10, "충남": 11, "전북": 12, "전남": 13,
    "경북": 14, "경남": 15, "제주": 16, "세종": 19
}

filtered_jobs = []
path = f'C:\\Users\\Seo Yeon\\OneDrive\\바탕 화면\\파이썬 vs\\{업종명}'

for filename in os.listdir(path):
    if filename.endswith(".xlsx") or filename.endswith(".csv"):
        file_path = os.path.join(path, filename)
        try:
            df = pd.read_excel(file_path) if filename.endswith(".xlsx") else pd.read_csv(file_path)
            location = df.loc[0, "근무지역"] if "근무지역" in df.columns else df.loc[0, "회사위치"]
            for name, code in location_name_to_code.items():
                if name in str(location):
                    if code in user_region_codes:
                        filtered_jobs.append(df)
                    break
        except Exception as e:
            print(f"Error reading {filename}: {e}")

if not filtered_jobs:
    print("선택한 지역의 채용공고가 없습니다.")
    exit()

result_df = pd.concat(filtered_jobs, ignore_index=True)
result_df.to_csv("추천_채용공고.csv", index=False)

# <3> 이직 사유 기반 기업 필터링
reason_map = {
    1: "직장의 파산, 폐업, 휴업 등으로 인해", 2: "정리해고로 인해", 3: "권고사직", 4: "명예퇴직", 5: "정년퇴직",
    6: "계약기간 끝나서", 7: "소득 또는 보수가 적어서", 8: "일거리가 없거나 적어서", 9: "일이 임시적이거나 장래성이 없어서",
    10: "적성, 지식, 기능 등이 맞지 않아서", 11: "근무시간 또는 근무환경이 나빠서", 12: "자기(가족) 사업을 하려고",
    13: "결혼, 가족간병 등 가사문제로", 14: "건강, 고령 등의 이유로", 15: "회사 내 인간관계 때문에", 16: "회사가 이사하여",
    17: "우리집이 이사하여", 18: "학업 때문에", 19: "군입대 때문에", 20: "좀더 좋은 일자리가 있어서",
    21: "출산,육아를위해서(11차조사 부터)", 22: "기타"
}

user_reason_text = reason_map[user_reason_code]

recommend_df = result_df
reason_df = pd.read_csv("기업_이직사유_추천.csv")

def clean_name(name):
    return re.sub(r"\s|\(주\)|㈜|\(|\)", "", str(name)).strip()

recommend_df["회사명_clean"] = recommend_df["회사명"].apply(clean_name)
reason_df["기업명_clean"] = reason_df["기업명"].apply(clean_name)

threshold = 0.415
drop_companies = (
    reason_df[(reason_df["이직 사유"] == user_reason_text) & (reason_df["유사도"] >= threshold)]
    ["기업명_clean"]
    .unique()
)

filtered_df = recommend_df[~recommend_df["회사명_clean"].isin(drop_companies)]

print("제외된 기업 수:", len(recommend_df) - len(filtered_df))
print("남은 기업 수:", len(filtered_df))
print(filtered_df[["회사명", "직무", "경력"]].sample(n=5))

filtered_df.drop(columns=["회사명_clean"]).to_csv("최종 추천 기업.csv", index=False)

# <4> (선택) 서울일 경우, 고용센터 및 국취 위탁기관 정보 5개 추천
if 1 in user_region_codes:
    try:
        import pandas as pd

        province_mapping = {
            "서울특별시": "서울", "부산광역시": "부산", "대구광역시": "대구",
            "인천광역시": "인천", "광주광역시": "광주", "대전광역시": "대전",
            "울산광역시": "울산", "세종특별자치시": "세종", "경기도": "경기",
            "강원도": "강원", "충청북도": "충북", "충청남도": "충남",
            "전라북도": "전북", "전라남도": "전남", "경상북도": "경북",
            "경상남도": "경남", "제주특별자치도": "제주"
        }

        def convert_province(address):
            for full_name, short_name in province_mapping.items():
                if isinstance(address, str) and address.startswith(full_name):
                    return address.replace(full_name, short_name, 1)
            return address

        기관_df = pd.read_csv("운영기관_목록.csv", encoding="cp949")  # ← 여기 수정
        기관_df["주소"] = 기관_df["주소"].apply(convert_province)

        서울_기관 = 기관_df[기관_df["주소"].str.contains("서울", na=False)]
        기관_5개 = 서울_기관.sample(n=5)

        # 이 부분에서만 한 번 출력되도록 수정
        print("\n※ 가까운 고용센터 또는 국취 위탁기관 정보:")
        for i, info in enumerate(기관_5개[["기관명", "주소", "전화번호"]].to_dict(orient="records"), start=1):
            print(f"{i}. {info['기관명']} / {info['주소']} / {info['전화번호']}")
    
    except Exception as e:
        print(f"오류 발생: {e}")

