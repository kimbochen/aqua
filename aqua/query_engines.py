from llama_index.core import SimpleDirectoryReader
from transformers import logging

from aqua.readers import *
from aqua.retrievers import *

logging.set_verbosity_error()


class QueryEngine:
    def __init__(self, retriever, reader):
        self.retriever = retriever
        self.reader = reader

    def query(self, query_str):
        rtvd_nodes = self.retriever.retrieve(query_str)
        if len(rtvd_nodes) == 0:
            return 'Sorry I cannot find relevant information to answer that.'

        context_str = '\n\n'.join(node.get_content() for node in rtvd_nodes)
        answer_str = self.reader.answer(context_str, query_str)

        sources_str = '\n\n'.join(
            f'[{i}] {node.metadata["file_name"]} | Score={node.score:.4f}\n{node.text}'
            for i, node in enumerate(rtvd_nodes, start=1)
        )

        return f'{answer_str}', sources_str

    def query_asmt(self, query_str, asmtq_file):
        with open(asmtq_file) as f:
            asmtq = f.read()
        answer_str = self.reader.answer(asmtq, query_str)
        return f'{answer_str}', asmtq

    def __str__ (self):
        f'{type(self).__name__}(\n\tretriever={self.retriever},\n\treader={self.reader}\n)'


class SummaryQueryEngine(QueryEngine):
    def __init__(self, corpus_path, top_k=5):
        corpus = SimpleDirectoryReader(corpus_path, recursive=True).load_data()
        retriever = EnsembleRetriever('base', corpus, top_k)
        reader = SummarizerReader()
        super().__init__(retriever, reader)


class StableLM2QueryEngine(QueryEngine):
    def __init__(self, corpus_path, top_k=5):
        corpus = SimpleDirectoryReader(corpus_path, recursive=True).load_data()
        retriever = EnsembleRetriever('base', corpus, top_k)
        reader = StableLM2Reader()
        super().__init__(retriever, reader)


class Gemma2BQueryEngine(QueryEngine):
    def __init__(self, corpus_path, top_k=5):
        corpus = SimpleDirectoryReader(corpus_path, recursive=True).load_data()
        retriever = EnsembleRetriever('base', corpus, top_k)
        reader = Gemma2BReader()
        super().__init__(retriever, reader)


class StableLM3BQueryEngine(QueryEngine):
    def __init__(self, corpus_path, top_k=5):
        corpus = SimpleDirectoryReader(corpus_path, recursive=True).load_data()
        retriever = EnsembleRetriever('base', corpus, top_k)
        reader = StableLM3BReader()
        super().__init__(retriever, reader)

    def __str__(self):
        return f'StableLM3BQueryEngine(\n\tretriever={self.retriever},\n\treader={self.reader}\n)'
