from src import rag_pipeline
rag = rag_pipeline.SimpleRAG(model_name="satellite-telemetry")
documents = rag.list_ingested_documents()
print("Current RAG documents: \n")
for i, doc in enumerate(documents, 1):
    print(f"Document {i}:\n{doc}\n")


# Clear all RAG documents
rag.clear_ingested_documents()

# List documents - should be empty
documents = rag.list_ingested_documents()
print("RAG documents after clearing: \n")
for i, doc in enumerate(documents, 1):
    print(f"Document {i}:\n{doc}\n")
