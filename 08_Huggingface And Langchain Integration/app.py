import validators
import streamlit as st
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEndpoint
from langchain_community.document_loaders import YoutubeLoader,UnstructuredURLLoader
from langchain.chains.summarize import load_summarize_chain
import os
from dotenv import load_dotenv
load_dotenv()

# Environment Setup
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ['LANGCHAIN_API_KEY'] = os.getenv('LANGCHAIN_API_KEY')
os.environ['LANGCHAIN_PROJECT'] = 'Langchain - Summarize Text From YT or Website'


# Streamlit App
st.set_page_config(page_title="LangChain: Summarize Text From YT or Website", page_icon="🦜")
st.title("🦜 LangChain: Summarize Text From YT or Website")
st.subheader('Summarize URL')


# Get Groq API key and URL to be summarized
with st.sidebar:
    hf_token = st.text_input("HuggingFace API key",type="password")

repo_id = "mistralai/Mistral-7B-Instruct-v0.3"


# LLM Model Initialization
# llm = ChatGroq(model='llama3-8b-8192',groq_api_key=groq_api_key)
llm = HuggingFaceEndpoint(
    repo_id=repo_id,
    temperature = 0.7,
    model_kwargs={
        "max_length": 150,
        "headers": {"Authorization": f"Bearer {hf_token}"}
    }
)

# Prompt Template
prompt_template = """
Provide Summary of the following content in 400 words:
Content: {text}
"""

prompt = PromptTemplate(template=prompt_template,
                        input_variables='text')


# Reading URL 
generic_url = st.text_input("URL",label_visibility="collapsed")


if st.button("Sumarize the content from YouTube or Website"):
    # Validate all the inputs
    if not hf_token.strip() or not generic_url.strip():
        st.error("Please provide the information o get started")
    elif not validators.url(generic_url):
        st.error("Please enter a valid URL. It can may be a YouTube video URL or Website URL")
    else:
        try:
            with st.spinner("Waiting..."):
            # Loading Website or YouTube Video Data
                if "youtube.com" in generic_url:
                    loader = YoutubeLoader.from_youtube_url(generic_url,add_video_info = True)
                else:
                    loader = UnstructuredURLLoader(urls = [generic_url], 
                                           ssl_verify = False,
                                           headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"}
                                           )
                docs = loader.load()

                # Chain For Summarization
                chain = load_summarize_chain(llm = llm, chain_type='stuff',prompt = prompt)
                output_summary = chain.run(docs)
                
                st.success(output_summary)
        except Exception as e:
            st.exception(f"Exception: {e}")
            