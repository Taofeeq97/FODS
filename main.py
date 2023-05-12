# from elasticsearch import Elasticsearch
#
# # Connect to Elasticsearch with authentication credentials
# es = Elasticsearch(
#     hosts='localhost',
#     port=9200,
#     http_auth=('elastic', '7PeMZZH7haepPZTxMBpP')
# )
#
# # Count the number of documents in the index
# document_count = es.count(index=index_name)['count']
# print("Number of documents in the index:", document_count)


# index_name = "search_index"
# search_query = {
#     "query": {
#         "match_all": {}
#     }
# }
#
# # Retrieve all documents from the index
# response = es.search(index=index_name, body=search_query)
#
# # Inspect the response to access the retrieved documents
# hits = response['hits']['hits']
# for hit in hits:
#     print(hit['_source'])


# from elasticsearch import Elasticsearch
#
# # Connect to Elasticsearch
# from elasticsearch import Elasticsearch
#
# # Connect to Elasticsearch with authentication credentials
# es = Elasticsearch(
#     hosts='localhost:9200',
#     http_auth=('elastic', '7PeMZZH7haepPZTxMBpP')
# )
#
#
# index_name = "search_index"
# search_query = {
#     "query": {
#         "match_all": {}
#     }
# }
#
# # Retrieve all documents from the index
# response = es.search(index=index_name, body=search_query)
#
# # Inspect the response to access the retrieved documents
# hits = response['hits']['hits']
# for hit in hits:
#     print(hit['_source'])

# response = es.search(index=index_name, body={"query": {"match_all": {}}})
# hits = response['hits']['hits']
# for hit in hits:
#     print(hit)


# search_body = {
#     "query": {
#         "term": {
#             "name.keyword": search_query
#         }
#     }
# }
#
# response = es.search(index=index_name, body=search_body)
#
# hits = response['hits']['hits']
# if hits:
#     print("Documents with the term 'Eba and Egusi' in the 'name' field exist.")
# else:
#     print("No documents found with the term 'Eba and Egusi' in the 'name' field.")
