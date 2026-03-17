import pandas as pd
import numpy as np
from nba_api.stats.endpoints import leaguegamefinder
from nba_api.stats.static import teams
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import time

def get_team_id(team_name: str):
    all_teams = teams.get_teams()
    for team in all_teams:
        if team_name.lower() in team['full_name'].lower() or team_name.lower() in team['nickname'].lower():
            return team['id'], team['full_name']
    return None, None

def get_team_season_stats(team_id: int):
    """Dohvati prosječne statistike tima za sezonu"""
    gamefinder = leaguegamefinder.LeagueGameFinder(
        team_id_nullable=team_id,
        season_nullable='2024-25',
        season_type_nullable='Regular Season'
    )
    df = gamefinder.get_data_frames()[0]
    
    if df.empty:
        return None
    
    return {
        'avg_pts': df['PTS'].mean(),
        'avg_ast': df['AST'].mean(),
        'avg_reb': df['REB'].mean(),
        'avg_fg_pct': df['FG_PCT'].mean(),
        'avg_fg3_pct': df['FG3_PCT'].mean(),
        'avg_ft_pct': df['FT_PCT'].mean(),
        'avg_tov': df['TOV'].mean(),
        'win_pct': (df['WL'] == 'W').mean()
    }

def predict_match(team_a_name: str, team_b_name: str):
    """Predviđa ishod utakmice između dva tima"""
    
    # Dohvati ID-eve
    team_a_id, team_a_full = get_team_id(team_a_name)
    team_b_id, team_b_full = get_team_id(team_b_name)
    
    if not team_a_id:
        return {"error": f"Tim '{team_a_name}' nije pronađen"}
    if not team_b_id:
        return {"error": f"Tim '{team_b_name}' nije pronađen"}
    
    # Dohvati statistike
    stats_a = get_team_season_stats(team_a_id)
    time.sleep(0.5)  # izbjegni rate limit
    stats_b = get_team_season_stats(team_b_id)
    
    if not stats_a or not stats_b:
        return {"error": "Nije moguće dohvatiti statistike"}
    
    # Feature engineering – razlika između timova
    features = np.array([[
        stats_a['avg_pts'] - stats_b['avg_pts'],
        stats_a['avg_ast'] - stats_b['avg_ast'],
        stats_a['avg_reb'] - stats_b['avg_reb'],
        stats_a['avg_fg_pct'] - stats_b['avg_fg_pct'],
        stats_a['avg_fg3_pct'] - stats_b['avg_fg3_pct'],
        stats_a['win_pct'] - stats_b['win_pct'],
        stats_a['avg_tov'] - stats_b['avg_tov'],
    ]])
    
    # Jednostavan model baziran na win_pct i statistikama
    # (bez treniranja na historijskim podacima za sada)
    score_a = (
        stats_a['win_pct'] * 40 +
        stats_a['avg_pts'] * 0.3 +
        stats_a['avg_fg_pct'] * 20 +
        stats_a['avg_ast'] * 0.5 -
        stats_a['avg_tov'] * 0.5
    )
    
    score_b = (
        stats_b['win_pct'] * 40 +
        stats_b['avg_pts'] * 0.3 +
        stats_b['avg_fg_pct'] * 20 +
        stats_b['avg_ast'] * 0.5 -
        stats_b['avg_tov'] * 0.5
    )
    
    total = score_a + score_b
    prob_a = round((score_a / total) * 100, 1)
    prob_b = round((score_b / total) * 100, 1)
    
    winner = team_a_full if prob_a > prob_b else team_b_full
    
    # Konvertuj numpy tipove u Python float
    return {k: float(v) if hasattr(v, 'item') else v for k, v in {
        "team_a": team_a_full,
        "team_b": team_b_full,
        "predicted_winner": winner,
        "probability_a": prob_a,
        "probability_b": prob_b,
        "team_a_win_pct": round(stats_a['win_pct'] * 100, 1),
        "team_b_win_pct": round(stats_b['win_pct'] * 100, 1),
        "team_a_avg_pts": round(stats_a['avg_pts'], 1),
        "team_b_avg_pts": round(stats_b['avg_pts'], 1),
    }.items()}
    