import { useEffect, useState } from 'react';
import { fetchMetrics } from '../api';
import { Activity, Database, Zap, AlertCircle, Loader2 } from 'lucide-react';

interface MetricsData {
  clustering: {
    silhouette_score?: number;
    interpretation?: string;
    error?: string;
  };
  classification: {
    standard_accuracy?: number;
    business_accuracy?: number;
    f1_score?: number;
    interpretation?: string;
    error?: string;
  };
  nlp_recommendations: {
    baseline?: {
      precision: number;
      recall: number;
    };
    scentai?: {
      precision: number;
      recall: number;
    };
    error?: string;
  };
}

export default function DevPanel() {
  const [metrics, setMetrics] = useState<MetricsData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const getMetrics = async () => {
      try {
        setLoading(true);
        const response = await fetchMetrics();
        if (response.status === 'success') {
          setMetrics(response.data);
        } else {
          setError(response.detail || 'Wystąpił nieoczekiwany błąd.');
        }
      } catch (err) {
        setError('Nie udało się pobrać metryk systemowych.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    getMetrics();
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
        <Loader2 className="w-12 h-12 text-brand-primary animate-spin" />
        <h2 className="text-xl font-medium text-brand-text">Generowanie raportu z modeli...</h2>
        <p className="text-brand-muted">To może potrwać kilka sekund, ponieważ wykonujemy testy na żywo.</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-red-500 space-y-4">
        <AlertCircle className="w-12 h-12" />
        <h2 className="text-xl font-medium">Błąd systemu</h2>
        <p>{error}</p>
        <button 
          onClick={() => window.location.reload()}
          className="px-4 py-2 bg-brand-primary text-white rounded-md hover:bg-opacity-90 transition-all"
        >
          Spróbuj ponownie
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-brand-text">Panel Deweloperski</h1>
          <p className="text-brand-muted">Monitorowanie wydajności modeli AI i jakości rekomendacji.</p>
        </div>
        <div className="flex items-center space-x-2 bg-green-50 text-green-700 px-3 py-1 rounded-full text-sm font-medium border border-green-200">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
          <span>System Online</span>
        </div>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Klastrowanie */}
        <section className="bg-brand-surface p-6 rounded-xl border border-gray-100 shadow-sm space-y-4">
          <div className="flex items-center space-x-3 text-brand-primary">
            <Database className="w-6 h-6" />
            <h2 className="text-lg font-semibold text-brand-text">Grupowanie (K-Means)</h2>
          </div>
          {metrics?.clustering.error ? (
            <p className="text-red-500 text-sm">{metrics.clustering.error}</p>
          ) : (
            <>
              <div className="space-y-1">
                <span className="text-3xl font-mono font-bold text-brand-text">
                  {metrics?.clustering.silhouette_score}
                </span>
                <p className="text-xs text-brand-muted uppercase tracking-wider">Silhouette Score</p>
              </div>
              <p className="text-sm text-gray-600 leading-relaxed">
                {metrics?.clustering.interpretation}
              </p>
            </>
          )}
        </section>

        {/* Klasyfikacja */}
        <section className="bg-brand-surface p-6 rounded-xl border border-gray-100 shadow-sm space-y-4">
          <div className="flex items-center space-x-3 text-brand-primary">
            <Zap className="w-6 h-6" />
            <h2 className="text-lg font-semibold text-brand-text">Intencje (SVM)</h2>
          </div>
          {metrics?.classification.error ? (
            <p className="text-red-500 text-sm">{metrics.classification.error}</p>
          ) : (
            <>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <span className="text-2xl font-mono font-bold text-brand-text">
                    {metrics?.classification.business_accuracy}%
                  </span>
                  <p className="text-[10px] text-brand-muted uppercase tracking-wider">Business Accuracy</p>
                </div>
                <div className="space-y-1">
                  <span className="text-2xl font-mono font-bold text-brand-text">
                    {metrics?.classification.f1_score}
                  </span>
                  <p className="text-[10px] text-brand-muted uppercase tracking-wider">F1 Score</p>
                </div>
              </div>
              <p className="text-sm text-gray-600 leading-relaxed">
                {metrics?.classification.interpretation}
              </p>
            </>
          )}
        </section>

        {/* NLP Recommendations */}
        <section className="bg-brand-surface p-6 rounded-xl border border-gray-100 shadow-sm space-y-4">
          <div className="flex items-center space-x-3 text-brand-primary">
            <Activity className="w-6 h-6" />
            <h2 className="text-lg font-semibold text-brand-text">Efektywność Wyszukiwania</h2>
          </div>
          {metrics?.nlp_recommendations.error ? (
            <p className="text-red-500 text-sm">{metrics.nlp_recommendations.error}</p>
          ) : (
            <div className="space-y-4">
              <div className="space-y-2">
                <div className="flex justify-between text-xs font-medium uppercase tracking-wider">
                  <span className="text-brand-muted">ScentAI (Hybrydowy)</span>
                  <span className="text-brand-primary">{metrics?.nlp_recommendations.scentai?.precision}%</span>
                </div>
                <div className="w-full bg-gray-100 h-2 rounded-full overflow-hidden">
                  <div 
                    className="bg-brand-primary h-full rounded-full transition-all duration-1000" 
                    style={{ width: `${metrics?.nlp_recommendations.scentai?.precision}%` }}
                  />
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between text-xs font-medium uppercase tracking-wider">
                  <span className="text-brand-muted">Baseline (Regex)</span>
                  <span className="text-gray-500">{metrics?.nlp_recommendations.baseline?.precision}%</span>
                </div>
                <div className="w-full bg-gray-100 h-2 rounded-full overflow-hidden">
                  <div 
                    className="bg-gray-400 h-full rounded-full transition-all duration-1000" 
                    style={{ width: `${metrics?.nlp_recommendations.baseline?.precision}%` }}
                  />
                </div>
              </div>
              <p className="text-[11px] text-brand-muted italic mt-2">
                Metryka Precision@5: procent trafnych nut zapachowych w top 5 wynikach.
              </p>
            </div>
          )}
        </section>
      </div>

      <div className="bg-blue-50 border border-blue-100 p-4 rounded-lg flex items-start space-x-3 text-blue-800">
        <AlertCircle className="w-5 h-5 mt-0.5 flex-shrink-0" />
        <div className="text-sm">
          <p className="font-semibold">Informacja o ewaluacji</p>
          <p className="opacity-90">Testy są przeprowadzane na zestawie 15 scenariuszy testowych (NER + Search). Wyniki odświeżają się przy każdym wejściu do panelu.</p>
        </div>
      </div>
    </div>
  );
}