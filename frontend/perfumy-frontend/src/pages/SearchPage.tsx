import { useState } from 'react';
import { Search, SlidersHorizontal, Loader2, AlertCircle } from 'lucide-react';
import ResultCard from '../components/ResultCard';
import { searchPerfumes } from '../api';

interface PerfumeResult {
  name: string;
  brand: string;
  accords: string;
  match_score: number;
}

interface Metadata {
  predicted_gender: string;
  assigned_cluster: string;
}

export default function SearchPage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<PerfumeResult[]>([]);
  const [metadata, setMetadata] = useState<Metadata | null>(null); 
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsLoading(true);
    setError(null);
    setResults([]); 
    setMetadata(null);

    try {
      // Korzystamy z nowej metody komunikacji, którą stworzyłeś
      const response = await searchPerfumes(query);
      
      // Zapisujemy zarówno wyniki jak i metadane z AI!
      setResults(response.results);
      setMetadata(response.metadata);
      
    } catch (err) {
      setError("Nie udało się połączyć z modelem ScentAI");
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto p-4 sm:p-6 lg:p-8">
      <div className="text-center mb-12 mt-8">
        <h1 className="text-3xl md:text-4xl font-sans font-bold text-brand-text mb-4 tracking-tight">
          Odkryj swój idealny zapach
        </h1>
        <p className="text-brand-muted mb-8 text-lg">
          Opisz, czego szukasz, np. "chłodny, mglisty poranek w lesie"...
        </p>

        <form onSubmit={handleSearch} className="relative max-w-3xl mx-auto">
          <div className="absolute inset-y-0 left-0 pl-5 flex items-center pointer-events-none">
            <Search className="h-6 w-6 text-brand-muted" />
          </div>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            disabled={isLoading}
            className="block w-full pl-14 pr-32 py-5 bg-brand-surface border border-gray-200 rounded-2xl text-brand-text focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-transparent shadow-sm transition-all hover:shadow-md text-lg disabled:opacity-50"
            placeholder="Jak chcesz dzisiaj pachnieć?"
          />
          <div className="absolute inset-y-0 right-2 flex items-center">
            <button 
              type="submit"
              disabled={isLoading || !query.trim()}
              className="bg-brand-text hover:bg-black text-white px-6 py-3 rounded-xl font-medium transition-colors disabled:opacity-50 disabled:hover:bg-brand-text"
            >
              Szukaj
            </button>
          </div>
        </form>
      </div>

      <div className="flex flex-col lg:flex-row gap-8">
        <div className="w-full lg:w-64 flex-shrink-0">
          <div className="bg-brand-surface rounded-xl p-6 border border-gray-100 shadow-sm sticky top-24">
            <div className="flex items-center mb-2">
              <SlidersHorizontal className="w-5 h-5 text-brand-primary mr-2" />
              <h2 className="font-bold text-brand-text">Analiza AI</h2>
            </div>
            <p className="text-xs text-brand-muted mb-6">
              Wnioski wygenerowane automatycznie na podstawie Twojego zapytania.
            </p>

            <div className="space-y-6">
              {/* Sekcja 1: Wykryta Płeć */}
              <div>
                <h3 className="text-xs font-bold text-brand-text uppercase tracking-widest border-b border-gray-100 pb-2 mb-3">
                  Wykryta Płeć
                </h3>
                <div className="flex flex-col gap-2">
                  {[
                    { label: 'Damskie', id: 'for women' },
                    { label: 'Unisex', id: 'for women and men' },
                    { label: 'Męskie', id: 'for men' }
                  ].map((gender) => {
                    // Sprawdzamy czy AI przewidziało tę konkretną płeć
                    const isActive = metadata?.predicted_gender === gender.id;
                    
                    return (
                      <div 
                        key={gender.id} 
                        className={`px-3 py-2 rounded-lg border text-sm font-medium transition-all ${
                          isActive 
                            ? 'bg-brand-primary/10 border-brand-primary text-brand-primary' 
                            : 'bg-gray-50 border-gray-100 text-gray-400'
                        }`}
                      >
                        {gender.label}
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Sekcja 2: Wykryty Profil (K-Means) */}
              {metadata?.assigned_cluster && (
                <div>
                  <h3 className="text-xs font-bold text-brand-text uppercase tracking-widest border-b border-gray-100 pb-2 mb-3 mt-4">
                    Profil Zapachowy
                  </h3>
                  <div className="px-3 py-2 bg-gradient-to-r from-gray-50 to-gray-100 border border-gray-200 rounded-lg">
                     <span className="text-sm font-bold text-brand-text">
                       {metadata.assigned_cluster}
                     </span>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="flex-1">
          {isLoading && (
            <div className="flex flex-col items-center justify-center py-20 animate-pulse">
              <Loader2 className="w-12 h-12 text-brand-primary animate-spin mb-4" />
              <p className="text-brand-text font-medium text-lg text-center">
                Analizuje semantykę zapytania i generowanie rekomendacji...
              </p>
            </div>
          )}

          {error && (
            <div className="bg-red-50 border border-red-100 rounded-xl p-8 text-center flex flex-col items-center justify-center">
              <AlertCircle className="w-12 h-12 text-red-400 mb-4" />
              <h3 className="text-lg font-bold text-red-800 mb-2">{error}</h3>
              <p className="text-red-600 text-sm">Upewnij się, że backend FastAPI jest uruchomiony.</p>
            </div>
          )}

          {!isLoading && !error && results.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {results.map((perfume, index) => (
                <ResultCard 
                  key={index}
                  name={perfume.name} 
                  brand={perfume.brand} 
                  accords={perfume.accords} 
                  match_score={perfume.match_score} 
                />
              ))}
            </div>
          )}

          {!isLoading && !error && results.length === 0 && (
            <div className="flex flex-col items-center justify-center py-20 text-brand-muted border-2 border-dashed border-gray-100 rounded-xl">
              <Search className="w-8 h-8 mb-3 opacity-20" />
              <p>Wpisz zapytanie, aby zobaczyć rekomendacje ScentAI.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}