from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import pandas as pd
import joblib
import os 
from dotenv import load_dotenv

import __main__
from schemas import UserIntent, PerfumeResult
from ai_service import analyze_query_with_llm
from search_service import search_perfumes

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
        
        print("Serwer gotowy do przyjmowania zapytań!")
        
        # Oddanie kontroli do FastAPI
        yield 
    
    except FileNotFoundError as e:
        print(f"BŁĄD: Nie znaleziono pliku modelu! Upewnij się, że folder 'modele' istnieje.")
        print(f"Szczegóły: {e}")
        raise e
    finally:
        ml_models.clear()
        print("Serwer zamknięty, pamięć wyczyszczona.")

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

# ENDPOINTY BAZOWE
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
    
@app.post('/api/search', response_model=list[PerfumeResult])
async def search_endpoint(query: str):
    """
    Główny produkcyjny endpoint wyszukiwarki. 
    Łączy rozumienie języka (Gemini) z przeszukiwaniem wektorowej bazy (Pandas).
    """
    if not ml_models:
        raise HTTPException(status_code=503, detail="Modele AI ładują się. Spróbuj za chwilę.")

    try:
        intent = analyze_query_with_llm(query)
        results = search_perfumes(intent, ml_models)
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Wewnętrzny błąd wyszukiwarki: {str(e)}")