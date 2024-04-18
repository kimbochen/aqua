from llama_index.core import ServiceContext, VectorStoreIndex
from llama_index.core.retrievers import BaseRetriever
from llama_index.embeddings.huggingface import HuggingFaceEmbedding


class EnsembleRetriever(BaseRetriever):
    def __init__(self, model_size, corpus, top_k):
        super().__init__()
        self.model_size = model_size

        baai_idx = EnsembleRetriever.init_index(f'BAAI/bge-{model_size}-en-v1.5', corpus)
        self.baai_rtvr = baai_idx.as_retriever(similarity_top_k=top_k)

        gte_idx = EnsembleRetriever.init_index(f'thenlper/gte-{model_size}', corpus)
        self.gte_rtvr = gte_idx.as_retriever(similarity_top_k=top_k)

    def _retrieve(self, query_bundle):
        query_str = query_bundle.query_str
        baai_nodes = {hash(n.node.text): n for n in self.baai_rtvr.retrieve(query_str)}
        gte_nodes = {hash(n.node.text): n for n in self.gte_rtvr.retrieve(query_str)}

        common_node_ids = baai_nodes.keys() & gte_nodes.keys()
        common_nodes = [baai_nodes[node_id] for node_id in common_node_ids]

        return common_nodes

    @staticmethod
    def init_index(embd_model_name, corpus):
        embd_model = HuggingFaceEmbedding(embd_model_name)
        embd_ctx = ServiceContext.from_defaults(
            llm=None, embed_model=embd_model, chunk_size=256, chunk_overlap=128
        )
        idx = VectorStoreIndex.from_documents(corpus, service_context=embd_ctx)
        return idx

    def __str__(self):
        return f'EnsembleRetriever(ensemble=[BAAI/bge-{self.model_size}-en-v1.5, thenlper/gte-{self.model_size}])'
