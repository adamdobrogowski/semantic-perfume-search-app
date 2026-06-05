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
