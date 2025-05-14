from sentence_transformers import SentenceTransformer
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
import matplotlib.font_manager as fm

df = pd.read_csv("이직 사유 예문.CSV", encoding="cp949", header=None)

# reason_examples 딕셔너리
reason_examples = {
    row[0]: [ex for ex in row[1:] if pd.notnull(ex)]
    for row in df.itertuples(index=False)
}

# 문장, 라벨 리스트로 정리
sentences = []
labels = []
for reason, examples in reason_examples.items():
    for s in examples:
        sentences.append(s)
        labels.append(reason)

# 임베딩 불러오기 
embeddings = np.load("sentence_embeddings.npy")

# t-SNE 차원 축소 
tsne = TSNE(n_components=2, random_state=42, perplexity=30)
reduced = tsne.fit_transform(embeddings)




# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False  # 마이너스 깨짐 방지

# --- 4. 시각화 ---
plt.figure(figsize=(14, 10))
unique_labels = list(set(labels))
colors = plt.cm.tab20.colors

for i, label in enumerate(unique_labels):
    idx = [j for j, l in enumerate(labels) if l == label]
    plt.scatter(reduced[idx, 0], reduced[idx, 1], label=label, color=colors[i % len(colors)], alpha=0.6)

plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.title("이직 사유 문장 임베딩 시각화 (t-SNE)")
plt.xlabel("Dimension 1")
plt.ylabel("Dimension 2")
plt.tight_layout()
plt.show()
