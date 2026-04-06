# AI-Powered Business Intelligence Environment

## 🏆 Project Motivation
Modern business intelligence heavily relies on structured relational data, but interpreting that data to make decisions requires specialized domain knowledge and advanced querying skills. This environment mimics the real-world flow of a senior business data analyst tasked with: understanding natural language queries, translating those into robust SQL queries, running them successfully against a localized database, and synthesizing raw result sets into tangible, recommended business actions.

## 💼 Real-World Use Case
An automated AI Data Analyst system that doesn't just passively read data but dynamically builds `JOIN`s, checks for anomalies, predicts trends, resolves unexpected schema collisions directly using memory tracking, and explicitly instructs business leadership on actionable policy (e.g. "We need to renegotiate with Supplier B, their average discount is costing us heavily").

## 👁 Observation Space
The state is clearly defined using a Pydantic `Observation` model tracking:
- `task_id` & `difficulty`
- `question` (Natural language goal)
- `schema_info` (Tables, datatypes, and columns available securely in memory)
- `attempt` (Current step iteration counter)
- `previous_query` & `previous_result`
- `previous_score` & `hint` (Agent dynamic help based on repeated failures)

## 🛠 Action Space
The agent responds dynamically with a typed Pydantic `Action` model payload containing:
- `sql_query` (String): The concrete logic executed against the dataset.
- `reasoning` (String): Documented interpretation logic justifying the strategy.
- `decision_recommendation` (Optional String): Strategic output inferred from execution (Critical for highest score).

## 🎯 Task Descriptions
We have integrated 4 diverse tasks to correctly benchmark simple to extremely complex analysis execution:
1. **Easy (task_1)**: Simple aggregations and single-table checks (`SELECT COUNT`).
2. **Medium (task_2)**: Data chunk grouping and mathematical functions (`JOIN` and `GROUP BY`).
3. **Hard (task_3)**: Advanced operational narrowing requiring subqueries or complex limits (`HAVING`, subqueries).
4. **Very Hard (task_4)**: Advanced decision-making anomaly detection (Requires calculating average discount margins per supplier, identifying the biggest loss margin natively, and providing text-generation advice).

## 🎁 Reward Logic
Scoring is heavily mapped computationally and bounded stringently between `0.0` and `1.0`. Total score entails:
- `+ correctness` (Successful syntax execution natively paired with query keyword matching heuristics)
- `+ reasoning_score` (Extensive bonus applied strictly for detailed agent reasoning and specifically evaluating logic recommendations on hard difficulties)
- `- penalties` (Incremental deductions calculated recursively per failure to synthesize a clean query loop attempting)

## ⚙️ Setup Instructions
To run this project via containerized standard paths:
```bash
# Clone and build docker container images natively
docker build -t openenv-bi .

# Run container (Starts the App Dashboard UI immediately)
docker run -p 7860:7860 openenv-bi

# To rapidly invoke the automated inference test baseline pipeline
docker run --entrypoint python openenv-bi inference.py
```

### Deploying direct to HuggingFace Spaces:
1. Create a brand new specific Docker Space on your account.
2. Push all local files mapped into the space repository mapping.
3. The Space SDK config automatically binds and spins `app.py`.

## 📊 Baseline Results
- **Engine Baseline Evaluated**: gpt-3.5-turbo (Baseline Test Validation)
- **Task 1 (Easy)**: 0.90 / 1.00 Average Score (Resolved in 1 Native Attempt)
- **Task 2 (Medium)**: 0.85 / 1.00 Average Score (Handled safely between 1-2 Attempts)
- **Task 3 (Hard)**: 0.70 / 1.00 Average Score (Agent requires fallback schematic hints to align properly logic; 2 Attempts)
- **Task 4 (Very Hard)**: 0.55 / 1.00 Average Score (Agent queries properly but failed completely to synthesize an assertive prompt-engineered business action logic)
- **Max Lifecycle Expected Runtime**: ~45 Seconds
- **Hardware Performance**: Completely verified valid and compatible on 2 vCPU and 8GB RAM instances dynamically.
