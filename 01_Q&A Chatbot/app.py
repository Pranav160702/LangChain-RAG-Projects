import streamlit as st
# from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq 

import os
from dotenv import load_dotenv

load_dotenv()

# LangSmith Tracing
os.environ['LANGCHAIN_API_KEY'] = os.getenv('LANGCHAIN_API_KEY')
os.environ['LANGCHAIN_TRACING_V2'] = 'true'
os.environ['LANGCHAIN_PROJECT'] = 'Simple Q&A Chatbot With Ollama'

groq_api_key = os.getenv('GROQ_API_KEY')

# Prompt Template
prompt = ChatPromptTemplate.from_messages(
    [
        ("system","You are a helpful assistant. Please response to the user queries"),
        ("user","Question:{question}")
    ]
)

def generate_response(question,groq_api_key,llm,temperature,max_tokens):
    # Initialize the model
    llm = ChatGroq(model = llm, groq_api_key = groq_api_key)
    # Output Parser
    output_parser = StrOutputParser()
    # Create Chain
    chain = prompt | llm | output_parser
    # Response
    answer = chain.invoke({'question':question})
    return answer


# Title of the app
st.title("Enhanced Q&A Chatbot With Ollama")

# Sidebar for Settings
st.sidebar.title("Settings")
# groq_api_key = st.sidebar.text_input("Enter your API Key")

# Drop down to select various Models
llm = st.sidebar.selectbox("Select the Model",["llama3-8b-8192","llama3-70b-8192","mixtral-8x7b-32768","gemma2-9b-it"])

# Adjust response parameter
temperature = st.sidebar.slider("Temperature", min_value = 0.0,max_value = 1.0, value = 0.7)
max_tokens = st.sidebar.slider("Max Tokens", min_value = 50,max_value = 300, value = 150)

# Main Interfacee for User Input
st.write("Go ahead and ask any question")
user_input = st.text_input("You:")

if user_input:
    response = generate_response(user_input,groq_api_key,llm,temperature,max_tokens)
    st.write(response)
else:
    st.write("Please Provide the query")