import os
import certifi
from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_pinecone import PineconeVectorStore

from src.helper import download_embedding_model
from src.prompt import *


app = Flask(__name__)

load_dotenv()

PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is missing. Check your .env or environment variables.")
if not PINECONE_API_KEY:
    raise RuntimeError("PINECONE_API_KEY is missing. Check your .env or environment variables.")

# Ensure cert chain is available for HTTPX/OpenAI
os.environ["SSL_CERT_FILE"] = certifi.where()

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY

embedding_model = download_embedding_model()

index_name = "medical-chatbot"

doc_search = PineconeVectorStore.from_existing_index(
    index_name=index_name,
    embedding=embedding_model
)

retriever = doc_search.as_retriever(search_type="similarity", search_kwargs={"k": 3})

llm = ChatOpenAI(model="gpt-5-nano")

prompt=ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}")
    ]
)

question_answer_chain = create_stuff_documents_chain(llm=llm, prompt=prompt)
retrieval_chain = create_retrieval_chain(retriever, question_answer_chain)


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    payload = request.get_json(silent=True) or {}
    user_input = (payload.get("question") or payload.get("message") or "").strip()
    if not user_input:
        return jsonify({"error": "Missing question/message."}), 400

    results = retrieval_chain.invoke({"input": user_input})
    answer = results.get("answer", "")
    return jsonify({"answer": answer})

if __name__ == "__main__":
    
    app.run(debug=True)
    print("App is running ")

