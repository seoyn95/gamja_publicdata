import pandas as pd
import matplotlib.pyplot as plt
import os

# 글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# CSV 파일 경로
downloads_path = os.path.expanduser("~/Downloads")
file_path = os.path.join(downloads_path, "118_DT_118N_MON056_20250506203621 - 복사본.csv")

# 데이터 불러오기
data = pd.read_csv(file_path, encoding='cp949')

# 필터링
filtered = data[
    (data['항목'] == '이직자_전체') &
    (data['규모'] == '전체') &
    (data['산업분류'] != '전체')  # '전체' 산업은 제외
]

# 기간 컬럼 추출
date_columns = filtered.columns[4:]

# 시각화
plt.figure(figsize=(16, 8))

# 산업별 이직자 수 라인 그리기
for i, row in filtered.iterrows():
    industry = row['산업분류']
    values = row[date_columns].astype(float) / 1000  # 천 명 단위로 정규화 (가독성 ↑)
    plt.plot(date_columns, values, marker='o', label=industry)

#그래프 설정
plt.title('산업별 이직자 수 추이')
plt.xlabel('기간')
plt.ylabel('이직자 수 (천 명)')
plt.xticks(rotation=45)
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend(title='산업분류', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()