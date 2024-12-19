import requests
from urllib.parse import urlencode, urljoin
from googleapiclient.discovery import build
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import re


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

def get_search_links(query, api, engine, num_results=200):
    
    """
    Args:
        query (str): The search query.
        instance (str): URL of the SearXNG instance (default: searx.be).
        num_results (int): Number of search results to retrieve.

    Returns:
        list: A list of search result links.
    """
    num_urls = 0
    next_page_start = None
    links = ""

    query = urlencode(query)

    # Create service to call Google Cloud APIs
    service = build(
        "customsearch", "v1", developerKey=api
    )
    
    # Make requested number of API calls
    while num_urls < num_results:
        try:
            result = service.cse().list(
                q=query,
                cx=engine,
                next=next_page_start
            ).execute()

            for res in result.get('items', []):
                num_urls += 1
                links += res['link']
            
            # TODO: delete; block used to minimize API calls during testing
            with open("data/links.txt", "w") as f:
                f.write(links)

            # Get next page of results
            next_page_start = result['queries'].get('nextPage', [{}])[0].get('startIndex', None)

        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            pass

    return links

    # TODO del: test search: https://www.google.com/search?q=swe+jobs+site%3Aboards.greenhouse.io+-%22jobs%22&sca_esv=32e55b09f5ce6c02&ei=MMdhZ8zqBu3a5NoP8Lj40A0&ved=0ahUKEwjMwvfMu6-KAxVtLVkFHXAcHtoQ4dUDCBA&uact=5&oq=swe+jobs+site%3Aboards.greenhouse.io+-%22jobs%22&gs_lp=Egxnd3Mtd2l6LXNlcnAiKnN3ZSBqb2JzIHNpdGU6Ym9hcmRzLmdyZWVuaG91c2UuaW8gLSJqb2JzIkjyGlDsBFjpGHABeACQAQCYAbMBoAHXBqoBAzUuM7gBA8gBAPgBAZgCAKACAJgDAIgGAZIHAKAH6AI&sclient=gws-wiz-serp

def get_html(url, analyze_jobs=True):
    try:
        # Send an HTTP request to the URL
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Check if the request was successful

        # Parse the HTML content
        bouillon = BeautifulSoup(response.text, 'html.parser')
        return bouillon
    
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"

def process_html(html, platform, analyze_jobs=True):
    """
    Extract the skills/qualifications section based on platform-specific patterns.
    html: Returned from BeautifulSoup()'s HTML parser ('html.parser')
    platform: Link to requested platform
    analyze_jobs: Whether or not the user goal is to get job skills keywords
    """
    if analyze_jobs:
        section = extract_skills_section(html, platform)
        
    # Clean skills section
    if section:
        # Remove HTML tags
        section = section.get_text(strip=True, separator="\n")
        section = extract_keywords(section)
    else:
        print("'section' variable was empty.")
        return None
    
    
def extract_skills_section(html, platform):
    try:
        # Get skills section of page
        if "lever" in platform:
            section = html.find("div", class_="section") or html.find("div", class_="posting-requirements")
        elif "trakstar" in platform:
            section = html.find("div", class_="jobdesciption")
        elif "greenhouse" in platform:
            section = html.find_all('li')
        elif "successfactors" in platform:
            section = html.find("div", id="qualifications") or html.find("div", class_="job-qualifications")
        elif "workday" in platform:
            section = html.find_all('li')
        elif "icims" in platform:
            section = html.find("div", id="jobPageBody")
        elif "taleo" in platform:
            section = html.find("div", id="requisitionDescriptionInterface") or html.find("div", class_="requisitionDescription")
        else:
            print(f"Platform '{platform}' not supported.")
            return None
    except Exception as e:
        print(f"Error extracting qualifications for {platform}: {e}")
        return None


def extract_keywords(raw_text): #TODO: may need more filtration if too many keywords result.
    clean_text = re.sub(r"[^a-zA-Z\s]", "", raw_text).lower()
    tokens = word_tokenize(clean_text)
    
    # Remove stopwords
    stop_words = set(stopwords.words("english"))
    filtered_words = [word for word in tokens if word not in stop_words]
    
    # Lemmatize (convert to infinitive/base form)
    lemmatizer = WordNetLemmatizer()
    lemmatized_words = [lemmatizer.lemmatize(word) for word in filtered_words]
    
    # Return only unique keywords
    return set(lemmatized_words)

def make_google_format(inclusions, exclusions):
    exclusion_str = ''
    for ex in exclusions:
        exclusion_str += f'-"{ex}" '

    inclusion_str = '('
    for term in inclusions:
        inclusion_str += f'intext:"{term}" OR '
    inclusion_str = inclusion_str[:-4]
    inclusion_str += ')'

    return exclusion_str + inclusion_str
