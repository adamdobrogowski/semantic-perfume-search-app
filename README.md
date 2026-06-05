# Nazwa Projektu

Opis Twojego projektu (dodaj tutaj krótki opis, co robi ta aplikacja).

## 🚀 Instalacja i Konfiguracja

Postępuj zgodnie z poniższymi krokami, aby poprawnie skonfigurować środowisko i uruchomić projekt.

### Krok 1: Przygotowanie struktury projektu
Upewnij się, że w głównym katalogu projektu znajdują się odpowiednie foldery i pliki:

* `data/` - folder zawierający bazę danych (np. `perfumes.csv`).
* `notebooks/` - folder zawierający pliki `.ipynb` do przetwarzania danych.
* `models/` - folder na wytrenowane modele.
* `requirements.txt` - plik z zależnościami Pythona.

### Krok 2: Konfiguracja Backend'u
Otwórz terminal w głównym folderze projektu i wykonaj następujące polecenia:

1.  **Stwórz wirtualne środowisko:**
    ```bash
    python -m venv venv
    ```

2.  **Aktywuj wirtualne środowisko:**
    * **Windows:**
        ```bash
        venv\Scripts\activate
        ```
    * **macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```

3.  **Zainstaluj zależności:**
    ```bash
    pip install --upgrade pip
    pip install -r requirements.txt
    ```

4.  **Konfiguracja zmiennych środowiskowych:**
    Utwórz plik `.env` w głównym folderze i dodaj swój klucz API:
    ```env
    GOOGLE_API_KEY=twoj_klucz_tutaj
    ```

### Krok 3: Generowanie Modeli
Kolejność uruchamiania notatników jest kluczowa. Uruchom Jupyter Notebook (`jupyter notebook`) i wykonaj pliki w następującej kolejności:

1.  **`01_data_cleaning.ipynb`**: Wczytuje dane, czyści wartości `NaN` i normalizuje tekst. Zapisuje `cleaned_perfumes.pkl` w folderze `data/`.
2.  **`02_embeddings_generation.ipynb`**: Generuje wektory SBERT (`paraphrase-multilingual-MiniLM-L12-v2`). Tworzy bazę wektorową dla `search_service.py`.
3.  **`03_ml_training.ipynb`**: Trenuje model SVM (klasyfikacja płci) oraz K-Means (grupowanie akordów). Zapisuje modele jako pliki `.joblib` w folderze `models/`.
4.  **`04_pca_reduction.ipynb`**: Redukuje wymiary danych (PCA_X, PCA_Y) do wizualizacji. Aktualizuje bazę perfum o współrzędne.

### Krok 4: Uruchomienie Backend'u
Będąc w głównym folderze (z aktywnym środowiskiem `venv`), uruchom serwer:

```bash
uvicorn main:app --reload
