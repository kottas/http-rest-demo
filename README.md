# HTTP REST demo 

An HTTP REST demo based on the FastAPI and Elasticsearch.


## Table of Contents
1. [Introduction](#introduction)
1. [Requirements](#requirements)
1. [Installation](#installation)
1. [Execution](#execution)
1. [API Endpoints](#api-endpoints)
    1. [Document Post](#document-post)
    1. [Document Get](#document-get)
    1. [Search Get](#search-get)


## Introduction

This demo provides three (3) main functionalities via HTTP requests:

1. **Add** English documents to a database (Elasticsearch) and assign document IDs to them.
1. **Retrieve** the correct document from the database given its corresponding document ID.
1. **Search** among the documents in the database given a query. Sort and return the best matching results. 

The "search" functionality is heavily based on the state-of-the-art DistilBERT model 
([msmarco-distilbert-base-v2](https://www.sbert.net/docs/pretrained-models/msmarco-v2.html)). This 
model variation has been finetuned specifically for semantic search, making ideal for the task.

- Each document that is added to the database is mapped to a 768-dimensional vector (embedding)
- The same transformation is applied to the search query text.
- A built-in cosine similarity function in Elasticsearch scores each document vector with the query 
  vector and sorts them with a descending order (the most similar document is first in the list).
  
A subset of the [BBC News Summary dataset](https://www.kaggle.com/pariza/bbc-news-summary/data)
is being used for the demo. This dataset consists of news articles and their corresponding summaries,
making it ideal for evaluating our search functionality. More specifically:

- Fifty (50) news articles are **added** to the database equally distributed among five (5) categories:
  i) business, ii) entertainment, iii) politics, iv) sport, and v) tech.
- The news article summaries are iteratively used as **search** queries.
- If the **1st** search result (news article) corresponds to the search query (summary), then the search
  is considered "successful".
- A classification **accuracy** is reported in the end, calculated as the ratio of "successful" searches
  to the total number of searches.
  
This demo achieves **100%** classification accuracy.


## Requirements
 
* Linux or macOS
* Python 3.8 
* [Elasticsearch 7.11](https://www.elastic.co/downloads/elasticsearch)


## Installation

1. Clone the repository: `$ git clone https://github.com/kottas/http-rest-demo`
1. Enter the repository: `$ cd http-rest-demo` 
1. Install pipenv: `$ pip install pipenv`
1. Create a Python 3.8 environment: `$ pipenv --python 3.8`
1. Activate the Python environment: `$ pipenv shell`
1. Install dependencies from Pipfile.lock: `$ pipenv sync`


## Execution

1. Start Elasticsearch: [Guide](https://www.elastic.co/guide/en/elasticsearch/reference/current/starting-elasticsearch.html)
1. Start the HTTP REST demo: `$ uvicorn main:app`
1. Open your internet browser and explore the available endpoints via the automatic FastAPI documentation:
   1. `http://127.0.0.1:8000/docs`
   1. `http://127.0.0.1:8000/redoc` 
1. Open a new terminal and execute the HTTP REST demo: `$ python test_main.py`

**Note**: If you run the demo for the 1st time, the finetuned DistilBERT model is going to be downloaded.


## API Endpoints

### Document Post

Add an English document to the database. A document ID is automatically assigned to it.

#### Curl

```shell
curl -X POST "http://127.0.0.1:8000/documents/add/" -H  "accept: application/json" -H  "Content-Type: application/x-www-form-urlencoded" -d "text=hello%20world"
```

#### Request URL

```text
http://127.0.0.1:8000/documents/add/
```

#### Response body

```json
{
  "index": "fDHToXcBPmwnBNnZF43J"
}
```

#### Response headers

```text
 content-length: 32 
 content-type: application/json 
 date: Current Date 
 server: uvicorn 
```


### Document Get

Retrieve the correct document from the database given its corresponding document ID.

#### Curl

```shell
curl -X GET "http://127.0.0.1:8000/documents/retrieve/STHMoXcBPmwnBNnZdY1K" -H  "accept: application/json"
```

#### Request URL

```text
http://127.0.0.1:8000/documents/retrieve/fDHToXcBPmwnBNnZF43J
```

#### Response body

```json
{
  "text": "hello world"
}
```

#### Response headers
```text
 content-length: 22 
 content-type: application/json 
 date: Current Date 
 server: uvicorn 
```

### Search Get

Search among the documents in the database given a query. Sort and return the top K matching results. 

#### Curl

```shell
curl -X GET "http://127.0.0.1:8000/documents/search?query=hi%20there&top_k=10" -H  "accept: application/json"
```

#### Request URL

```text
http://127.0.0.1:8000/documents/search?query=hi%20there&top_k=10
```

#### Response body

```json
[
  {
    "index": "fDHToXcBPmwnBNnZF43J",
    "text": "hello world",
    "score": 1.4086875
  }
]
```

#### Response headers

```text
 content-length: 83 
 content-type: application/json 
 date: Current Date 
 server: uvicorn 
```
