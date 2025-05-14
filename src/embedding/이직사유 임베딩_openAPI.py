import openai
import pandas as pd
import numpy as np
import time

openai.api_key = " "  

# CSV 파일
df = pd.read_csv("이직 사유 예문.CSV", encoding="cp949", header=None)
reason_examples = {
    row[0]: [ex for ex in row[1:] if pd.notnull(ex)]
    for row in df.itertuples(index=False)
}

# 문장 & 라벨 정리
sentences = []
labels = []
for reason, examples in reason_examples.items():
    for s in examples:
        sentences.append(s)
        labels.append(reason)

# 임베딩
def get_embedding(text, model="text-embedding-3-small"):
    try:
        response = openai.embeddings.create(
            model=model,
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"오류 발생: {e}")
        return None

# 임베딩 실행
embeddings = []
for i, sentence in enumerate(sentences):
    print(f"임베딩 중: {i+1}/{len(sentences)}")
    emb = get_embedding(sentence)
    if emb:
        embeddings.append(emb)
    else:
        embeddings.append([None] * 1536) 
    time.sleep(0.6) 

# 결과 저장
np.save("sentence_embeddings_openai.npy", embeddings)

# DataFrame으로 보기
embed_df = pd.DataFrame(embeddings)
embed_df["사유"] = labels
embed_df["문장"] = sentences
embed_df.to_csv("임베딩_결과_openai.csv", index=False, encoding="utf-8-sig")
