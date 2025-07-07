from vector_store.embedder import get_embedding

embedding = get_embedding("What is my assignment?")
print(embedding)

print("Starting embedding...")

from vector_store.embedder import get_embedding

embedding = get_embedding("What is my assignment?")
print("Done!\n")

print(f"Vector size: {len(embedding)}")
print("Sample:", embedding[:5])

