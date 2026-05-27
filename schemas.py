from pydantic import BaseModel, Field

class UserIntent(BaseModel):
    brands: list[str] = Field(
        default_factory=list, 
        description="Lista marek perfum wymienionych w zapytaniu (np. 'Dior', 'Chanel'). Jeśli brak, zwróć pustą listę."
    )
    explicit_notes: list[str] = Field(
        default_factory=list, 
        description="Konkretne nuty zapachowe, np. 'wanilia', 'drzewo sandałowe'. Jeśli brak, zwróć pustą listę."
    )
    abstract_mood: str | None = Field(
        default=None, 
        description="Abstrakcyjny opis nastroju, okazji lub emocji z zapytania. Jeśli zapytanie jest techniczne, to pole musi być None."
    )
    evidence: str | None = Field(
        default=None,
        description="Cytat z zapytania, który uzasadnia przypisanie pola abstract_mood. Jeśli abstract_mood to None, to pole musi być None."
    )