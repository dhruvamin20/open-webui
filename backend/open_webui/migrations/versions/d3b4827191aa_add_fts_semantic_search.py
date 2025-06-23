"""add fts_semantic_search function

Revision ID: d3b4827191aa
Revises: ca81bd47c050
Create Date: 2024-09-01 00:00:00.000000
"""

from alembic import op
from typing import Sequence, Union

revision: str = "d3b4827191aa"
down_revision: Union[str, None] = "ca81bd47c050"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
CREATE OR REPLACE FUNCTION fts_semantic_search(query_vec vector, query_text text, k integer DEFAULT 8)
RETURNS TABLE(id text, text text, vmetadata jsonb, score float) AS $$
    WITH vector_top AS (
        SELECT id, text, vmetadata,
               (vector <=> query_vec) AS v_dist,
               ts_rank_cd(to_tsvector('simple', text), plainto_tsquery(query_text)) AS bm25
        FROM document_chunk
        ORDER BY vector <=> query_vec
        LIMIT k
    ),
    bm25_top AS (
        SELECT id, text, vmetadata,
               (vector <=> query_vec) AS v_dist,
               ts_rank_cd(to_tsvector('simple', text), plainto_tsquery(query_text)) AS bm25
        FROM document_chunk
        WHERE to_tsvector('simple', text) @@ plainto_tsquery(query_text)
        ORDER BY bm25 DESC
        LIMIT k
    ),
    merged AS (
        SELECT * FROM vector_top
        UNION ALL
        SELECT * FROM bm25_top
    )
    SELECT id, text, vmetadata, (1 - v_dist) + bm25 AS score
    FROM merged
    ORDER BY score DESC
    LIMIT k;
$$ LANGUAGE SQL;
        """
    )


def downgrade() -> None:
    op.execute("DROP FUNCTION IF EXISTS fts_semantic_search(vector, text, integer);")

