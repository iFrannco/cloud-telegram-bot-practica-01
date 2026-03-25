"""
LLM and agent setup module.
"""
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain import hub
from langgraph.prebuilt import create_react_agent
from config import logger

class LLMAgent:
    """Class to manage the LLM agent and tools."""

    def __init__(self, db):
        """Initialize the LLM and toolkit with the given database."""
        logger.info("Setting up LLM agent...")
        self.db = db
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7)
        self.toolkit = SQLDatabaseToolkit(db=self.db, llm=self.llm)

        # Get the prompt template
        # https://smith.langchain.com/hub/langchain-ai/sql-agent-system-prompt?organizationId=abbb9e9c-39f6-42e7-92d8-07eb07b3f18a
        prompt_template = hub.pull("langchain-ai/sql-agent-system-prompt")
        dialect = os.getenv("DB_DIALECT", "SQLite")
        self.system_message = prompt_template.format(dialect=dialect, top_k=5)
        logger.info("LLM agent setup complete")

    def create_agent(self):
        """Create and return a reactive agent with the toolkit."""
        return create_react_agent(
            self.llm,
            self.toolkit.get_tools(),
            prompt=self.system_message
        )