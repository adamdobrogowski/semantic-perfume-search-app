import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from schemas import UserIntent, PerfumeResult

def search_perfumes(intent: UserIntent, ml_models: dict) -> list[PerfumeResult]:
    db = ml_models['database']
    filtered_db = db.copy()

    filtered_db = filtered_db.dropna(subset=['Clean_Accords'])
    filtered_db = filtered_db[
        (filtered_db['Clean_Accords'].astype(str).str.strip() != '') &
        (filtered_db['Clean_Accords'].astype(str).str.lower() != 'nan')
    ]
    # 1. Filtrowanie po Marce
    if intent.brands:
        brands_lower = [b.lower() for b in intent.brands]
        filtered_db = filtered_db[filtered_db['Brand'].str.lower().isin(brands_lower)]
    
    # 2. Filtrowanie po jawnych nutach
    if intent.explicit_notes:
        masks = []
        for note in intent.explicit_notes:
            note_lower = note.lower()
            mask = (
                filtered_db['Description'].str.lower().str.contains(note_lower, na=False) |
                filtered_db['Clean_Accords'].str.lower().str.contains(note_lower, na=False)
            )
            masks.append(mask)
            
        if masks:
            combined_mask = pd.concat(masks, axis=1).any(axis=1)
            filtered_db = filtered_db[combined_mask]
            
    # 3. Filtrowanie po jawnej płci (Wyciągniętej przez LLM)
    if intent.explicit_gender:
        filtered_db = filtered_db[filtered_db['Gender'] == intent.explicit_gender]
        
    # Jeśli filtry zabiły wszystkie wyniki, zwracamy od razu pustą listę
    if filtered_db.empty:
        return []

    # 4. Wyszukiwanie Semantyczne (SBERT + TF-IDF)
    if intent.abstract_mood:
        embedder = ml_models['embedder']
        tfidf = ml_models['tfidf']
        mood_matrix = ml_models['mood_matrix']

        try:
            query_embedding = embedder.encode(intent.abstract_mood).reshape(1, -1)
            
            db_embeddings = np.stack(filtered_db['Embeddings'].values)
            
            semantic_scores = cosine_similarity(query_embedding, db_embeddings).flatten()
            filtered_db['semantic_score'] = semantic_scores

            query_tfidf = tfidf.transform([intent.abstract_mood])
            moods_tfidf = tfidf.transform(mood_matrix['Nastrój_PL'])
            tfidf_similarities = cosine_similarity(query_tfidf, moods_tfidf).flatten()
            
            best_idx = tfidf_similarities.argmax()
            best_score = tfidf_similarities[best_idx]
            
            target_accords = []
            if best_score > 0.0: 
                target_accords = [a.strip() for a in str(mood_matrix.iloc[best_idx]['Akordy_EN']).split(',')]

            def calculate_mood_accords_score(row):
                if not target_accords: return 0.0
                perfume_accords = [a.strip() for a in str(row.get('Clean_Accords', '')).lower().split(',')]
                if not perfume_accords: return 0.0
                
                score = 0.0
                for expected in target_accords:
                    expected_lower = expected.lower()
                    pos = len(perfume_accords)
                    for i, acc in enumerate(perfume_accords):
                        if expected_lower in acc:
                            pos = i
                            break
                    score += (len(perfume_accords) - pos) / len(perfume_accords)
                return score / len(target_accords)

            filtered_db['tfidf_score'] = filtered_db.apply(calculate_mood_accords_score, axis=1)

            filtered_db['match_score'] = (filtered_db['semantic_score'] * 0.7) + (filtered_db['tfidf_score'] * 0.3)
            
            filtered_db = filtered_db[filtered_db['match_score'] > 0.1]
            filtered_db = filtered_db.sort_values(by='match_score', ascending=False)
            
        except Exception as e:
            print(f"Błąd silnika hybrydowego: {e}")
            filtered_db['match_score'] = 1.0 
    else:
        if intent.explicit_notes:
            def calculate_positional_score(row):
                accords_str = str(row.get('Clean_Accords', '')).lower()
                accords_list = [a.strip() for a in accords_str.split(',')]
                
                if not accords_list: return 0.5 
                
                total_score = 0.0
                for note in intent.explicit_notes:
                    note_lower = note.lower()
                    position = len(accords_list) 
                    for i, accord in enumerate(accords_list):
                        if note_lower in accord:
                            position = i
                            break
                    total_score += (len(accords_list) - position) / len(accords_list)
                return total_score / len(intent.explicit_notes)

            filtered_db['match_score'] = filtered_db.apply(calculate_positional_score, axis=1)
            filtered_db = filtered_db.sort_values(by='match_score', ascending=False)
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