from django.conf import settings
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings


class VectorRetriever:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VectorRetriever, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """실제 초기화 로직 (한 번만 실행)"""
        self.chroma_db_dir = settings.CHROMA_DB_DIR
        self.embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")
        self.vector_store = Chroma(
            persist_directory=self.chroma_db_dir,
            embedding_function=self.embedding_model,
            collection_name="startup_support_policies",
        )

        self.retriever = self.vector_store.as_retriever()

        # MultiQueryRetriever 생성 (재사용)
        self.llm = ChatOpenAI(model_name="gpt-4o-mini")
        self.multi_query_retriever = MultiQueryRetriever.from_llm(
            retriever=self.retriever, llm=self.llm
        )

    def get_multi_query_retriever(self):
        """MultiQueryRetriever 객체 반환 (한 번만 생성 후 재사용)"""
        return self.multi_query_retriever
