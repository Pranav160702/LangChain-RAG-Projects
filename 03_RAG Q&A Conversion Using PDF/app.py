import streamlit as st
from langchain.chains import create_history_aware_retriever
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.vectorstores import FAISS
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_groq import ChatGroq
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

import os
from dotenv import load_dotenv
load_dotenv()

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ['LANGCHAIN_API_KEY'] = os.getenv('LANGCHAIN_API_KEY')
os.environ['LANGCHAIN_PROJECT'] = 'RAG Q&A Conversion Using PDF'

os.environ['HF_TOKEN'] = os.getenv('HF_TOKEN')

embeddings = HuggingFaceEmbeddings(model_name = "all-MiniLM-L6-v2")

# Set up Streamlit App
st.title("Conversational RAG With PDF uploads and Chat History")
st.write("Upload Pdf's and chat with their content")

# Imput the Groq API Key
api_key = st.text_input("Enter your Groq API key:",type = "password")

# Check if Groq Api key is provided
if api_key:
    llm = ChatGroq(groq_api_key = api_key, model = 'llama3-8b-8192')

    session_id = st.text_input("Session ID", value = "default_session")

    # Statefully manage chat history
    if 'store' not in st.session_state:
        st.session_state.store = {}

    uploaded_file = st.file_uploader("Choose A PDF file", type = "pdf", accept_multiple_files=False)

    # Process uploaded PDF's
    if uploaded_file:
        
        # Create a list to store documents
        documents = []

        # File uploader widget
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf", accept_multiple_files = False)

        if uploaded_file is not None:
            # Save the uploaded file to a temporary location
            temp_pdf = "./temp.pdf"
            with open(temp_pdf, 'wb') as file:
                file.write(uploaded_file.read())  # Use read() directly since uploaded_file is a file-like object

            # Load the PDF using PyPDFLoader
            loader = PyPDFLoader(temp_pdf)
            docs = loader.load()

            # Append the documents to the list
            documents.extend(docs)

            st.success("PDF file processed successfully!")
            st.write(f"Processed {len(docs)} documents.")

        # Split and create embeddings for the documents
        text_splitter = RecursiveCharacterTextSplitter(chunk_size = 1000, chunk_overlap = 200)
        splits = text_splitter.split_documents(documents)
        vectorstore = FAISS.from_documents(embedding = embeddings, documents = documents)
        retriever = vectorstore.as_retriever()

        contextualize_q_system_prompt = (
            "Given a chat history and latest user question"
            "which might reference context in the chat history,"
            "formulate a standalone question which can be understood"
            "without the chat history. Do NOT answer the question,"
            "just reformulate it if needed and otherwise return it as is."    
            )

        contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system",contextualize_q_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human","{input}")
            ]
            )


        history_aware_retriever = create_history_aware_retriever(llm,retriever,contextualize_q_prompt)

        # Answer Question Prompt
        system_prompt = (
            "You are an assistant for question-answering tasks. "
            "Use the following pieces of retrieved context to answer "
            "the question. If you don't know the answer, say that you "
            "don't know. Use three sentences maximum and keep the "
            "answer concise."
            "\n\n"
            "{context}"
        )

        qa_prompt = ChatPromptTemplate.from_messages(
            [
                ("system",system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human","{input}")
            ]
        )

        question_answer_chain = create_stuff_documents_chain(llm,qa_prompt)
        rag_chain = create_retrieval_chain(history_aware_retriever,question_answer_chain)

        def get_session_history(session:str)->BaseChatMessageHistory:
            if session_id not in st.session_state.store:
                st.session_state.store[session_id] = ChatMessageHistory()
            return st.session_state.store[session_id]

        conversational_rag_chain = RunnableWithMessageHistory(
            rag_chain,
            get_session_history,
            input_messages_key = "input",
            history_messages_key = "chat_history",
            output_messages_key = "answer"
        )

        user_input = st.text_input("Your Question:")
        if user_input:
            session_history = get_session_history(session_id)

            response = conversational_rag_chain.invoke(
                {"input":user_input},
                config={
                    "configurable":{"session_id":session_id}
                }
            )

            st.write(st.session_state.store)
            st.write("Assistant:", response['answer'])
            st.write("Chat History:", session_history.messages)
    else:
        st.warning("Please enter your Groq API Key")

