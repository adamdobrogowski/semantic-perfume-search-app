import { useState, useEffect } from 'react';
import axios from 'axios';
import { fetchClusters } from '../api';
import { 
  ScatterChart, Scatter, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, Legend 
} from 'recharts';
import { Loader2, AlertCircle, Info } from 'lucide-react';

interface ClusterPoint {
  id: string;
  name: string;
  brand: string;
  cluster: string;
  x: number;
  y: number;
}

const BASE_PALETTE = [
  "#264653", "#2a9d8f", "#e9c46a", "#f4a261", "#e76f51", 
  "#8A9A86", "#DDBEA9", "#5C4D42", "#a8dadc", "#457b9d"
];

const CustomTooltip = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div className="bg-brand-surface p-4 border border-gray-100 rounded-xl shadow-lg max-w-xs z-50">
        <p className="font-bold text-brand-text mb-1">{data.name}</p>
        <p className="text-xs text-brand-muted uppercase tracking-wider mb-3">{data.brand}</p>
        <span className="inline-block px-3 py-1 bg-gray-50 text-xs font-medium text-brand-text rounded-full border border-gray-200">
          Grupa zapachowa: {data.cluster}
        </span>
      </div>
    );
  }
  return null;
};

export default function DataDashboard() {
  const [data, setData] = useState<ClusterPoint[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadClusters = async () => {
      try {
        setIsLoading(true);
        const response = await fetchClusters(500);
        
        setData(response.data || response);
      } catch (err: any) {
        setError("Błąd połączenia z serwerem. Upewnij się, że FastAPI działa.");
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };

    loadClusters();
  }, []);

  const groupedData = data.reduce((acc, point) => {
    if (!acc[point.cluster]) acc[point.cluster] = [];
    acc[point.cluster].push(point);
    return acc;
  }, {} as Record<string, ClusterPoint[]>);

  const clusterNames = Object.keys(groupedData);
  const dynamicColorMap: Record<string, string> = {};
  
  clusterNames.forEach((clusterName, index) => {
    dynamicColorMap[clusterName] = BASE_PALETTE[index % BASE_PALETTE.length];
  });

  return (
    <div className="max-w-6xl mx-auto p-4 sm:p-6 lg:p-8">
      <div className="mb-10">
        <h1 className="text-3xl font-sans font-bold text-brand-text mb-2">
          Mapa Przestrzeni Semantycznej
        </h1>
        <p className="text-brand-muted flex items-center">
          <Info className="w-4 h-4 mr-2" />
          Każdy punkt to perfumy. Klastry (galaktyki) wyznaczane są na podstawie odległości wektorowych ich nut zapachowych.
        </p>
      </div>

      <div className="bg-brand-surface rounded-2xl p-6 shadow-sm border border-gray-100 min-h-[600px] flex flex-col relative overflow-hidden">
        {isLoading && (
          <div className="absolute inset-0 flex flex-col items-center justify-center bg-brand-surface/80 z-10 animate-pulse">
            <Loader2 className="w-12 h-12 text-brand-primary animate-spin mb-4" />
            <p className="text-brand-text font-medium">Renderowanie przestrzeni wektorowej...</p>
          </div>
        )}

        {error && (
          <div className="flex-1 flex flex-col items-center justify-center text-center">
            <AlertCircle className="w-12 h-12 text-red-400 mb-4" />
            <h3 className="text-lg font-bold text-red-800 mb-2">Błąd wczytywania klastrów</h3>
            <p className="text-red-600 text-sm">{error}</p>
          </div>
        )}
        
        {!isLoading && !error && data.length === 0 && (
          <div className="absolute inset-0 flex flex-col items-center justify-center bg-brand-surface z-10">
            <Info className="w-12 h-12 text-brand-muted mb-4 opacity-50" />
            <h3 className="text-lg font-bold text-brand-text mb-2">Brak punktów do wyświetlenia</h3>
            <p className="text-brand-muted text-sm">Serwer zwrócił sukces, ale przefiltrowana baza nie zawiera elementów.</p>
          </div>
        )}

        {!isLoading && !error && data.length > 0 && (
          <div className="w-full" style={{ height: "600px", minHeight: "600px" }}>
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                {/* Zaktualizowane osie łapiące ujemne współrzędne PCA */}
                <XAxis type="number" dataKey="x" name="PCA 1" hide={true} domain={['auto', 'auto']} />
                <YAxis type="number" dataKey="y" name="PCA 2" hide={true} domain={['auto', 'auto']} />
                
                <Tooltip content={<CustomTooltip />} cursor={{ strokeDasharray: '3 3', stroke: '#e5e7eb' }} />
                <Legend iconType="circle" wrapperStyle={{ paddingTop: '20px' }} />
                
                {clusterNames.map((clusterName) => (
                  <Scatter 
                    key={clusterName} 
                    name={clusterName} 
                    data={groupedData[clusterName]} 
                    fill={dynamicColorMap[clusterName]}
                  >
                    {groupedData[clusterName].map((_, index) => (
                      <Cell 
                        key={`cell-${index}`} 
                        fill={dynamicColorMap[clusterName]} 
                      />
                    ))}
                  </Scatter>
                ))}
              </ScatterChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </div>
  );
}