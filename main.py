import uvicorn

from elasticsearch import NotFoundError
from fastapi import FastAPI, Form, HTTPException
from sentence_transformers import SentenceTransformer
from typing import List

from api.database import (
    document_add,
    document_retrieve,
    document_search,
    initialize_elastic_search,
    shutdown_elastic_search,
)
from api.schemas import Document, DocumentIndex, DocumentText, SearchResult

app = FastAPI()
es, es_indices = initialize_elastic_search()
encoder = SentenceTransformer(model_name_or_path="msmarco-distilbert-base-v2")


@app.get("/", include_in_schema=False)
async def root():
    return {"message": "HTTP REST Demo", "author": "M. Kottas", "status": "OK"}


@app.post("/documents/add/", response_model=DocumentIndex)
async def document_post(text: str = Form(...)):
    return await document_add(
        elasticsearch=es, document=Document(text=text, vector=encoder.encode(text).tolist())
    )


@app.get("/documents/retrieve/{document_id}", response_model=DocumentText)
async def document_get(document_id: str):
    try:
        return await document_retrieve(elasticsearch=es, index=document_id)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Item not found")


@app.get("/documents/search", response_model=List[SearchResult])
async def search_get(query: str, top_k: int = 10):
    return await document_search(
        elasticsearch=es, vector=encoder.encode(query).tolist(), top_k=top_k
    )


@app.on_event("shutdown")
async def app_shutdown():
    await shutdown_elastic_search(elastic_search=es, indices_client=es_indices)


if __name__ == "__main__":
    uvicorn.run(app=app)
