"""Game rules and role behavior corpus for RAG."""

ROLE_BEHAVIORS = [
    "Werewolf: Each night, may attack and kill one human player. Werewolves can communicate with one another through a private channel.",
    "Werewolf count: There are 2 werewolves in villages of up to 12 players, and 3 werewolves in villages of 13 or more players.",
    "Seer: Each night, may divine one player. The Seer learns whether that player is a werewolf or a human.",
    "Medium: Can determine whether a player who died by execution or sudden death was a werewolf or a human.",
    "Madman: A human aligned with the werewolf side. A werewolf victory is also a victory for the Madman. The Madman and the werewolves do not know each other's identities. Added in villages with 11 or more players.",
    "Hunter: Each night, may protect one player from a werewolf attack. The Hunter does not know whether the protection was successful. Added in villages with 11 or more players.",
    "Villager: Has no special ability. Goal is to identify and execute werewolves.",
]

GAME_RULES = [
    "Village win condition: If all werewolves are executed, the villagers win.",
    "Werewolf win condition: If the number of villagers is reduced to the same as or fewer than the number of werewolves, the werewolves win.",
    "Voting: The player to be executed is determined by a vote among the surviving villagers.",
    "Sudden death: Any player who does not post will die from sudden death.",
    "Day structure: The state of the village changes at each daily update. Before the update, players must set their vote target, divination target, and other required actions.",
    "Prologue: If at least 10 players have entered, the game proceeds to Day 1. Each player learns their role and alignment. Werewolves may use this phase to discuss and prepare their strategy.",
]

EVIDENCE_PATTERNS = [
    "Vote accusation: When a player accuses another, note the accuser and target.",
    "Defense statement: Players may defend themselves when accused.",
    "Role claim: A player may claim to be Seer, Medium, or other roles.",
    "Seer result: A claimed Seer may reveal a player's identity (white=human, black=werewolf).",
    "Medium result: A claimed Medium may reveal a dead player's identity.",
    "Sudden death: Player dies without vote or attack.",
    "Werewolf attack: Player dies at night, not by execution.",
]

TERMINOLOGY = [
    "white = likely villager (human)",
    "black = likely werewolf",
    "gray = unresolved",
    "GS = ranking from white to black among unresolved players",
    "CO = claim",
    "will = prewritten role reveal or instructions if attacked or killed",
    "confirmed town = role-confirmed non-wolf from village perspective",
    "panda = one white result and one black result on the same target",
]

ALL_CORPUS = (
    ROLE_BEHAVIORS
    + GAME_RULES
    + EVIDENCE_PATTERNS
    + TERMINOLOGY
)


def get_rule_corpus() -> list[str]:
    return ALL_CORPUS


def get_role_behaviors() -> list[str]:
    return ROLE_BEHAVIORS


def get_game_rules() -> list[str]:
    return GAME_RULES


def get_evidence_patterns() -> list[str]:
    return EVIDENCE_PATTERNS