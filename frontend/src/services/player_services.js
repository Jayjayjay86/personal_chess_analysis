import { getPlayerNames } from '../api';

let cachedPlayers = null;
let lastFetchTime = 0;

export const fetchPlayerNames = async (forceRefresh = false) => {
  // Cache for 5 minutes
  if (!forceRefresh && cachedPlayers && Date.now() - lastFetchTime < 300000) {
    return cachedPlayers;
  }

  try {
    const data = await getPlayerNames();
    cachedPlayers = data.players;
    lastFetchTime = Date.now();
    return cachedPlayers;
  } catch (error) {
    console.error('PlayerService:', error);
    return [];
  }
};