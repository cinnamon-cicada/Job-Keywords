import os
import requests
from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy
from selenium.webdriver.common.proxy import ProxyType
from urllib.parse import urlencode, urljoin
from selenium.webdriver.common.by import By


def format_input(file):
    formatted = []

    with open(file) as f:
        for line in f:
            # More than one input
            if line.count(',') > 0:
                formatted.append(line.split(': ')[1].split(','))
                for item in formatted[-1]:
                    item = item.strip()
            # One input
            else:
                formatted.append(line.split(': ')[1])

    # Return
    return formatted

#TODO: trim each link/entry

def api_search(query, api, engine, num_results=200):
    
    """
    Args:
        query (str): The search query.
        instance (str): URL of the SearXNG instance (default: searx.be).
        num_results (int): Number of search results to retrieve.

    Returns:
        list: A list of search result titles and links.
    """
    num_urls = 0
    links = ""

    url = f"https://www.googleapis.com/customsearch/v1"
    query = urlencode({"q": query})
    
    params = {
        "q": query,         # Your search query
        "format": "json",   # Get results in JSON format
        "count": num_results,  # Number of results to fetch
        "key": api,  # Your API key
        "cx": engine  # Programmable Search Engine ID
    }
    
    try:
        # Send a GET request
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an error for bad responses
        
        # Parse the JSON response
        data = response.json()
        results = []

        # Extract and print results
        for result in data.get("results", []):
            results.append(result.get("url"))
        
        return results

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return []

    

# class="yuRUbf" that has the href to your link.
# jsname="UWckNb" is the <a> element w/ href
# test search: https://www.google.com/search?q=swe+jobs+site%3Aboards.greenhouse.io+-%22jobs%22&sca_esv=32e55b09f5ce6c02&ei=MMdhZ8zqBu3a5NoP8Lj40A0&ved=0ahUKEwjMwvfMu6-KAxVtLVkFHXAcHtoQ4dUDCBA&uact=5&oq=swe+jobs+site%3Aboards.greenhouse.io+-%22jobs%22&gs_lp=Egxnd3Mtd2l6LXNlcnAiKnN3ZSBqb2JzIHNpdGU6Ym9hcmRzLmdyZWVuaG91c2UuaW8gLSJqb2JzIkjyGlDsBFjpGHABeACQAQCYAbMBoAHXBqoBAzUuM7gBA8gBAPgBAZgCAKACAJgDAIgGAZIHAKAH6AI&sclient=gws-wiz-serp