from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import pandas as pd
from sentence_transformers import SentenceTransformer
import joblib
import os 
import numpy as np
from dotenv import load_dotenv

import __main__
from schemas import UserIntent, PerfumeResult
from ai_service import analyze_query_with_llm
from search_service import search_perfumes
from evaluate_search import run_evaluation

load_dotenv()

def accord_tokenizer(text):
    if isinstance(text, str):
        return [x.strip().lower() for x in text.split(',') if x.strip()]
    return []

__main__.accord_tokenizer = accord_tokenizer

ml_models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Wczytywanie modeli do pamięci RAM...")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    models_dir = os.path.join(base_dir, 'modele')

    try: 
        # 1. Główna wektoryzowana baza perfum
        db_path = os.path.join(models_dir, 'final_perfume_database.pkl')
        ml_models['database'] = pd.read_pickle(db_path)
        print(f"Baza perfum wczytana: {len(ml_models['database'])} rekordów.")

        # 2. Most TF-IDF (Macierz nastrojów)
        mood_path = os.path.join(models_dir, 'mood_matrix_bridge.pkl')
        ml_models['mood_matrix'] = pd.read_pickle(mood_path)
        print("Macierz nastrojów wczytana.")

        # 3. Wektoryzator TF-IDF
        tfidf_path = os.path.join(models_dir, 'tfidf_vectorizer.joblib')
        ml_models['tfidf'] = joblib.load(tfidf_path)
        print("Wektoryzator TF-IDF wczytany.")

        # 4. Klasyfikator SVM (Smart Filters)
        svm_path = os.path.join(models_dir, 'svm_classifier.joblib')
        ml_models['svm'] = joblib.load(svm_path)
        print("Klasyfikator SVM wczytany.")
        
        # 5. Wielojęzyczny Model NLP (Sentence-Transformers)
        ml_models['embedder'] = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        print("Model wielojęzyczny załadowany pomyślnie.")
        
        print("Serwer gotowy do przyjmowania zapytań.")
        
        # Oddanie kontroli do FastAPI
        yield 

    except Exception as e:
        print(f"Wystąpił błąd podczas ładowania modeli ML: {e}")
        raise e 
    finally:
        print("Zatrzymywanie serwera...")
        ml_models.clear()

app = FastAPI(
    title="Perfume Semantic Search API",
    description="Backend AI realizujący wyszukiwanie i profilowanie zapachów",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Endpoint diagnostyczny. Zwraca informację, czy serwer żyje i czy modele są w RAM."""
    is_ready = bool(ml_models)
    return {
        "status": "ok",
        "models_loaded": is_ready,
        "message": "API is running securely."
    }

@app.post("/api/test-ner", response_model=UserIntent)
async def test_llm_parsing(query: str):
    """Endpoint do weryfikacji strukturalnej ekstrakcji bytów (NER) przez Gemini."""
    try:
        response = analyze_query_with_llm(query)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd przetwarzania LLM: {str(e)}")
    
@app.post('/api/search')
async def search_endpoint(query: str):
    """
    Główny produkcyjny endpoint wyszukiwarki. 
    Łączy rozumienie języka (Gemini - NER) z przeszukiwaniem wektorowej bazy (SBERT),
    dodając klasyfikację intencji (SVM) oraz profilowanie zapachowe (K-Means).
    """
    if not ml_models:
        raise HTTPException(status_code=503, detail="Modele AI ładują się. Spróbuj za chwilę.")

    try:
        # 1. Kwalifikator Zapytań (NER) z użyciem Gemini
        intent = analyze_query_with_llm(query)
        
        # 2. Wyszukiwanie wektorowe SBERT + TF-IDF (tutaj baza jest już obcięta o jawną płeć)
        results = search_perfumes(intent, ml_models)
        
        # 3. Klasyfikacja intencji (Smart Filters dla interfejsu React)
        predicted_gender = intent.explicit_gender 
        
        # Jeśli LLM nic nie wyciągnął, a mamy abstrakcyjny opis, używamy SVM
        if not predicted_gender and intent.abstract_mood:
            query_vector = ml_models['embedder'].encode([intent.abstract_mood])
            predicted_gender = ml_models['svm'].predict(query_vector)[0]

        if not predicted_gender:
            predicted_gender = "for women and men"

        # 4. Przyporządkowanie Profilu (K-Means)
        assigned_cluster = "Nieznany Profil"
        if results:
            db = ml_models['database']
            top_perfume_name = results[0].name
            cluster_info = db[db['Name'] == top_perfume_name]['Cluster_Name'].values
            if len(cluster_info) > 0:
                assigned_cluster = str(cluster_info[0])

        return {
            "metadata": {
                "predicted_gender": str(predicted_gender),
                "assigned_cluster": assigned_cluster
            },
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Wewnętrzny błąd wyszukiwarki: {str(e)}")
    
@app.get("/api/evaluate")
async def evaluate_system_endpoint():
    """
    Endpoint wykonujący na żywo testy ewaluacyjne (Precision@k) i zwracający
    porównanie modelu Baseline z hybrydowym modelem ScentAI.
    """
    try:
        report = run_evaluation(ml_models)
        return {"status": "success", "data": report}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
    
@app.get("/api/metrics")
async def get_metrics():
    """
    Zwraca wyliczone statystyki ewaluacyjne (NLP & EDI) dla panelu deweloperskiego.
    Wykorzystuje zmodyfikowaną metrykę Business Accuracy.
    """
    try:
        report = run_evaluation(ml_models)
        return {"status": "success", "data": report}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@app.get("/api/clusters")
async def get_clusters(limit: int = 300):
    """
    Zwraca próbkowną listę punktów do narysowania wykresu PCA (Scatter Plot).
    Ogranicza dane do najbardziej znanych marek, aby wykres był czytelny dla użytkownika.
    """
    try:
        db = ml_models['database']
        
        # Wybrane popularne domeny zapachowe do pokazania na wykresie
        top_brands = [
            'Tom Ford', 'Dior', 'Chanel', 'Jo Malone London', 
            'Yves Saint Laurent', 'Guerlain', 'Mugler', 'Creed', 'Versace', 'Giorgio Armani'
        ]
        
        # Sprawdzamy czy nasza baza ma na pewno wyliczone PCA
        if 'PCA_X' not in db.columns or 'PCA_Y' not in db.columns:
            return {"status": "error", "detail": "Brak wyliczonych współrzędnych PCA w bazie."}
            
        # Filtrujemy tylko wybrane marki i usuwamy ewentualne braki danych
        filtered_db = db[db['Brand'].isin(top_brands)].dropna(subset=['PCA_X', 'PCA_Y', 'Cluster_Name'])
        
        # Zabezpieczenie: Jeśli marek nie ma w bazie, losujemy z całości
        if filtered_db.empty:
            filtered_db = db.dropna(subset=['PCA_X', 'PCA_Y', 'Cluster_Name'])
            
        # Próbkowanie do określonego limitu (np. 300 punktów)
        sample = filtered_db.sample(n=min(limit, len(filtered_db)), random_state=42)
        
        points = []
        for _, row in sample.iterrows():
            points.append({
                "id": str(row.get('Perfume_ID', np.random.randint(10000, 99999))),
                "name": str(row['Name']),
                "brand": str(row['Brand']),
                "cluster": str(row['Cluster_Name']),
                "x": float(row['PCA_X']),
                "y": float(row['PCA_Y'])
            })
            
        return {"status": "success", "data": points}
    except Exception as e:
        return {"status": "error", "detail": str(e)}