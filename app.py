import streamlit as st
import asyncio
from autogen import ConversableAgent
from AutogenWriter import AutogenWriter

st.header(':rainbow[Drug Adverse events Powered By AutoGen]',divider='rainbow')


class TrackableConversableAgent(ConversableAgent):
    def _process_received_message(self, message, sender, silent):
        with st.chat_message(sender.name):
            st.markdown(message)
        return super()._process_received_message(message, sender, silent)

CONFIG_PATH = r"C:\Users\amimukherjee\OneDrive - Microsoft\Documents\Demo\AutoGen\llm_config.json"
agent_model = AutogenWriter(CONFIG_PATH)

with st.sidebar:
    model = agent_model.config_data["model"]
    api_type = agent_model.config_data["api_type"]
    api_version = agent_model.config_data["api_version"]
    st.header(':green[Azure OpenAI Configuration]')
    st.subheader(':orange[Model:] ' + model)
    st.subheader(':orange[API Type:] ' + api_type)
    st.subheader(':orange[API Version:] ' + api_version)

with st.container():
    # for message in st.session_state["messages"]:
    #    st.markdown(message)

    user_input = st.chat_input("Enter a medication to get all the adverse events associated with that medication...")
    if user_input:
        
        # Create an event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Define an asynchronous function
        async def initiate_chat():
            await agent_model.run_agents(user_input)

        # Run the asynchronous function within the event loop
        loop.run_until_complete(initiate_chat())