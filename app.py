import gradio as gr
import pandas as pd
from env.environment import BusinessIntelligenceEnv
from env.models import Action

# Instantiate master environment
env = BusinessIntelligenceEnv()

def process_query(task_id: str, sql_query: str, reasoning: str, decision: str):
    """
    Main hook triggering a single simulation step within the UI bounding.
    """
    # Recover active task lookup table index
    idx = 0
    for i, t in enumerate(env.tasks):
        if t.task_id == task_id:
            idx = i
            break
            
    # Soft Reset if shifting to totally untracked new task execution
    if env.current_task is None or env.current_task.task_id != task_id:
         env.reset(idx)
         
    # Form action payload
    action = Action(
        sql_query=sql_query, 
        reasoning=reasoning, 
        decision_recommendation=decision if decision.strip() else None
    )
    
    # Process
    obs, score, done, reward_obj, error = env.step(action)
    
    res_display = str(obs.previous_result) if error is None else "Query Errored"
    
    return res_display, f"{score:.2f}", str(error) if error else "None", str(obs.hint)

# Compose minimal viable interactive block UI (Gradio limits configuration bloat)
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🏆 AI Business Intelligence & Decision Environment")
    gr.Markdown("Agent Simulation Panel for exploring Schema and Database Tasks.")
    
    with gr.Row():
        task_dropdown = gr.Dropdown(
            choices=[t.task_id for t in env.tasks], 
            label="1. Select Evaluation Task", 
            value="task_1"
        )
        
    with gr.Row():
        sql_input = gr.Textbox(label="Generated SQL Query", lines=3, placeholder="SELECT * FROM ...")
        
    with gr.Row():
        reasoning_input = gr.Textbox(label="Agent Reasoning", lines=2)
        decision_input = gr.Textbox(label="Recommended Business Action", lines=2)
        
    submit_btn = gr.Button("Execute Agent Step", variant="primary")
    
    gr.Markdown("### Execution Results & Score Feedback")
    
    with gr.Row():
        result_output = gr.Textbox(label="Result Dictionary", interactive=False)
        score_output = gr.Textbox(label="Calculated Reward Score (0.0 to 1.0)", interactive=False)
        
    with gr.Row():
        error_output = gr.Textbox(label="SQL Error (If Any)", interactive=False)
        hint_output = gr.Textbox(label="Environment Dynamic Hint", interactive=False)
        
    submit_btn.click(
        fn=process_query,
        inputs=[task_dropdown, sql_input, reasoning_input, decision_input],
        outputs=[result_output, score_output, error_output, hint_output]
    )

if __name__ == "__main__":
    # Bound to standard host configuration optimized for Spaces deployment container
    demo.launch(server_name="0.0.0.0", server_port=7860)
