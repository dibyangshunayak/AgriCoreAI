# =====================================================================
# FILE: backend/app/skills/translator/translate.py
# DESCRIPTION: Translation skill.
# =====================================================================

import logging

logger = logging.getLogger(__name__)

def translate_query(text: str, target_lang: str) -> str:
    """Wrapper to translate message via language engine."""
    logger.info(f"Executing translation skill: target={target_lang}")
    from app.services.translator_service import translator_service
    return translator_service.translate_from_english(text, target_lang)
