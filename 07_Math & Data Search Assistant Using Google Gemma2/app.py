import streamlit as st
from langchain_groq import ChatGroq
from langchain.chains import LLMChain, LLMMathChain
from langchain.prompts import PromptTemplate
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.agents.agent_types import AgentType
from langchain.agents import Tool, initialize_agent
from dotenv import load_dotenv
import os
from langchain.callbacks import StreamlitCallbackHandler

load_dotenv()

# Environment Setup
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ['LANGCHAIN_API_KEY'] = os.getenv('LANGCHAIN_API_KEY')
os.environ['LANGCHAIN_PROJECT'] = 'Langchain - Text To Math Problem Solver and Data Search Assistant'

# Set up Streamlit App
st.set_page_config(page_title="LangChain: Text To Math Problem Solver and Data Search Assistant", page_icon="🦜")
st.title("🦜 LangChain: Text To Math Problem Solver Using Gemma 2")


groq_api_key = st.sidebar.text_input(label="Groq API Key", type="password")


if not groq_api_key:
    st.info("Please add your Groq API Key to Continue")
    st.stop()


# Initialize LLM model
llm_model = ChatGroq(groq_api_key = groq_api_key,model = 'Gemma2-9b-It')


# Initialize Wikipedia Tools
wikipedia_wrapper = WikipediaAPIWrapper()

wikipedi_tool = Tool(
    name ="Wikipedia",
    func =wikipedia_wrapper.run,
    description ="Tool for Searchinf the Internetto ind the various info on the mentioned topics."
)


# Initialize the Math Tool
math_chain = LLMMathChain.from_llm(llm = llm_model)

calcuator = Tool(
    name = "Calculator",
    func = math_chain.run,
    description = "The tools for answering math related questions. Onl input mathematical expression needs to be provided."
)

prompt = """
You are a agent tasked for solving users mathematical question. 
Logically arrive at the solution and provide detailed explaination.
and display it point wise for the question below:
Question : {question}
Answer:
"""

prompt_template = PromptTemplate(
    input_variables = ['question'],
    template = prompt
)


# Combine all the tools into chain
chain = LLMChain(llm=llm_model, prompt= prompt_template)

# Creating Reasoning Tool
reasoning_tool = Tool(
    name = "Reasoning",
    func = chain.run,
    description = "A too for answering logic-based and reasoning questions."
)


#Initialize the Agents 
assistant_agent = initialize_agent(
    tools = [wikipedi_tool,calcuator,reasoning_tool],
    llm = llm_model,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose = True,
    handle_parsing_errors = True
)


if "messages" not in st.session_state:
    st.session_state['messages'] = [
        {'role':'assistant_agent', 'content':"Hi I am a Math Chatbot, Who can Answer all your Math questions."}
    ]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])


question = st.text_area("Enter Tour Question Here.")


if st.button("Find my Answer"):
    if question:
        with st.spinner("Generate Response"):
            st.session_state.messages.append( {'role':'user', 'content':question})
            st.chat_message("user").write(question)

            st_cb = StreamlitCallbackHandler(st.container(),expand_new_thoughts=False)
            response = assistant_agent.run(st.session_state.messages,callbacks=[st_cb])

            st.session_state.messages.append({'role':'assistant', 'content':response})
            st.write("### Response")
            st.success(response)
    else:
       st.warning("Please Enter The Question.") 
