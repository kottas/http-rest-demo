from elasticsearch import Elasticsearch, NotFoundError, RequestError, ElasticsearchException
from elasticsearch.client.indices import IndicesClient
from typing import List, Tuple

from .schemas import Document, DocumentIndex, DocumentText, SearchResult


INDEX = "en_documents"


async def document_add(elasticsearch: Elasticsearch, document: Document) -> DocumentIndex:
    response = elasticsearch.index(index=INDEX, body=document.dict())
    return DocumentIndex(index=response.get("_id", ""))


async def document_retrieve(elasticsearch: Elasticsearch, index: str) -> DocumentText:
    response = elasticsearch.get(index=INDEX, id=index)
    source = response.get("_source", {})
    return DocumentText(text=source.get("text", ""))


async def document_search(
    elasticsearch: Elasticsearch, vector: List[float], top_k: int
) -> List[SearchResult]:
    response = elasticsearch.search(
        index=INDEX,
        body={
            "size": top_k,
            "query": {
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": "cosineSimilarity(params.queryVector, 'vector') + 1.0",
                        "params": {"queryVector": vector},
                    },
                }
            },
        },
    )

    return [
        SearchResult(index=hit["_id"], text=hit["_source"]["text"], score=hit["_score"])
        for hit in response["hits"]["hits"]
    ]


def initialize_elastic_search() -> Tuple[Elasticsearch, IndicesClient]:
    elastic_search = Elasticsearch(hosts=[{"host": "localhost", "port": 9200}])
    indices_client = IndicesClient(client=elastic_search)
    try:
        indices_client.create(
            index=INDEX,
            body={
                "mappings": {
                    "properties": {
                        "doc": {"type": "text"},
                        "vector": {"type": "dense_vector", "dims": 768},
                    }
                }
            },
        )
    except RequestError:
        pass

    return elastic_search, indices_client


async def shutdown_elastic_search(
    elastic_search: Elasticsearch, indices_client: IndicesClient
) -> None:
    indices_client.delete(index=INDEX)
    elastic_search.close()
