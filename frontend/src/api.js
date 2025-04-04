// Configuration
const API_CONFIG = {
  baseUrl: process.env.NODE_ENV === 'development'
    ? 'http://localhost:5000/api'
    : '/api',
  timeout: 10000
};

// api.js
const API_BASE = 'http://localhost:5000/api';


export const getPlayerNames = async () => {
  const response = await fetch(`${API_BASE}/players`);
  if (!response.ok) {
    throw new Error('Failed to fetch player names');
  }
  return response.json();
};

export const analyzeGame = async (gameId) => {
  const response = await fetch(`${API_BASE}/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ game_id: gameId })
  });
  
  if (!response.ok) {
    throw new Error('Analysis failed');
  }
  
  return response.json();
};

export const importPgn = async (pgnText) => {
  const response = await fetch(`${API_BASE}/import`, {
    method: 'POST',
    body: pgnText
  });
  
  if (!response.ok) {
    throw new Error('Import failed');
  }
  
  return response.json();
};

export const getPlayerStats = async (username) => {
  const response = await fetch(`${API_BASE}/stats?username=${username}`);
  
  if (!response.ok) {
    throw new Error('Failed to get stats');
  }
  
  return response.json();
};

export const getPlayerGames = async (username) => {
  const response = await fetch(`${API_BASE}/games?username=${username}`);
  
  if (!response.ok) {
    throw new Error('Failed to get games');
  }
  
  return response.json();
};

export const getGameAnalysis = async (gameId) => {
  const response = await fetch(`${API_BASE}/analysis/${gameId}`);
  
  if (!response.ok) {
    throw new Error('Failed to get analysis');
  }
  
  return response.json();
};