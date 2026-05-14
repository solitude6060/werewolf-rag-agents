"""Data schema for Werewolf prediction system."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class Role(str, Enum):
    """Werewolf game roles."""
    VILLAGER = "Villager"
    WEREWOLF = "Werewolf"
    SEER = "Seer"
    MEDIUM = "Medium"
    MADMAN = "Madman"
    HUNTER = "Hunter"


class DeathCause(str, Enum):
    """Causes of player death in Werewolf."""
    EXECUTION = "execution"
    WEREWOLF_ATTACK = "werewolf_attack"
    SUDDEN_DEATH = "sudden_death"


class Statement(BaseModel):
    """A single player's statement in the game."""
    player_id: int = Field(description="Player ID")
    character: str = Field(description="Character name")
    timestamp: str = Field(description="Timestamp of statement")
    content: str = Field(description="Statement content")
    day_num: int = Field(description="Day number")
    line_start: int = Field(description="Starting line number in transcript")
    line_end: Optional[int] = Field(default=None, description="Ending line number")


class Vote(BaseModel):
    """A vote record in the game."""
    voter_id: int = Field(description="Voter player ID")
    voter_character: str = Field(description="Voter character name")
    target_id: int = Field(description="Target player ID")
    target_character: str = Field(description="Target character name")
    day_num: int = Field(description="Day number")
    vote_text: str = Field(description="Original vote text")


class Death(BaseModel):
    """A death record in the game."""
    player_id: int = Field(description="Dead player ID")
    character: str = Field(description="Character name")
    cause: DeathCause = Field(description="Cause of death")
    day_num: int = Field(description="Day number")


class Claim(BaseModel):
    """A role claim in the game."""
    player_id: int = Field(description="Claiming player ID")
    character: str = Field(description="Character name")
    claimed_role: Role = Field(description="Claimed role")
    day_num: int = Field(description="Day number")
    target_id: Optional[int] = Field(default=None, description="Target of claim (for Seer)")
    claim_text: str = Field(description="Original claim text")


class NightAction(BaseModel):
    """A night action in the game."""
    player_id: int = Field(description="Player performing action")
    character: str = Field(description="Character name")
    action_type: str = Field(description="Type of action (divine, protect, kill)")
    target_id: Optional[int] = Field(default=None, description="Target player ID")
    target_character: Optional[str] = Field(default=None, description="Target character name")
    night_num: int = Field(description="Night number")


class DayPhase(BaseModel):
    """A day phase in the game."""
    day_num: int = Field(description="Day number")
    statements: list[Statement] = Field(default_factory=list, description="Statements made")
    votes: list[Vote] = Field(default_factory=list, description="Votes cast")
    deaths: list[Death] = Field(default_factory=list, description="Deaths this day")
    claims: list[Claim] = Field(default_factory=list, description="Role claims made")
    night_actions: list[NightAction] = Field(default_factory=list, description="Night actions")


class Player(BaseModel):
    """A player in the game."""
    id: int = Field(description="Player ID")
    index: str = Field(description="Game index (01, 02, etc.)")
    character: str = Field(description="Character name")
    role: Optional[Role] = Field(default=None, description="Actual role (for ground truth)")
    wolf_score: Optional[float] = Field(default=None, description="Wolf probability (0.0-1.0)")


class GameRecord(BaseModel):
    """A complete game record."""
    game_id: str = Field(description="Unique game ID")
    index: str = Field(description="Game index (01, 02, etc.)")
    players: list[Player] = Field(default_factory=list, description="Players in game")
    day_count: int = Field(default=0, description="Number of days")
    days: list[DayPhase] = Field(default_factory=list, description="Day phases")
    raw_text: Optional[str] = Field(default=None, description="Raw transcript text")

    class Config:
        use_enum_values = True


class Prediction(BaseModel):
    """A single prediction for a player."""
    id: int = Field(description="Player ID")
    index: str = Field(description="Game index")
    character: str = Field(description="Character name")
    role: Role = Field(description="Predicted role")
    wolf_score: float = Field(description="Werewolf probability (0.0-1.0)")

    class Config:
        use_enum_values = True


class Submission(BaseModel):
    """Kaggle submission format."""
    predictions: list[Prediction] = Field(default_factory=list)

    def to_csv(self) -> str:
        """Convert to CSV format for Kaggle submission."""
        lines = ["id,index,character,role,wolf_score"]
        for p in self.predictions:
            lines.append(f"{p.id},{p.index},{p.character},{p.role},{p.wolf_score}")
        return "\n".join(lines)


class FetchingResult(BaseModel):
    """Result from Stage 1: Fetching Agent."""
    game_id: str
    player_count: int
    day_count: int
    total_statements: int
    total_votes: int
    total_deaths: int
    total_claims: list[Claim]
    votes: list[Vote]
    deaths: list[Death]
    statements: list[Statement] = Field(default_factory=list)
    suspicious_patterns: list[str] = Field(default_factory=list)
    key_events: list[str] = Field(default_factory=list)


class PlayerAnalysis(BaseModel):
    """Analysis result for a single player."""
    player_id: int
    character: str
    role_candidates: dict[str, float] = Field(
        default_factory=dict,
        description="Role -> probability ranking"
    )
    wolf_score: float = Field(description="Werewolf probability (0.0-1.0)")
    key_evidence: list[str] = Field(default_factory=list)
    deception_indicators: list[str] = Field(default_factory=list)
    reasoning: str = Field(default="", description="Analysis reasoning")


class AnalysisResult(BaseModel):
    """Result from Stage 2: Analysis Agent."""
    game_id: str
    player_count: int
    day_count: int
    player_analyses: list[PlayerAnalysis]
    overall_wolf_odds: float = Field(description="Overall wolf probability in game")
    suspicious_players: list[int] = Field(
        default_factory=list,
        description="Player IDs sorted by suspicion"
    )


class SolverResult(BaseModel):
    """Result from Stage 3: Constrained Solver."""
    game_id: str
    assignments: dict[int, Role] = Field(
        description="Player ID -> assigned role"
    )
    wolf_scores: dict[int, float] = Field(
        description="Player ID -> final wolf score"
    )
    confidence: float = Field(description="Assignment confidence (0.0-1.0)")
    constraints_satisfied: bool = Field(
        description="Whether all constraints are satisfied"
    )
    reasoning: str = Field(default="", description="Assignment reasoning")

    class Config:
        use_enum_values = True


class GameConstraints(BaseModel):
    """Game constraints based on player count."""
    total_players: int
    werewolf_count: int = Field(description="2 if <=12 players, 3 if >=13")
    has_seer: bool = Field(default=True)
    has_medium: bool = Field(default=True)
    has_hunter: bool = Field(description="True if >=11 players")
    has_madman: bool = Field(description="True if >=11 players")

    @classmethod
    def from_player_count(cls, count: int) -> "GameConstraints":
        """Create constraints from player count."""
        return cls(
            total_players=count,
            werewolf_count=3 if count >= 13 else 2,
            has_seer=True,
            has_medium=True,
            has_hunter=(count >= 11),
            has_madman=(count >= 11),
        )
