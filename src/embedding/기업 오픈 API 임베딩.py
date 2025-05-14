import os
import re
import time
import numpy as np
import pandas as pd
from tqdm import tqdm
import openai

# OpenAI API 키 설정
openai.api_key = " "  

# 기업명 정제
def clean_company_name(filename):
    name = filename.replace("잡플래닛 리뷰_", "")
    name = re.sub(r"\(.*?\)", "", name)  
    return os.path.splitext(name)[0].strip()

# 리뷰 텍스트 추출
def extract_review_sentences(filepath):
    df = pd.read_excel(filepath)
    df = df.fillna("")
    pos_texts = (df["요약"].astype(str) + " " + df["장점"].astype(str)).tolist()
    neg_texts = (df["단점"].astype(str) + " " + df["경영진에게 바라는 점"].astype(str)).tolist()
    # 짧은 문장 
    pos_texts = [t.strip() for t in pos_texts if len(t.strip()) > 5]
    neg_texts = [t.strip() for t in neg_texts if len(t.strip()) > 5]
    return pos_texts, neg_texts

# 임베딩
def get_embeddings(texts, model="text-embedding-3-small"):
    embeddings = []
    BATCH_SIZE = 50
    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i:i + BATCH_SIZE]
        try:
            response = openai.embeddings.create(
                model=model,
                input=batch
            )
            batch_embeddings = [d.embedding for d in response.data]
            embeddings.extend(batch_embeddings)
        except Exception as e:
            print(f"임베딩 오류: {e}")
            embeddings.extend([[0.0] * 1536] * len(batch))  # fallback: 0 벡터
        time.sleep(1)  # 속도
    return embeddings

# 평균 벡터 계산
def compute_average_embedding(texts):
    if not texts:
        return np.zeros(1536)
    embeddings = get_embeddings(texts)
    return np.mean(embeddings, axis=0)

# 전체 파일 처리
def process_all_company_files(folder_path, output_path):
    os.makedirs(output_path, exist_ok=True)
    files = [f for f in os.listdir(folder_path) if f.endswith(".xlsx")]

    for file in tqdm(files, desc="기업 파일 처리 중"):
        try:
            filepath = os.path.join(folder_path, file)
            company_name = clean_company_name(file)

            pos_texts, neg_texts = extract_review_sentences(filepath)
            pos_emb = compute_average_embedding(pos_texts)
            neg_emb = compute_average_embedding(neg_texts)

            np.save(os.path.join(output_path, f"{company_name}_positive.npy"), pos_emb)
            np.save(os.path.join(output_path, f"{company_name}_negative.npy"), neg_emb)
        except Exception as e:
            print(f"{file} 처리 중 오류 발생: {e}")

# 실행
process_all_company_files(
    folder_path = r"C:\Users\Seo Yeon\OneDrive\바탕 화면\파이썬 vs\잡플래닛 리뷰",
    output_path = r"C:\Users\Seo Yeon\OneDrive\바탕 화면\파이썬 vs"
)
