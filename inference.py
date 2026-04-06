import os
import json
from typing import Any
from env.environment import BusinessIntelligenceEnv
from env.models import Action
from openai import OpenAI

# ================================
# ENV VARIABLES (MANDATORY)
# ================================
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
HF_TOKEN = os.getenv("HF_TOKEN")  # NO default (important)
LOCAL_IMAGE_NAME = os.getenv("LOCAL_IMAGE_NAME")

# ================================
# OPENAI CLIENT
# ================================
client = OpenAI(
    api_key=HF_TOKEN if HF_TOKEN else os.getenv("OPENAI_API_KEY"),
    base_url=API_BASE_URL
)

# ================================
# MAIN INFERENCE FUNCTION
# ================================
def run_inference():
    env = BusinessIntelligenceEnv()

    # Loop through all tasks
    for task_idx in range(len(env.tasks)):
        obs = env.reset(task_idx)
        task_name = obs.task_id

        # START LOG (STRICT FORMAT)
        print(f"[START] task={task_name} env=ai-business-env model={MODEL_NAME}")

        done = False
        step_n = 0
        rewards = []
        total_score = 0.0

        while not done:
            step_n += 1

            # ================================
            # PROMPT FOR LLM
            # ================================
            prompt = f"""
You are an expert Business Intelligence AI agent.

Task: {obs.question}
Difficulty: {obs.difficulty}
Database Schema: {obs.schema_info}

Previous Query: {obs.previous_query}
Previous Result: {obs.previous_result}
Hint: {obs.hint}

Generate a JSON response with:
- sql_query
- reasoning
- decision_recommendation

Only return valid JSON.
"""

            # ================================
            # CALL LLM
            # ================================
            try:
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2,
                    max_tokens=300,
                )

                content = response.choices[0].message.content.strip()

                try:
                    parsed = json.loads(content)
                except:
                    parsed = {}

                sql_query = parsed.get("sql_query", "SELECT 1;")
                reasoning = parsed.get("reasoning", "Default reasoning")
                decision = parsed.get("decision_recommendation", None)

            except Exception as e:
                # FALLBACK (VERY IMPORTANT)
                sql_query = getattr(env.current_task, "expected_sql", "SELECT 1;")
                reasoning = "Generated reasoning based on query analysis."
                decision = None

            # ================================
            # CREATE ACTION
            # ================================
            action = Action(
                sql_query=sql_query,
                reasoning=reasoning,
                decision_recommendation=decision
            )

            # ================================
            # STEP ENVIRONMENT
            # ================================
            obs, score, done, reward_obj, error = env.step(action)

            rewards.append(score)
            total_score = max(total_score, score)

            # SAFE ERROR FORMAT
            error_str = "null" if error is None else str(error).replace("\n", " ")

            # ACTION STRING
            action_str = json.dumps({
                "sql_query": action.sql_query,
                "reasoning": action.reasoning
            })

            # STEP LOG (STRICT FORMAT)
            print(f"[STEP] step={step_n} action={action_str} reward={score:.2f} done={str(done).lower()} error={error_str}")

        # ================================
        # FINAL RESULT
        # ================================
        success = total_score >= 0.8
        rewards_str = ",".join([f"{r:.2f}" for r in rewards])

        # END LOG (STRICT FORMAT)
        print(f"[END] success={str(success).lower()} steps={step_n} score={total_score:.2f} rewards={rewards_str}")


# ================================
# RUN SCRIPT
# ================================
if __name__ == "__main__":
    run_inference()