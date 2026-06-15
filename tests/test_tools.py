from tools import search_listings

def test_search_returns_results():
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    assert isinstance(results, list)
    assert len(results) > 0

def test_search_top_result_is_relevant():
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    top = results[0]["title"].lower()
    assert "graphic" in top or "tee" in top or "vintage" in top

def test_search_empty_results():
    results = search_listings("designer ballgown", size="XXS", max_price=5)
    assert results == []

def test_search_price_filter():
    results = search_listings("vintage", size=None, max_price=25)
    assert all(item["price"] <= 25 for item in results)

def test_search_size_filter():
    results = search_listings("tee", size="M", max_price=100)
    assert all("m" in item["size"].lower() for item in results)


from tools import suggest_outfit
from utils.data_loader import get_example_wardrobe, get_empty_wardrobe

def test_suggest_outfit_returns_string():
    from tools import search_listings
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    result = suggest_outfit(results[0], get_example_wardrobe())
    assert isinstance(result, str)
    assert len(result) > 0

def test_suggest_outfit_empty_wardrobe():
    from tools import search_listings
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    result = suggest_outfit(results[0], get_empty_wardrobe())
    assert isinstance(result, str)
    assert len(result) > 0  # must not return empty string

from tools import create_fit_card

def test_create_fit_card_returns_string():
    from tools import search_listings, suggest_outfit
    from utils.data_loader import get_example_wardrobe
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    outfit = suggest_outfit(results[0], get_example_wardrobe())
    result = create_fit_card(outfit, results[0])
    assert isinstance(result, str)
    assert len(result) > 0

def test_create_fit_card_empty_outfit():
    from tools import search_listings
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    result = create_fit_card("", results[0])
    assert result == "Cannot generate a fit card without an outfit suggestion."

def test_create_fit_card_whitespace_outfit():
    from tools import search_listings
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    result = create_fit_card("   ", results[0])
    assert result == "Cannot generate a fit card without an outfit suggestion."