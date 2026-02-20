from sentence_transformers import SentenceTransformer
from transformers import pipeline

embed_model = SentenceTransformer("all-MiniLM-L6-v2")
sentiment_model = pipeline("sentiment-analysis")
emotion_model = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base")

def analyze_society(script_text: str):
    embedding = embed_model.encode(script_text)

    sentiment = sentiment_model(script_text[:400])[0]["label"]
    emotion = emotion_model(script_text[:400])[0]["label"]

    return {
        "embedding": embedding,
        "sentiment": sentiment,
        "emotion": emotion
    }