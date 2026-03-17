from nba_api.stats.endpoints import leaguestandings, teamgamelog, commonteamroster, playercareerstats, commonallplayers
from nba_api.stats.static import teams
import pandas as pd

def get_standings():
    """Vraća trenutnu NBA tabelu"""
    standings = leaguestandings.LeagueStandings()
    df = standings.get_data_frames()[0]
    return df[['TeamName', 'Conference', 'WINS', 'LOSSES']].to_dict(orient='records')

def get_team_id(team_name: str):
    """Pronađi team ID po imenu"""
    all_teams = teams.get_teams()
    for team in all_teams:
        if team_name.lower() in team['full_name'].lower() or team_name.lower() in team['nickname'].lower():
            return team['id']
    return None

def get_team_stats(team_name: str):
    """Vraća statistike tima"""
    team_id = get_team_id(team_name)
    if not team_id:
        return {"error": f"Tim '{team_name}' nije pronađen"}
    
    gamelog = teamgamelog.TeamGameLog(team_id=team_id, season='2024-25')
    df = gamelog.get_data_frames()[0]
    
    avg_pts = df['PTS'].mean()
    avg_ast = df['AST'].mean()
    avg_reb = df['REB'].mean()
    
    return {
        "team": team_name,
        "games_played": len(df),
        "avg_points": round(avg_pts, 1),
        "avg_assists": round(avg_ast, 1),
        "avg_rebounds": round(avg_reb, 1)
    }
    

def get_player_stats(player_name: str):
    """Vraća statistike igrača za trenutnu sezonu"""
    
    # Pronađi igrača
    all_players = commonallplayers.CommonAllPlayers(is_only_current_season=1)
    players_df = all_players.get_data_frames()[0]
    
    # Pretraži po imenu
    mask = players_df['DISPLAY_FIRST_LAST'].str.lower().str.contains(player_name.lower())
    found = players_df[mask]
    
    if found.empty:
        return {"error": f"Igrač '{player_name}' nije pronađen"}
    
    player_id = found.iloc[0]['PERSON_ID']
    full_name = found.iloc[0]['DISPLAY_FIRST_LAST']
    
    # Dohvati statistike
    career = playercareerstats.PlayerCareerStats(player_id=player_id)
    df = career.get_data_frames()[0]
    
    # Uzmi trenutnu sezonu (zadnji red)
    current = df[df['SEASON_ID'] == '2024-25']
    if current.empty:
        current = df.iloc[[-1]]
    
    row = current.iloc[0]
    
    return {
        "player": full_name,
        "season": row['SEASON_ID'],
        "games_played": int(row['GP']),
        "avg_points": round(row['PTS'] / row['GP'], 1),
        "avg_assists": round(row['AST'] / row['GP'], 1),
        "avg_rebounds": round(row['REB'] / row['GP'], 1),
        "avg_minutes": round(row['MIN'] / row['GP'], 1)
    }
    
def compare_players(player_a_name: str, player_b_name: str):
    """Poredi statistike dva igrača"""
    
    stats_a = get_player_stats(player_a_name)
    stats_b = get_player_stats(player_b_name)
    
    if "error" in stats_a:
        return stats_a
    if "error" in stats_b:
        return stats_b
    
    # Odredi ko je bolji u svakoj kategoriji
    comparison = {
        "player_a": stats_a,
        "player_b": stats_b,
        "better_scorer": stats_a['player'] if stats_a['avg_points'] > stats_b['avg_points'] else stats_b['player'],
        "better_playmaker": stats_a['player'] if stats_a['avg_assists'] > stats_b['avg_assists'] else stats_b['player'],
        "better_rebounder": stats_a['player'] if stats_a['avg_rebounds'] > stats_b['avg_rebounds'] else stats_b['player'],
    }
    
    return comparison