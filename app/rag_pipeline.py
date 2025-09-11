import os
from pinecone import Pinecone as ps
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.llms import HuggingFacePipeline
from langchain_community.llms import HuggingFaceEndpoint
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_core.runnables import RunnablePassthrough
from langchain.schema import StrOutputParser

load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACEHUB_API_TOKEN")
MODEL_NAME = os.getenv("MODEL_NAME")
INDEX_NAME = "student-qa"

if not PINECONE_API_KEY or not HUGGINGFACE_API_KEY:
    raise ValueError("❌ Missing API keys. Please check your .env file.")
# 🟢 Init Pinecone client
pc = ps(api_key=PINECONE_API_KEY)
INDEX_NAME = "student-qa"
index = pc.Index(INDEX_NAME)

# ✅ Embedding model wrapper (LangChain compatible)
embeddings = HuggingFaceEmbeddings( model_name="sentence-transformers/all-MiniLM-L6-v2" )
def embed_and_store(text: str):
    """Split document into chunks, embed, and push to Pinecone."""
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_text(text)
    
    
    vectorstore = PineconeVectorStore.from_existing_index(
    index_name=INDEX_NAME,
    embedding=embeddings,
    text_key="text"
    )
    vectorstore.add_texts(chunks)
    

    # vectorstore = Chroma.from_texts(chunks, embeddings, collection_name=INDEX_NAME) # Alternative using Chroma for local testing
    return {"status": "success", "chunks_stored": len(chunks)}

def query_rag(query: str) -> str:
    """Retriever relevant chunks and generate an answer."""
    # ✅ Wrap Pinecone with LangChain retriever
    vectorstore = PineconeVectorStore.from_existing_index(
        index_name=INDEX_NAME,
        embedding=embeddings
    )
    #vectorstore = Chroma(collection_name=INDEX_NAME, embedding_function=embeddings)# Alternative using Chroma for local testing
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})
    
    # ✅ LLM wrapper (HuggingFace Inference API)
    # llm=HuggingFaceEndpoint(
    #     repo_id = "google/flan-t5-large",
    #     task="text2text-generation",
    #     huggingfacehub_api_token=HUGGINGFACE_API_KEY
    # )
    # ✅ this is faster but less accurate than flan-t5-large for testing
    llm=HuggingFacePipeline.from_model_id(
        model_id="google/flan-t5-small",
        task="text2text-generation",
        model_kwargs={"temperature":0.7, "max_length":2048}
    )
    
    # ✅ Prompt template
    Template = (
        "You are a helpful assistant. Use the context to answer clearly.\n"
        "Context:\n{context}\n\n"
        "Question: {question}\n\n"
        "Answer:"
    )
    
    prompt=PromptTemplate(
        input_variables=["context", "question"],
        template=Template
    )
    # ✅ Chain setup
    def format_docs(docs):
        return "\n".join([doc.page_content for doc in docs])
    rag_chain = ({"context": retriever | format_docs, "question": RunnablePassthrough()}) | prompt | llm | StrOutputParser()

    response = rag_chain.invoke(query)
    return response
