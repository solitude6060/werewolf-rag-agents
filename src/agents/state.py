from typing import TypedDict, Optional
from src.data.schema import FetchingResult, Vote, Death, Claim


class AgentState(TypedDict):
    game_id: str
    transcript: str
    players: list[dict]
    fetching_result: Optional[FetchingResult]
    analysis_result: Optional[dict]
    solver_result: Optional[dict]
    errors: list[str]