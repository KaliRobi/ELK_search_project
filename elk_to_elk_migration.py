# https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-simple-query-string-query.html
from elasticsearch import Elasticsearch
import time


#establsih connection between the two instances. First bridgehead  is the test environment.
def connect_to_es():
    con = Elasticsearch(['https://server:9999'], http_auth=('mainmastersuperuser', 'anditspasword123'))

    if con.ping():
        print('Successfully connected to Elasticsearch')
    else:
        print('Could not connect to Elasticsearch')

 #   making it a bit more complex may also helps to filter out useless auto tickets
    query_to_mig  = {
        "size" : 5,  # to limit how many obejcts to fetch
        "query" : {
            "simple_query_string": {
                   "query":  'QUERY',
                    "fields": ['queue']
                }
        }
    }
    resp = con.search(index='rt_search', body=query_to_mig,  )  
    

    tickets = resp['hits']['hits']
    
    #  handles the elk obejct by this id
    print(len(tickets))
    for tic in tickets:
            elk_id = tic['_id']
            # posts back the RT ticket object mapped by another index with the correct ELK id
            # if the _id already exists it gets updated only
            resp = con.index(index='rt_search', id=elk_id, document=tic['_source']  ) 
            print(resp)
  
    con.close()
    

connect_to_es()







  








