from app.ai.embedding import get_embedding
from sentence_transformers import util

sentence1="Login failed"
sentence2="Unable to sign in"

embedding1=get_embedding(sentence1)
embedding2=get_embedding(sentence2)

similarity=util.cos_sim(embedding1,embedding2)

print("Sentence1:",sentence1)
print("Sentence2:",sentence2)
print("Simmilarity:",similarity.item())