from langchain_ollama import OllamaEmbeddings
import os
import redis

from queries import retriever
from langchain_redis import RedisConfig, RedisVectorStore




REDIS_URL = os.getenv("REDIS_URL", "redis://:mypassword@localhost:6379")
# connection to host "redis" port 7379 with db 2 and password "secret" (old style authentication scheme without username / pre 6.x)
#redis://user:password@host:port/db 





def test_redis():
    print(f"Connecting to Redis at: {REDIS_URL}")
    #verify reddis connection:
    try:

        redis_client = redis.from_url(REDIS_URL)
        redis_client.ping()
        return True
    except Exception as e:
        print("Erro at URL:",e)
        return False


def create_vector_store():


    embeddings = OllamaEmbeddings(
        model="mxbai-embed-large",
        base_url="http://172.16.226.32:11434"
    )
    config = RedisConfig(
        index_name="gnuhealth",
        redis_url=REDIS_URL,
        metadata_schema=[
            {"name": "category", "type": "tag"},
        ],
    )
    vector_store = RedisVectorStore(embeddings, config=config)
    return vector_store


def load_docs():
    docs=["party_party_table_gpt.txt","pathology_table_gpt.txt","patient_table_gpt.txt","pregnancy_table_gpt.txt"]

    kbs={}
    for doc in docs:
        with open(doc, 'r', encoding='utf-8') as file:
            content = file.read()
            kbs[doc]=content
    return kbs



def store_procedure():
    if test_redis():
        vec_store=create_vector_store()

    metadata=[{"category":"party"},
              {"category":"pathology"},
              {"category":"patient"},
              {"category":"pregnancy"}]
    
    kbs=load_docs()
    ids=vec_store.add_texts(kbs.values(),metadata)
    print(ids[0:2])



def direct_query(text_input):
    query = "How to read the pregnancy table"
    vec=create_vector_store()
    results = vec.similarity_search(query, k=2)
    
    print("how to read pathology table")
    for doc in results:
        print(f"Content: {doc.page_content[:100]}...")
        print(f"Metadata: {doc.metadata}")
        print()
    
def main():
    vector_store=create_vector_store()
    input_text="I need to list all the births  for this month "
    direct_query(input_text)
    ret=retriever(input_text,vector_store)
    context=""
    for doc in ret:
        context+=str(doc)+"\n"

        


    # 'w' mode means "write" mode. It will create the file if it doesn't exist,
    # or overwrite its content if it does.
    with open("out.txr", 'w', encoding='utf-8') as file:
        file.write(context)
        print(f"Successfully wrote to out.txt")

    print(ret)



    




main()