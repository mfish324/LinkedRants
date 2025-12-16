"""AI client functions for each translation provider."""

import os
from dotenv import load_dotenv

# System prompts for translation modes
SYSTEM_PROMPTS = {
    'to_linkedin': """You are a LinkedIn post translator. Take the user's authentic, real thoughts and transform them into a typical LinkedIn post. Include:
- Unnecessary dramatic framing ("I'll never forget the day...")
- Line breaks after every sentence for "engagement"
- Humble bragging
- Gratitude performance ("So grateful for...")
- Business lessons extracted from mundane events
- End with "Agree?" or "Thoughts?"
- Strategic emoji use throughout
- Making everything about "the journey"
- Self-congratulation disguised as helping others

Keep the core message but make it extremely performative and cringe-worthy (in a funny way).
Return ONLY the LinkedIn version, no explanations or preamble.""",

    'to_reality': """You are a LinkedIn post translator. Take the cringey LinkedIn post and translate it to what the person actually meant. Be:
- Brutally honest
- Funny but not mean-spirited
- Call out the humble brag
- Translate corporate speak to plain English
- Expose the obvious self-promotion
- Keep it concise

Return ONLY the reality translation, no explanations or preamble."""
}


def translate_anthropic(text: str, mode: str) -> str:
    """Translate using Anthropic Claude."""
    import anthropic

    load_dotenv(override=True)
    client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

    message = client.messages.create(
        model="claude-3-5-haiku-20241022",
        max_tokens=512,
        system=SYSTEM_PROMPTS[mode],
        messages=[{"role": "user", "content": text}]
    )

    return message.content[0].text.strip()


def translate_openai(text: str, mode: str) -> str:
    """Translate using OpenAI GPT-4."""
    import openai

    load_dotenv(override=True)
    client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPTS[mode]},
            {"role": "user", "content": text}
        ],
        max_tokens=512
    )

    return response.choices[0].message.content.strip()


def translate_google(text: str, mode: str) -> str:
    """Translate using Google Gemini."""
    import google.generativeai as genai

    load_dotenv(override=True)
    genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"{SYSTEM_PROMPTS[mode]}\n\nText to translate:\n{text}"
    response = model.generate_content(prompt)

    return response.text.strip()


def translate_groq(text: str, mode: str) -> str:
    """Translate using Groq (Llama)."""
    from groq import Groq

    load_dotenv(override=True)
    client = Groq(api_key=os.getenv('GROQ_API_KEY'))

    response = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPTS[mode]},
            {"role": "user", "content": text}
        ],
        max_tokens=512
    )

    return response.choices[0].message.content.strip()


# Map provider names to translation functions
TRANSLATE_FUNCTIONS = {
    'anthropic': translate_anthropic,
    'openai': translate_openai,
    'google': translate_google,
    'groq': translate_groq,
}
