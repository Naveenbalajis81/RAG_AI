from langchain_huggingface import HuggingFaceEmbeddings

embeddings_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def get_embeddings(text: str):
    return embeddings_model.embed_query(text)  # returns a list[float]

##This for checking the embedding model works
#if __name__ == "__main__":
#    sample_text = "Hello, this is a test sentence for embeddings."
#    vector = get_embeddings(sample_text)

#     print(f"Text: {sample_text}")
#     print(f"Embedding length: {len(vector)}")
#     print(f"First 10 values: {vector[:10]}")