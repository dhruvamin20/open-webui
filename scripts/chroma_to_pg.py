import logging

from open_webui.retrieval.vector.dbs.pgvector import PgvectorClient
from open_webui.retrieval.vector.dbs.chroma import ChromaClient


log = logging.getLogger(__name__)


def migrate():
    chroma = ChromaClient()
    pg = PgvectorClient()

    # access underlying client to get collection names
    collections = chroma.client.list_collections()
    for name in collections:
        col = chroma.client.get_collection(name=name)
        data = col.get(include=["embeddings", "metadatas", "documents"])
        items = []
        for idx, cid in enumerate(data["ids"]):
            items.append(
                {
                    "id": cid,
                    "text": data["documents"][idx],
                    "vector": data["embeddings"][idx],
                    "metadata": data["metadatas"][idx],
                }
            )
        if items:
            log.info(f"Migrating {len(items)} items for collection {name}")
            pg.upsert(name, items)


if __name__ == "__main__":
    migrate()
