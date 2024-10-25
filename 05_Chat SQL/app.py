import streamlit as st
from pathlib import Path
from langchain.agents import create_sql_agent   #Construct a SQL agent from an LLM and Toolkit or database
from langchain.sql_database import SQLDatabase  # 
from langchain.agents.agent_types import AgentType
from langchain.callbacks import StreamlitCallbackHandler
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from sqlalchemy import create_engine    # Will help to map with respect to the output that specifically coming from SQL Database
import sqlite3
from langchain_groq import ChatGroq
import os

# Environment Setup
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ['LANGCHAIN_API_KEY'] = os.getenv('LANGCHAIN_API_KEY')
os.environ['LANGCHAIN_PROJECT'] = 'Langchain - Chat with SQL DB'

st.set_page_config(page_title="LangChain: Chat with SQL DB", page_icon="🦜")
st.title("🦜 LangChain: Chat with SQL DB")

INJECTION_WARNING = """
                    SQL agent can be vulnerable to prompt injection. Use a DB role with limited permissions.
                    Read More [here](https://python.langchain.com/docs/security).
                    """

LOCALDB = "USE_LOCALDB"
MYSQL = "USE _MYSQL"

# Radio Options
radio_opt = ["Use SQLLite 3 Database - Student.db","Connect to your SQL Database"]
selected_opt = st.sidebar.radio(label="Choose the DB which you want to chat",options = radio_opt)


if radio_opt.index(selected_opt) == 1:
    db_uri = MYSQL
    mysql_host = st.sidebar.text_input("Provide My SQL Host")
    mysql_user = st.sidebar.text_input("MYSQL User")
    mysql_password = st.sidebar.text_input("MYSQL Password",type="password")
    mysql_db = st.sidebar.text_input("MySQL Database")
else:
    db_uri = LOCALDB

api_key = st.sidebar.text_input(label="Groq API Key",type="password")

if not db_uri:
    st.info("Please enter the database information and url")

if not api_key:
    st.info("Please add te Groq API Key")

# LLM Model
llm_model = ChatGroq(groq_api_key = api_key, model_name = 'llama3-8b-8192',streaming=True)

@st.cache_resource(ttl="2h")
def configure_db(db_uri,mysql_host = None, mysql_user = None, mysql_password = None, mysql_db = None):
    if db_uri == LOCALDB:
        db_file_path = (Path(__file__).parent/"student.db").absolute()
        print(db_file_path)
        creator = lambda: sqlite3.connect(f"file:{db_file_path}? mode = ro",uri=True)
        return SQLDatabase(create_engine("sqlite:///",creator = creator))
    elif db_uri == MYSQL:
        if not (mysql_host and mysql_user and mysql_password and mysql_db):
            st.error("Please Provide all MySQL connection details.")
            st.stop()
        return SQLDatabase(create_engine(f"mysql+mysqlconnector://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_db}"))

if db_uri == MYSQL:
    db = configure_db(db_uri,mysql_host,mysql_user,mysql_password,mysql_db)
else:
    db = configure_db(db_uri)

# Toolkit
toolkit = SQLDatabaseToolkit(db= db,llm = llm_model)

agent = create_sql_agent(
    llm = llm_model,
    toolkit = toolkit,
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    handle_parsing_errors=True
)

if "messages" not in st.session_state or st.sidebar.button("Clear Message History"):
    st.session_state["messages"] = [{"role":"assistant","content":"How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_query = st.chat_input(placeholder='Ask anything from the database')

if user_query:
    st.session_state.messages.append({"role":"user", "content":user_query})
    st.chat_message("user").write(user_query)

    with st.chat_message("assistant"):
        streamlit_callback = StreamlitCallbackHandler(st.container())
        response = agent.run(user_query, callbacks = [streamlit_callback])
        st.session_state.messages.append({"role":"assistant","content":response})
        st.write(response)