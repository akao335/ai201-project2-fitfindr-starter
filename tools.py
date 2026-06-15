"""
tools.py

The three required FitFindr tools. Each tool is a standalone function that
can be called and tested independently before being wired into the agent loop.

Complete and test each tool before moving to agent.py.

Tools:
    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)              → str
    create_fit_card(outfit, new_item)               → str
"""

import os

from dotenv import load_dotenv
from groq import Groq

from utils.data_loader import load_listings

load_dotenv()


# ── Groq client ───────────────────────────────────────────────────────────────

def _get_groq_client():
    """Initialize and return a Groq client using GROQ_API_KEY from .env."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not set. Add it to a .env file in the project root."
        )
    return Groq(api_key=api_key)


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the mock listings dataset for items matching the description,
    optional size, and optional price ceiling.

    Args:
        description: Keywords describing what the user is looking for
                     (e.g., "vintage graphic tee").
        size:        Size string to filter by, or None to skip size filtering.
                     Matching is case-insensitive (e.g., "M" matches "S/M").
        max_price:   Maximum price (inclusive), or None to skip price filtering.

    Returns:
        A list of matching listing dicts, sorted by relevance (best match first).
        Returns an empty list if nothing matches — does NOT raise an exception.

    Each listing dict has the following fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand, platform

    TODO:
        1. Load all listings with load_listings().
        2. Filter by max_price and size (if provided).
        3. Score each remaining listing by keyword overlap with `description`.
        4. Drop any listings with a score of 0 (no relevant matches).
        5. Sort by score, highest first, and return the listing dicts.

    Before writing code, fill in the Tool 1 section of planning.md.
    """
    # Replace this with your implementation

    listings = load_listings()

    if max_price is not None:
        listings = [l for l in listings if l["price"] <= max_price]

    if size is not None:
        listings = [l for l in listings if size.lower() in l["size"].lower()]

    keywords = description.lower().split()

    def score(listing):
        title = listing["title"].lower()
        tags = " ".join(listing["style_tags"]).lower()
        description = listing["description"].lower()
        category = listing["category"].lower()
        colors = " ".join(listing["colors"]).lower()
        brand = (listing["brand"] or "").lower()

        total = 0
        for kw in keywords:
            if kw in title:
                total += 3        # title match counts most
            if kw in tags:
                total += 2        # style tag match counts second
            if kw in description:
                total += 1
            if kw in category:
                total += 1
            if kw in colors:
                total += 1
            if kw in brand:
                total += 1
        return total
    
    scored = [(score(l), l) for l in listings]
    scored = [(s, l) for s, l in scored if s > 0]
    scored.sort(key=lambda x: x[0], reverse=True)

    return [l for _, l in scored]

    
    

# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest 1–2 complete outfits.

    Args:
        new_item: A listing dict (the item the user is considering buying).
        wardrobe: A wardrobe dict with an 'items' key containing a list of
                  wardrobe item dicts. May be empty — handle this gracefully.

    Returns:
        A non-empty string with outfit suggestions.
        If the wardrobe is empty, offer general styling advice for the item
        rather than raising an exception or returning an empty string.

    TODO:
        1. Check whether wardrobe['items'] is empty.
        2. If empty: call the LLM with a prompt for general styling ideas
           (what kinds of items pair well, what vibe it suits, etc.).
        3. If not empty: format the wardrobe items into a prompt and ask
           the LLM to suggest specific outfit combinations using the new item
           and named pieces from the wardrobe.
        4. Return the LLM's response as a string.

    Before writing code, fill in the Tool 2 section of planning.md.
    """
    client = _get_groq_client()
    
    
    items = wardrobe.get("items", [])
    
    if not items:
        #if empty, general advice
        prompt = (
            f"I just thrifted this item:\n"
            f"Title: {new_item['title']}\n"
            f"Style tags: {', '.join(new_item['style_tags'])}\n"
            f"Colors: {', '.join(new_item['colors'])}\n"
            f"Description: {new_item['description']}\n\n"
            f"I don't have much in my wardrobe yet. Give me general styling "
            f"advice for this piece — what kinds of items pair well with it, "
            f"what vibe it suits, and how to wear it."
        )
    else:
        #has wardrobe, prompt outfit suggestion
        wardrobe_text = "\n".join(
            f"- {item['name']} ({', '.join(item['style_tags'])})"
            for item in items
        )
        prompt = (
            f"I just thrifted this item:\n"
            f"Title: {new_item['title']}\n"
            f"Style tags: {', '.join(new_item['style_tags'])}\n"
            f"Colors: {', '.join(new_item['colors'])}\n"
            f"Description: {new_item['description']}\n\n"
            f"Here's what I already own:\n{wardrobe_text}\n\n"
            f"Suggest 1-2 complete outfit combinations using the new item "
            f"and specific pieces from my wardrobe. Be specific about which "
            f"pieces to pair together and how to style them."
        )

    # call the LLM
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
    )
    
    return response.choices[0].message.content



# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Generate a short, shareable outfit caption for the thrifted find.

    Args:
        outfit:   The outfit suggestion string from suggest_outfit().
        new_item: The listing dict for the thrifted item.

    Returns:
        A 2–4 sentence string usable as an Instagram/TikTok caption.
        If outfit is empty or missing, return a descriptive error message
        string — do NOT raise an exception.

    The caption should:
    - Feel casual and authentic (like a real OOTD post, not a product description)
    - Mention the item name, price, and platform naturally (once each)
    - Capture the outfit vibe in specific terms
    - Sound different each time for different inputs (use higher LLM temperature)

    TODO:
        1. Guard against an empty or whitespace-only outfit string.
        2. Build a prompt that gives the LLM the item details and the outfit,
           and asks for a caption matching the style guidelines above.
        3. Call the LLM and return the response.

    Before writing code, fill in the Tool 3 section of planning.md.
    """
    # Replace this with your implementation
    # Step 1 — guard against empty outfit string
    if not outfit or not outfit.strip():
        return "Cannot generate a fit card without an outfit suggestion."
    
    client = _get_groq_client()
    
    # Step 2 — build the prompt
    prompt = (
        f"Write a 2-4 sentence Instagram/TikTok caption for this thrifted outfit.\n\n"
        f"Item: {new_item['title']}\n"
        f"Price: ${new_item['price']}\n"
        f"Platform: {new_item['platform']}\n"
        f"Outfit: {outfit}\n\n"
        f"The caption should:\n"
        f"- Feel casual and authentic, like a real OOTD post\n"
        f"- Mention the item name, price, and platform naturally (once each)\n"
        f"- Capture the outfit vibe in specific terms\n"
        f"- NOT sound like a product description\n"
        f"Just write the caption, nothing else."
    )
    
    # Step 3 — call LLM with higher temperature for variety
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=150,
        temperature=1.2,
    )
    
    return response.choices[0].message.content
