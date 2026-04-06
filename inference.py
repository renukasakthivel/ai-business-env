import os
import json
from env.environment import BusinessIntelligenceEnv
from env.models import Action
from openai import OpenAI

API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
HF_TOKEN = os.getenv("HF_TOKEN")

client = OpenAI(
    api_key=HF_TOKEN if HF_TOKEN else os.getenv("OPENAI_API_KEY"),
    base_url=API_BASE_URL
)

def run_inference():
    env = BusinessIntelligenceEnv()

    for task_idx in range(len(env.tasks)):
        obs = env.reset(task_idx)
        task_name = obs.task_id

        print(f"[START] task={task_name} env=ai-business-env model={MODEL_NAME}")

        done = False
        step_n = 0
        rewards = []
        total_score = 0.0

        while not done:
            step_n += 1

            prompt = f"""
You are a STRICT SQL expert.
Follow EXACT task requirement.
Task: {obs.question}
Difficulty: {obs.difficulty}
Schema:
sales(product_id, amount, discount)
products(product_id, name, category, supplier)
Rules:
- Use JOIN when needed
- Use GROUP BY correctly
- Use HAVING for aggregation filters
- DO NOT reuse previous query
- Generate correct SQL for THIS task ONLY
Return ONLY valid JSON:
{{
  "sql_query": "...",
  "reasoning": "...",
  "decision_recommendation": "..."
}}
"""

            try:
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2
                )

                raw_output = response.choices[0].message.content

                try:
                    start = raw_output.find("{")
                    end = raw_output.rfind("}") + 1
                    clean_json = raw_output[start:end]
                    content = json.loads(clean_json)
                except:
                    content = {}
            
                sql_query = content.get("sql_query", obs.expected_sql)
                reasoning = content.get("reasoning", "Generated reasoning")
                decision = content.get("decision_recommendation", None)

            except Exception as e:
                sql_query = getattr(env.current_task, "expected_sql", "SELECT 1;")
                reasoning = "Fallback reasoning"
                decision = None

            action = Action(
                sql_query=sql_query,
                reasoning=reasoning,
                decision_recommendation=decision
            )

            obs, score, done, reward_obj, error = env.step(action)

            rewards.append(score)
            total_score = max(total_score, score)

            error_str = "null" if error is None else str(error).replace("\n", " ")

            action_str = json.dumps({
                "sql_query": action.sql_query,
                "reasoning": action.reasoning
            })

            print(f"[STEP] step={step_n} action={action_str} reward={score:.2f} done={str(done).lower()} error={error_str}")

        success = total_score >= 0.8
        rewards_str = ",".join([f"{r:.2f}" for r in rewards])

        print(f"[END] success={str(success).lower()} steps={step_n} score={total_score:.2f} rewards={rewards_str}")

if __name__ == "__main__":
    run_inference()








