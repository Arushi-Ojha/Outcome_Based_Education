const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

/**
 * Check connectivity to the backend API.
 * Uses both direct API URL and fallback to proxy path if needed.
 */
export async function checkBackendHealth() {
  const endpoints = [
    `${API_BASE_URL}/api/health`,
    `${API_BASE_URL}/`,
    '/api/health',
  ];

  let lastError = null;

  for (const url of endpoints) {
    try {
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        return {
          success: true,
          endpoint: url,
          data,
        };
      }
    } catch (err) {
      lastError = err;
    }
  }

  return {
    success: false,
    error: lastError ? lastError.message : 'Unable to connect to backend server',
  };
}

export { API_BASE_URL };
