from __future__ import annotations

from typing import Any, Dict, List, Mapping, Sequence, Union
import os
import logging

import chromadb
from chromadb.config import Settings
from chromadb.api.types import IncludeEnum, Metadata
import numpy as np


class ActionVectorStore:
    """Persistent ChromaDB store for action embeddings.

    - Collection name: "actions"
    - Persistent directory: "chroma_db/"
    - Uses cosine distance and converts to similarity (1 - distance)
    """

    def __init__(self, persist_directory: str = "chroma_db") -> None:
        # Hard-disable ChromaDB telemetry to avoid PostHog capture errors
        os.environ.setdefault("CHROMADB_ANONYMIZED_TELEMETRY", "false")
        os.environ.setdefault("ANONYMIZED_TELEMETRY", "false")
        os.environ.setdefault("CHROMADB_DISABLE_TELEMETRY", "1")
        os.environ.setdefault("CHROMADB_TELEMETRY_IMPLEMENTATION", "noop")
        # Monkeypatch PostHog capture to a no-op to avoid signature errors
        try:  # pragma: no cover
            import posthog  # type: ignore

            def _silent_capture(*args: Any, **kwargs: Any) -> None:
                return None

            def _silent_identify(*args: Any, **kwargs: Any) -> None:
                return None

            posthog.capture = _silent_capture  # type: ignore[attr-defined]
            posthog.identify = _silent_identify  # type: ignore[attr-defined]
        except Exception:
            pass
        # Silence telemetry/log noise
        logging.getLogger("chromadb").setLevel(logging.ERROR)
        logging.getLogger("chromadb.telemetry").setLevel(logging.ERROR)

        # Disable telemetry via client settings too
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False),
        )
        # Ensure cosine space for distances
        self.collection = self.client.get_or_create_collection(
            name="actions",
            metadata={"hnsw:space": "cosine"},
        )

    def upsert_actions(
        self,
        ids: Sequence[str],
        documents: Sequence[str],
        embeddings: Any,
        metadatas: Sequence[Mapping[str, Union[str, int, float, bool]]],
    ) -> None:
        """Upsert action documents with embeddings and metadata."""
        # Convert to float32 numpy array to satisfy Chroma's expected types
        embeddings_np = np.asarray(embeddings, dtype=np.float32)

        # Sanitize metadata values to primitives (str/int/float/bool)
        def _sanitize(md: Mapping[str, Any]) -> Dict[str, Union[str, int, float, bool]]:
            out: Dict[str, Union[str, int, float, bool]] = {}
            for k, v in md.items():
                if v is None:
                    out[k] = ""
                elif isinstance(v, (str, int, float, bool)):
                    out[k] = v
                else:
                    out[k] = str(v)
            return out

        metadatas_sanitized: List[Metadata] = [_sanitize(m) for m in list(metadatas)]
        # Chroma 0.5+ supports upsert; fall back to add if needed.
        if hasattr(self.collection, "upsert"):
            self.collection.upsert(
                ids=list(ids),
                documents=list(documents),
                embeddings=embeddings_np,
                metadatas=metadatas_sanitized,
            )
        else:  # pragma: no cover
            self.collection.add(
                ids=list(ids),
                documents=list(documents),
                embeddings=embeddings_np,
                metadatas=metadatas_sanitized,
            )

    def query_by_embedding(
        self, embedding: List[float], top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Query similar actions by embedding.

        Returns list of dicts: {id, similarity, metadata, document}
        """
        res = self.collection.query(
            query_embeddings=[list(embedding)],
            n_results=top_k,
            include=[
                IncludeEnum.distances,
                IncludeEnum.metadatas,
                IncludeEnum.documents,
            ],
        )
        ids = (res.get("ids") or [[]])[0]
        dists = (res.get("distances") or [[]])[0]
        metas = (res.get("metadatas") or [[]])[0]
        docs = (res.get("documents") or [[]])[0]

        out: List[Dict[str, Any]] = []
        for i, _id in enumerate(ids):
            dist = float(dists[i]) if i < len(dists) else 1.0
            sim = max(0.0, min(1.0, 1.0 - dist))  # convert cosine distance → similarity
            out.append(
                {
                    "id": _id,
                    "similarity": sim,
                    "metadata": metas[i] if i < len(metas) else {},
                    "document": docs[i] if i < len(docs) else "",
                }
            )
        return out
