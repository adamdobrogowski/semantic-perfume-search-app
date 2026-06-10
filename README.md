# Przewodnik po aplikacji

## Aplikacja oferuje trzy główne moduły:

**Inteligentna Wyszukiwarka (GłÓWNY MODUŁ):** Wpisz w pasek wyszukiwania zapytanie naturalne (np. "zmysłowe perfumy na wieczorną randkę" lub "spacer nad morzem"). Zaimplementowany model SVM automatycznie rozpozna intencję płci (Męskie/Damskie/Unisex) i zastosuje odpowiednie filtry, a silnik hybrydowy (SBERT + TF-IDF) zwróci 10 najtrafniejszych propozycji.

Link do filmu przedstawiającego działanie aplikacji: https://www.youtube.com/watch?v=Zmm_-ld_GUQ

<img width="1138" height="808" alt="image" src="https://github.com/user-attachments/assets/9f0d1d3d-8479-46d0-af6b-b57994047fe4" />

**Eksplorator Danych (Dashboard z klastrami perfum):** Przejdź do zakładki z wizualizacjami, aby zobaczyć rozkład zapachów w naszej bazie. Mapa 2D (wygenerowana dzięki redukcji PCA) prezentuje grupy zapachowe wyznaczone algorytmem K-Means na macierzy TF-IDF. Umożliwia to wizualną analizę podobieństw między poszczególnymi profilami zapachowymi.

<img width="1134" height="890" alt="image" src="https://github.com/user-attachments/assets/6dd070ca-f736-4906-8c02-4164471a1ae9" />

**Panel Deweloperski (Ewaluacja):** Zakładka przeznaczona do monitorowania efektywności modeli w czasie rzeczywistym. Wyświetla ona autorską metrykę Business Accuracy dla klasyfikatora intencji, Silhouette Score dla jakości klastrów oraz surową skuteczność wyszukiwania NLP (Precision@5), porównując autorski algorytm hybrydowy ScentAI z klasycznym wyszukiwaniem opartym na wyrażeniach regularnych.

<img width="1204" height="895" alt="image" src="https://github.com/user-attachments/assets/78453a73-51f8-4600-aa29-5eeb6b4e035a" />

## Baza  Danych
Bazę danych stanowi plik CSV, który zawiera bazę perfum z portalu Fragrantica. Zbiór ten został oczyszczony oraz przystosowany na potrzeby naszego projektu.



# Instrukcja uruchomienia projektu

## Krok 1: Przygotowanie struktury projektu

Upewnij się, że w głównym folderze projektu (tam, gdzie masz plik `main.py`) znajdują się:

- Folder `data/`
- Plik `requirements.txt`

---

## Krok 2: Konfiguracja Backend'u (Python)

Otwórz terminal w głównym folderze projektu.

### Stwórz wirtualne środowisko

```bash
python -m venv venv
```

### Aktywuj je

**Windows**

```bash
venv\Scripts\activate
```

**macOS/Linux**

```bash
source venv/bin/activate
```

### Zaktualizuj pip i pobierz biblioteki

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Konfiguracja klucza API

Upewnij się, że plik `.env` istnieje w głównym folderze i zawiera Twój klucz API:

```env
GOOGLE_API_KEY=twoj_klucz_tutaj
```

---

## Krok 3: Generowanie Modeli

Uruchom cały notatnik:

```text
data_modeling_and_nlp.ipynb
```

---

## Krok 4: Uruchomienie Backend'u

W terminalu (z wciąż aktywnym `venv`):

```bash
uvicorn main:app --reload
```

---

## Krok 5: Uruchomienie Frontend'u

```bash
cd frontend/perfumy-frontend
npm install
npm run dev
```

