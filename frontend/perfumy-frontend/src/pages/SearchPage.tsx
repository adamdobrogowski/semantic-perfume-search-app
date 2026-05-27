import { Search, SlidersHorizontal } from 'lucide-react';
import ResultCard from '../components/ResultCard';

export default function SearchPage() {
  return (
    <div className="max-w-5xl mx-auto p-4 sm:p-6 lg:p-8">
      {/* Sekcja 1: Główne pole wyszukiwania wzorowane na AI */}
      <div className="text-center mb-12 mt-8">
        <h1 className="text-3xl md:text-4xl font-sans font-bold text-brand-text mb-4 tracking-tight">
          Odkryj swój idealny zapach
        </h1>
        <p className="text-brand-muted mb-8 text-lg">
          Opisz, czego szukasz, np. "elegancki zapach na zimową randkę" lub "świeży las po burzy"...
        </p>

        <div className="relative max-w-3xl mx-auto">
          <div className="absolute inset-y-0 left-0 pl-5 flex items-center pointer-events-none">
            <Search className="h-6 w-6 text-brand-muted" />
          </div>
          <input
            type="text"
            className="block w-full pl-14 pr-32 py-5 bg-brand-surface border border-gray-200 rounded-2xl text-brand-text focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-transparent shadow-sm transition-all hover:shadow-md text-lg"
            placeholder="Jak chcesz dzisiaj pachnieć?"
          />
          <div className="absolute inset-y-0 right-2 flex items-center">
            <button className="bg-brand-text hover:bg-black text-white px-6 py-3 rounded-xl font-medium transition-colors">
              Szukaj
            </button>
          </div>
        </div>
      </div>

      <div className="flex flex-col lg:flex-row gap-8">
        {/* Sekcja 2: Panel boczny - Smart Filters */}
        <div className="w-full lg:w-64 flex-shrink-0">
          <div className="bg-brand-surface rounded-xl p-6 border border-gray-100 shadow-sm sticky top-24">
            <div className="flex items-center mb-2">
              <SlidersHorizontal className="w-5 h-5 text-brand-primary mr-2" />
              <h2 className="font-bold text-brand-text">Smart Filters</h2>
            </div>
            <p className="text-xs text-brand-muted mb-6">
              Zaznaczane automatycznie przez model AI na podstawie Twojego opisu.
            </p>

            {/* Kategoria: Płeć (Filtry są na razie zablokowane dla użytkownika) */}
            <div className="space-y-4">
              <h3 className="text-xs font-bold text-brand-text uppercase tracking-widest border-b border-gray-100 pb-2">
                Rozpoznana Płeć
              </h3>
              <div className="space-y-3">
                {['Damskie', 'Męskie', 'Unisex'].map((gender) => (
                  <label key={gender} className="flex items-center space-x-3 cursor-not-allowed opacity-60">
                    <input
                      type="checkbox"
                      disabled
                      className="form-checkbox h-4 w-4 text-brand-primary border-gray-300 rounded focus:ring-brand-primary disabled:bg-gray-100"
                    />
                    <span className="text-sm font-medium text-brand-text">{gender}</span>
                  </label>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Sekcja 3: Siatka wyników (Mockup dla Task 3.3) */}
        <div className="flex-1">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <ResultCard 
              name="Black Oudh" 
              brand="Al Haramain Perfumes" 
              accords={['woody', 'powdery', 'musky']} 
              similarity={94} 
            />
            <ResultCard 
              name="9am Dive" 
              brand="Afnan" 
              accords={['fruity', 'woody', 'green']} 
              similarity={88} 
            />
          </div>
        </div>
      </div>
    </div>
  );
}