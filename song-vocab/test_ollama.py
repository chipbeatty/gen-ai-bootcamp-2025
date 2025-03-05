from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage

def test_ollama():
    print("Creating ChatOllama instance...")
    llm = ChatOllama(model="mistral")
    
    print("Testing with a simple message...")
    messages = [HumanMessage(content="Say hello!")]
    response = llm.invoke(messages)
    
    print("Response:", response.content)

if __name__ == "__main__":
    test_ollama()
