from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from vectorstore.chroma_db import get_vectorstore
from config import OLLAMA_BASE_URL, LLM_MODEL, LLM_TEMPERATURE, TOP_K_RETRIEVAL

def get_llm():
    """
    Inicializa o modelo local via Ollama.
    """
    return ChatOllama(
        base_url=OLLAMA_BASE_URL,
        model=LLM_MODEL,
        temperature=LLM_TEMPERATURE
    )

def query_system(question: str) -> dict:
    """
    Recebe uma pergunta do usuário, busca o contexto no ChromaDB,
    constrói um prompt anti-alucinação e chama o LLM local.
    Retorna a resposta do LLM e as fontes consultadas.
    """
    llm = get_llm()
    vectorstore = get_vectorstore()
    
    # Retriever que vai buscar os top-K chunks mais relevantes
    retriever = vectorstore.as_retriever(search_kwargs={"k": TOP_K_RETRIEVAL})
    
    # Prompt com controle restrito de alucinação
    system_prompt = (
        "Você é o assistente técnico do sistema D-SearchAi.\n"
        "Seu objetivo é responder a perguntas usando **EXCLUSIVAMENTE** o contexto fornecido abaixo.\n"
        "Siga estas regras rigorosamente:\n"
        "1. Se a informação não estiver no contexto, responda: 'Não há informações suficientes nos documentos para responder a esta pergunta.'\n"
        "2. Não invente informações, não assuma conhecimentos prévios e não seja criativo.\n"
        "3. Seja direto, técnico e objetivo.\n"
        "4. Sempre que possível, cite partes importantes do texto.\n"
        "\n"
        "Contexto:\n"
        "{context}"
    )
    
    prompt = PromptTemplate(
        template="System:\n" + system_prompt + "\n\nHuman: {input}\nAssistant:",
        input_variables=["context", "input"]
    )
    
    # Cadeia para juntar os documentos e preencher o {context}
    combine_docs_chain = create_stuff_documents_chain(llm, prompt)
    
    # Cadeia final de retrieval
    retrieval_chain = create_retrieval_chain(retriever, combine_docs_chain)
    
    # Executa a cadeia
    response = retrieval_chain.invoke({"input": question})
    
    # A resposta de create_retrieval_chain contém 'answer' e 'context'
    return {
        "answer": response.get("answer", "Erro ao obter resposta."),
        "sources": response.get("context", [])
    }
