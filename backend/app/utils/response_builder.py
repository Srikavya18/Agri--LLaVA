"""
Builds the final validated AnalysisResponse.

The knowledge base is stored in English so that RAG retrieval works reliably.
This file translates the final user-facing response into English, Hindi, or
Telugu after the RAG lookup is complete.
"""

import logging
from typing import Dict

from pydantic import ValidationError

from app.models.schemas import AnalysisResponse

logger = logging.getLogger(__name__)


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
        "వ్యవసాయ విస్తరణ కార్యాలయాన్ని లేదా అర్హత కలిగిన నిపుణుడిని సంప్రదించండి."
    ),
}


_FALLBACK_RECOMMENDATION = {
    "en": (
        "We could not generate a reliable analysis. Please try again with "
        "a clearer image, or consult a local agricultural expert."
    ),
    "hi": (
        "हम एक विश्वसनीय विश्लेषण उत्पन्न नहीं कर सके। कृपया स्पष्ट छवि के साथ "
        "पुनः प्रयास करें, या किसी स्थानीय कृषि विशेषज्ञ से सलाह लें।"
    ),
    "te": (
        "మేము నమ్మదగిన విశ్లేషణను రూపొందించలేకపోయాము. దయచేసి స్పష్టమైన చిత్రంతో "
        "మళ్ళీ ప్రయత్నించండి, లేదా స్థానిక వ్యవసాయ నిపుణుడిని సంప్రదించండి."
    ),
}


# -------------------------------------------------------------------
# Crop translations
# -------------------------------------------------------------------

_CROP_TRANSLATIONS = {
    "hi": {
        "Tomato": "टमाटर",
        "Potato": "आलू",
        "Bell Pepper": "शिमला मिर्च",
        "Apple": "सेब",
        "Corn (Maize)": "मक्का",
    },
    "te": {
        "Tomato": "టమాటా",
        "Potato": "బంగాళాదుంప",
        "Bell Pepper": "క్యాప్సికమ్",
        "Apple": "ఆపిల్",
        "Corn (Maize)": "మొక్కజొన్న",
    },
}


# -------------------------------------------------------------------
# Disease translations
# -------------------------------------------------------------------

_DISEASE_TRANSLATIONS = {
    "hi": {
        "Early Blight": "अर्ली ब्लाइट",
        "Late Blight": "लेट ब्लाइट",
        "Healthy": "स्वस्थ",
        "Bacterial Spot": "बैक्टीरियल स्पॉट",
        "Cedar Apple Rust": "सीडर एप्पल रस्ट",
        "Common Rust": "कॉमन रस्ट",
    },
    "te": {
        "Early Blight": "ఎర్లీ బ్లైట్",
        "Late Blight": "లేట్ బ్లైట్",
        "Healthy": "ఆరోగ్యకరమైనది",
        "Bacterial Spot": "బాక్టీరియల్ స్పాట్",
        "Cedar Apple Rust": "సీడర్ ఆపిల్ రస్ట్",
        "Common Rust": "కామన్ రస్ట్",
    },
}


# -------------------------------------------------------------------
# Section translations
# -------------------------------------------------------------------

_SECTION_TRANSLATIONS = {
    "hi": {
        "symptoms": {
            "Dark brown spots with concentric ring pattern on older leaves":
                "पुरानी पत्तियों पर गोलाकार छल्ले के पैटर्न वाले गहरे भूरे धब्बे",
            "Yellow halo around lesions":
                "घावों के चारों ओर पीला घेरा",
            "Premature leaf drop reducing tuber yield":
                "समय से पहले पत्तियों का गिरना, जिससे कंद की उपज कम होती है",
        },
        "causes": {
            "Fungal infection by Alternaria solani":
                "Alternaria solani नामक फफूंद के कारण संक्रमण",
            "Plant stress, warm temperatures, and leaf wetness":
                "पौधे पर तनाव, गर्म तापमान और पत्तियों पर नमी",
        },
        "prevention": {
            "Rotate crops with non-solanaceous plants":
                "सोलनैसियस परिवार से अलग फसलों के साथ फसल चक्र अपनाएं",
            "Maintain adequate plant nutrition to reduce stress":
                "पौधे के तनाव को कम करने के लिए पर्याप्त पोषण दें",
            "Avoid overhead irrigation":
                "ऊपर से पानी देने से बचें",
        },
        "organic_treatment": {
            "Remove infected foliage":
                "संक्रमित पत्तियों को हटा दें",
            "Apply copper-based or biological fungicides":
                "तांबा आधारित या जैविक फफूंदनाशकों का उपयोग करें",
        },
        "chemical_treatment": {
            "Use a fungicide labeled for early blight on potato according to local guidance":
                "स्थानीय दिशानिर्देशों के अनुसार आलू के अर्ली ब्लाइट के लिए लेबल किए गए फफूंदनाशक का उपयोग करें",
        },
    },

    "te": {
        "symptoms": {
            "Dark brown spots with concentric ring pattern on older leaves":
                "పాత ఆకులపై వలయాకార నమూనాతో ముదురు గోధుమ రంగు మచ్చలు",
            "Yellow halo around lesions":
                "మచ్చల చుట్టూ పసుపు వలయం",
            "Premature leaf drop reducing tuber yield":
                "ఆకులు ముందుగానే రాలిపోవడం వల్ల దుంపల దిగుబడి తగ్గుతుంది",
        },
        "causes": {
            "Fungal infection by Alternaria solani":
                "Alternaria solani అనే శిలీంధ్రం వల్ల సంక్రమణ",
            "Plant stress, warm temperatures, and leaf wetness":
                "మొక్కపై ఒత్తిడి, వెచ్చని ఉష్ణోగ్రతలు మరియు ఆకులపై తేమ",
        },
        "prevention": {
            "Rotate crops with non-solanaceous plants":
                "సోలనేసియస్ కుటుంబానికి చెందని పంటలతో పంట మార్పిడి చేయండి",
            "Maintain adequate plant nutrition to reduce stress":
                "మొక్కపై ఒత్తిడిని తగ్గించడానికి తగిన పోషకాలను అందించండి",
            "Avoid overhead irrigation":
                "పై నుంచి నీటిపారుదల చేయడం నివారించండి",
        },
        "organic_treatment": {
            "Remove infected foliage":
                "సోకిన ఆకులను తొలగించండి",
            "Apply copper-based or biological fungicides":
                "రాగి ఆధారిత లేదా జీవ శిలీంద్రనాశకాలను ఉపయోగించండి",
        },
        "chemical_treatment": {
            "Use a fungicide labeled for early blight on potato according to local guidance":
                "స్థానిక మార్గదర్శకాల ప్రకారం బంగాళాదుంప ఎర్లీ బ్లైట్ కోసం సూచించబడిన శిలీంద్రనాశకాన్ని ఉపయోగించండి",
        },
    },
}


def _translate_value(value: str, language: str, category: str) -> str:
    """
    Translate one crop/disease value while keeping English as the
    canonical internal value.
    """

    if language == "en":
        return value

    if category == "crop":
        return _CROP_TRANSLATIONS.get(language, {}).get(value, value)

    if category == "disease":
        return _DISEASE_TRANSLATIONS.get(language, {}).get(value, value)

    return value


def _translate_list(
    values: list,
    language: str,
    category: str,
) -> list:
    """
    Translate a list of knowledge-base strings.
    """

    if language == "en":
        return values

    translations = (
        _SECTION_TRANSLATIONS
        .get(language, {})
        .get(category, {})
    )

    return [
        translations.get(item, item)
        for item in values
    ]


def build_safe_fallback(language: str) -> AnalysisResponse:

    lang = (
        language
        if language in _FALLBACK_RECOMMENDATION
        else "en"
    )

    crop = "Unknown"
    disease = "Unable to determine"

    if lang == "hi":
        crop = "अज्ञात"
        disease = "निर्धारित नहीं किया जा सका"

    elif lang == "te":
        crop = "తెలియదు"
        disease = "నిర్ధారించలేకపోయాము"

    return AnalysisResponse(
        crop=crop,
        disease=disease,
        confidence=0.0,
        symptoms=[],
        causes=[],
        prevention=[],
        organic_treatment=[],
        chemical_treatment=[],
        recommendation=_FALLBACK_RECOMMENDATION[lang],
        language=lang,
        is_fallback=True,
        is_mock=False,
    )


def build_analysis_response(
    model_prediction: Dict,
    knowledge_entry: Dict,
    language: str,
    is_mock: bool,
) -> AnalysisResponse:
    """
    Merge model prediction with RAG knowledge and translate the final
    user-facing response.
    """

    try:

        lang = (
            language
            if language in _RECOMMENDATION_TEMPLATES
            else "en"
        )

        # -----------------------------------------------------------
        # Keep canonical English values for internal RAG processing.
        # Translation happens only at the final response stage.
        # -----------------------------------------------------------

        crop = (
            knowledge_entry.get("crop")
            or model_prediction.get("crop", "Unknown")
        )

        disease = (
            knowledge_entry.get("disease")
            or model_prediction.get("disease", "Unknown")
        )

        symptoms = knowledge_entry.get("symptoms", [])
        causes = knowledge_entry.get("causes", [])
        prevention = knowledge_entry.get("prevention", [])
        organic_treatment = knowledge_entry.get(
            "organic_treatment", []
        )
        chemical_treatment = knowledge_entry.get(
            "chemical_treatment", []
        )

        # -----------------------------------------------------------
        # Translate final response
        # -----------------------------------------------------------

        translated_crop = _translate_value(
            crop,
            lang,
            "crop"
        )

        translated_disease = _translate_value(
            disease,
            lang,
            "disease"
        )

        translated_symptoms = _translate_list(
            symptoms,
            lang,
            "symptoms"
        )

        translated_causes = _translate_list(
            causes,
            lang,
            "causes"
        )

        translated_prevention = _translate_list(
            prevention,
            lang,
            "prevention"
        )

        translated_organic_treatment = _translate_list(
            organic_treatment,
            lang,
            "organic_treatment"
        )

        translated_chemical_treatment = _translate_list(
            chemical_treatment,
            lang,
            "chemical_treatment"
        )

        recommendation = _RECOMMENDATION_TEMPLATES[lang]

        if is_mock:
            recommendation = (
                "[DEVELOPMENT MOCK RESPONSE] "
                + recommendation
            )

        response = AnalysisResponse(
            crop=translated_crop,
            disease=translated_disease,
            confidence=float(
                model_prediction.get(
                    "confidence",
                    0.0
                )
            ),
            symptoms=translated_symptoms,
            causes=translated_causes,
            prevention=translated_prevention,
            organic_treatment=translated_organic_treatment,
            chemical_treatment=translated_chemical_treatment,
            recommendation=recommendation,
            language=lang,
            is_mock=is_mock,
            is_fallback=False,
        )

        return response

    except (
        ValidationError,
        ValueError,
        TypeError,
    ) as e:

        logger.error(
            "Failed to build a valid AnalysisResponse, "
            "using fallback: %s",
            e,
        )

        return build_safe_fallback(language)