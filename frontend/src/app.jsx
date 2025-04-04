// App.jsx (Main Frontend Component)
import React, { useState, useEffect, useCallback } from 'react';
import { Chessboard } from 'react-chessboard';
import { analyzeGame, importPgn, getPlayerStats } from './api';
import { MistakeChart, TimeChart, OpeningChart } from './charts';
// Add to your imports
import PlayerSelector from './components/PlayerSelector';

const App = () => {
  const [games, setGames] = useState([]);
  const [selectedGame, setSelectedGame] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [stats, setStats] = useState(null);
  const [username, setUsername] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [selectedPlayer, setSelectedPlayer] = useState(null);

  const fetchPlayerGames = useCallback(async () => {
    const response = await fetch(`/api/games?username=${username}`);
    const data = await response.json();
    setGames(data);
  }, [username]); // Now stable unless username changes
  
  useEffect(() => {
    if (username) {
      fetchPlayerGames();
    }
  }, [username, fetchPlayerGames]);

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    const reader = new FileReader();
    
    reader.onload = async (e) => {
      const pgnText = e.target.result;
      await importPgn(pgnText);
      fetchPlayerGames();
    };
    
    reader.readAsText(file);
  };

  const analyzeSelectedGame = async () => {
    if (!selectedGame) return;
    
    setIsAnalyzing(true);
    try {
      const result = await analyzeGame(selectedGame.id);
      setAnalysis(result);
      
      // Update stats after analysis
      const statsResult = await getPlayerStats(username);
      setStats(statsResult);
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
          <div className="min-h-screen bg-gray-50">
            <header className="bg-indigo-600 text-white p-4">
              <h1 className="text-2xl font-bold">Chess Mistake Analyzer</h1>
            </header>
            
            <main className="container mx-auto p-4">
            <div className="player-section">
        <h3>Select Player</h3>
        <PlayerSelector 
          onSelectPlayer={(player) => {
            setSelectedPlayer(player);
            setUsername(player); // If you want to auto-fill the username field
          }} 
        />
      </div>
        <div className="mb-6">
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Enter your chess username"
            className="p-2 border rounded"
          />
          <input
            type="file"
            accept=".pgn"
            onChange={handleFileUpload}
            className="ml-4 p-2"
          />
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1">
            <div className="bg-white p-4 rounded shadow">
              <h2 className="text-xl font-semibold mb-4">Your Games</h2>
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {games.map(game => (
                  <div 
                    key={game.id}
                    onClick={() => setSelectedGame(game)}
                    className={`p-2 cursor-pointer rounded ${selectedGame?.id === game.id ? 'bg-indigo-100' : 'hover:bg-gray-100'}`}
                  >
                    <div className="flex justify-between">
                      <span>{game.white} vs {game.black}</span>
                      <span>{game.result}</span>
                    </div>
                    <div className="text-sm text-gray-500">{game.date}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
          
          <div className="lg:col-span-2 space-y-6">
            {selectedGame && (
              <div className="bg-white p-4 rounded shadow">
                <div className="flex justify-between items-center mb-4">
                  <h2 className="text-xl font-semibold">
                    {selectedGame.white} vs {selectedGame.black} - {selectedGame.result}
                  </h2>
                  <button
                    onClick={analyzeSelectedGame}
                    disabled={isAnalyzing}
                    className="bg-indigo-600 text-white px-4 py-2 rounded disabled:opacity-50"
                  >
                    {isAnalyzing ? 'Analyzing...' : 'Analyze Game'}
                  </button>
                </div>
                
                {analysis && (
                  <div className="mt-4">
                    <h3 className="text-lg font-medium mb-2">Game Analysis</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <Chessboard 
                          position={analysis.mistakes[0]?.fen_before || 'start'} 
                          boardWidth={400}
                        />
                      </div>
                      <div>
                        <h4 className="font-medium">Mistakes Summary</h4>
                        <p>White mistakes: {analysis.summary.white_mistakes}</p>
                        <p>Black mistakes: {analysis.summary.black_mistakes}</p>
                        
                        {analysis.summary.worst_mistake && (
                          <div className="mt-4">
                            <h4 className="font-medium">Worst Mistake</h4>
                            <p>Move {analysis.summary.worst_mistake.move_number}: 
                              {analysis.summary.worst_mistake.move_san}</p>
                            <p>Evaluation change: {analysis.summary.worst_mistake.eval_diff}</p>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
            
            {stats && (
              <div className="bg-white p-4 rounded shadow">
                <h2 className="text-xl font-semibold mb-4">Your Statistics</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <MistakeChart data={stats.mistakeDistribution} />
                  <TimeChart data={stats.timePressureStats} />
                  <OpeningChart data={stats.openingStats} />
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default App;