import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, f1_score, silhouette_score
from schemas import UserIntent
from search_service import search_perfumes

def calculate_business_accuracy(y_true, y_pred):
    """
    Oblicza 'Business Accuracy' z uwzględnieniem wag pomyłek.
    - 1.0 pkt: Pełne trafienie
    - 0.5 pkt: Pomyłka z kategorią 'unisex' (bezpieczna)
    - 0.0 pkt: Pomyłka krytyczna (np. męskie uznane za damskie)
    """
    score = 0.0
    for true_val, pred_val in zip(y_true, y_pred):
        if true_val == pred_val:
            score += 1.0
        elif "and men" in true_val or "and men" in pred_val:
            # Jeśli faktyczny zapach to unisex, albo model przewidział unisex - dajemy 0.5 pkt
            score += 0.5
        else:
            # Błąd krytyczny (np. true='for men', pred='for women')
            score += 0.0
    return (score / len(y_true)) * 100

def run_evaluation(ml_models: dict) -> dict:
    """
    Uruchamia ewaluację wszystkich 3 modeli i zwraca ustandaryzowany słownik
    gotowy do wysłania przez endpoint /api/metrics.
    """
    db = ml_models['database']
    report_data = {
        "clustering": {},
        "classification": {},
        "nlp_recommendations": {}
    }

    # =================================================================
    # 1. EWALUACJA GRUPOWANIA (K-Means - Silhouette Score)
    # =================================================================
    try:
        sample_db = db.dropna(subset=['Embeddings', 'Cluster_ID']).sample(n=min(3000, len(db)), random_state=42)
        embeddings_matrix = np.stack(sample_db['Embeddings'].values)
        cluster_labels = sample_db['Cluster_ID'].values
        
        sil_score = silhouette_score(embeddings_matrix, cluster_labels)
        report_data['clustering'] = {
            "silhouette_score": round(sil_score, 4),
            "interpretation": "Klastry zapachowe są płynne i przenikają się wzajemnie (wynik bliski zera to norma w gęstym NLP)."
        }
    except Exception as e:
        report_data['clustering'] = {"error": str(e)}

    # =================================================================
    # 2. EWALUACJA KLASYFIKACJI (SVM - Cost-Sensitive Accuracy)
    # =================================================================
    print("\n[2/3] Ewaluacja Klasyfikatora Płci (SVM)...")
    svm_test_cases = [
        ("Odpoczynek w klasycznym klubie, paląc cygaro z Dominikany na starej skórzanej kanapie.", "for men"),
        ("Poranne golenie tradycyjną brzytwą u barbera, z dominującą, chłodną nutą dębowego mchu i ostrego cedru.", "for men"),
        ("Wymiana opon w przydomowym garażu, z unoszącym się w powietrzu specyficznym zapachem rozgrzanej gumy.", "for men"),
        ("Wieczorny powrót z lasu, podczas którego na ubraniach roboczych utrzymuje się intensywna woń świeżo rąbanego drewna sosnowego i żywicy.", "for men"),
        ("Poranny makijaż przy eleganckiej toaletce, któremu towarzyszy intensywny, pudrowy zapach rozkruszonego różu do policzków i słodkiej pomadki.", "for women"),
        ("Spacer po ogrodzie, przesiąknięty delikatną, zmysłową wonią białego piżma i róży", "for women"),
        ("Przymierzanie jedwabnej sukni w salonie krawieckim, gdzie w powietrzu wyraźnie dominuje gęsty, upojny zapach białego jaśminu.", "for women"),
        ("Pieczenie owocowej tarty w domowej kuchni, z wyraźnie wyczuwalnym, otulającym aromatem ciepłej wanilii i karmelizowanych malin.", "for women"),
        ("Wiosenne bieganie po miejskim parku w deszczowy dzień, z orzeźwiającym zapachem mokrej trawy i świeżego powietrza.", "for women and men"),
        ("Poranne picie schłodzonej wody z cytryną na słonecznym tarasie, uwalniające rześką, cytrusową nutę i delikatny aromat mięty.", "for women and men"),
        ("Czytanie książki w nowoczesnej, minimalistycznej bibliotece, otulone zapachem czystego papieru i świeżo zaparzonej, zielonej herbaty.", "for women and men"),
        ("Prasowanie wypranych w płatkach mydlanych lnianych koszul, dające poczucie surowej czystości i neutralnego, bawełnianego chłodu.", "for women and men")
    ]
    
    X_texts = [text for text, _ in svm_test_cases]
    y_true = [label for _, label in svm_test_cases]
    
    try:
        # Pamiętamy z błędu z terminala, że SVM oczekuje 384 wektorów z embeddera
        X_vectors = ml_models['embedder'].encode(X_texts)
        y_pred = ml_models['svm'].predict(X_vectors)
        
        standard_acc = accuracy_score(y_true, y_pred) * 100
        business_acc = calculate_business_accuracy(y_true, y_pred)
        f1 = f1_score(y_true, y_pred, average='weighted')
        
        report_data['classification'] = {
            "standard_accuracy": round(standard_acc, 2),
            "business_accuracy": round(business_acc, 2),
            "f1_score": round(f1, 4),
            "interpretation": "Business Accuracy traktuje pomyłki z klasą Unisex jako w połowie trafione (mniejszy koszt biznesowy)."
        }
    except Exception as e:
        report_data['classification'] = {"error": str(e)}

    # =================================================================
    # 3. EWALUACJA REKOMENDACJI NLP (Precision & Recall)
    # =================================================================
    nlp_test_cases = [
        {"query": "zapach mrocznego lasu", "expected": ['woody', 'earthy', 'smoky', 'pine', 'conifer']},
        {"query": "zmysłowe perfumy na wieczorną randkę", "expected": ['vanilla', 'amber', 'warm spicy', 'leather']},
        {"query": "rześki poranek nad morzem", "expected": ['aquatic', 'marine', 'citrus', 'fresh']}
    ]
    
    k = 5
    baseline_precisions, baseline_recalls = [], []
    scentai_precisions, scentai_recalls = [], []
    
    try:
        for test in nlp_test_cases:
            query, expected = test['query'], test['expected']
            total_relevant = sum(1 for _, row in db.iterrows() if any(exp in str(row.get('Clean_Accords', '')).lower() for exp in expected))
            
            # --- BASELINE ---
            mask = db['Description'].str.lower().str.contains(query.lower(), na=False)
            baseline_res = db[mask].head(k)
            baseline_accords = [str(row['Clean_Accords']) for _, row in baseline_res.iterrows()]
            b_hits = sum(1 for acc_str in baseline_accords if any(exp in acc_str.lower() for exp in expected))
            
            baseline_precisions.append((b_hits / k) * 100 if baseline_accords else 0.0)
            baseline_recalls.append((b_hits / total_relevant) * 100 if total_relevant > 0 else 0.0)
            
            # --- SCENT AI ---
            intent = UserIntent(brands=[], explicit_notes=[], abstract_mood=query)
            scentai_results = search_perfumes(intent, ml_models)[:k]
            s_hits = sum(1 for res in scentai_results if any(exp in res.accords.lower() for exp in expected))
            
            scentai_precisions.append((s_hits / k) * 100 if scentai_results else 0.0)
            scentai_recalls.append((s_hits / total_relevant) * 100 if total_relevant > 0 else 0.0)

        report_data['nlp_recommendations'] = {
            "baseline": {
                "precision": round(sum(baseline_precisions) / len(baseline_precisions), 2),
                "recall": round(sum(baseline_recalls) / len(baseline_recalls), 4)
            },
            "scentai": {
                "precision": round(sum(scentai_precisions) / len(scentai_precisions), 2),
                "recall": round(sum(scentai_recalls) / len(scentai_recalls), 4)
            }
        }
    except Exception as e:
        report_data['nlp_recommendations'] = {"error": str(e)}

    return report_data