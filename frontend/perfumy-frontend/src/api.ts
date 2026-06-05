const BASE_URL = 'http://127.0.0.1:8000/api';

/**
 * 1. Pobieranie Metryk (Dla zakładki DevPanel)
 * Endpoint: GET /api/metrics
 */
export const fetchMetrics = async () => {
    try {
        const response = await fetch(`${BASE_URL}/metrics`);
        if (!response.ok) throw new Error(`Błąd HTTP: ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error("Błąd pobierania metryk:", error);
        throw error;
    }
};

/**
 * 2. Pobieranie Klastrów (Dla zakładki DataDashboard)
 * Endpoint: GET /api/clusters
 */
export const fetchClusters = async (limit: number = 300) => {
    try {
        const response = await fetch(`${BASE_URL}/clusters?limit=${limit}`);
        if (!response.ok) throw new Error(`Błąd HTTP: ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error("Błąd pobierania klastrów:", error);
        throw error;
    }
};

/**
 * 3. Wyszukiwanie Perfum (Dla zakładki SearchPage)
 * Endpoint: POST /api/search
 * Uwaga: FastAPI oczekuje 'query' jako parametru URL, dlatego używamy encodeURIComponent
 */
export const searchPerfumes = async (query: string) => {
    try {
        const response = await fetch(`${BASE_URL}/search?query=${encodeURIComponent(query)}`, {
            method: 'POST',
            headers: { 
                'Accept': 'application/json',
                'Content-Type': 'application/json' 
            }
        });
        
        if (!response.ok) throw new Error(`Błąd HTTP: ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error("Błąd wyszukiwania:", error);
        throw error;
    }
};