import os
import requests


def format_input():
    links = []
    search_terms = []
    n_days = ''

    with open('inputs.txt') as f:
        for line in f:
            if len(links) == 0:
                links = line.split(': ')[1].split(',')
            elif len(search_terms) == 0:
                search_terms = line.split(': ')[1].split(',')
            elif n_days == '':
                n_days = line.split(': ')[1]
    
    # Strip whitespaces
    for link in links:
        link = link.strip()
    for term in search_terms:
        term = term.strip()

    # Return
    return links, search_terms, n_days

#TODO: trim each link/entry

def search_searxng(query, instance="https://searx.be", num_results=100):
    """
    Perform a search using the SearXNG search engine API.
    
    Args:
        query (str): The search query.
        instance (str): URL of the SearXNG instance (default: searx.be).
        num_results (int): Number of search results to retrieve.

    Returns:
        list: A list of search result titles and links.
    """
    url = f"{instance}/search"
    params = {
        "q": query,         # Your search query
        "format": "json",   # Get results in JSON format
        "count": num_results  # Number of results to fetch
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    
    try:
        # Send a GET request to the SearXNG instance
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses
        
        # Parse the JSON response
        data = response.json()
        results = []

        # Extract and return URLs
        for result in data.get("results", []):
            results.append(result.get("url"))
        
        return results

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return []

