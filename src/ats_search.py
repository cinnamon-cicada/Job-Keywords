import requests
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
import re
import time
from googleapiclient.discovery import build
from sentence_transformers import SentenceTransformer, util # pip install -U sentence-transformers
from nltk.stem import WordNetLemmatizer as wnLemmatizer
from selenium import webdriver
from selenium.webdriver.common.by import By


## API-dependent functions
# Return correct search object for respective engine
def search_wrapper(engine):
    if 'bing' in engine:
        return bing_search()
    else: 
        return google_search()

## Google API-dependent functions
class google_search():
    def __init__(self):
        pass

    def get_search_links(self, query, api, target_file, engine = '', engine_id = '', num_results=200):
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

        service = build(
            "customsearch", "v1", developerKey=api
        )

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36', 
            'X-My-Application-ID': 'job-keywords-71', 
            'Referer': 'https://www.google.com'
        } #TODO: may be unnecessary
        
        while num_urls < num_results:
            links = []
            try:
                result = service.cse().list(
                    q=query,
                    cx=engine_id,
                    start=next_page_start
                ).execute()

                if(result['searchInformation']['totalResults'] == '0'):
                    print("Not enough results")
                    with open("data/links.txt", "a") as f: # Add line, not overwrite
                        f.write("Not enough results after " + str(num_urls) + " links")
                    break
                
                for res in result.get('items', []):
                    num_urls += 1
                    links.append(res['link'])
                
                links = '\n'.join(filter_links(links))
                
                with open(target_file, "w") as f: # Create fresh links file for each run
                    f.write(links)

                next_page_start = result['queries'].get('nextPage', [{}])[0].get('startIndex', None)

            except requests.exceptions.RequestException as e:
                print(f"Error: {e}")
                pass

        return links

    def get_html(self, url, analyze_jobs=True): #TODO: not linking?
        """
        Sends a GET request to a URL and parses the response HTML.

        Args:
            url (str): The webpage URL.
            analyze_jobs (bool): Whether the goal is job analysis (default: True).

        Returns:
            BeautifulSoup object or str: Parsed HTML or an error message.
        """
        try:
            soupArray = [] # Array to store HTML of each visited job listing
            
            # Set up scraper
            driver = webdriver.Chrome() 
            driver.get(url)

            # Find all <a> elements with an href attribute
            a_tags = driver.find_elements(By.XPATH, "//a[@href]")

            for a_tag in a_tags:
                link_text = a_tag.text
                link_url = a_tag.get_attribute('href')

                # Your condition here (replace with your logic)
                if similar(link_text, ):  # Example: if link_text is not empty
                    print(f"Clicking: {link_text} ({link_url})")
                    a_tag.click()
                    time.sleep(2)  # Wait for the page to load or for any JS to execute

                    # Optionally, go back to the original page to continue with the next link
                    driver.back()
                    time.sleep(1)

                    # Re-find all <a> elements after navigating back, as the DOM may have changed
                    a_tags = driver.find_elements(By.XPATH, "//a[@href]")

            # Close the browser when done
            driver.quit()

            # response is a requests.models.Response object
            soupArray.append(BeautifulSoup(response.text, 'html.parser'))


            return soupArray
        
        except requests.exceptions.RequestException as e:
            return f"An error occurred: {e}"

    def process_html(self, html, platform, analyze_jobs=True):
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
            section = self.extract_skills_section(html, platform)
            
        if section:
            section_as_str = ''
            if isinstance(section, list):
                for str in section:
                    section_as_str += str.contents[0].text + ' '
            else:
                section_as_str = section.contents[0].text
            return self.extract_keywords(section_as_str)
        else:
            print("Input HTML section was empty for " + platform)
            return [' ']

    def extract_skills_section(self, html, platform):
        """
        Extracts the skills/qualifications section from the HTML.

        Args:
            html (BeautifulSoup): Parsed HTML content.
            platform (str): Job platform name.

        Returns:
            BeautifulSoup element or None: Extracted section, if found.
        """
        keywords = ['qualification', 'requirement', 'skill', 'what we look for', "work on", "working on"]
        try:
            if "lever" in platform:
                return html.find("div", class_="section") or html.find("div", class_="posting-requirements")
            elif "trakstar" in platform:
                return html.find("div", class_="jobdesciption")
            elif "greenhouse" in platform:
                initial_find = html.find_all('ul')
                matches = [ul for ul in initial_find if ul.find_previous_sibling(string=lambda t: any(keyword.lower() in t.lower() if t else False for keyword in keywords))]
                # Extract all <li> elements from matched <ul>s
                #TODO: potential error: links were dead. new ones fetched
                all_lis = []
                for ul in matches:
                    all_lis.extend(ul.find_all('li'))
                return all_lis
            elif "successfactors" in platform:
                return html.find("div", id="qualifications") or html.find("div", class_="job-qualifications")
            elif "workday" in platform:
                initial_find = html.find_all('ul')
                matches = [ul for ul in initial_find if ul.find_previous_sibling(text=lambda t: any(keyword.lower() in t.lower() if t else False for keyword in keywords))]
                # Extract all <li> elements from matched <ul>s
                all_lis = []
                for ul in matches:
                    all_lis.extend(ul.find_all('li'))
                return all_lis
            elif "icims" in platform:
                return html.find("div", id="jobPageBody")
            elif "taleo" in platform:
                return html.find("div", id="requisitionDescriptionInterface") or html.find("div", class_="requisitionDescription")
            else:
                print(f"Platform '{platform}' not supported.") # Hardcoded skills section identifier may also not exist
                return None
        except Exception as e:
            print(f"Error extracting qualifications for {platform}: {e}")
            return None

    def extract_keywords(self, raw_text):
        """
        Extracts unique keywords from raw text by lemmatizing and removing stopwords.

        Args:
            raw_text (str): Text to process.

        Returns:
            set: A set of unique keywords.
        """
        clean_text = re.sub(r"[^a-zA-Z\s]", "", raw_text).lower()
        tokens = pos_tag(word_tokenize(clean_text))

        # Remove stop words
        stop_words = set(stopwords.words("english"))
        filtered_words = [pair for pair in tokens if pair[0] not in stop_words]

        # Lemmatize
        lemmatizer = wnLemmatizer()
        def apply_tag(word, tag):
            wntag = tag[0].lower()
            wntag = wntag if wntag in ['a', 'r', 'n', 'v'] else None
            if not wntag:
                lemma = word
            elif wntag == 'a': # Remove adjectives
                lemma = ''
            else:
                lemma = lemmatizer.lemmatize(word, wntag)
            return lemma
        lemmatized_words = [apply_tag(word, tag) for word, tag in filtered_words]
        lemmatized_words = set(lemmatized_words)
        lemmatized_words.discard('')
        lemmatized_words.discard(' ')
        
        return lemmatized_words

    def make_api_format(self, search_terms, exclusions, inclusions):
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

        search_term_str = '("' + '" OR "'.join(f'{term}' for term in search_terms) + '")'

        return ' '.join([exclusion_str, inclusion_str, search_term_str])

## Bing API-dependent functions
class bing_search():
    def __init__(self):
        pass

    def get_search_links(self, query, api, target_file, endpoint = '', engine_id = '', num_results=200):
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
        limit_reached = False
        query = urlencode(query)

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36', 
            'X-My-Application-ID': 'job-keywords-71', 
            'Referer': 'https://www.google.com',
            'Ocp-Apim-Subscription-Key': api
        }
        endpoint += '/v7.0/search'

        while num_urls < num_results and not limit_reached:
            links = []
            params = {
                    "q": query,
                    "count": min(50, num_results - num_urls),          # Number of results per request
                    "offset": next_page_start,          # Pagination offset
                    "mkt": "en-US",       # Market/language
                    "responseFilter": "Webpages"
                }

            try:
                result = requests.get(endpoint, headers=headers, params=params)
                for res in result['webPages']['value']:
                    num_urls += 1
                    links = links.append(res['url'])
                
                links = '\n'.join(filter_links(links))

                with open(target_file, "a") as f:
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

    def get_html(self, url, analyze_jobs=True):
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

    def extract_skills_section(self, html, platform):
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
                keywords = ['qualifications', 'requirements', 'skills', 'what we look for']
                initial_find = html.find_all('ul')
                matches = [ul for ul in initial_find if ul.find_previous_sibling(text=lambda t: any(keyword.lower() in t.lower() if t else False for keyword in keywords))]
                # Extract all li elements from matched uls
                all_lis = []
                for ul in matches:
                    all_lis.extend(ul.find_all('li'))
                return all_lis if all_lis else html.find_all('li')
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
                return ''
        except Exception as e:
            print(f"Error extracting qualifications for {platform}: {e}")
            return ''

    def extract_keywords(self, raw_text):
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

        lemmatizer = wnLemmatizer()
        lemmatized_words = [lemmatizer.lemmatize(word) for word in filtered_words]

        return set(lemmatized_words)

    def make_api_format(self, search_terms, exclusions, inclusions):
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

    def process_html(self, html, platform, analyze_jobs=True):
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
            section = self.extract_skills_section(html, platform)
            
        if section:
            section = section.get_text(strip=True, separator="\n")
            return self.extract_keywords(section)
        else:
            print("'section' variable was empty.")
            return None
    # site:job-boards.greenhouse.io ("swe" OR "software")  -"careers" -"roles" -jobs responseFilter=Webpages

## Classes for Platform-Specific Functions
from bs4 import BeautifulSoup

class LeverPlatform:
    @staticmethod
    def extract_skills_section(html: BeautifulSoup):
        return html.find("div", class_="section") or html.find("div", class_="posting-requirements")

class TrakstarPlatform:
    @staticmethod
    def extract_skills_section(html: BeautifulSoup):
        return html.find("div", class_="jobdesciption")

class GreenhousePlatform:
    @staticmethod
    def extract_skills_section(html: BeautifulSoup):
        keywords = ['qualification', 'requirement', 'skill', 'what we look for', "work on", "working on"]
        initial_find = html.find_all('ul')
        matches = [ul for ul in initial_find if ul.find_previous_sibling(string=lambda t: any(keyword.lower() in t.lower() if t else False for keyword in keywords))]
        all_lis = []
        for ul in matches:
            all_lis.extend(ul.find_all('li'))
        return all_lis

class SuccessfactorsPlatform:
    @staticmethod
    def extract_skills_section(html: BeautifulSoup):
        return html.find("div", id="qualifications") or html.find("div", class_="job-qualifications")

class WorkdayPlatform:
    @staticmethod
    def extract_skills_section(html: BeautifulSoup):
        keywords = ['qualification', 'requirement', 'skill', 'what we look for', "work on", "working on"]
        initial_find = html.find_all('ul')
        matches = [ul for ul in initial_find if ul.find_previous_sibling(text=lambda t: any(keyword.lower() in t.lower() if t else False for keyword in keywords))]
        all_lis = []
        for ul in matches:
            all_lis.extend(ul.find_all('li'))
        return all_lis

class IcimsPlatform:
    @staticmethod
    def extract_skills_section(html: BeautifulSoup):
        return html.find("div", id="jobPageBody")

class TaleoPlatform:
    @staticmethod
    def extract_skills_section(html: BeautifulSoup):
        return html.find("div", id="requisitionDescriptionInterface") or html.find("div", class_="requisitionDescription") 

## Helpers

# Wrapper method to allow uniform functionality across different platforms
def platformWrapper(link):
    PLATFORM_CLASSES = {
        "lever": LeverPlatform,
        "trakstar": TrakstarPlatform,
        "greenhouse": GreenhousePlatform,
        "successfactors": SuccessfactorsPlatform,
        "workday": WorkdayPlatform,
        "icims": IcimsPlatform,
        "taleo": TaleoPlatform,
    }

    link_lower = link.lower()
    for key, cls in PLATFORM_CLASSES.items():
        if key in link_lower:
            return cls()  # Return an instance of the matched class
    return None

# Filter links to exclude non-job descriptions
# n: number of links scraped this session
# @return array of links (str)
def filter_links(links):
    patterns = [
            r'https://jobs\.lever\.co/[^/]+/\d+',
            r'https://boards\.greenhouse\.io/[^/]+/jobs/\d+',
            r'https://[^/]+\.icims\.com/jobs/\d+',
            r'https://[^/]+\.taleo\.net/careersection/[^/]+/jobdetail\.ftl\?job=\d+',
            r'https://[^/]+\.myworkdayjobs\.com/[^/]+/job/[^/]+/[^_]+_[a-zA-Z0-9]+',
            r'https://career\d+\.successfactors\.eu/career\?company=[^&]+&.*?jobId=\d+',
            r'https://[^/]+\.recruiterbox\.com/(apply|jobs)/\d+'
        ]
    valid_links = []

    for link in links:
        if any(re.match(pattern, link) for pattern in patterns):
            valid_links.append(link)
    return valid_links