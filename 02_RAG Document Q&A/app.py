import streamlit as st
import os
from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain

from dotenv import load_dotenv
load_dotenv()

#Groq api key
groq_api_key = os.getenv('GROQ_API_KEY')  

os.environ['LANGCHAIN_API_KEY'] = os.getenv('LANGCHAIN_API_KEY')
os.environ['LANGCHAIN_TRACING_V2'] = 'true'
os.environ['LANGCHAIN_PROJECT'] = 'RAG Document Q&A'
os.environ['HF_TOKEN'] = os.getenv('HF_TOKEN')

# LLM model
llm = ChatGroq(model = 'llama3-8b-8192',groq_api_key = groq_api_key)

# Prompt Template
prompt = ChatPromptTemplate.from_template(
    """
    Answer the questions based on the provided conntext only.
    Please provide the most accurate response based on the question
    <conext>
    {context}
    </context>
    Question : {input}
    """
)


def create_vector_embedding():
    if "vectors" not in st.session_state:
        st.session_state.embeddings = HuggingFaceEmbeddings(model_name = "all-MiniLM-L6-v2")
        # st.session_state.embeddings = OllamaEmbeddings(model='llama3:8b')
        st.session_state.loader = PyPDFDirectoryLoader('research_papers') # Data ingestion
        st.session_state.docs = st.session_state.loader.load()  # Document Loading
        st.session_state.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200) 
        st.session_state.final_documents = st.session_state.text_splitter.split_documents(st.session_state.docs) 
        st.session_state.vectors = FAISS.from_documents(st.session_state.final_documents, st.session_state.embeddings)


st.title("RAG Document Q&A With Groq And Lamma3")

user_prompt = st.text_input("Enter your query from the research paper.")

if st.button("Document Embedding"):
    create_vector_embedding()
    st.write("Vector Database is Ready!")

import time

if user_prompt:
    document_chain = create_stuff_documents_chain(llm,prompt)
    retriever = st.session_state.vectors.as_retriever()    
    retriever_chain = create_retrieval_chain(retriever, document_chain)
    
    start = time.process_time()
    response = retriever_chain.invoke({'input':user_prompt})
    st.write(f"Response time: {time.process_time() - start:.2f} seconds")
    
    st.write(response['answer'])

    # With a streamlit expander
    with st.expander("Document Similarity Search:"):
        for i,doc in enumerate(response['context']):
            st.write(doc.page_content)
            st.write('---------------------------')




