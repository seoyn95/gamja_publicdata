import numpy as np
import os
from sentence_transformers.util import cos_sim
import json
import pandas as pd


embedding_dir = r"C:\Users\Seo Yeon\OneDrive\바탕 화면\파이썬 vs\기업 임베딩 GPT"
original_reason_embeddings = np.load("sentence_embeddings_openai.npy") 

# 이직 사유 
reasons = [
    "직장의 파산, 폐업, 휴업 등으로 인해",
    "정리해고로 인해",
    "권고사직",
    "명예퇴직",
    "정년퇴직",
    "계약기간 끝나서",
    "소득 또는 보수가 적어서",
    "일거리가 없거나 적어서",
    "일이 임시적이거나 장래성이 없어서",
    "적성, 지식, 기능 등이 맞지 않아서",
    "근무시간 또는 근무환경이 나빠서",
    "자기(가족) 사업을 하려고",
    "결혼, 가족간병 등 가사문제로",
    "건강, 고령 등의 이유로",
    "회사 내 인간관계 때문에",
    "회사가 이사하여",
    "우리집이 이사하여",
    "학업 때문에",
    "군입대 때문에",
    "좀더 좋은 일자리가 있어서",
    "출산, 육아를 위해서",
    "기타"
]


summary = []

for file in os.listdir(embedding_dir):
    if not file.endswith("_negative.npy"):
        continue

    company_name = file.replace("_negative.npy", "")
    neg_emb = np.load(os.path.join(embedding_dir, file))

    # 유사도 계산
    neg_sim_all = cos_sim(neg_emb, original_reason_embeddings).numpy().flatten()
    original_group_avg = [neg_sim_all[i*5:(i+1)*5].mean() for i in range(22)]

    # top5
    top5_neg_idx = np.argsort(original_group_avg)[::-1][:5]

    summary.append({
        "기업명": company_name,
        "original_top5": [
            {"이유": reasons[i], "유사도": round(float(original_group_avg[i]), 3)}
            for i in top5_neg_idx
        ]
    })


def flatten_summary(summary):
    flattened_data = []
    for entry in summary:
        company_name = entry["기업명"]
        for reason in entry["original_top5"]:
            flattened_data.append({
                "기업명": company_name,
                "이직 사유": reason["이유"],
                "유사도": reason["유사도"],
                "유형": "원래 의미"
            })
    return flattened_data

# 평탄화
flattened_summary = flatten_summary(summary)

# DataFrame
df_summary = pd.DataFrame(flattened_summary)
df_summary.to_csv("기업_이직사유_추천.csv", index=False, encoding="utf-8-sig")
print("CSV 파일이 저장되었습니다.")

