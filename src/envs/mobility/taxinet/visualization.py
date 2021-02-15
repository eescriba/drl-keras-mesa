from .agents import GridAgent, TargetAgent, PassengerAgent, VehicleAgent
from .enums import GridSymbol

SYMBOLS_MAP = {
    "#": "#f1f3f4",
    "△": "white",
    "▽": "white",
    "▷": "white",
    "◁": "white",
    "X": "white",
    "+": "#fde293",
}

TARGET_COLORS = [
    "#EF5350",
    "#AB47BC",
    "#5C6BC0",
    "#42A5F5",
    "#26A69A",
    "#9CCC65",
    "#FFEE58",
    "#FFA726",
]


def agent_portrayal(agent):
    portrayal = {}

    if hasattr(agent, "portrayal"):
        portrayal = agent.portrayal

    elif isinstance(agent, PassengerAgent):
        portrayal = {
            "Filled": "true",
            "Shape": "circle",
            "r": 0.8,
            "Layer": 4,
            "Color": TARGET_COLORS[agent.target_id % len(TARGET_COLORS)],
        }

    elif isinstance(agent, VehicleAgent):
        portrayal = {
            "Shape": "resources/taxi-" + agent.heading + ".png",
            "h": 0.75,
            "w": 0.75,
            "Layer": 3,
        }

    elif isinstance(agent, TargetAgent):
        portrayal = {
            "Filled": "true",
            "Shape": "rect",
            "h": 1,
            "w": 1,
            "Layer": 2,
            "Color": TARGET_COLORS[agent.target_id % len(TARGET_COLORS)],
        }

    elif isinstance(agent, GridAgent):
        portrayal = {
            "Filled": "true",
            "Shape": "rect",
            "h": 1,
            "w": 1,
            "Layer": 1,
            "Color": SYMBOLS_MAP.get(agent.symbol.value, "white"),
        }
        if agent.symbol.is_direction and agent.model.show_symbols:
            portrayal.update(
                {
                    "text": agent.symbol.value,
                    "text_color": "grey",
                }
            )
    return portrayal
