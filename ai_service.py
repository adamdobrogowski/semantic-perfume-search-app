import os 
from dotenv import load_dotenv
from google import genai 
import instructor
from schemas import UserIntent

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print('UWAGA: Brak klucza GEMINI_API_KEY w pliku .env')

google_client = genai.Client(api_key=api_key)

llm_client = instructor.from_genai(
    client=google_client,
    mode=instructor.Mode.GENAI_STRUCTURED_OUTPUTS,
)

SCENT_AI_SYSTEM_PROMPT = """Jesteś zaawansowanym systemem ekstrakcji danych NLP (Named Entity Recognition), specjalizującym się w branży perfumiarskiej. 
Twoim wyłącznym zadaniem jest analiza zapytań użytkowników i wyciąganie twardych danych bez ich interpretacji.

### ZASADY EKSTRAKCJI I DEFINICJE PÓL
1. brands: Dokładne nazwy marek perfum. Poprawiaj literówki (np. "szanel" -> "Chanel").
2. explicit_notes: Konkretne, fizyczne nuty zapachowe. ZASADA BEZWZGLĘDNA: Przetłumacz je od razu na angielski (np. "róża" -> "rose").
3. abstract_mood: Abstrakcyjny opis nastroju lub okazji (np. "eleganckie", "mroczny las"). Wyciągnij ten fragment z zapytania użytkownika.
4. evidence: Dosłowny cytat uzasadniający przypisanie nastroju.

### REGUŁY KRYTYCZNE (ZERO HALUCYNACJI)
- Nie dopowiadaj, nie zgaduj ani nie interpretuj intencji.
- Jeśli zapytanie ma charakter czysto techniczny i nie zawiera nastroju, pola abstract_mood oraz evidence muszą wynosić null.

### PRZYKŁADY WZORCOWE
Input: "Szukam czegoś eleganckiego od Diora na randkę, z wanilią"
Output: {"brands": ["Dior"], "explicit_notes": ["vanilla"], "abstract_mood": "eleganckie na randkę", "evidence": "czegoś eleganckiego od Diora na randkę"}

Input: "zapach mrocznego lasu"
Output: {"brands": [], "explicit_notes": [], "abstract_mood": "zapach mrocznego lasu", "evidence": "zapach mrocznego lasu"}
"""

def analyze_query_with_llm(query: str) -> UserIntent:
    """
    Wysyła zapytanie użytkownika do modelu LLM i wymusza zwrot danych 
    zgodnie z kontraktem (UserIntent).
    """
    response = llm_client.messages.create(
        model="gemini-3.5-flash", 
        messages=[
            {
                "role": "system",
                "content": SCENT_AI_SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": f"Przeanalizuj to zapytanie użytkownika: '{query}'"
            }
        ],
        response_model=UserIntent,
        max_retries=1, 
    )
    return response