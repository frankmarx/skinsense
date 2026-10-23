from chalicelib.connectors.csfloat.client import fetch_endpoint

# Change these to probe a different endpoint. Run with `pytest -s` to see the JSON.
# Note: "listings" search requires browser login; "listings/price-list" is public.
ENDPOINT = "listings/price-list"
PARAMS = None


def test_csfloat_fetch_endpoint(capsys):
    """
    Hits the live CSFloat API and prints the raw JSON response.
    No database interaction. Requires CSFLOAT_API_KEY to be set.
    """
    data = fetch_endpoint(ENDPOINT, params=PARAMS)

    assert isinstance(data, list)
    assert len(data) > 0
    assert "market_hash_name" in data[0]
    assert capsys.readouterr().out.strip()
