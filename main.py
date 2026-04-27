import os
import uuid
import logging
import datetime
import inngest
import inngest.fast_api
from inngest.experimental import ai
from fastapi import FastAPI
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
    trigger=inngest.TriggerEvent(event="raag/inngest_pdf")
)

async def rag_inngest_pdf(ctx: inngest.Context):
    ctx.logger.info(ctx.event)
    return "done"

app = FastAPI()

inngest.fast_api.serve(app, inngest_client, [rag_inngest_pdf])