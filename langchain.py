import os
import requests
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from bs4 import BeautifulSoup

from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import HuggingFaceHub
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationSummaryMemory
from youtube_transcript_api import YouTubeTranscriptApi

app = FastAPI(title="LangChain FAISS Chatbot")


# Pydantic
class ChatRequest(BaseModel):
    question: str
    session_id: Optional[str] = "default"


def scrape_text_from_url(url: str) -> str:
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        # Extract visible text
        texts = soup.stripped_strings
        return " ".join(texts)
    except Exception as e:
        return f"Failed to scrape {url}: {e}"


def extract_youtube_transcript(video_id: str) -> str:
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=["en"])
        return " ".join([t["text"] for t in transcript])
    except Exception as e:
        return f"Failed to fetch transcript for {video_id}: {e}"

# Setup: embeddings + FAISS
EMBED_MODEL = "all-MiniLM-L6-v2"
embeddings = SentenceTransformerEmbeddings(model_name=EMBED_MODEL)

# Ingestion sources
urls = [
    "https://icar.org.in/",
    "https://agmarknet.gov.in/",
    "https://farmer.gov.in/",
    "https://niti.gov.in/",
    "https://www.fao.org/india/en/",
    "https://vikaspedia.in/agriculture",
    "https://agricoop.nic.in/",
    "https://www.india.gov.in/topics/agriculture",
    "https://www.iari.res.in/",
    "https://rbi.org.in/Scripts/BS_ViewBulletin.aspx"
]

# Web scrape
documents = []
for url in urls:
    text = scrape_text_from_url(url)
    documents.append(Document(page_content=text, metadata={"source": url}))

youtube_videos = ["1-vcErOPofQ", "To8zM0QxTu0", "PfQ8D9sb2-A" , "goUswnV3pKc" , "HnZ1N7eH6JY", "Sn5xXByPfxY",
                  "3S63r8_g5ic", "Z_5Qp5V0NDY"]
for vid in youtube_videos:
    text = extract_youtube_transcript(vid)
    documents.append(Document(page_content=text, metadata={"source": f"https://youtube.com/watch?v={vid}"}))


splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
chunks = splitter.split_documents(documents)
vectorstore = FAISS.from_documents(chunks, embeddings)


hf_token = os.getenv("HUGGINGFACEHUB_API_KEY")
if not hf_token:
    raise RuntimeError("Please set HUGGINGFACEHUB_API_KEY for HuggingFaceHub LLM usage.")

llm = HuggingFaceHub(
    repo_id=os.getenv("HF_REPO", "tiiuae/falcon-7b-instruct"),
    huggingfacehub_api_token=hf_token
)

# Memory (Summary)
memory = ConversationSummaryMemory(llm=llm, memory_key="chat_history", max_token_limit=500)

# RAG chain
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
qa = ConversationalRetrievalChain.from_llm(llm, retriever, memory=memory)

# Prompt template
SYSTEM_INSTRUCTION = "Do not use technical terms in your response. Answer simply, politely and clearly for a farmer."

@app.post("/chat")
def chat(req: ChatRequest):
    if not req.question:
        raise HTTPException(status_code=400, detail="Question empty")
    
    out = qa({"question": f"{SYSTEM_INSTRUCTION}\nUser: {req.question}"})
    answer = out.get("answer") or out.get("text") or ""
    sources = []
    for d in out.get("source_documents", []):
        sources.append(d.metadata.get("source"))
    return {"answer": answer.strip(), "sources": sources}
