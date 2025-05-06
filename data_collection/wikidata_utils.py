import requests

SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
HEADERS = {"User-Agent": "MassiveDataProject/1.0 (cmvilleroy@gmail.com)"}

def build_sparql_query(limit=100):
    return f"""
    SELECT DISTINCT ?ville ?villeLabel ?pays ?paysLabel ?image WHERE {{
      ?ville wdt:P31 wd:Q1549591;
             wdt:P17 ?pays;
             wdt:P18 ?image.
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "fr". }}
    }}
    LIMIT {limit}
    """

def run_sparql_query(query):
    response = requests.get(SPARQL_ENDPOINT, params={"query": query, "format": "json"}, headers=HEADERS)
    response.raise_for_status()
    return response.json()["results"]["bindings"]
