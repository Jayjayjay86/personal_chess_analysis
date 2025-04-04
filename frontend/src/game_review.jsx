// GameReview.jsx
import React, { useState, useEffect } from 'react';
import { Chessboard } from 'react-chessboard';
import { getGameReview } from './api';

const GameReview = ({ gameId }) => {
  const [review, setReview] = useState(null);
  const [loading, setLoading] = useState(true);
  const [currentMistake, setCurrentMistake] = useState(0);
  const [boardWidth, setBoardWidth] = useState(400);
  
  useEffect(() => {
    const fetchReview = async () => {
      try {
        setLoading(true);
        const data = await getGameReview(gameId);
        setReview(data);
      } catch (error) {
        console.error("Failed to load review:", error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchReview();
    
    // Handle responsive board size
    const handleResize = () => {
      setBoardWidth(Math.min(window.innerWidth - 40, 600));
    };
    
    window.addEventListener('resize', handleResize);
    handleResize();
    
    return () => window.removeEventListener('resize', handleResize);
  }, [gameId]);
  
  if (loading) {
    return <div className="text-center py-8">Loading game review...</div>;
  }
  
  if (!review) {
    return <div className="text-center py-8">Failed to load game review</div>;
  }
  
  const navigateMistake = (direction) => {
    if (!review.key_moments) return;
    
    setCurrentMistake(prev => {
      if (direction === 'next') {
        return Math.min(prev + 1, review.key_moments.length - 1);
      } else {
        return Math.max(prev - 1, 0);
      }
    });
  };
  
  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <div className="p-4 border-b">
        <h2 className="text-xl font-semibold">Game Review</h2>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 p-4">
        <div className="lg:col-span-2">
          <div className="bg-gray-100 p-4 rounded-lg">
            {review.key_moments && review.key_moments.length > 0 ? (
              <>
                <div className="mb-4">
                  <Chessboard 
                    position={review.key_moments[currentMistake].fen_before}
                    boardWidth={boardWidth}
                  />
                </div>
                
                <div className="flex justify-between items-center">
                  <button
                    onClick={() => navigateMistake('prev')}
                    disabled={currentMistake === 0}
                    className="bg-indigo-600 text-white px-4 py-2 rounded disabled:opacity-50"
                  >
                    Previous
                  </button>
                  
                  <div className="text-center">
                    <h3 className="font-medium">Key Moment {currentMistake + 1}/{review.key_moments.length}</h3>
                    <p>Move {review.key_moments[currentMistake].move_number}: 
                      {review.key_moments[currentMistake].move_san}</p>
                    <p className={`font-bold ${
                      review.key_moments[currentMistake].eval_diff > 200 ? 'text-red-600' : 
                      review.key_moments[currentMistake].eval_diff > 100 ? 'text-orange-500' : 'text-yellow-500'
                    }`}>
                      {review.key_moments[currentMistake].mistake_type} ({review.key_moments[currentMistake].eval_diff})
                    </p>
                  </div>
                  
                  <button
                    onClick={() => navigateMistake('next')}
                    disabled={currentMistake === review.key_moments.length - 1}
                    className="bg-indigo-600 text-white px-4 py-2 rounded disabled:opacity-50"
                  >
                    Next
                  </button>
                </div>
              </>
            ) : (
              <div className="text-center py-8">
                <p>No critical mistakes found in this game</p>
              </div>
            )}
          </div>
        </div>
        
        <div className="space-y-6">
          <div className="bg-white p-4 rounded-lg border">
            <h3 className="font-medium mb-2">Game Summary</h3>
            <div className="space-y-2">
              <p>Total mistakes: {review.summary.white_mistakes + review.summary.black_mistakes}</p>
              <p>White mistakes: {review.summary.white_mistakes}</p>
              <p>Black mistakes: {review.summary.black_mistakes}</p>
              {review.summary.worst_mistake && (
                <p>
                  Worst mistake: {review.summary.worst_mistake.eval_diff} cp
                </p>
              )}
            </div>
          </div>
          
          {review.learning_opportunities && review.learning_opportunities.length > 0 && (
            <div className="bg-white p-4 rounded-lg border">
              <h3 className="font-medium mb-2">Learning Opportunities</h3>
              <div className="space-y-4">
                {review.learning_opportunities.map((opp, index) => (
                  <div key={index} className="border-b pb-4 last:border-0">
                    <p className="font-medium">
                      Repeated mistake ({opp.count} times)
                    </p>
                    <div className="mt-2">
                      <Chessboard 
                        position={opp.position}
                        boardWidth={200}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default GameReview;