from langchain_core.tools import tool


@tool
def get_weather(city:str) -> str:
    """get weather for the city """
    city_name = city.strip()
    return f"{city_name}下小雪"
    