# api_extensions.py
from flask import Blueprint, jsonify, request
from typing import List, Dict
import json
from datetime import datetime
from .models import GameModel, MistakeModel
from .advanced_analysis import (
    TimePressureAnalyzer,
    OpeningAnalyzer,
    RatingTrendAnalyzer,
    EndgameAnalyzer
)

api = Blueprint('api', __name__)
game_model = GameModel('./chess_games.db')
mistake_model = MistakeModel('./chess_games.db')


@api.route('/stats/<username>')
def get_player_stats(username: str):
    games = game_model.get_all_games(username)
    analyzed_games = [g for g in games if g['analyzed']]
    
    if not analyzed_games:
        return jsonify({"error": "No analyzed games found"}), 404
    
    # Basic mistake statistics
    all_mistakes = mistake_model.get_mistakes_by_player(username)
    mistake_counts = {
        "blunder": 0,
        "mistake": 0,
        "inaccuracy": 0
    }
    
    for mistake in all_mistakes:
        if mistake['mistake_type'] == 'blunder':
            mistake_counts['blunder'] += 1
        elif mistake['mistake_type'] == 'mistake':
            mistake_counts['mistake'] += 1
        elif mistake['mistake_type'] == 'inaccuracy':
            mistake_counts['inaccuracy'] += 1
    
    # Time pressure analysis
    time_stats = TimePressureAnalyzer.analyze_time_mistakes(all_mistakes)
    
    # Opening analysis
    opening_stats = OpeningAnalyzer().analyze_opening_mistakes(analyzed_games)
    
    # Rating trend
    rating_trend = RatingTrendAnalyzer.calculate_rating_trend(games)
    
    # Endgame performance
    endgame_stats = EndgameAnalyzer.analyze_endgame_performance(analyzed_games)
    
    return jsonify({
        "username": username,
        "total_games": len(games),
        "analyzed_games": len(analyzed_games),
        "mistakeDistribution": mistake_counts,
        "timePressureStats": time_stats,
        "openingStats": opening_stats,
        "ratingTrend": rating_trend,
        "endgamePerformance": endgame_stats,
        "lastUpdated": datetime.now().isoformat()
    })

@api.route('/games/batch-analyze', methods=['POST'])
def batch_analyze():
    data = request.json
    game_ids = data.get('game_ids', [])
    depth = data.get('depth', 18)
    username = data.get('username')
    
    if not game_ids:
        return jsonify({"error": "No game IDs provided"}), 400
    
    results = []
    for game_id in game_ids:
        game = game_model.get_game(game_id)
        if not game['analyzed']:
            analysis = analyzer.analyze_game(game_id, depth)
            results.append({
                "game_id": game_id,
                "status": "analyzed",
                "mistakes": len(analysis['mistakes'])
            })
        else:
            results.append({
                "game_id": game_id,
                "status": "already_analyzed"
            })
    
    # Update player stats after batch analysis
    stats = get_player_stats(username)
    
    return jsonify({
        "results": results,
        "updated_stats": stats.json
    })

@api.route('/mistakes/common', methods=['GET'])
def get_common_mistakes():
    username = request.args.get('username')
    limit = int(request.args.get('limit', 5))
    
    if not username:
        return jsonify({"error": "Username required"}), 400
    
    mistakes = mistake_model.get_mistakes_by_player(username)
    
    # Group similar mistakes by position
    position_groups = defaultdict(list)
    for mistake in mistakes:
        # Use FEN before move (without move counters) to group similar positions
        simplified_fen = " ".join(mistake['fen_before'].split(" ")[:4])
        position_groups[simplified_fen].append(mistake)
    
    # Get most frequent mistake positions
    common_positions = sorted(
        position_groups.items(),
        key=lambda x: len(x[1]),
        reverse=True
    )[:limit]
    
    result = []
    for fen, mistakes in common_positions:
        result.append({
            "fen": fen,
            "count": len(mistakes),
            "average_eval_diff": sum(m['eval_diff'] for m in mistakes) / len(mistakes),
            "example_mistake": mistakes[0]  # Include one example
        })
    
    return jsonify(result)

@api.route('/games/<game_id>/review', methods=['GET'])
def get_game_review(game_id: str):
    game = game_model.get_game(game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404
    
    if not game['analyzed']:
        return jsonify({"error": "Game not analyzed"}), 400
    
    analysis = json.loads(game['analysis_json'])
    
    # Enhanced review with additional insights
    review = {
        "summary": analysis['summary'],
        "key_moments": [],
        "learning_opportunities": []
    }
    
    # Identify key moments (biggest swings)
    if analysis['mistakes']:
        sorted_mistakes = sorted(
            analysis['mistakes'],
            key=lambda m: m['eval_diff'],
            reverse=True
        )
        review['key_moments'] = sorted_mistakes[:3]
    
    # Identify patterns (same mistake multiple times)
    mistake_positions = defaultdict(list)
    for mistake in analysis['mistakes']:
        simplified_fen = " ".join(mistake['fen_before'].split(" ")[:4])
        mistake_positions[simplified_fen].append(mistake)
    
    for fen, mistakes in mistake_positions.items():
        if len(mistakes) > 1:
            review['learning_opportunities'].append({
                "position": fen,
                "count": len(mistakes),
                "type": "repeated_mistake",
                "examples": mistakes[:2]
            })
    
    return jsonify(review)