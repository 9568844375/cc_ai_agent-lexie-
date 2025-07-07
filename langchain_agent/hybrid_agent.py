from langchain.agents import initialize_agent, Tool
from langchain.chains import RetrievalQA
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import RedisChatMessageHistory
from langchain.llms import OpenAI

from .mongo_tool import find_high_cgpa_students
from .vector_store import get_vector_store

def get_context_aware_hybrid_agent(user_id: str = "default_user"):
    llm = OpenAI(temperature=0)

    # 🧠 Redis-based memory (chat history for each user)
    history = RedisChatMessageHistory(
        session_id=user_id,
        url="redis://localhost:6379"  # Change if you're using cloud or Docker
    )
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        chat_memory=history,
        return_messages=True
    )

    # MongoDB query tool
    mongo_tool = Tool(
        name="MongoDBTool",
        func=find_high_cgpa_students,
        description="Fetch student data from MongoDB using filters"
    )

    # Vector DB document search tool
    vectorstore = get_vector_store()
    vector_tool = Tool(
        name="DocumentSearchTool",
        func=RetrievalQA.from_chain_type(
            llm=llm,
            retriever=vectorstore.as_retriever()
        ).run,
        description="Searches documents like assignments, project reports, etc."
    )

    # LangChain agent with both tools and Redis memory
    agent = initialize_agent(
        tools=[mongo_tool, vector_tool],
        llm=llm,
        agent="chat-conversational-react-description",
        memory=memory,
        verbose=True
    )

    return agent
