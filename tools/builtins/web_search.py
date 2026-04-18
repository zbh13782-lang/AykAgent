from langchain_core.tools import tool
from langchain_community.tools import TavilySearchResults
from config.settings import get_settings

settings = get_settings()
web_search = TavilySearchResults(
    api_key=settings.tavily_api_key,
    max_results = 5,
)
