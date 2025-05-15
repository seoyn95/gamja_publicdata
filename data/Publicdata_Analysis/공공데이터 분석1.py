import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager
import seaborn as sns

# 한글 폰트
font_path = "C:/Windows/Fonts/malgun.ttf" 
font_name = font_manager.FontProperties(fname=font_path).get_name()
plt.rc('font', family=font_name)

# 데이터 불러오기
df = pd.read_csv(r"C:\Users\Seo Yeon\OneDrive\바탕 화면\감자_공공데이터\data\Publicdata_Analysis\118_DT_118N_MON056_20250506203621.csv", encoding='cp949')

# 필터링
target_items = ['빈일자리_전체', '근로자_상용', '이직자_전체']
df_filtered = df[df['항목'].isin(target_items)].copy()

# 2018-2024년 분기
quarters = ['2018. 1/4', '2018. 2/4', '2018. 3/4', '2018. 4/4', 
            '2019. 1/4', '2019. 2/4', '2019. 3/4', '2019. 4/4', 
            '2020. 1/4', '2020. 2/4', '2020. 3/4', '2020. 4/4', 
            '2021. 1/4', '2021. 2/4', '2021. 3/4', '2021. 4/4',
            '2022. 1/4', '2022. 2/4', '2022. 3/4', '2022. 4/4', 
            '2023. 1/4', '2023. 2/4', '2023. 3/4', '2023. 4/4', 
            '2024. 1/4', '2024. 2/4', '2024. 3/4', '2024. 4/4']

df_filtered[quarters] = df_filtered[quarters].replace('-', '0').astype(float)
df_filtered.loc[:, '1년평균'] = df_filtered[quarters].mean(axis=1) #평균열
pivot = pd.pivot_table(df_filtered, index='산업분류', columns='항목', values='1년평균', aggfunc='mean').dropna() #피벗

# 지표 계산
pivot['Turnover_Index'] = (pivot['이직자_전체'] / pivot['빈일자리_전체']) * 100
pivot['Stability_Index'] = pivot['근로자_상용'] / pivot['이직자_전체']

# 알파벳 코드 정렬
custom_order = ['전체'] + sorted([x for x in pivot.index if x != '전체'])
pivot_sorted = pivot.loc[custom_order]

# 결과 출력
print(pivot_sorted[['Turnover_Index', 'Stability_Index']])

# 시각화 - 막대 + 선 그래프
fig, ax1 = plt.subplots(figsize=(14, 6))
bars = ax1.bar(pivot_sorted.index, pivot_sorted['Turnover_Index'], color='teal', label='Turnover Index')
ax1.set_ylabel('Turnover Index', color='teal')
ax1.tick_params(axis='y', labelcolor='teal')

ax1.set_xticks(range(len(pivot_sorted.index))) # x축 tick
ax1.set_xticklabels(pivot_sorted.index, rotation=45, ha='right')

# 선그래프: Stability Index
ax2 = ax1.twinx()
ax2.plot(pivot_sorted.index, pivot_sorted['Stability_Index'], color='orange', marker='o', label='Stability Index')
ax2.set_ylabel('Stability Index', color='orange')
ax2.tick_params(axis='y', labelcolor='orange')

# 범례 및 제목
fig.suptitle("산업별 고용 회전율 및 고용 안정성 지표 (2018-2024년 기준)", fontsize=14)
fig.tight_layout()
plt.show()

# 인사이트 출력
print("\n>> 인사이트 예시:")
print("- Turnover Index ↑ : 고용 회전율 높음 → 이직 빈도 많음")
print("- Stability Index ↑ : 근속 안정성 높음 → 장기 재직 가능성 높음")
print("- 두 지표를 함께 보면 단기직/장기직 산업 판별이 가능함")

# 고용안정성(Stability Index)과 고용회전율(Turnover Index) 간의 상관관계 분석
correlation = pivot_sorted[['Turnover_Index', 'Stability_Index']].corr().iloc[0, 1]
print(f"\n>> 고용 회전율과 고용 안정성 간 상관계수: {correlation:.2f}")

# 상관관계 시각화 - 산점도 + 회귀선
plt.figure(figsize=(8, 6))
sns.regplot(x='Turnover_Index', y='Stability_Index', data=pivot_sorted, scatter_kws={'color': 'teal'}, line_kws={'color': 'orange'})
plt.title('고용 회전율 vs 고용 안정성 상관관계', fontsize=14)
plt.xlabel('Turnover Index')
plt.ylabel('Stability Index')
plt.grid(True)
plt.tight_layout()
plt.show()