"""
Builds the final, validated AnalysisResponse from:
  1. The model's crop/disease/confidence guess (model_service)
  2. The grounded knowledge base entry (rag/retriever)

If anything is malformed at any step, falls back to a safe, generic response
rather than crashing or returning invalid data to the frontend (spec section 13/17).
"""
import logging
from typing import Dict, Optional

from pydantic import ValidationError

from app.models.schemas import AnalysisResponse

logger = logging.getLogger(__name__)

# Minimal per-language strings so the mock/fallback path isn't English-only.
# Real translation of the full response is the trained model's job (via prompting);
# this is only used for the safe-fallback and mock disclaimers.
_RECOMMENDATION_TEMPLATES = {
    "en": (
        "This is an automated analysis for informational purposes only. "
        "For significant crop damage, please consult your local agricultural "
        "extension office or a qualified expert before applying any treatment."
    ),
    "hi": (
        "यह केवल जानकारी के लिए एक स्वचालित विश्लेषण है। "
        "गंभीर फसल क्षति के लिए, कृपया कोई भी उपचार लागू करने से पहले अपने स्थानीय "
        "कृषि विस्तार कार्यालय या किसी योग्य विशेषज्ञ से सलाह लें।"
    ),
    "te": (
        "ఇది కేవలం సమాచార ప్రయోజనాల కోసం స్వయంచాలక విశ్లేషణ. "
        "తీవ్రమైన పంట నష్టం జరిగితే, ఏదైనా చికిత్స వర్తింపజేయడానికి ముందు దయచేసి మీ స్థానిక "
        "వ్యవసాయ విస్తరణ కార్యాలయం లేదా అర్హత కలిగిన నిపుణుడిని సంప్రదించండి."
    ),
}

_FALLBACK_RECOMMENDATION = {
    "en": "We could not generate a reliable analysis. Please try again with a clearer image, or consult a local agricultural expert.",
    "hi": "हम एक विश्वसनीय विश्लेषण उत्पन्न नहीं कर सके। कृपया स्पष्ट छवि के साथ पुनः प्रयास करें, या किसी स्थानीय कृषि विशेषज्ञ से सलाह लें।",
    "te": "మేము నమ్మదగిన విశ్లేషణను రూపొందించలేకపోయాము. దయచేసి స్పష్టమైన చిత్రంతో మళ్ళీ ప్రయత్నించండి, లేదా స్థానిక వ్యవసాయ నిపుణుడిని సంప్రదించండి.",
}


def build_safe_fallback(language: str) -> AnalysisResponse:
    lang = language if language in _FALLBACK_RECOMMENDATION else "en"
    return AnalysisResponse(
        crop="Unknown",
        disease="Unable to determine",
        confidence=0.0,
        symptoms=[],
        causes=[],
        prevention=[],
        organic_treatment=[],
        chemical_treatment=[],
        recommendation=_FALLBACK_RECOMMENDATION[lang],
        language=lang,
        is_fallback=True,
    )


def build_analysis_response(
    model_prediction: Dict,
    knowledge_entry: Dict,
    language: str,
    is_mock: bool,
) -> AnalysisResponse:
    """
    Merges model prediction (crop/disease/confidence) with the grounded knowledge
    entry (symptoms/causes/prevention/treatments), validates the result, and
    returns a safe fallback if validation fails for any reason.
    """
    try:
        lang = language if language in _RECOMMENDATION_TEMPLATES else "en"
        recommendation = _RECOMMENDATION_TEMPLATES[lang]
        if is_mock:
            recommendation = "[DEVELOPMENT MOCK RESPONSE] " + recommendation

        response = AnalysisResponse(
            crop=knowledge_entry.get("crop") or model_prediction.get("crop", "Unknown"),
            disease=knowledge_entry.get("disease") or model_prediction.get("disease", "Unknown"),
            confidence=float(model_prediction.get("confidence", 0.0)),
            symptoms=knowledge_entry.get("symptoms", []),
            causes=knowledge_entry.get("causes", []),
            prevention=knowledge_entry.get("prevention", []),
            organic_treatment=knowledge_entry.get("organic_treatment", []),
            chemical_treatment=knowledge_entry.get("chemical_treatment", []),
            recommendation=recommendation,
            language=lang,
            is_mock=is_mock,
            is_fallback=False,
        )
        return response
    except (ValidationError, ValueError, TypeError) as e:
        logger.error("Failed to build a valid AnalysisResponse, using fallback: %s", e)
        return build_safe_fallback(language)
