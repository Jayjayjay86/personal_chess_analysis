import React, { useState, useEffect } from 'react';
import { fetchPlayerNames } from '../services/playerService';

const PlayerSelector = ({ onSelectPlayer }) => {
  const [players, setPlayers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    const loadPlayers = async () => {
      setLoading(true);
      try {
        const playerList = await fetchPlayerNames();
        setPlayers(playerList);
      } finally {
        setLoading(false);
      }
    };
    loadPlayers();
  }, []);

  const filteredPlayers = players.filter(player =>
    player.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="player-selector">
      <input
        type="text"
        placeholder="Search players..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        className="search-input"
      />
      
      {loading ? (
        <div className="loading">Loading players...</div>
      ) : (
        <ul className="player-list">
          {filteredPlayers.map((player) => (
            <li 
              key={player} 
              onClick={() => onSelectPlayer(player)}
              className="player-item"
            >
              {player}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default PlayerSelector;