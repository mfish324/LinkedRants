"""LinkedIn Translator service with multi-provider support."""

import random
from typing import Dict, Any

from .providers import get_enabled_providers, select_random_provider
from .ai_clients import TRANSLATE_FUNCTIONS


def translate(text: str, mode: str) -> Dict[str, Any]:
    """
    Translate text using a randomly selected AI provider.
    Falls back to other providers on failure.

    Args:
        text: The text to translate
        mode: 'to_linkedin' or 'to_reality'

    Returns:
        dict with 'translation', 'provider_name', 'model'

    Raises:
        Exception: If all providers fail
    """
    if mode not in ['to_linkedin', 'to_reality']:
        raise ValueError(f"Invalid mode: {mode}")

    providers = get_enabled_providers()

    if not providers:
        raise ValueError("No valid AI providers configured")

    # Shuffle for random fallback order
    random.shuffle(providers)

    last_error = None

    for name, provider in providers:
        try:
            translate_func = TRANSLATE_FUNCTIONS.get(name)

            if not translate_func:
                continue

            translation = translate_func(text, mode)

            return {
                'translation': translation,
                'provider_name': provider.name,
                'model': provider.model,
            }

        except Exception as e:
            last_error = e
            continue  # Try next provider

    # All providers failed
    error_msg = str(last_error) if last_error else "All translation providers failed"
    raise Exception(f"Translation failed: {error_msg}")


def translate_simple(text: str, mode: str) -> str:
    """
    Simple translation interface (backwards compatible).
    Returns just the translation text.

    Args:
        text: The text to translate
        mode: 'to_linkedin' or 'to_reality'

    Returns:
        The translated text
    """
    try:
        result = translate(text, mode)
        return result['translation']
    except Exception as e:
        return f"Translation failed: {str(e)}"
