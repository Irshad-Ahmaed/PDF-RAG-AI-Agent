import datetime
import os
import uuid
import logging
import inngest
import inngest.fast_api
from fastapi import FastAPI
from google import genai
from dotenv import load_dotenv

from data_loader import load_chunk_pdf, embed_texts
from vector_db import VectorDB
from custom_types import RAGChunkAndSrc, RAGUpsertResult, RAGSearchResult, RAGQueryResult

load_dotenv()

# Inngest client, which is used to send events to an Inngest server.
inngest_client = inngest.Inngest(
    app_id="rag_app",
    logger=logging.getLogger("uvicorn"),
    is_production=os.getenv("PYTHON_ENV") == "production",
    serializer=inngest.PydanticSerializer()
)

# Inngest function, which receives events.


@inngest_client.create_function(
    fn_id="RAG: Inngest PDF",
    # Event that triggers this function
    trigger=inngest.TriggerEvent(event="rag/inngest_pdf"),
    throttle=inngest.Throttle(
        limit=2,
        period=datetime.timedelta(minutes=1)
    ),
    rate_limit=inngest.RateLimit(
        limit=1,
        period=datetime.timedelta(seconds=30),
        key="event.data.source_id"
    )
)
async def rag_inngest_pdf(ctx: inngest.Context):
    async def _load() -> RAGChunkAndSrc:
        pdf_path = ctx.event.data["pdf_path"]
        source_id = ctx.event.data.get("source_id", pdf_path)
        chunks = load_chunk_pdf(str(pdf_path))
        return RAGChunkAndSrc(chunks=chunks, source_id=str(source_id))

    chunks_and_src = await ctx.step.run("load-and-chunk", _load, output_type=RAGChunkAndSrc)

    async def _upsert() -> RAGUpsertResult:
        chunks = chunks_and_src.chunks
        source_id = chunks_and_src.source_id
        vectors = embed_texts(chunks)
        ids = [str(uuid.uuid5(uuid.NAMESPACE_URL, f"{source_id}:{i}")) for i in range(len(chunks))]
        payloads = [{"source": source_id, "text": chunks[i]} for i in range(len(chunks))]
        VectorDB().upsert(ids, vectors, payloads)
        return RAGUpsertResult(ingested=len(chunks))

    ingested = await ctx.step.run("embed-and-upsert", _upsert, output_type=RAGUpsertResult)
    return ingested.model_dump()


@inngest_client.create_function(
    fn_id="RAG: Query PDF",
    trigger=inngest.TriggerEvent(event="rag/query_pdf_ai"),

    throttle=inngest.Throttle(
        limit=2,
        period=datetime.timedelta(minutes=1)
    ),
    rate_limit=inngest.RateLimit(
        limit=1,
        period=datetime.timedelta(seconds=30),
        key="event.data.source_id"
    )
)
async def rag_query_inngest_pdf(ctx: inngest.Context):
    question = str(ctx.event.data["question"])
    top_k = int(str(ctx.event.data.get("top_k", 5)))

    async def _search() -> RAGSearchResult:
        query_vec = embed_texts([question])[0]
        store = VectorDB()
        result = store.search(query_vec, top_k=top_k)
        return RAGSearchResult(contexts=result["contexts"], sources=result["sources"])

    found = await ctx.step.run("embed-and-search", _search, output_type=RAGSearchResult)

    async def _generate() -> RAGQueryResult:
        if not found.contexts:
            return RAGQueryResult(answer="No relevant context found in the knowledge base.", contexts=[], num_contexts=0)
        context_block = "\n\n".join(f" - {c}" for c in found.contexts)
        user_content = (
            "Use the following context to answer the question.\n\n"
            f"Question: {question}\n\n"
            f"Context:\n{context_block}\n\n"
            "Answer the question based on the context provided. If you don't know the answer, say you don't know."
        )
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        response = client.models.generate_content(
            model=os.getenv("MODEL") or "gemini-2.0-flash-lite",
            contents=user_content,
            config=genai.types.GenerateContentConfig(max_output_tokens=1024, temperature=0.2)
        )
        if response.text is None:
            raise RuntimeError("No text returned from Gemini API")
        return RAGQueryResult(answer=response.text, contexts=found.contexts, num_contexts=len(found.contexts))

    result = await ctx.step.run("generate-answer", _generate, output_type=RAGQueryResult)

    return result.model_dump()

app = FastAPI()

inngest.fast_api.serve(app, inngest_client, [rag_inngest_pdf, rag_query_inngest_pdf])
