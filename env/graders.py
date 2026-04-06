from .models import Reward
from .tasks import Task
from typing import Any

class Grader:
    """Evaluates agent actions, applies bonuses and penalties, and enforces a non-binary score scale."""

    def evaluate(self, action_sql: str, reasoning: str, decision: str, task: Task, is_success: bool, db_result: Any, attempt: int) -> Reward:
        score = 0.0
        correctness = 0.0
        reasoning_score = 0.0
        penalties = 0.0
        
        # 1. Base Correctness scoring
        if is_success:
            # Flat points for generating syntactically valid code that runs
            correctness += 0.3
            
            # Text match heuristic for matching logic (simulating correctness without exact string match)
            matched_keywords = sum([1 for kw in task.keywords if kw.upper() in action_sql.upper()])
            if len(task.keywords) > 0:
                correctness += 0.5 * (matched_keywords / len(task.keywords))
        else:
            # Query failed entirely to run
            penalties += 0.2
            
        # 2. Reasoning evaluation
        if len(reasoning) > 50:
            reasoning_score += 0.15
        elif len(reasoning) > 10:
            reasoning_score += 0.05
            
        # Reward business insights and strategic logic on harder tasks
        if decision is not None and len(decision) > 10:
            if task.difficulty in ["hard", "very hard"]:
                reasoning_score += 0.15 # Up to 0.30 max reasoning score total
            else:
                reasoning_score += 0.05
                
        # 3. Apply penalty for retry iterations
        # The higher the attempts, the more points are docked
        if attempt > 1:
            penalties += (attempt * 0.05)
        
        # 4. Final tally - clamped carefully between 0.0 and 1.0 per requirement
        total = correctness + reasoning_score - penalties
        score = max(0.0, min(1.0, total))
        
        return Reward(
            score=score,
            correctness=correctness,
            reasoning_score=reasoning_score,
            penalties=penalties,
            details={"is_success": is_success, "attempt": attempt}
        )
