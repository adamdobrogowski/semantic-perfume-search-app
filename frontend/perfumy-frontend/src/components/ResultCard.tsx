import { Sparkles } from 'lucide-react';

interface PerfumeProps {
  name: string;
  brand: string;
  accords: string[];
  similarity: number;
}

export default function ResultCard({ name, brand, accords, similarity }: PerfumeProps) {
  return (
    <div className="bg-brand-surface rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow border border-gray-100 flex flex-col h-full">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-lg font-bold text-brand-text leading-tight">{name}</h3>
          <p className="text-sm text-brand-muted uppercase tracking-wider mt-1">{brand}</p>
        </div>
        <div className="flex items-center bg-brand-bg px-3 py-1 rounded-full border border-gray-200">
          <Sparkles className="w-4 h-4 text-brand-primary mr-2" />
          <span className="text-sm font-mono font-bold text-brand-text">{similarity}%</span>
        </div>
      </div>
      
      <div className="mt-auto pt-4 border-t border-gray-50">
        <div className="flex flex-wrap gap-2">
          {accords.map((accord, index) => (
            <span 
              key={index} 
              className="text-xs px-2 py-1 bg-gray-50 text-brand-text rounded-md border border-gray-100 capitalize"
            >
              {accord}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}