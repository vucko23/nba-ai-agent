# 🏀 NBA AI Agent

An AI-powered NBA assistant built with Claude (Anthropic) and real-time NBA data.
Ask questions in natural language and get instant, data-driven answers about teams, players, and match predictions.

🔗 **Live Demo:** [coming soon]

---

## Features

- 📊 **Live NBA standings** – real-time win/loss records for all 30 teams
- 🏃 **Player stats** – points, assists, rebounds, and minutes per game
- 🏆 **Team stats** – offensive and defensive performance metrics
- 🔮 **Match prediction** – predicts match outcomes based on season statistics
- ⚔️ **Player comparison** – head-to-head stat comparison between any two players
- 💬 **Conversational memory** – remembers context across the conversation

---

## Tech Stack

- **Claude API** (Anthropic) – LLM with tool use / function calling
- **nba_api** – real-time NBA statistics
- **Streamlit** – web interface
- **pandas** – data processing
- **Python 3.13**

---

## How It Works

The agent uses Claude's tool use feature to decide which data to fetch based on the user's question.

```
User question → Claude decides which tool to call → Fetches live NBA data → Claude formulates answer
```

**Available tools:**

- `get_standings()` – fetches current NBA standings
- `get_team_stats(team_name)` – fetches team season averages
- `get_player_stats(player_name)` – fetches player season stats
- `predict_match(team_a, team_b)` – predicts match outcome
- `compare_players(player_a, player_b)` – compares two players

---

## Installation

```bash
git clone https://github.com/vucko23/nba-ai-agent
cd nba-ai-agent
pip install -r requirements.txt
```

Add your Anthropic API key to `.env`:

```
ANTHROPIC_API_KEY=your_key_here
```

Run the app:

```bash
streamlit run app.py
```

---

## Example Questions

- *"Which team has the most wins?"*
- *"What are LeBron James' stats this season?"*
- *"Who would win, Thunder or Celtics?"*
- *"Compare Stephen Curry and Luka Doncic"*
- *"Show me the full NBA standings"*

---

## Author

**Jelena Vucetic**
[LinkedIn](https://linkedin.com/in/jelena-vucetic-663078317) · [GitHub](https://github.com/vucko23)pip freeze > requirements.txt
