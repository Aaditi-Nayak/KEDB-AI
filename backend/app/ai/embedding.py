from sentence_transformers import SentenceTransformer

# this is an embedding model
# its job is to convert text into vectors for tasks like search and similarity
model=SentenceTransformer(
    "all-miniLM-L6-v2"
)

def get_embedding(text:str):

    return model.encode(text).tolist()