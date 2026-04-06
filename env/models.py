from pydantic import BaseModel
from typing import Optional, Any, Dict

# Represents the information exposed to the agent at each step
class Observation(BaseModel):
    task_id: str
    difficulty: str
    question: str
    schema_info: str
    attempt: int
    previous_query: Optional[str] = None
    previous_result: Optional[str] = None
    previous_score: float = 0.0
    hint: Optional[str] = None

# Represents the action taken by the agent
class Action(BaseModel):
    sql_query: str
    reasoning: str
    decision_recommendation: Optional[str] = None

# Provides a breakdown of the agent's reward
class Reward(BaseModel):
    score: float
    correctness: float
    reasoning_score: float
    penalties: float
    details: Dict[str, Any]

# Represents the complete environment state
class State(BaseModel):
    obs: Observation
    reward: float
    done: bool
    info: Dict[str, Any]
