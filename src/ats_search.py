import requests
from urllib.parse import urlencode, urljoin
from googleapiclient.discovery import build
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import re

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
                formatted.append(line.split(': ')[1])

    return formatted

def get_search_links(query, api, engine, num_results=200):
    """
    Retrieves search result links using Google Custom Search API.

    Args:
        query (str): The search query.
        api (str): Google API key.
        engine (str): Custom search engine ID.
        num_results (int): Number of search results to retrieve (default: 200).

    Returns:
        str: All retrieved search links as a concatenated string.
    """
    num_urls = 0
    next_page_start = 1
    links = ""

    service = build(
        "customsearch", "v1", developerKey=api
    )
    
    while num_urls < num_results:
        try:
            result = service.cse().list(
                q=query,
                cx=engine,
                start=next_page_start
            ).execute(http=requests.Session().get)

            for res in result.get('items', []):
                num_urls += 1
                links += res['link']
            
            with open("data/links.txt", "a") as f:
                f.write(links)

            next_page_start = result['queries'].get('nextPage', [{}])[0].get('startIndex', None)

        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
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

def make_google_format(inclusions, exclusions):
    """
    Creates a formatted Google search query with inclusions and exclusions.

    Args:
        inclusions (list): List of required keywords.
        exclusions (list): List of excluded keywords.

    Returns:
        str: Formatted search query string.
    """
    exclusion_str = ''.join(f'-"{ex}" ' for ex in exclusions)

    inclusion_str = '(' + ' OR '.join(f'intext:"{term}"' for term in inclusions) + ')'

    return exclusion_str + inclusion_str