from llm.agent import LLMAgent


def test_llm_agent_initializes_with_expected_prompt(monkeypatch):
    llm_instances = []
    toolkit_instances = []

    class FakeChatGroq:
        def __init__(self, **kwargs):
            self.kwargs = kwargs
            llm_instances.append(self)

    class FakeToolkit:
        def __init__(self, db, llm):
            self.db = db
            self.llm = llm
            toolkit_instances.append(self)

        def get_tools(self):
            return ["sql-tool"]

    monkeypatch.setenv("DB_DIALECT", "PostgreSQL")
    monkeypatch.setattr("llm.agent.ChatGroq", FakeChatGroq)
    monkeypatch.setattr("llm.agent.SQLDatabaseToolkit", FakeToolkit)

    agent = LLMAgent(db="db-conn")

    assert llm_instances[0].kwargs == {
        "model": "llama-3.3-70b-versatile",
        "temperature": 0,
    }
    assert toolkit_instances[0].db == "db-conn"
    assert toolkit_instances[0].llm is llm_instances[0]
    assert "PostgreSQL database" in agent.system_message
    assert "limit your query to 5 results" in agent.system_message


def test_create_agent_uses_toolkit_tools_and_prompt(monkeypatch):
    calls = []

    class FakeChatGroq:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    class FakeToolkit:
        def __init__(self, db, llm):
            self.db = db
            self.llm = llm

        def get_tools(self):
            return ["tool-a", "tool-b"]

    def fake_create_react_agent(llm, tools, prompt):
        calls.append((llm, tools, prompt))
        return "agent-executor"

    monkeypatch.setattr("llm.agent.ChatGroq", FakeChatGroq)
    monkeypatch.setattr("llm.agent.SQLDatabaseToolkit", FakeToolkit)
    monkeypatch.setattr("llm.agent.create_react_agent", fake_create_react_agent)

    agent = LLMAgent(db="db-conn")
    created = agent.create_agent()

    assert created == "agent-executor"
    assert calls == [(agent.llm, ["tool-a", "tool-b"], agent.system_message)]
