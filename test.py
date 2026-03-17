from nba_api.stats.endpoints import leaguestandings
import pandas as pd

standings = leaguestandings.LeagueStandings()
df = standings.get_data_frames()[0]
print(df[['TeamName', 'WINS', 'LOSSES']].head(10))
