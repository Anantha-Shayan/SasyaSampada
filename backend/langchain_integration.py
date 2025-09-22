import os
from typing import List, Optional
from fastapi import HTTPException
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import HuggingFaceHub
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationSummaryMemory

# Setup: embeddings + vectorstore(FAISS)
EMBED_MODEL = "all-MiniLM-L6-v2"
embeddings = SentenceTransformerEmbeddings(model_name=EMBED_MODEL)

# Sample agricultural knowledge base
raw_texts = [
    ("agricultural_basics", "Crop rotation is essential for maintaining soil health. Different crops have different nutrient requirements and pest vulnerabilities."),
    ("soil_management", "Soil pH affects nutrient availability. Most crops prefer pH between 6.0 and 7.5. Regular soil testing helps determine fertilizer needs."),
    ("irrigation_tips", "Water crops early in the morning to reduce evaporation. Drip irrigation is more efficient than sprinkler systems."),
    ("pest_control", "Integrated Pest Management (IPM) combines biological, cultural, and chemical methods to control pests while minimizing environmental impact."),
    ("fertilizer_guide", "Nitrogen promotes leaf growth, phosphorus supports root development, and potassium improves overall plant health and disease resistance."),
    ("weather_impact", "Monitor weather forecasts to plan planting and harvesting. Extreme temperatures and heavy rainfall can damage crops."),
    ("market_timing", "Harvest timing affects crop quality and market prices. Early harvest may yield lower quality, while late harvest risks weather damage."),
    ("crop_selection", "Choose crops based on soil type, climate, water availability, and market demand. Consider crop rotation for sustainable farming."),
    ("disease_prevention", "Prevent plant diseases by maintaining proper spacing, ensuring good air circulation, and using disease-resistant varieties."),
    ("harvest_storage", "Proper storage conditions prevent post-harvest losses. Control temperature, humidity, and ventilation in storage facilities.")
]

documents = [Document(page_content=txt, metadata={"source": src}) for src, txt in raw_texts]

# Split & create FAISS index
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
chunks = splitter.split_documents(documents)
vectorstore = FAISS.from_documents(chunks, embeddings)

# Choose LLM backend
hf_token = os.getenv("HUGGINGFACEHUB_API_KEY")
if not hf_token:
    print("Warning: HUGGINGFACEHUB_API_KEY not found. Using mock responses.")
    llm = None
else:
    llm = HuggingFaceHub(
        repo_id=os.getenv("HF_REPO", "tiiuae/falcon-7b-instruct"),
        huggingfacehub_api_token=hf_token
    )

# Memory (Summary)
if llm:
    memory = ConversationSummaryMemory(llm=llm, memory_key="chat_history", max_token_limit=500)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    qa = ConversationalRetrievalChain.from_llm(llm, retriever, memory=memory)
else:
    memory = None
    qa = None

# Prompt template
SYSTEM_INSTRUCTION = "You are a helpful agricultural assistant. Provide clear, practical advice for farmers. Use simple language and focus on actionable recommendations."

def get_chat_response(question: str, session_id: str = "default") -> str:
    """
    Get a response from the agricultural AI assistant
    """
    try:
        if not qa:
            # Return mock response if LLM is not available
            return get_mock_response(question)
        
        # Build inputs for chain
        out = qa({"question": f"{SYSTEM_INSTRUCTION}\nUser: {question}"})
        
        answer = out.get("answer") or out.get("text") or ""
        sources = []
        for d in out.get("source_documents", []):
            sources.append(d.metadata.get("source"))
        
        return {
            "answer": answer.strip(),
            "sources": sources
        }
    except Exception as e:
        print(f"Error in chat response: {e}")
        return get_mock_response(question)

def get_mock_response(question: str) -> str:
    """
    Provide mock responses when LLM is not available
    """
    question_lower = question.lower()
    
    if "soil" in question_lower:
        return {
            "answer": "For healthy soil, test pH levels regularly and maintain organic matter content. Most crops prefer pH between 6.0-7.5. Add compost or manure to improve soil structure and fertility.",
            "sources": ["soil_management"]
        }
    elif "pest" in question_lower or "insect" in question_lower:
        return {
            "answer": "Use Integrated Pest Management (IPM) approach. Start with cultural methods like crop rotation and proper spacing. Use biological controls like beneficial insects. Chemical pesticides should be the last resort.",
            "sources": ["pest_control"]
        }
    elif "water" in question_lower or "irrigation" in question_lower:
        return {
            "answer": "Water crops early in the morning to reduce evaporation. Drip irrigation is more efficient than sprinkler systems. Monitor soil moisture and adjust watering based on weather conditions.",
            "sources": ["irrigation_tips"]
        }
    elif "fertilizer" in question_lower or "nutrient" in question_lower:
        return {
            "answer": "Nitrogen promotes leaf growth, phosphorus supports root development, and potassium improves plant health. Test your soil to determine specific nutrient needs. Apply fertilizers at the right time and in proper amounts.",
            "sources": ["fertilizer_guide"]
        }
    elif "weather" in question_lower or "climate" in question_lower:
        return {
            "answer": "Monitor weather forecasts regularly to plan farming activities. Protect crops from extreme temperatures and heavy rainfall. Use weather data to optimize planting and harvesting times.",
            "sources": ["weather_impact"]
        }
    else:
        return {
            "answer": "I'm here to help with your farming questions! Ask me about soil management, pest control, irrigation, fertilizers, weather, or any other agricultural topic.",
            "sources": ["agricultural_basics"]
        }
