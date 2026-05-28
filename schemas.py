from pydantic import BaseModel, Field

class UserIntent(BaseModel):
    brands: list[str] = Field(
        default_factory=list, 
        description="Lista marek perfum wymienionych w zapytaniu. Jeśli brak, zwróć pustą listę."
    )
    explicit_notes: list[str] = Field(
        default_factory=list, 
        description="Konkretne nuty zapachowe z zapytania, przetłumaczone na angielski. Jeśli brak, pusty."
    )
    abstract_mood: str | None = Field(
        default=None, 
        description="Abstrakcyjny opis nastroju, okazji lub emocji. Jeśli zapytanie jest techniczne, to pole musi być None."
    )
    evidence: str | None = Field(
        default=None,
        description="Cytat z zapytania, który uzasadnia przypisanie pola abstract_mood. Jeśli abstract_mood to None, to pole musi być None."
    )

class PerfumeResult(BaseModel):
    name: str
    brand: str
    accords: str
    match_score: float # Procentowe dopasowanie nastroju