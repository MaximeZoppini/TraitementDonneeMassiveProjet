{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "id": "7c24fd6f",
   "metadata": {},
   "outputs": [],
   "source": [
    "SPARQL_ENDPOINT = \"https://query.wikidata.org/sparql\"\n",
    "HEADERS = {\"User-Agent\": \"MassiveDataProject/1.0 (cmvilleroy@gmail.com)\"}\n",
    "import requests\n",
    "\n",
    "def build_sparql_query(limit=100):\n",
    "    return f\"\"\"\n",
    "    SELECT DISTINCT ?ville ?villeLabel ?pays ?paysLabel ?image WHERE {{\n",
    "      ?ville wdt:P31 wd:Q1549591;\n",
    "             wdt:P17 ?pays;\n",
    "             wdt:P18 ?image.\n",
    "      SERVICE wikibase:label {{ bd:serviceParam wikibase:language \"fr\". }}\n",
    "    }}\n",
    "    LIMIT {limit}\n",
    "    \"\"\"\n",
    "\n",
    "def run_sparql_query(query):\n",
    "    response = requests.get(SPARQL_ENDPOINT, params={\"query\": query, \"format\": \"json\"}, headers=HEADERS)\n",
    "    response.raise_for_status()\n",
    "    return response.json()[\"results\"][\"bindings\"]\n"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.13.3"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
