import json
import os
from fastapi import FastAPI
from pydantic import BaseModel
from open_webui.model_providers.bedrock import BedrockClient

app = FastAPI()
client = BedrockClient()


class RerankRequest(BaseModel):
    model: str = os.getenv("RAG_RERANK_MODEL", "claude-rerank")
    query: str
    documents: list[str]
    top_n: int = 8


@app.post("/v1/rerank")
async def rerank(req: RerankRequest):
    payload = {
        "query": req.query,
        "documents": req.documents[: req.top_n],
        "top_n": req.top_n,
    }
    response = client.runtime.invoke_model(
        modelId=req.model,
        body=json.dumps(payload).encode(),
        contentType="application/json",
    )
    data = json.loads(response["body"].read())
    return {"results": data.get("results", [])}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
