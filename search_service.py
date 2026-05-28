import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from schemas import UserIntent, PerfumeResult

def search_perfumes(intent: UserIntent, ml_models: dict) -> list[PerfumeResult]:
    """
    Główny silnik filtrujący i obliczający prawdopodobieństwo semantyczne.
    Odbiera wstrzyknięty obiekt użytkownika oraz słownik z modelami ML.
    """
    db = ml_models['database']

    filtered_db = db.copy()

    if intent.brands:
        brands_lower = [b.lower() for b in intent.brands]
        filtered_db = filtered_db[filtered_db['Brand'].str.lower().isin(brands_lower)]
    
    if intent.explicit_notes:
        for note in intent.explicit_notes:
            note_lower = note.lower()
            mask = (
                filtered_db['Description'].str.lower().str.contains(note_lower, na=False) |
                filtered_db['Clean_Accords'].str.lower().str.contains(note_lower, na=False)
            )
            filtered_db = filtered_db[mask]
        
    if filtered_db.empty:
        return []
    
    if intent.abstract_mood:
        tfidf = ml_models['tfidf']
        mood_matrix = ml_models['mood_matrix']

        try:
            query_tfidf = tfidf.transform([intent.abstract_mood])
            
            query_embedding = query_tfidf.dot(mood_matrix)
            
            db_embeddings = np.stack(filtered_db['Embeddings'].values)
            
            similarities = cosine_similarity(query_embedding, db_embeddings).flatten()
            
            filtered_db['match_score'] = similarities
            
            filtered_db = filtered_db.sort_values(by='match_score', ascending=False)
        except Exception as e:
            print(f"Błąd podczas liczenia wektorów: {e}")
            filtered_db['match_score'] = 1.0 
    else:
        filtered_db['match_score'] = 1.0

    top_results = filtered_db.head(10) 
    
    results = []
    for _, row in top_results.iterrows():
        score = row.get('match_score', 1.0)
        results.append(
            PerfumeResult(
                name=row.get('Name', 'Brak nazwy'),
                brand=row.get('Brand', 'Brak marki'),
                accords=row.get('Clean_Accords', 'Brak akordów'),
                match_score=round(float(score) * 100, 2) 
            )
        )

    return results

