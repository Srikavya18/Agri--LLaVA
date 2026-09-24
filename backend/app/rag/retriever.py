"""
Deterministic knowledge retrieval for the RAG step.

Pipeline (see docs/architecture.md):
  model predicts crop + disease (rough guess)
      -> retriever finds the best-matching knowledge base entry
      -> that grounded entry supplies symptoms/causes/prevention/treatment
      -> the model (or, in mock mode, this service) is not trusted to invent these facts

Deliberately simple keyword-based matching, no vector database — sufficient and
reliable at this knowledge base size (see project spec: avoid unnecessary complexity).
"""
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

FALLBACK_ENTRY = {
    "crop": "Unknown",
    "disease": "Unrecognized condition",
    "symptoms": ["The system could not confidently match this to a known condition."],
    "causes": [],
    "prevention": ["Consult a local agricultural extension officer for an in-person assessment."],
    "organic_treatment": [],
    "chemical_treatment": [],
}


def _normalize(text: str) -> str:
    return text.strip().lower().replace(" ", "_").replace("-", "_")


def retrieve(
    knowledge_base: Dict[str, dict],
    crop_guess: str,
    disease_guess: str,
    language: str = "en",
) -> Dict:
    """
    Finds the best matching knowledge base entry for a predicted crop + disease,
    localized to `language` when a translation exists.

    Matching strategy (in order):
      1. Exact key match on "{crop}_{disease}" normalized.
      2. Entry whose crop AND disease fields both loosely match the guesses.
      3. Entry whose disease field matches (crop mismatch tolerated).
      4. Safe fallback entry — never silently invents agricultural facts.

    If a match is found but has no translation for the requested language,
    the English content is returned rather than a broken/partial entry —
    partial translation is worse than a clearly-consistent English fallback.
    """
    if not crop_guess and not disease_guess:
        return _localize(dict(FALLBACK_ENTRY), language)

    crop_norm = _normalize(crop_guess)
    disease_norm = _normalize(disease_guess)

    # Strategy 1: exact composite key
    candidate_key = f"{crop_norm}_{disease_norm}"
    if candidate_key in knowledge_base:
        logger.info("RAG: exact key match '%s'", candidate_key)
        return _localize(dict(knowledge_base[candidate_key]), language)

    # Strategy 2: both crop and disease loosely match
    for key, entry in knowledge_base.items():
        entry_crop = _normalize(entry.get("crop", ""))
        entry_disease = _normalize(entry.get("disease", ""))
        if crop_norm in entry_crop or entry_crop in crop_norm:
            if disease_norm in entry_disease or entry_disease in disease_norm:
                logger.info("RAG: crop+disease fuzzy match -> '%s'", key)
                return _localize(dict(entry), language)

    # Strategy 3: disease-only match
    for key, entry in knowledge_base.items():
        entry_disease = _normalize(entry.get("disease", ""))
        if disease_norm and (disease_norm in entry_disease or entry_disease in disease_norm):
            logger.info("RAG: disease-only fuzzy match -> '%s'", key)
            return _localize(dict(entry), language)

    logger.warning(
        "RAG: no match found for crop='%s' disease='%s'; using fallback entry",
        crop_guess, disease_guess,
    )
    fallback = dict(FALLBACK_ENTRY)
    fallback["crop"] = crop_guess or "Unknown"
    fallback["disease"] = disease_guess or "Unrecognized condition"
    return _localize(fallback, language)


def _localize(entry: Dict, language: str) -> Dict:
    """
    Returns entry content in the requested language if a translation exists,
    otherwise returns the English content unchanged. Never mixes languages
    within one entry — that would be more confusing than consistent English.
    """
    if language == "en":
        entry.pop("translations", None)
        return entry

    translations = entry.get("translations", {})
    localized = translations.get(language)
    if not localized:
        entry.pop("translations", None)
        return entry

    result = dict(entry)
    result.pop("translations", None)
    result.update(localized)
    return result
