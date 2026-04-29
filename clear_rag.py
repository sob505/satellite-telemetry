from src import rag_pipeline
rag = rag_pipeline.SimpleRAG(model_name="phi")
rag.clear_ingested_documents()

documents = rag.list_ingested_documents()
for i, doc in enumerate(documents, 1):
    print(f"Document {i}:\n{doc}\n")