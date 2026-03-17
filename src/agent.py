import anthropic
import json
import os
from dotenv import load_dotenv
from src.tools import get_standings, get_team_stats, get_player_stats, compare_players
from src.predictor import predict_match

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Definišemo alate koje Claude može koristiti
tools = [
    {
        "name": "get_standings",
        "description": "Vraća trenutnu NBA tabelu sa pobjedama i porazima svih timova",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_team_stats",
        "description": "Vraća statistike određenog NBA tima (poeni, asistencije, skokovi po utakmici)",
        "input_schema": {
            "type": "object",
            "properties": {
                "team_name": {
                    "type": "string",
                    "description": "Ime tima, npr. Lakers, Celtics, Thunder"
                }
            },
            "required": ["team_name"]
        }
    },
    {
        "name": "get_player_stats",
        "description": "Vraća statistike određenog NBA igrača za trenutnu sezonu",
        "input_schema": {
            "type": "object",
            "properties": {
                "player_name": {
                    "type": "string",
                    "description": "Ime igrača, npr. LeBron James, Kevin Durant"
                }
            },
            "required": ["player_name"]
        }
    },
    {
        "name": "predict_match",
        "description": "Predviđa ishod utakmice između dva NBA tima na osnovu sezonskih statistika",
        "input_schema": {
            "type": "object",
            "properties": {
                "team_a_name": {
                    "type": "string",
                    "description": "Ime prvog tima, npr. Lakers"
                },
                "team_b_name": {
                    "type": "string",
                    "description": "Ime drugog tima, npr. Celtics"
                }
            },
            "required": ["team_a_name", "team_b_name"]
        }
    },
    {
        "name": "compare_players",
        "description": "Poredi statistike dva NBA igrača i određuje ko je bolji u kojoj kategoriji",
        "input_schema": {
            "type": "object",
            "properties": {
                "player_a_name": {
                    "type": "string",
                    "description": "Ime prvog igrača, npr. LeBron James"
                },
                "player_b_name": {
                    "type": "string",
                    "description": "Ime drugog igrača, npr. Stephen Curry"
                }
            },
            "required": ["player_a_name", "player_b_name"]
        }
    }
]


def run_agent(user_message: str, conversation_history: list):
    """Pokreće agenta sa historijom razgovora"""

    conversation_history.append({
        "role": "user",
        "content": user_message
    })

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system="Ti si NBA ekspert asistent. Koristiš dostupne alate da odgovaraš na pitanja o NBA statistikama i timovima. Odgovaraj koncizno i informativno.",
        tools=tools,
        messages=conversation_history
    )

    # Ako Claude želi da koristi tool
    while response.stop_reason == "tool_use":
        tool_results = []

        for block in response.content:
            if block.type == "tool_use":
                tool_name = block.name
                tool_input = block.input

                # Pozovi pravi tool
                if tool_name == "get_standings":
                    result = get_standings()
                elif tool_name == "get_team_stats":
                    result = get_team_stats(tool_input["team_name"])
                elif tool_name == "get_player_stats":
                    result = get_player_stats(tool_input["player_name"])
                elif tool_name == "predict_match":
                    result = predict_match(
                        tool_input["team_a_name"], tool_input["team_b_name"])
                elif tool_name == "compare_players":
                    result = compare_players(
                        tool_input["player_a_name"], tool_input["player_b_name"])
                else:
                    result = {"error": "Nepoznat tool"}

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result)
                })

        # Dodaj Claudeov odgovor i rezultate toola u historiju
        conversation_history.append(
            {"role": "assistant", "content": response.content})
        conversation_history.append({"role": "user", "content": tool_results})

        # Pozovi Claude ponovo sa rezultatima
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system="You are an NBA expert assistant. You use available tools to answer questions about NBA statistics, teams, players, and match predictions. Respond concisely and informatively. Always respond in the same language the user is writing in.",
            tools=tools,
            messages=conversation_history
        )

    # Izvuci finalni tekst
    final_response = ""
    for block in response.content:
        if hasattr(block, "text"):
            final_response = block.text
            break

    conversation_history.append({
        "role": "assistant",
        "content": final_response
    })

    return final_response, conversation_history
