import streamlit as st
import plotly.graph_objects as go
import os
from agent.openai_cfo_agent import OpenAICFOAgent 

st.cache_data.clear()

def create_chart(config):
    """
    Create a Plotly chart based on configuration.
    """
    if not config or "data" not in config:
        return None
    
    chart_type = config.get("chart_type", "bar")
    title = config.get("title", "")
    data = config["data"]
    
    try:
        if chart_type == "bar":
            fig = go.Figure(data=[
                go.Bar(
                    x=data.get("labels", []),
                    y=data.get("values", []),
                    marker_color='rgb(55, 83, 109)'
                )
            ])
            fig.update_layout(
                title=title,
                xaxis_title=config.get("x_label", ""),
                yaxis_title=config.get("y_label", ""),
                template="plotly_white",
                height=400
            )
            
        elif chart_type == "line":
            fig = go.Figure(data=[
                go.Scatter(
                    x=data.get("labels", []),
                    y=data.get("values", []),
                    mode='lines+markers',
                    line=dict(color='rgb(55, 83, 109)', width=3),
                    marker=dict(size=8)
                )
            ])
            fig.update_layout(
                title=title,
                xaxis_title=config.get("x_label", ""),
                yaxis_title=config.get("y_label", ""),
                template="plotly_white",
                height=400
            )
            
        elif chart_type == "pie":
            fig = go.Figure(data=[
                go.Pie(
                    labels=data.get("labels", []),
                    values=data.get("values", []),
                    hole=0.3
                )
            ])
            fig.update_layout(
                title=title,
                template="plotly_white",
                height=400
            )
            
        elif chart_type == "area":
            fig = go.Figure(data=[
                go.Scatter(
                    x=data.get("labels", []),
                    y=data.get("values", []),
                    fill='tozeroy',
                    line=dict(color='rgb(55, 83, 109)')
                )
            ])
            fig.update_layout(
                title=title,
                xaxis_title=config.get("x_label", ""),
                yaxis_title=config.get("y_label", ""),
                template="plotly_white",
                height=400
            )
        
        else:
            return None
        
        return fig
        
    except Exception as e:
        st.error(f"Error creating chart: {str(e)}")
        return None
    

st.set_page_config(
    page_title="CFO AI Assistant",
    layout="wide"
)

if 'agent' not in st.session_state:
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        st.error("⚠️ No API key found! Please set OPENAI_API_KEY environment variable")
        st.info("""
        **Setup Instructions:**
        
        ```bash
        export OPENAI_API_KEY='sk-proj-...'
        ```
        
        Then restart the app.
        """)
        st.stop()
    st.session_state.agent = OpenAICFOAgent(api_key)

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

st.title("CFO AI Assistant")
st.markdown("Ask me anything about your company's financials! *Powered by OpenAI GPT-4*")

with st.sidebar:
    st.header("Example Questions")
    
    examples = [
        "What was our revenue vs budget for Q2 2025?",
        "Show me the gross margin trend for the last 6 months",
        "Break down our operating expenses for this year",
        "What's our cash runway based on last 3 months?",
        "Calculate EBITDA for Q1 2025",
        "How did we perform against our revenue targets in June?",
        "What's our biggest operating expense category this quarter?"
    ]
    
    for i, example in enumerate(examples):
        if st.button(example, key=f"example_{i}", use_container_width=True):
            st.session_state.pending_query = example
            st.rerun()
    
    st.divider()
    

    st.info("🤖 Using: **OpenAI GPT-4**")
    
    if st.button("🔄 Reset Conversation", use_container_width=True):
        st.session_state.agent.reset_conversation()
        st.session_state.chat_history = []
        st.rerun()


if 'pending_query' in st.session_state:
    prompt = st.session_state.pending_query
    del st.session_state.pending_query
    
    st.session_state.chat_history.append({
        "role": "user",
        "content": prompt
    })
    
    with st.spinner("Analyzing..."):
        try:
            response = st.session_state.agent.ask(prompt)
            
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response["answer"],
                "chart": response.get("chart_config")
            })
            
        except Exception as e:
            error_msg = f"Sorry, I encountered an error: {str(e)}"
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": error_msg
            })

for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.text(message["content"])

        if message["role"] == "assistant" and "chart" in message and message["chart"]:
            fig = create_chart(message["chart"])
            if fig:
                st.plotly_chart(fig, use_container_width=True)

if prompt := st.chat_input("Ask a financial question..."):
    st.session_state.chat_history.append({
        "role": "user",
        "content": prompt
    })
    
    with st.chat_message("user"):
        st.text(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            try:
                response = st.session_state.agent.ask(prompt)
                
                st.text(response["answer"])
                
                chart_config = response.get("chart_config")
                if chart_config:
                    fig = create_chart(chart_config)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response["answer"],
                    "chart": chart_config
                })
                
            except Exception as e:
                error_msg = f"Sorry, I encountered an error: {str(e)}"
                st.error(error_msg)
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": error_msg
                })


st.divider()
st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 0.8em;'>
    Powered by OpenAI GPT-4 | Financial data is analyzed in real-time
    </div>
    """,
    unsafe_allow_html=True
)