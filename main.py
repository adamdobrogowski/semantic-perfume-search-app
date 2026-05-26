from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import pandas as pd
import joblib
import os 
from dotenv import load_dotenv

import __main__

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

@app.get("/api/debug-models")
async def debug_models():
    """Tymczasowy endpoint do testowania, czy modele ML poprawnie liczą dane."""
    try:
        # 1. Test Bazy Danych
        db = ml_models['database']
        first_perfume = db.iloc[0] # Pobieramy pierwszy wiersz (pierwsze perfumy w bazie)
        perfume_name = first_perfume.get('Name', 'Brak nazwy')
        
        # 2. Test wektoryzatora TF-IDF
        tfidf = ml_models['tfidf']
        test_text = "eleganckie spotkanie biznesowe"
        # Próbujemy wektoryzować tekst
        tfidf_vector = tfidf.transform([test_text])
        recognized_words = tfidf_vector.nnz # Ilość słów, które model rozpoznał ze słownika
        
        # 3. Test klasyfikatora SVM
        svm = ml_models['svm']
        # Pobieramy 384-wymiarowy wektor pierwszych perfum
        sample_embedding = first_perfume['Embeddings']
        # Każemy SVM przewidzieć, czy to zapach męski, damski czy unisex
        prediction = svm.predict([sample_embedding])[0]
        
        return {
            "status": "SUKCES - Modele działają i liczą poprawnie!",
            "test_bazy": {
                "pierwsze_perfumy": perfume_name,
                "wymiar_bazy": f"{db.shape[0]} wierszy, {db.shape[1]} kolumn"
            },
            "test_tfidf": {
                "tekst_wejsciowy": test_text,
                "rozpoznane_slowa": recognized_words
            },
            "test_svm": {
                "testowane_perfumy": perfume_name,
                "predykcja_plci_przez_svm": str(prediction)
            }
        }
    except Exception as e:
        # Jeśli coś wybuchnie, dostaniemy dokładny powód
        return {"status": "BŁĄD", "szczegoly": str(e)}