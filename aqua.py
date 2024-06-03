import json
import os
import logging
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter_ns

import torch
import torch.nn.functional as F

from annoy import AnnoyIndex
from langchain_core.documents import Document
from llama_index.core.node_parser import SentenceSplitter
from transformers import AutoTokenizer, AutoModel, AutoModelForCausalLM
from transformers import logging as tf_logging
from tqdm import tqdm


os.environ['TOKENIZERS_PARALLELISM'] = '(true | false)'
tf_logging.set_verbosity_error()
logging.basicConfig(level=logging.INFO)


# Embedding Model
MODEL_NAME = 'BAAI/bge-base-en-v1.5'
logging.info(f'Loading embedding model {MODEL_NAME} ...')
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModel.from_pretrained(MODEL_NAME).to('cuda')

@torch.no_grad()
def vector_embed(text):
    input_tokens = tokenizer(text, padding=True, truncation=True, return_tensors='pt')
    output = model(**{k: v.to(model.device) for k, v in input_tokens.items()})
    embd = F.normalize(output.last_hidden_state[:, 0, :], p=2, dim=1)  # Last hidden state: [1, seq_len, 768]
    return embd.to('cpu').reshape(-1)


# Reader Model
READER_NAME = 'stabilityai/stablelm-zephyr-3b'
logging.info(f'Loading reader model {READER_NAME} ...')
tokenizer_r = AutoTokenizer.from_pretrained(READER_NAME)
reader = AutoModelForCausalLM.from_pretrained(
    READER_NAME, torch_dtype=torch.float16, trust_remote_code=True
).to('cuda')
instr_tmpl = '''\
Context information is below.
===
{context}
===
You are a helpful and educational teaching assistant for the computer architecture course.
Given the context information above and not prior knowledge, answer the query.
Respond "Sorry I cannot answer that" if no relevant information is in the context.
Query: {query}'''

def llm_complete(context, query):
    prompt = [{'role': 'user', 'content': instr_tmpl.format(context=context, query=query)}]
    in_tokens = tokenizer_r.apply_chat_template(prompt, add_generation_prompt=True, return_tensors='pt')
    out_tokens = reader.generate(in_tokens.to(model.device), max_new_tokens=256, temperature=0.8, do_sample=True)
    answer = tokenizer_r.decode(out_tokens[0, in_tokens.size(-1):], skip_special_tokens=True)
    return answer


# Configure Aqua API
def config_aqua(save_path, chunk_size, overlap_ratio, top_k, max_dist, **kwargs):
    # Creating documents
    docs = []
    parser = SentenceSplitter(chunk_size=chunk_size, chunk_overlap=int(chunk_size*overlap_ratio))
    with open(f'{save_path}/doc_src_paths.json') as f:
        doc_src_paths = list(map(Path, json.load(f)))
    logging.info(f'Creating documents from {len(doc_src_paths)} document sources ...')
    
    for doc_src_path in doc_src_paths:
        with open(doc_src_path) as f:
            doc_src = f.read()
        doc_chunks = parser.split_text(doc_src)
        docs.extend(
            Document(page_content=txt, metadata={'source': doc_src_path.name}) for txt in doc_chunks
        )

    # Creating vector index
    n_trees = len(docs)
    Path('.deploy_ann/').mkdir(exist_ok=True)
    filename = f'.deploy_ann/idx_bge_{chunk_size}_{int(chunk_size*overlap_ratio)}_{n_trees}.ann'
    vector_idx = AnnoyIndex(768, 'euclidean')  # Hidden dim of BERT = 768
    logging.info(f'Loading vector index {filename} ...')

    if not Path(filename).exists():
        for i, doc in enumerate(tqdm(docs)):
            embd = vector_embed(doc.page_content)
            vector_idx.add_item(i, embd)
        vector_idx.build(n_trees)
        vector_idx.save(filename)
    else:
        vector_idx.load(filename)

    def retrieve_docs(query):
        '''Output: List[tuple(float, int)]: (distance, doc_idx)'''
        q_embd = vector_embed(query)
        idxs, dists = vector_idx.get_nns_by_vector(q_embd, top_k, len(docs), include_distances=True)

        top_doc_idxs = filter(lambda p: p[0] < max_dist, zip(dists, idxs))
        top_docs = []
        for dist, idx in top_doc_idxs:
            top_doc = docs[idx].copy(update={'dist': dist})
            top_docs.append(top_doc)
    
        return top_docs

    # Query API
    def format_source(idx, top_doc):
        return f'[{idx}] {top_doc.metadata["source"]} | dist={top_doc.dist:.4f}\n{top_doc.page_content}'

    def query_fn(query, qtype):
        if qtype.startswith('asmt'):
            asmt_name = qtype.split('-')[0]
            with open(f'deploy_data/asmt/{asmt_name}/{qtype}.md') as f:
                context = f.read()
            answer = llm_complete(context, query)
            sources = context
        else:
            if top_docs := retrieve_docs(query):
                context = '\n---\n'.join(top_doc.page_content for top_doc in top_docs)
                answer = llm_complete(context, query)
                sources = '\n\n'.join(format_source(i, top_doc) for i, top_doc in enumerate(top_docs, start=1))
            else:
                answer = 'Sorry, I do not have relevant information to answer the question.'
                sources = ''
        return answer, sources

    return query_fn
