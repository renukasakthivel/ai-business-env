from .models import Observation, Action, Reward, State
from .database import DatabaseConnection
from .tasks import get_tasks, Task
from .graders import Grader
from .utils import format_hint
from typing import Optional, Tuple

class BusinessIntelligenceEnv:
    """
    Core implementation matching OpenEnv specification.
    Allows for executing Business Analyst scenarios.
    """
    def __init__(self):
        self.db = DatabaseConnection()
        self.tasks = get_tasks()
        self.grader = Grader()
        self.current_task_idx = 0
        self.current_task: Optional[Task] = None
        
        # State tracking variables
        self.attempt = 0
        self.previous_score = 0.0
        self.previous_query = None
        self.previous_result = None
        
    def reset(self, task_idx: int = 0) -> Observation:
        """
        Resets the environment. Loads the prescribed task and nullifies attempt history.
        """
        self.current_task_idx = task_idx % len(self.tasks)
        self.current_task = self.tasks[self.current_task_idx]
        
        self.attempt = 0
        self.previous_score = 0.0
        self.previous_query = None
        self.previous_result = None
        
        return self._get_observation()
        
    def _get_observation(self) -> Observation:
        """Helper to yield a strongly-typed Observation of the current internal state."""
        hint = format_hint(self.current_task.hints, self.attempt) if self.attempt > 0 else None
        
        # Safely represent previous result to avoid non-serializable objects
        prev_result_str = str(self.previous_result) if self.previous_result is not None else None
        
        return Observation(
            task_id=self.current_task.task_id,
            difficulty=self.current_task.difficulty,
            question=self.current_task.question,
            schema_info=self.db.get_schema(),
            attempt=self.attempt,
            previous_query=self.previous_query,
            previous_result=prev_result_str,
            previous_score=self.previous_score,
            hint=hint
        )

    def step(self, action: Action) -> Tuple[Observation, float, bool, Reward, Optional[str]]:
        """
        Processes a requested database query, delegates to Grader,
        and determines if the agent should continue.
        """
        self.attempt += 1
        self.previous_query = action.sql_query
        
        # Execute query dynamically
        success, result = self.db.execute_query(action.sql_query)
        self.previous_result = result
        
        # Grade performance based on strict requirements (correctness, reasoning, penalty clamping)
        reward_obj = self.grader.evaluate(
            action_sql=action.sql_query,
            reasoning=action.reasoning,
            decision=action.decision_recommendation,
            task=self.current_task,
            is_success=success,
            db_result=result,
            attempt=self.attempt
        )
        
        self.previous_score = reward_obj.score
        
        done = False
        error = None
        
        # End step if correctness threshold implies an accepted query or we hit our limit
        if success and reward_obj.correctness >= 0.4:
            done = True
        elif self.attempt >= 3:
            done = True # Max limit on attempts to prevent infinite loops
            
        if not success:
            error = str(result) # Bubble up SQL engine exception details
            
        obs = self._get_observation()
        
        return obs, reward_obj.score, done, reward_obj, error

    def state(self) -> State:
        """Publishes full environment state as a snapshot according to OpenEnv spec."""
        return State(
            obs=self._get_observation(),
            reward=self.previous_score,
            done=False, # Arbitrary baseline setting representing general step readiness
            info={"attempt": self.attempt}
        )
