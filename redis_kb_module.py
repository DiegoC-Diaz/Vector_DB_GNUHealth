from langchain_ollama import OllamaEmbeddings
import os
import redis
from langchain.text_splitter import RecursiveCharacterTextSplitter
from redis_query_module import retriever
from langchain_redis import RedisConfig, RedisVectorStore
import re
from langchain.text_splitter import RecursiveCharacterTextSplitter
from glob import glob
import re




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



def split_doc_content(doc_content):
    # Dividir por secciones como: 'tabla:', 'descripción:', 'columnas:', etc.
    pattern = r'(?=^(tabla|descripción|columnas|llaves_foráneas|índices):)'
    raw_sections = re.split(pattern, doc_content, flags=re.MULTILINE)

    # Agrupar los encabezados con sus contenidos
    sections = []
    i = 0
    while i < len(raw_sections):
        if raw_sections[i] in ["tabla", "descripción", "columnas", "llaves_foráneas", "índices"]:
            header = raw_sections[i]
            content = raw_sections[i + 1] if i + 1 < len(raw_sections) else ""
            full_section = f"{header}:{content}".strip()
            sections.append(full_section)
            i += 2
        else:
            i += 1

    # Dividir cada sección si es demasiado larga (más de 500 caracteres aprox)
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = []
    for section in sections:
        chunks.extend(splitter.split_text(section))

    return chunks

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
    folder_path = "Reports-TableDocumentation/Tables"
    pattern = os.path.join(folder_path, "*.txt")

    files = glob(pattern)
    kbs = {}
    metadata = []

    for file_path in files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            file_name = os.path.basename(file_path)
            kbs[file_name] = content
            
            # Derivar categoría desde nombre de archivo sin extensión
            category_name = file_name.replace("_table_gpt.txt", "").replace(".txt", "").strip()
            metadata.append({"category": category_name})

    

    return kbs, metadata


def split_doc_content(doc_content):
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    return splitter.split_text(doc_content)

def store_procedure():
    if test_redis():
        vec_store = create_vector_store()

    kbs, metadata = load_docs()

    for i, (doc_name, content) in enumerate(kbs.items()):
        chunks = split_doc_content(content)
        metas = [{"category": metadata[i]["category"]} for _ in chunks]
        vec_store.add_texts(chunks, metas)




def direct_query(text_input):
    query = "How to read the pregnancy table"
    vec=create_vector_store()
    results = vec.similarity_search(query, k=2)
    
    print("how to read pathology table")
    for doc in results:
        print(f"Content: {doc.page_content[:100]}...")
        print(f"Metadata: {doc.metadata}")
        print()
    
def load_kb_to_redis():
    store_procedure()

 

def load_few_shots():
    with open("Reports-TableDocumentation/ReportsExample.md", "r", encoding="utf-8") as f:
        return f.read()

def query_tables(input_text):
    vector_store = create_vector_store()
    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 2})
    
    # Retrieve relevant documents based on the input text
    retrieved_docs = retriever.invoke(input_text)
    
    # Combine the content of the retrieved documents
    context = "\n".join([doc.page_content for doc in retrieved_docs])
    #Return the context
    
    return  context

def build_few_shot_prompt(text_input):
    few_shots = load_few_shots()
    context=query_tables("text_input")
    
    prompt = f"""
    database context:
    {context}
    

    {few_shots}

    """
    return prompt




