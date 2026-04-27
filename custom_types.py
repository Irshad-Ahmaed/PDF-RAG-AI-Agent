import pydentic

class RAGChunkAndSrc(pydentic.BaseModel):
    chunks: list[str]
    source_id: str = None

class RAGUpsertResult(pydentic.BaseModel):
    inngested: int

class RAGSearchResult(pydentic.BaseModel):
    contexts: list[str]
    sources: list[str]

class RAGQueryResult(pydentic.BaseModel):
    answer: str
    contexts: list[str]
    num_contexts: int