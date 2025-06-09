from langchain_ollama import OllamaEmbeddings
import os
import redis


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
        model="nomic-embed-text",
        base_url="http://172.16.226.32:11434"
    )
    config = RedisConfig(
        index_name="newsgroups",
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

def main():
    if test_redis():
        pass
        vec_store=create_vector_store()

    kbs=load_docs()
    print(kbs["party_party_table_gpt.txt"])


main()