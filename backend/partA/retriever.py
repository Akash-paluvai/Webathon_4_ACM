import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer
import os

BASE_DIR = os.path.dirname(__file__)
csv_path = os.path.join(BASE_DIR, "films.csv")

df = pd.read_csv(csv_path)

model = SentenceTransformer("all-MiniLM-L6-v2")

embeddings = model.encode(df["theme"].tolist())

index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)

def retrieve_similar(script_text, k=3):
    query_vec = model.encode([script_text])
    distances, indices = index.search(query_vec, k)

    results = []
    for idx in indices[0]:
        film = df.iloc[idx]
        results.append({
            "title": film["title"],
            "genre": film["genre"],
            "theme": film["theme"],
            "audience": film["audience"]
        })

    return results