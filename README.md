# FitFindr

FitFindr is a multi-tool AI agent that helps users find secondhand clothing 
and figure out how to wear it. It searches thrift listings, suggests outfit 
combinations based on your wardrobe, and generates a shareable fit card caption.

---
## Tool Inventory

### search_listings(description: str, size: str | None, max_price: float | None) → list[dict]
Searches the mock listings dataset for items matching the description, size, 
and price ceiling. Returns a list of matching listing dicts sorted by relevance. 
Returns an empty list if nothing matches.

### suggest_outfit(new_item: dict, wardrobe: dict) → str
Given a thrifted item and the user's wardrobe, suggests 1–2 complete outfit 
combinations using specific wardrobe pieces. If the wardrobe is empty, returns 
general styling advice instead.

### create_fit_card(outfit: str, new_item: dict) → str
Generates a 2–4 sentence Instagram/TikTok caption for the outfit. Returns an 
error message string if outfit is empty — does not crash.

## What's Included

```
ai201-project2-fitfindr-starter/
├── data/
│   ├── listings.json          # 40 mock secondhand listings
│   └── wardrobe_schema.json   # Wardrobe format + example wardrobe
├── utils/
│   └── data_loader.py         # Helper functions for loading the data
├── planning.md                # Your planning template — fill this out first
└── requirements.txt           # Python dependencies
```
## Planning Loop

**How does your agent decide which tool to call next?**
<!-- Describe the logic your planning loop uses. What does it look at? What conditions change its behavior? How does it know when it's done? -->
The agent starts with searching for a item based on the  user's preferences by calling search_listings. If this is successful, then it will continue to call the suggest_outfit tool. After generating the outfit, the tool create_fit_card will be called. Once that tool is finisthed returning, the agent will be finished with its output. If the initial search_listings did not find anything, the suggest_outfit tool will not be called and the agent will return nothing and prompt the user to try a different prompt. 
---

## State Management

The agent uses a session dict to pass data between tools within one interaction:
- `session["selected_item"]`: top listing dict from search_listings
- `session["outfit_suggestion"]`: string from suggest_outfit
- `session["fit_card"]`: caption string from create_fit_card
- `session["error"]`: set if any tool fails; stops further tool calls

Each tool reads from the session and writes its result back before the next tool runs.

---
## Error Handling

For each tool, describe the specific failure mode you're handling and what the agent does in response.

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| search_listings | No results match the query |Sets session["error"] with a message telling the user to try broader keywords or raise their max price. Does not call suggest_outfit.  |
| suggest_outfit | Wardrobe is empty |  Calls LLM for general styling advice instead of wardrobe-specific combinations. Returns a non-empty string. |
| create_fit_card | Outfit input is missing or incomplete | Returns "Cannot generate a fit card without an outfit suggestion." without calling the LLM. |

---
## Setup

```bash
pip install -r requirements.txt
```

Set your Groq API key in a `.env` file (get a free key at [console.groq.com](https://console.groq.com)):
```
GROQ_API_KEY=your_key_here
```

## The Mock Listings Dataset

`data/listings.json` contains 40 mock secondhand listings across categories (tops, bottoms, outerwear, shoes, accessories) and styles (vintage, y2k, grunge, cottagecore, streetwear, and more).

Each listing has: `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand`, and `platform`.

Load it with:
```python
from utils.data_loader import load_listings
listings = load_listings()
```

## The Wardrobe Schema

`data/wardrobe_schema.json` defines the format your agent uses to represent a user's existing wardrobe. It includes:

- `schema`: field definitions for a wardrobe item
- `example_wardrobe`: a sample wardrobe with 10 items you can use for testing
- `empty_wardrobe`: a starting template for a new user

Load an example wardrobe with:
```python
from utils.data_loader import get_example_wardrobe
wardrobe = get_example_wardrobe()
```

## Where to Start

1. **Read `planning.md` and fill it out before writing any code.**
2. Verify the data loads correctly by running `python utils/data_loader.py`.
3. Build and test each tool individually before connecting them through your planning loop.

Your implementation files go in this same directory. There's no required file structure for your agent code — organize it however makes sense for your design.
