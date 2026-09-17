"""
Loads the structured agricultural knowledge base (knowledge/crop_diseases.json)
once and caches it in memory. See knowledge/crop_diseases.json for the schema.
"""
import json
import logging
from functools import lru_cache
from pathlib import Path
from typing import Dict

logger = logging.getLogger(__name__)


class KnowledgeBaseError(Exception):
    pass


@lru_cache()
def load_knowledge_base(path: str) -> Dict[str, dict]:
    kb_path = Path(__file__).resolve().parent.parent.parent / path
    kb_path = kb_path.resolve()

    if not kb_path.exists():
        raise KnowledgeBaseError(f"Knowledge base file not found at {kb_path}")

    try:
        with open(kb_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise KnowledgeBaseError(f"Knowledge base file is not valid JSON: {e}")

    if not isinstance(data, dict) or not data:
        raise KnowledgeBaseError("Knowledge base file is empty or malformed.")

    logger.info("Loaded knowledge base with %d entries from %s", len(data), kb_path)
    return data
