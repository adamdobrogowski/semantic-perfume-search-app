from pydantic import BaseModel, Field

class UserIntent(BaseModel):
    brands: list[str] = Field(
        default_factory=list, 
        description="Lista marek perfum wymienionych w zapytaniu. Jeśli brak, zwróć pustą listę."
    )
    explicit_notes: list[str] = Field(
        default_factory=list, 
        description="Konkretne nuty zapachowe z zapytania, PRZETŁUMACZONE NA JĘZYK ANGIELSKI. Jeśli brak, pusta lista."
    )
    abstract_mood: str | None = Field(
        default=None, 
        description="Abstrakcyjny opis nastroju, emocji lub sytuacji (np. 'mroczny las', 'do biura'). Jeśli zapytanie jest techniczne, to pole musi być None."
    )
    evidence: str | None = Field(
        default=None,
        description="Cytat z zapytania, który uzasadnia przypisanie pola abstract_mood."
    )

class PerfumeResult(BaseModel):
    name: str
    brand: str
    accords: str
    match_score: float