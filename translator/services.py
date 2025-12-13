"""LinkedIn Translator service using Anthropic Claude API."""

import os
import anthropic
from dotenv import load_dotenv


class LinkedInTranslator:
    """Translate between honest thoughts and LinkedIn-speak."""

    def __init__(self):
        # Reload .env each time to pick up changes
        load_dotenv(override=True)
        api_key = os.getenv('ANTHROPIC_API_KEY', '')
        self.client = anthropic.Anthropic(api_key=api_key)

    def to_linkedin(self, honest_text: str) -> str:
        """Transform honest thoughts into insufferable LinkedIn speak."""
        prompt = f"""Transform the following honest thought into a typical LinkedIn post.

Make it include these LinkedIn tropes:
- Unnecessarily dramatic framing ("I'll never forget the day...")
- Line breaks after every sentence (the LinkedIn engagement hack)
- Humble bragging
- Gratitude performance ("So grateful for...")
- Extract business lessons from mundane events
- End with "Agree?" or "Thoughts?" and relevant emoji
- Strategic emoji use throughout
- Make it about "the journey"
- Self-congratulation disguised as helping others
- Use phrases like "I'm thrilled to announce...", "After much reflection..."

Keep the core message but make it extremely performative and cringe-worthy (in a funny way).

Original honest thought:
{honest_text}

LinkedIn version:"""

        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return message.content[0].text.strip()
        except Exception as e:
            return f"Translation failed: {str(e)}"

    def to_reality(self, linkedin_text: str) -> str:
        """Translate LinkedIn-speak to what the person actually meant."""
        prompt = f"""Translate the following LinkedIn post to what the person actually meant.

Be brutally honest but funny:
- Strip away the performance
- Identify the actual underlying emotion/situation
- Call out any humble brags
- Translate corporate speak to plain English
- Expose the obvious self-promotion
- Be witty but not mean-spirited

LinkedIn post:
{linkedin_text}

What they actually meant:"""

        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return message.content[0].text.strip()
        except Exception as e:
            return f"Translation failed: {str(e)}"


def translate(text: str, mode: str) -> str:
    """
    Translate text between LinkedIn-speak and reality.

    Args:
        text: The input text to translate
        mode: Either 'to_linkedin' or 'to_reality'

    Returns:
        The translated text
    """
    translator = LinkedInTranslator()

    if mode == 'to_linkedin':
        return translator.to_linkedin(text)
    elif mode == 'to_reality':
        return translator.to_reality(text)
    else:
        raise ValueError(f"Invalid mode: {mode}")
