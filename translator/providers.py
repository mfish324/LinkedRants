"""AI Provider configuration for the LinkedIn Translator."""

import os
import random
from dataclasses import dataclass
from typing import List, Tuple, Optional
from dotenv import load_dotenv


@dataclass
class AIProvider:
    """Configuration for an AI provider."""
    name: str           # Display name (e.g., "Claude", "GPT-4")
    model: str          # Model identifier
    api_key_env: str    # Environment variable name for API key
    weight: int = 1     # Higher weight = more likely to be selected


# Available providers configuration
PROVIDERS = {
    'anthropic': AIProvider(
        name='Claude',
        model='claude-3-5-haiku-20241022',
        api_key_env='ANTHROPIC_API_KEY',
        weight=2
    ),
    'openai': AIProvider(
        name='GPT-4',
        model='gpt-4o-mini',
        api_key_env='OPENAI_API_KEY',
        weight=2
    ),
    'google': AIProvider(
        name='Gemini',
        model='gemini-1.5-flash',
        api_key_env='GOOGLE_API_KEY',
        weight=1
    ),
    'groq': AIProvider(
        name='Llama',
        model='llama-3.1-70b-versatile',
        api_key_env='GROQ_API_KEY',
        weight=1
    ),
}


def get_enabled_providers() -> List[Tuple[str, AIProvider]]:
    """
    Get list of providers that are enabled and have valid API keys.

    Returns:
        List of (provider_name, AIProvider) tuples
    """
    load_dotenv(override=True)

    # Get enabled providers from env, default to just anthropic
    enabled_names = os.getenv('TRANSLATOR_PROVIDERS', 'anthropic').split(',')
    valid = []

    for name in enabled_names:
        name = name.strip().lower()
        if name in PROVIDERS:
            provider = PROVIDERS[name]
            api_key = os.getenv(provider.api_key_env, '').strip()
            if api_key:
                valid.append((name, provider))

    return valid


def select_random_provider() -> Tuple[str, AIProvider]:
    """
    Select a random provider using weighted selection.

    Returns:
        Tuple of (provider_name, AIProvider)

    Raises:
        ValueError: If no valid providers are configured
    """
    providers = get_enabled_providers()

    if not providers:
        raise ValueError("No valid AI providers configured. Check your API keys and TRANSLATOR_PROVIDERS setting.")

    # If only one provider, just return it
    if len(providers) == 1:
        return providers[0]

    names, provider_objs = zip(*providers)
    weights = [p.weight for p in provider_objs]

    selected_name = random.choices(names, weights=weights, k=1)[0]
    return selected_name, PROVIDERS[selected_name]


def get_provider_by_name(name: str) -> Optional[AIProvider]:
    """Get a specific provider by name."""
    return PROVIDERS.get(name.lower())
