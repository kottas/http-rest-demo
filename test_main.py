import os
from starlette.testclient import TestClient
from tqdm import tqdm

from main import app


DIR_RESOURCES = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources")
DIR_NEWS = os.path.join(DIR_RESOURCES, "News Articles")
DIR_SUMMARIES = os.path.join(DIR_RESOURCES, "Summaries")


def test_index(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "HTTP REST Demo", "author": "M. Kottas", "status": "OK"}


def test_document_post(client: TestClient, text: str) -> str:
    response = client.post(url="/documents/add/", data={"text": text})
    assert response.status_code == 200
    return response.json()["index"]


def test_document_get(client: TestClient, document_id: str) -> str:
    response = client.get(url=f"/documents/retrieve/{document_id}")
    assert response.status_code == 200
    return response.json()["text"]


def test_search_results(client: TestClient, query: str, top_k: int):
    response = client.get(url="/documents/search", params={"query": query, "top_k": top_k})
    assert response.status_code == 200
    return response.json()


if __name__ == "__main__":
    # initializing client
    test_client = TestClient(app=app)

    # loading test resources
    fname2doc, fname2query = {}, {}
    for category in ["business", "entertainment", "politics", "sport", "tech"]:
        for fname in [f"0{idx}.txt" for idx in range(10, 20)]:
            with open(os.path.join(os.path.join(DIR_NEWS, category), fname), "r") as f:
                fname2doc[f"{category}_{fname}"] = f.read()
            with open(os.path.join(os.path.join(DIR_SUMMARIES, category), fname), "r") as f:
                fname2query[f"{category}_{fname}"] = f.read()

    # homepage
    test_index(client=test_client)

    # post new documents
    fname2idx = {}
    for fname, doc in tqdm(fname2doc.items(), desc="Posting", dynamic_ncols=True):
        fname2idx[fname] = test_document_post(client=test_client, text=doc)

    # retrieve documents given their index
    idx2fname = {value: key for key, value in fname2idx.items()}
    for idx, fname in tqdm(idx2fname.items(), desc="Retrieving", dynamic_ncols=True):
        document = test_document_get(client=test_client, document_id=idx)
        assert document == fname2doc[fname]

    # text similarity
    hits = 0
    for fname, q in tqdm(fname2query.items(), desc="Searching", dynamic_ncols=True):
        results = test_search_results(client=test_client, query=q, top_k=10)
        top_index = results[0]["index"]
        top_fname = idx2fname.get(top_index, "")
        hits = hits + 1 if top_fname == fname else hits
    print(f"Accuracy: {hits / len(fname2query):.4f}")
