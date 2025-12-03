import os
import sys
from typing import Any

from langchain_nvidia import NVIDIAEmbeddings
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.vectorstores import Pinecone
from langchain.chains import RetrievalQA
from langchain.schema import BaseChatMessageHistory, ChatMessage
from langchain.memory import ConversationBufferMemory

from src.utils.logger import logging
from src.utils.exception import Custom_exception
from dotenv import load_dotenv

load_dotenv()


class BuildChatbot:
    def __init__(self):
        self.store = {}  # For chat history

    def get_session_id(self, session_id: str) -> BaseChatMessageHistory:
        """Creates and retrieves a chat history session."""
        if session_id not in self.store:
            self.store[session_id] = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True
            )
        return self.store[session_id]

    def load_embeddings(self):
        """Initialize NVIDIA embeddings"""
        try:
            logging.info("Initializing NVIDIA Embeddings.")
            embeddings = NVIDIAEmbeddings(
                model="nvidia/nv-embedqa-mistral-7b-v2",
                api_key=os.getenv("NVIDIA_API_KEY"),
                truncate="NONE"
            )
            logging.info("Embeddings initialized successfully.")
            return embeddings
        except Exception as e:
            logging.error(f"Error initializing embeddings: {str(e)}")
            raise Custom_exception(e, sys)

    def load_llm(self):
        """Initialize Groq LLM"""
        try:
            logging.info("Initializing Groq LLM")
            llm = ChatGroq(
                temperature=0.6,
                model_name="llama-3.3-70b-versatile",
                groq_api_key=os.getenv("GROQ_API_KEY"),
                max_tokens=4096
            )
            logging.info("LLM initialized successfully")
            return llm
        except Exception as e:
            logging.error(f"Error initializing LLM: {str(e)}")
            raise Custom_exception(e, sys)

    def setup_prompt(self):
        """Create prompt template"""
        try:
            logging.info("Creating prompt template")
            template = """
You are a knowledgeable and friendly e-commerce assistant.  

Use only information from the context. If details are missing, answer gracefully.

Context: {context}

Question: {question}
Answer:"""
            prompt = PromptTemplate(
                template=template,
                input_variables=["context", "question"]
            )
            logging.info("Prompt template created")
            return prompt
        except Exception as e:
            logging.error(f"Error creating prompt: {str(e)}")
            raise Custom_exception(e, sys)

    def load_vectorstore(self, embeddings):
        """Load Pinecone vector store"""
        try:
            logging.info("Loading Pinecone vector store")
            vector_store = Pinecone.from_existing_index(
                index_name="ecommerce-chatbot-project",
                embedding=embeddings
            )
            logging.info("Vector store loaded successfully")
            return vector_store
        except Exception as e:
            logging.error(f"Error loading vector store: {str(e)}")
            raise Custom_exception(e, sys)

    def build_retrieval_chain(self):
        """Combine embeddings, LLM, prompt, vector store into a retriever chain"""
        try:
            embeddings = self.load_embeddings()
            llm = self.load_llm()
            prompt = self.setup_prompt()
            vector_store = self.load_vectorstore(embeddings)

            # Create RetrievalQA chain
            retriever = vector_store.as_retriever(
                search_type="similarity_score_threshold",
                search_kwargs={"k": 5, "score_threshold": 0.7}
            )

            chain = RetrievalQA.from_chain_type(
                llm=llm,
                retriever=retriever,
                chain_type_kwargs={"prompt": prompt}
            )
            logging.info("Retrieval chain created successfully")
            return chain

        except Exception as e:
            logging.error(f"Error building retrieval chain: {str(e)}")
            raise Custom_exception(e, sys)

    def initialize_chatbot(self):
        """Initialize chatbot with session memory"""
        try:
            retrieval_chain = self.build_retrieval_chain()

            # Wrap chain with memory
            chatbot = {
                "chain": retrieval_chain,
                "get_session_history": self.get_session_id
            }
            return chatbot
        except Exception as e:
            logging.error(f"Error initializing chatbot: {str(e)}")
            raise Custom_exception(e, sys)
