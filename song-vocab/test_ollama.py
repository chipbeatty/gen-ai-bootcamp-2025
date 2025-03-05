from langchain.chat_models import ChatOllama

def test_ollama():
    print("Creating ChatOllama instance...")
    llm = ChatOllama(model="mistral")
    
    print("Testing with a simple prompt...")
    response = llm.predict("Say hello!")
    
    print("Response:", response)

if __name__ == "__main__":
    test_ollama()
