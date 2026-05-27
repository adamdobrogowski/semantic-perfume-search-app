import { Link, useLocation } from 'react-router-dom';
import { Search, BarChart2, Settings } from 'lucide-react';

export default function Layout({ children }: { children: React.ReactNode }) {
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Wyszukiwarka', icon: Search },
    { path: '/dashboard', label: 'Eksploracja Danych', icon: BarChart2 },
    { path: '/dev', label: 'Panel Deweloperski', icon: Settings },
  ];

  return (
    <div className="min-h-screen bg-brand-bg font-sans text-brand-text flex flex-col">
      {/* Pasek nawigacji */}
      <nav className="bg-brand-surface border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <span className="text-xl font-bold tracking-widest uppercase">
                Scent<span className="text-brand-primary">AI</span>
              </span>
            </div>
            <div className="flex space-x-8">
              {navItems.map((item) => {
                const isActive = location.pathname === item.path;
                const Icon = item.icon;
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors ${
                      isActive
                        ? 'border-brand-primary text-brand-text'
                        : 'border-transparent text-brand-muted hover:border-gray-300 hover:text-gray-700'
                    }`}
                  >
                    <Icon className="w-4 h-4 mr-2" />
                    {item.label}
                  </Link>
                );
              })}
            </div>
          </div>
        </div>
      </nav>

      {/* Główna zawartość strony */}
      <main className="flex-1 w-full max-w-6xl mx-auto py-8">
        {children}
      </main>
    </div>
  );
}