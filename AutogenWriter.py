import autogen
from autogen import ConversableAgent, UserProxyAgent, GroupChat, GroupChatManager
import json
import sys
import io
import streamlit as st
import requests
from typing import Annotated

class AutogenWriter:
    agents = {}
    def __init__(self, config_path):
        self.CONFIG_PATH = config_path
        self.config_data = self.read_config()
        self.agents = self.initialize_agents(self.config_data)
        self.initialize_callbacks()
        self.firstrun = True
           
    def read_config(self):
        config = {}
        with open(self.CONFIG_PATH, "r") as f:
            config = json.load(f)
        return config[0]
    
    def initialize_callbacks(self):
        self.agents["writer_agent"].register_reply(
            [autogen.Agent, None],
            reply_func=self.send_to_frontend, 
            config={"callback": None},
        ) 
        self.agents["proxy_agent"].register_reply(
            [autogen.Agent, None],
            reply_func=self.send_to_frontend, 
            config={"callback": None},
        ) 
        self.agents["reviewer_agent"].register_reply(
            [autogen.Agent, None],
            reply_func=self.send_to_frontend, 
            config={"callback": None},
        ) 

    def send_to_frontend(self,recipient, messages, sender, config):
        message = messages[-1]
        name = "Human"
        keys = message.keys()
        if "name" in keys:
            name = message["name"]
            if "reviewer" in name:
                name = "Reviewer Agent"
            elif "writer" in name:
                name = "Writer Agent"
            else:
                name = "Human"
        with st.chat_message(name):
            st.markdown(message["content"])
        self.firstrun = False
        return False, None  # required to ensure the agent communication flow continues
    
    def state_transition(self,last_speaker, groupchat):
        messages = groupchat.messages
        if last_speaker is self.agents["proxy_agent"]:
            return self.agents["writer_agent"]
        elif last_speaker is self.agents["writer_agent"]:
            return self.agents["reviewer_agent"]
        elif last_speaker is self.agents["reviewer_agent"]:
            if not "FINISHED" in messages[-1]["content"]:
                return self.agents["writer_agent"]
            else:         
                return self.agents["proxy_agent"]

        else:
            return None
    ''''  
    @staticmethod
    def get_drug_info(self, medication: str, limit: int = 1) -> str:
        """
        Retrieves drug information for a given indication from the OpenFDA API.
    
        :param indication: The medical condition or symptom to query.
        :param limit: The maximum number of results to return.
        :return: A JSON object with the drug information or an error message.
        """
        api_key = "SnxC8nr4Si3zQhI5zgAGOXK2BumHgbnJxtEa3SGV"
        base_url = 'https://api.fda.gov/drug/event.json'
        query = medication
        request_url = f'{base_url}?search={query}&limit={limit}&api_key={api_key}'
    
        response = requests.get(request_url)
    
        if response.status_code == 200:
            result = response.json()
            manufacturer_name = result["results"][0]["patient"]["drug"][0]["openfda"]["manufacturer_name"][0]
            return manufacturer_name
        else:
            return f'Error: {response.status_code} - {response.text}'
        
    def manufacture_name(medication: Annotated[str,"Medication name to get the manufacture name"]) -> str:
        company_name = AutogenWriter.get_drug_info(medication)
        return company_name
    '''
    
    def initialize_agents(self,config_data):
        llm_config_list = [{
            "model": config_data['model'],
            "api_type": config_data['api_type'],
            "api_key": config_data['api_key'],
            "base_url": config_data['base_url'],
            "api_version": config_data['api_version'],
            "temperature": config_data['temperature']
        }]
        

        writer_agent = ConversableAgent(
                "writer_agent",
                system_message="You are a medical writer responsible for writing a summary of adverse events based on the provided medication.",
                llm_config={"config_list": llm_config_list},
                max_consecutive_auto_reply=3,  # maximum number of consecutive auto-replies before asking for human input
                is_termination_msg=lambda msg: "FINISHED" in msg["content"],  # terminate if the reviewer says finished
                human_input_mode="NEVER" # never ask for human input
            )
        
        reviewer_agent = ConversableAgent(
                "reviewer",
                system_message="you are a medical reviewer, you have one primary responsibility: verify the presence of the drug manufacturer's name within the summary provided by the writer agent. If drug manufacturer name doesn’t exist then give feedback to writer agent to rewrite the summary with drug manufacture name. Drug manufacture name is necessary information which is included for regulatory compliance and patient safety. When you fond the drug manufacture name type 'FINISHED'",
                llm_config={"config_list": llm_config_list},
                human_input_mode="NEVER"
            )
        
        proxy_agent = UserProxyAgent(
            "Human",
            system_message="You are the admin for the writer_agent. You can provide feedback to the writer_agent if the summary is incomplete or inaccurate.",
            code_execution_config=False,
            human_input_mode="ALWAYS"
        )

        # Register the tool signature with the reviewer_agent agent.
        '''
        autogen.register_function(
            AutogenWriter.manufacture_name,
            caller=reviewer_agent,
            executor=writer_agent,
            description="Used for getting the manufacture information of a given drug"
       )
       '''
        
        return {
            "writer_agent": writer_agent, 
            "reviewer_agent": reviewer_agent,
            "proxy_agent": proxy_agent
            }
    
    async def run_agents(self,input_medication):
        self.group_chat = GroupChat(
        agents=[self.agents["writer_agent"],self.agents["proxy_agent"],self.agents["reviewer_agent"]], 
        messages=[], 
        max_round=50,
        speaker_selection_method=self.state_transition)
        self.group_chat_manager = GroupChatManager(self.group_chat)
        return self.agents['proxy_agent'].initiate_chat(
                self.group_chat_manager,
                message="Write a summary of all the adverse events associated with: "+input_medication,           
        )

def main():
    global agents  
    agent_model = AutogenWriter(r"C:\Users\amimukherjee\OneDrive - Microsoft\Documents\Demo\AutoGen\llm_config.json")
    group_chat = GroupChat(
        agents=[agents["writer_agent"],agents["proxy_agent"],agents["reviewer_agent"]], 
        messages=[], 
        max_round=50,
        speaker_selection_method=agent_model.state_transition)
    group_chat_manager = GroupChatManager(group_chat)
    console_prompt = ""
    while True:
        console_prompt = input("Enter an adverse events or type 'exit' to quit the program: ")
        if console_prompt == "exit":
            break
        agents['proxy_agent'].initiate_chat(
            group_chat_manager,
            message="Write a summary of all the adverse events associated with: "+console_prompt,
            
        )

    if __name__ == "__main__":
        main()