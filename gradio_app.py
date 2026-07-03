import gradio as gr
import pandas as pd
import copy

from src.world import setup_initial_world
from src.context import DialogueContext
from src.unified_resolver import UnifiedResolver
from src.planner import plan_and_execute

# Initialize Global State
print("Initializing MedBot V2 World & Models...")
world = setup_initial_world()
resolver = UnifiedResolver(world)
context = DialogueContext()
history_stack = []

def generate_dashboard():
    data = []
    for o_id, obj in world.objects.items():
        for b in obj.batches:
            if b.quantity > 0:
                alert = "OK"
                if b.expiry_date.timestamp() < __import__('datetime').datetime.now().timestamp():
                    alert = "EXPIRED"
                elif obj.total_quantity < obj.par_level:
                    alert = "LOW STOCK"
                
                data.append({
                    "Name": obj.name,
                    "Category": obj.category,
                    "Zone": b.zone,
                    "Quantity": b.quantity,
                    "Expiry": b.expiry_date.strftime("%Y-%m-%d"),
                    "Alert": alert
                })
    df = pd.DataFrame(data) if data else pd.DataFrame(columns=["Name", "Category", "Zone", "Quantity", "Expiry", "Alert"])
    return df

def get_audit_log():
    try:
        with open("audit.log", "r", encoding="utf-8") as f:
            lines = f.readlines()
            return "".join(lines[-20:])
    except:
        return "No audit logs yet."

def process_command(user_msg, chat_history, role, zone, auth_toggle):
    global world, history_stack
    
    if not user_msg: return "", chat_history, "No input", generate_dashboard(), get_audit_log()
    
    world.agents["user"].role = role
    world.agents["user"].location = zone
    
    # Save state for undo
    history_stack.append(copy.deepcopy(world))
    if len(history_stack) > 10: history_stack.pop(0)
    
    results = resolver.resolve_command(user_msg, context)
    
    responses = []
    debug_traces = []
    
    for res in results:
        debug_traces.append(f"--- Atomic Action ---\nDecomposer Output: {res.get('raw_atomic', {})}")
        debug_traces.append(f"Routing: {res['layer']} | Confidence: {res['confidence']:.2f}")
        
        if res["error"]:
            responses.append(f"🚫 {res['error']}")
            debug_traces.append(f"Error: {res['error']}")
            continue
            
        action_req = res["action_req"]
        if auth_toggle:
            action_req["auth_provided"] = True
            
        plan_res = plan_and_execute(action_req, world, context)
        status = plan_res["status"]
        
        icon = "✅" if status == "success" else "⚠️" if status == "auth_required" else "❌"
        msg = plan_res["trace"][0] if plan_res["trace"] else "Action completed."
        responses.append(f"{icon} {msg}")
        
        for t in plan_res["trace"]:
            debug_traces.append(f"  -> {t}")
            
    bot_reply = "\n\n".join(responses)
    chat_history.append({"role": "user", "content": user_msg})
    chat_history.append({"role": "assistant", "content": bot_reply})
    
    return "", chat_history, "\n".join(debug_traces), generate_dashboard(), get_audit_log()

def undo_last(chat_history):
    global world, history_stack
    if not history_stack:
        return chat_history, "Nothing to undo.", generate_dashboard()
    world = history_stack.pop()
    chat_history.append({"role": "user", "content": "UNDO"})
    chat_history.append({"role": "assistant", "content": "✅ Reverted to previous state."})
    return chat_history, "Undid last action.", generate_dashboard()

with gr.Blocks() as demo:
    gr.Markdown("# 🏥 MedBot V2: Advanced Clinical Grounded NLU")
    
    with gr.Row():
        with gr.Column(scale=1):
            role_dd = gr.Dropdown(choices=["nurse", "pharmacist", "doctor"], value="nurse", label="User Role")
            zone_dd = gr.Dropdown(choices=["Φαρμακείο", "ΜΕΘ", "Αποθήκη", "Θάλαμος"], value="Φαρμακείο", label="Current Zone")
            auth_toggle = gr.Checkbox(label="Provide Override Authorization (for Controlled Substances)", value=False)
            undo_btn = gr.Button("⏪ Undo Last Action")
            
        with gr.Column(scale=3):
            with gr.Tabs():
                with gr.Tab("💬 Clinical Chat"):
                    chatbot = gr.Chatbot(height=500)
                    with gr.Row():
                        msg = gr.Textbox(placeholder="E.g., bring two syringes and check if the antibiotic is expired...", show_label=False, scale=4)
                        submit_btn = gr.Button("Send", variant="primary", scale=1)
                    
                    with gr.Accordion("🔍 Explainability & Routing Trace (Expand to see AI reasoning)", open=False):
                        trace_box = gr.Textbox(lines=10, interactive=False, label="Decomposer & Planner Trace")
                        
                with gr.Tab("📊 Live Inventory Dashboard"):
                    inventory_df = gr.Dataframe(value=generate_dashboard(), interactive=False)
                    gr.Markdown("### Audit Log (Recent)")
                    audit_box = gr.Textbox(lines=10, interactive=False, value=get_audit_log())

    submit_btn.click(process_command, [msg, chatbot, role_dd, zone_dd, auth_toggle], [msg, chatbot, trace_box, inventory_df, audit_box])
    msg.submit(process_command, [msg, chatbot, role_dd, zone_dd, auth_toggle], [msg, chatbot, trace_box, inventory_df, audit_box])
    undo_btn.click(undo_last, [chatbot], [chatbot, trace_box, inventory_df])
    
if __name__ == "__main__":
    demo.launch(theme=gr.themes.Soft())
