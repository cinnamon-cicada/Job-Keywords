import requests
from urllib.parse import urlencode, urljoin
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import re
import time
# from googleapiclient.discovery import build
import json

def format_input(file):
    """
    Parses an input file and extracts formatted content.

    Args:
        file (str): Path to the input file.

    Returns:
        list: A list containing parsed inputs, each entry representing a line.
    """
    formatted = []

    with open(file) as f:
        for line in f:
            # More than one input
            if line.count(',') > 0:
                formatted.append(line.split(': ')[1].split(','))
                for i in range(len(formatted[-1])):
                    formatted[-1][i] = formatted[-1][i].strip()
            # One input
            else:
                formatted.append(line.split(': ')[1].strip())

    return formatted

def get_search_links(query, api, endpoint = '', num_results=200):
    """
    Retrieves search result links using Google Custom Search API.

    Args:
        query (str): The search query.
        api (str): Google API key.
        endpoint (str): Custom search engine ID.
        num_results (int): Number of search results to retrieve (default: 200).

    Returns:
        str: All retrieved search links as a concatenated string.
    """
    num_urls = 0
    next_page_start = 0
    links = ''
    limit_reached = False

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36', 
        'X-My-Application-ID': 'job-keywords-71', 
        'Referer': 'https://www.google.com',
        'Ocp-Apim-Subscription-Key': api
    }
    endpoint += '/v7.0/search'

    while num_urls < num_results and not limit_reached:
        params = {
                "q": query,
                "count": 50,          # Number of results per request
                "offset": next_page_start,          # Pagination offset
                "mkt": "en-US",       # Market/language
                "responseFilter": "Webpages"
            }

        try:
            result = requests.get(endpoint, headers=headers, params=params)
            for res in result['webPages']['value']:
                num_urls += 1
                links += res['url'] + '\n'
            
            with open("data/links.txt", "a") as f:
                f.write(links)

            next_page_start += min(50, result['webPages']['totalEstimatedMatches'] - next_page_start)
            # No more possible matches
            if next_page_start != 50:
                limit_reached = True

            time.sleep(0.333)

        except:
            print(f"Error occurred during API call.")
            pass

    return links

def get_html(url, analyze_jobs=True):
    """
    Sends a GET request to a URL and parses the response HTML.

    Args:
        url (str): The webpage URL.
        analyze_jobs (bool): Whether the goal is job analysis (default: True).

    Returns:
        BeautifulSoup object or str: Parsed HTML or an error message.
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        return BeautifulSoup(response.text, 'html.parser')
    
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"

def process_html(html, platform, analyze_jobs=True):
    """
    Processes HTML content to extract relevant sections and keywords.

    Args:
        html (BeautifulSoup): Parsed HTML content.
        platform (str): Platform link 
        analyze_jobs (bool): Whether the goal is job keyword extraction.

    Returns:
        set: Extracted keywords, or None if no keywords found.
    """
    if analyze_jobs:
        section = extract_skills_section(html, platform)
        
    if section:
        section = section.get_text(strip=True, separator="\n")
        return extract_keywords(section)
    else:
        print("'section' variable was empty.")
        return None

def extract_skills_section(html, platform):
    """
    Extracts the skills/qualifications section from the HTML.

    Args:
        html (BeautifulSoup): Parsed HTML content.
        platform (str): Job platform name.

    Returns:
        BeautifulSoup element or None: Extracted section, if found.
    """
    try:
        if "lever" in platform:
            return html.find("div", class_="section") or html.find("div", class_="posting-requirements")
        elif "trakstar" in platform:
            return html.find("div", class_="jobdesciption")
        elif "greenhouse" in platform:
            return html.find_all('li')
        elif "successfactors" in platform:
            return html.find("div", id="qualifications") or html.find("div", class_="job-qualifications")
        elif "workday" in platform:
            return html.find_all('li')
        elif "icims" in platform:
            return html.find("div", id="jobPageBody")
        elif "taleo" in platform:
            return html.find("div", id="requisitionDescriptionInterface") or html.find("div", class_="requisitionDescription")
        else:
            print(f"Platform '{platform}' not supported.")
            return None
    except Exception as e:
        print(f"Error extracting qualifications for {platform}: {e}")
        return None

def extract_keywords(raw_text):
    """
    Extracts unique keywords from raw text by lemmatizing and removing stopwords.

    Args:
        raw_text (str): Text to process.

    Returns:
        set: A set of unique keywords.
    """
    clean_text = re.sub(r"[^a-zA-Z\s]", "", raw_text).lower()
    tokens = word_tokenize(clean_text)

    stop_words = set(stopwords.words("english"))
    filtered_words = [word for word in tokens if word not in stop_words]

    lemmatizer = WordNetLemmatizer()
    lemmatized_words = [lemmatizer.lemmatize(word) for word in filtered_words]

    return set(lemmatized_words)

def make_google_format(search_terms, exclusions, inclusions):
    """
    Creates a formatted Google search query with inclusions and exclusions.

    Args:
        search_terms (list): List of keywords to search (mutual OR relationship).
        exclusions (list): List of excluded keywords.
        inclusions (list): List of required keywords.

    Returns:
        str: Formatted search query string.
    """
    if type(exclusions) is list:
        exclusion_str = ''.join(f'-"{ex}" ' for ex in exclusions)
    else:
        exclusion_str = f'-"{exclusions}"'

    if type(inclusions) is list:
        inclusion_str = ' '.join(inclusions)
    else:
        inclusion_str = inclusions

    search_term_str = '("' + '" OR "'.join(f'contains:{term}' for term in search_terms) + '")'
    # search_term_str = ' '.join(search_terms)
    search_term_str += ' responseFilter=Webpages'

    return ' '.join([exclusion_str, inclusion_str, search_term_str])

# site:job-boards.greenhouse.io ("swe" OR "software")  -"careers" -"roles" -jobs responseFilter=Webpages