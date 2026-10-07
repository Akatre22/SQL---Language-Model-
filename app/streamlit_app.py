"""
Unified AI Chat Interface for Tiny SQL LLM
Specialized pure SQL conversational assistant combining:
- Autonomous SQL Execution on PostgreSQL, SQL Server (SSMS), or SQLite
- Live Database Schema Introspection & In-Context Conditioning
- ChromaDB Vector RAG & Relational Knowledge Grounding
- NLP Intent Router for High-Precision Query Handling
"""

import sys
import json
import time
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
import pandas as pd
from inference.generate import TinyLLMInference
from evaluation.evaluate_sql import SQLEvaluator
from knowledge.vector_store import DomainVectorStore
from knowledge.rag_pipeline import TinyLLMRAG
from agent_engine.agent import SQLAgent
from agent_engine.db_sandbox import EnterpriseDBSandbox
from agent_engine.intent_router import SQLIntentRouter, SQLIntent
from agent_engine.schema_formatter import SchemaFormatter

st.set_page_config(
    page_title="Tiny SQL AI Assistant",
    page_icon="⚡",
    layout="wide"
)

# Custom Styling for modern unified chat interface
st.markdown("""
<style>
    .main-title {
        font-size: 2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.1rem;
    }
    .subtitle {
        font-size: 0.95rem;
        color: #64748B;
        margin-bottom: 1.2rem;
    }
    .source-tag {
        background-color: #EFF6FF;
        color: #1D4ED8;
        padding: 0.2rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
    }
    .db-status-connected {
        background-color: #DCFCE7;
        color: #15803D;
        padding: 0.25rem 0.6rem;
        border-radius: 0.375rem;
        font-weight: 600;
        font-size: 0.8rem;
        display: inline-block;
        margin-bottom: 0.5rem;
    }
    .db-status-error {
        background-color: #FEE2E2;
        color: #B91C1C;
        padding: 0.25rem 0.6rem;
        border-radius: 0.375rem;
        font-weight: 600;
        font-size: 0.8rem;
        display: inline-block;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_intent_router():
    return SQLIntentRouter()

@st.cache_resource
def load_rag_pipeline():
    return TinyLLMRAG()

@st.cache_resource
def load_base_sql_agent():
    return SQLAgent()

# Header
st.markdown('<div class="main-title">⚡ Tiny SQL AI Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Autonomous Schema-Conditioned Text-to-SQL + Multi-DB Connectivity (Postgres, SSMS, SQLite) + ChromaDB RAG.</div>', unsafe_allow_html=True)

# Initialize AI Engines
try:
    intent_router = load_intent_router()
    rag_engine = load_rag_pipeline()
    base_agent = load_base_sql_agent()
    system_ready = True
except Exception as e:
    st.error(f"⚠️ Engine initializing error: {e}")
    system_ready = False

# Initialize Session State
if "db_sandbox" not in st.session_state:
    st.session_state.db_sandbox = EnterpriseDBSandbox()
if "db_name_display" not in st.session_state:
    st.session_state.db_name_display = "Sample Enterprise DB (SQLite)"
if "db_status" not in st.session_state:
    st.session_state.db_status = "connected"

# Sidebar Options
with st.sidebar:
    st.header("🗄️ Database Connection")
    
    db_type = st.selectbox(
        "Select Database Type",
        [
            "⚡ Sample Enterprise DB (Default SQLite)",
            "🐘 PostgreSQL",
            "🪟 Microsoft SQL Server (SSMS)",
            "📁 Custom SQLite File",
            "📝 Custom DDL Schema Text"
        ]
    )

    conn_uri = None
    custom_ddl = None

    if db_type == "🐘 PostgreSQL":
        st.caption("Connect to your live PostgreSQL database:")
        use_uri = st.toggle("Enter URI directly", value=False, key="pg_use_uri")
        if use_uri:
            conn_uri = st.text_input("Postgres URI", value="postgresql+psycopg2://postgres:password@localhost:5432/mydb", type="password")
        else:
            col1, col2 = st.columns(2)
            pg_host = col1.text_input("Host", value="localhost", key="pg_host")
            pg_port = col2.text_input("Port", value="5432", key="pg_port")
            pg_db = st.text_input("Database Name", value="postgres", key="pg_db")
            pg_user = st.text_input("Username", value="postgres", key="pg_user")
            pg_pass = st.text_input("Password", type="password", key="pg_pass")
            if pg_host and pg_db and pg_user:
                conn_uri = f"postgresql+psycopg2://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}"

    elif db_type == "🪟 Microsoft SQL Server (SSMS)":
        st.caption("Connect to your SQL Server / SSMS instance:")
        use_uri = st.toggle("Enter URI directly", value=False, key="ms_use_uri")
        if use_uri:
            conn_uri = st.text_input("MSSQL URI", value="mssql+pymssql://sa:password@localhost:1433/mydb", type="password")
        else:
            col1, col2 = st.columns(2)
            ms_host = col1.text_input("Server / Host", value="localhost", key="ms_host")
            ms_port = col2.text_input("Port", value="1433", key="ms_port")
            ms_db = st.text_input("Database Name", value="master", key="ms_db")
            ms_user = st.text_input("Username (SQL Auth)", value="sa", key="ms_user")
            ms_pass = st.text_input("Password", type="password", key="ms_pass")
            if ms_host and ms_db and ms_user:
                conn_uri = f"mssql+pymssql://{ms_user}:{ms_pass}@{ms_host}:{ms_port}/{ms_db}"

    elif db_type == "📁 Custom SQLite File":
        sqlite_path = st.text_input("Path to .db / .sqlite file", value="data/custom.db")
        if sqlite_path:
            conn_uri = f"sqlite:///{sqlite_path.strip().replace('\\', '/')}"

    elif db_type == "📝 Custom DDL Schema Text":
        custom_ddl = st.text_area(
            "Paste CREATE TABLE statements",
            value="CREATE TABLE patients (patient_id INT PRIMARY KEY, name TEXT, age INT, condition TEXT);\nCREATE TABLE visits (visit_id INT PRIMARY KEY, patient_id INT, visit_date DATE, fee REAL);",
            height=120
        )

    if st.button("🔌 Connect & Inspect Database", use_container_width=True, type="primary"):
        try:
            with st.spinner("Connecting and introspecting database schema..."):
                if db_type == "⚡ Sample Enterprise DB (Default SQLite)":
                    st.session_state.db_sandbox = EnterpriseDBSandbox()
                    base_agent.set_database(st.session_state.db_sandbox)
                    st.session_state.db_name_display = "Sample Enterprise DB (SQLite)"
                    st.session_state.db_status = "connected"
                    st.toast("✅ Connected to default Enterprise SQLite Sandbox!", icon="🟢")
                elif custom_ddl:
                    st.session_state.db_sandbox = EnterpriseDBSandbox()
                    base_agent.set_database(st.session_state.db_sandbox)
                    base_agent.set_custom_schema_text(custom_ddl)
                    st.session_state.db_name_display = "Custom In-Memory Schema"
                    st.session_state.db_status = "connected"
                    st.toast("✅ Custom DDL Schema loaded into model context!", icon="🟢")
                elif conn_uri:
                    sandbox = EnterpriseDBSandbox(connection_uri=conn_uri)
                    catalog = base_agent.set_database(sandbox)
                    schema = sandbox.get_schema_summary()
                    st.session_state.db_sandbox = sandbox
                    table_count = len(catalog.tables) if catalog and catalog.tables else len(schema)
                    st.session_state.db_name_display = f"{db_type.split(' ')[1]} ({table_count} tables)"
                    st.session_state.db_status = "connected"
                    st.toast(f"✅ Connected successfully! {table_count} table(s) found.", icon="🟢")
        except Exception as e:
            st.session_state.db_status = f"error: {str(e)}"
            st.error(f"❌ Connection failed: {e}")

    # Display Current Status
    if st.session_state.db_status == "connected":
        st.markdown(f'<div class="db-status-connected">🟢 {st.session_state.db_name_display}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="db-status-error">🔴 {st.session_state.db_status}</div>', unsafe_allow_html=True)

    with st.expander("🔍 Live Database Schema", expanded=False):
        try:
            active_sandbox = st.session_state.db_sandbox
            schema = active_sandbox.get_schema_summary()
            if schema:
                for t, cols in schema.items():
                    st.markdown(f"**`{t}`**")
                    st.caption(f"{', '.join(cols)}")
            else:
                st.caption("No tables detected or using custom DDL context.")
        except Exception as e:
            st.caption(f"Error inspecting schema: {e}")

    st.divider()
    st.header("⚙️ Assistant Settings")
    auto_route = st.checkbox("🧠 Smart Auto-Routing", value=True, help="Automatically routes queries to SQL execution or ChromaDB RAG.")
    use_rag = st.toggle("⚡ Enable ChromaDB RAG", value=True)
    
    st.divider()
    st.subheader("Model Parameters")
    temp = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.15, step=0.05)
    top_k = st.slider("Top-K", min_value=1, max_value=100, value=40, step=5)
    top_p = st.slider("Top-P", min_value=0.1, max_value=1.0, value=0.9, step=0.05)
    rep_penalty = st.slider("Repetition Penalty", min_value=1.0, max_value=2.0, value=1.2, step=0.05)
    max_tokens = st.slider("Max Tokens", min_value=32, max_value=256, value=140, step=16)

    st.divider()
    st.header("🔑 Developer API Keys")
    with st.expander("Generate `AK-nice-*` Key", expanded=False):
        from app.key_manager import APIKeyManager
        km = APIKeyManager()
        client_name_input = st.text_input("Application / Client Name", value="My SQL App", key="km_client_name")
        if st.button("✨ Generate New Key", use_container_width=True):
            new_key_meta = km.create_key(client_name=client_name_input)
            st.success(f"Key created for **{client_name_input}**!")
            st.code(new_key_meta["api_key"], language="text")
            st.caption("🔒 Save this key. Use it in header `Authorization: Bearer AK-nice-...`")

        keys = km.list_keys()
        if keys:
            st.caption(f"**Active Registered Keys ({len(keys)}):**")
            for k in keys[-3:]:
                st.code(f"{k.get('masked_key')} ({k.get('client_name')}) | Calls: {k.get('total_requests')}", language="text")

    st.divider()
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Session Chat History
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello! I am your **Tiny SQL AI Assistant**. You can connect your **PostgreSQL**, **SSMS / SQL Server**, or **SQLite** database and ask me in natural language to **write queries, analyze data, and run them live** on your connected database!"
        }
    ]

# Render Dynamic Suggestion Buttons
st.markdown("##### 💡 Suggested Questions:")
cols = st.columns(4)
quick_prompt = None

active_tables = list(base_agent.catalog.tables.keys()) if base_agent.catalog and base_agent.catalog.tables else []
is_custom_db = st.session_state.get("db_status") == "connected" and st.session_state.get("db_name_display") != "Sample Enterprise DB (SQLite)"

if is_custom_db and active_tables:
    first_tbl = active_tables[0]
    second_tbl = active_tables[1] if len(active_tables) > 1 else first_tbl
    if cols[0].button(f"📋 List All {len(active_tables)} Tables"):
        quick_prompt = f"list name of {len(active_tables)} tables in connected database"
    if cols[1].button(f"🔍 Sample `{first_tbl}`"):
        quick_prompt = f"show top 5 records from {first_tbl}"
    if cols[2].button(f"🔢 Count in `{second_tbl}`"):
        quick_prompt = f"count total records in {second_tbl}"
    if cols[3].button("🪟 WHERE vs HAVING"):
        quick_prompt = "difference between Where and having clause in SQL"
else:
    if cols[0].button("🏆 Top 5 Customers by Spend"):
        quick_prompt = "show top 5 customers by total spend"
    if cols[1].button("👥 Employees & Department"):
        quick_prompt = "show all employees with their department name and salary"
    if cols[2].button("🪟 WHERE vs HAVING"):
        quick_prompt = "difference between Where and having clause in SQL"
    if cols[3].button("🔄 What is CTE in SQL"):
        quick_prompt = "what is CTE and how to write CTE query ?"

# Render Existing Messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("sql_query"):
            st.markdown("**Generated SQL Query:**")
            st.code(msg["sql_query"], language="sql")
        if msg.get("df_data") is not None and not msg["df_data"].empty:
            st.markdown(f"**Execution Results ({msg.get('db_name', 'Connected DB')}):**")
            st.dataframe(msg["df_data"], use_container_width=True)
        st.markdown(msg["content"])
        if msg.get("source_tag"):
            st.markdown(f'<span class="source-tag">📌 {msg["source_tag"]}</span> &nbsp; <span style="color:#6B7280; font-size:0.75rem;">⏱️ {msg.get("latency", 0)}s</span>', unsafe_allow_html=True)

# Handle Chat Input
user_input = st.chat_input("Ask a SQL question or request an analytical query...")
prompt_to_process = quick_prompt if quick_prompt else user_input

if prompt_to_process:
    st.session_state.messages.append({"role": "user", "content": prompt_to_process})
    with st.chat_message("user"):
        st.markdown(prompt_to_process)

    with st.chat_message("assistant"):
        with st.spinner("Processing query..."):
            # Determine Intent via NLP Intent Router
            intent, meta = intent_router.route(prompt_to_process) if auto_route else (SQLIntent.TEXT_TO_SQL, {})

            if intent == SQLIntent.TEXT_TO_SQL:
                # Update SQLAgent to use currently active user database
                active_sandbox = st.session_state.db_sandbox
                base_agent.set_database(active_sandbox)
                if db_type == "📝 Custom DDL Schema Text" and custom_ddl:
                    base_agent.set_custom_schema_text(custom_ddl)

                agent_res = base_agent.run(prompt_to_process)
                sql_code = agent_res["generated_sql"]
                exec_res = agent_res["execution"]
                explanation = agent_res["explanation"]
                latency = agent_res["total_latency_sec"]
                
                df_data = pd.DataFrame(exec_res["rows"], columns=exec_res["columns"]) if exec_res and exec_res["success"] and exec_res["rows"] else None
                
                st.markdown(f"**Generated SQL Query:**")
                st.code(sql_code, language="sql")
                
                if df_data is not None:
                    st.markdown(f"**Execution Results ({st.session_state.db_name_display}):**")
                    st.dataframe(df_data, use_container_width=True)
                    
                st.markdown(f"**Explanation:**\n{explanation}")
                st.markdown(f'<span class="source-tag">⚡ SQL Agent ({st.session_state.db_name_display})</span> &nbsp; <span style="color:#6B7280; font-size:0.75rem;">⏱️ {latency}s</span>', unsafe_allow_html=True)
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"**Explanation:**\n{explanation}",
                    "sql_query": sql_code,
                    "df_data": df_data,
                    "db_name": st.session_state.db_name_display,
                    "source_tag": f"SQL Agent ({st.session_state.db_name_display})",
                    "latency": latency
                })
            else:
                # Route to ChromaDB RAG / Concept Synthesizer
                rag_res = rag_engine.answer_with_rag(
                    question=prompt_to_process,
                    n_results=2,
                    use_rag=use_rag,
                    max_new_tokens=max_tokens,
                    temperature=temp,
                    chat_history=st.session_state.messages
                )
                answer_text = rag_res["answer"]
                source_tag = f"{rag_res['primary_source']} — {rag_res['document_title']}"
                latency = rag_res["latency_sec"]
                
                st.markdown(answer_text)
                st.markdown(f'<span class="source-tag">📌 {source_tag}</span> &nbsp; <span style="color:#6B7280; font-size:0.75rem;">⏱️ {latency}s</span>', unsafe_allow_html=True)
                
                if rag_res.get("retrieved_docs"):
                    with st.expander("📚 Inspect Retrieved Context & Hybrid Scoring", expanded=False):
                        if rag_res.get("search_query") and rag_res.get("search_query") != prompt_to_process:
                            st.caption(f"🔄 **Contextualized Search Query:** `{rag_res['search_query']}`")
                        for idx, doc in enumerate(rag_res["retrieved_docs"][:2]):
                            st.markdown(f"**Doc {idx+1}:** `{doc.get('id')}` — *{doc['metadata'].get('title')}*")
                            st.caption(f"Overall Boosted Score: **{doc.get('final_score')}** | Dense Vector Sim: **{doc.get('similarity')}** | BM25 Score: **{doc.get('bm25_score', 'N/A')}**")
                            st.info(doc["text"])

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer_text,
                    "source_tag": source_tag,
                    "latency": latency
                })
