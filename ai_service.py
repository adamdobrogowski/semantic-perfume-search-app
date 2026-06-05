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
    5. explicit_gender: Jeśli użytkownik JAWNIE określa płeć, przypisz odpowiednią kategorię:
    - Słowa "męskie", "dla niego", "dla mężczyzny", "męski" -> "for men"
    - Słowa "damskie", "dla niej", "dla kobiet", "damski" -> "for women"
    - Słowa "unisex", "uniwersalne", "dla obojga" -> "for women and men"
    Jeśli brakuje informacji o płci, ZWRÓĆ BEZWZGLĘDNIE null.

    ### REGUŁY KRYTYCZNE (ZERO HALUCYNACJI)
    - Nie dopowiadaj, nie zgaduj ani nie interpretuj intencji (od tego jest inny model w systemie).
    - Jeśli zapytanie ma charakter czysto techniczny i nie zawiera nastroju, pola abstract_mood oraz evidence muszą wynosić null.

    ### PRZYKŁADY WZORCOWE
    Input: "Szukam czegoś eleganckiego od Diora na randkę, z wanilią"
    Output: {"brands": ["Dior"], "explicit_notes": ["vanilla"], "abstract_mood": "eleganckie na randkę", "evidence": "czegoś eleganckiego od Diora na randkę", "explicit_gender": null}

    Input: "zapach mrocznego lasu dla mężczyzny"
    Output: {"brands": [], "explicit_notes": [], "abstract_mood": "zapach mrocznego lasu", "evidence": "zapach mrocznego lasu", "explicit_gender": "for men"}

    Input: "damskie perfumy z nutą truskawki"
    Output: {"brands": [], "explicit_notes": ["strawberry"], "abstract_mood": null, "evidence": null, "explicit_gender": "for women"} """

def analyze_query_with_llm(query: str) -> UserIntent:
    """
    Wysyła zapytanie użytkownika do modelu LLM i wymusza zwrot danych 
    zgodnie z kontraktem (UserIntent).
    """
    response = llm_client.messages.create(
        model="gemini-3.1-flash-lite", 
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