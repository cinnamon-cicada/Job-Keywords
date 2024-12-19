from ats_search import *
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import nltk

def run_keyword_analyzer():
    # 1. Get inputs
    user_input = format_input('data/inputs.txt')
    ats_links, search_terms, days, exclusions = user_input[0], user_input[1], user_input[2], user_input[3]

    env_input = format_input('.env')
    api_key, search_engine = env_input[0], env_input[1]

    # Comment out if necessary
    # nltk.download("punkt")
    # nltk.download("wordnet")
    # nltk.download("stopwords")

    # 2. Visit each ATS site
    for link in ats_links:
        # Format query
        exclusion_str = ''
        for ex in exclusions:
            exclusion_str += f'-"{ex}" '

        inclusion_str = '('
        for term in search_terms:
            inclusion_str += f'intext:"{term}" OR '
        inclusion_str = inclusion_str[:-4]

        #TODO: check it's not cut too short
        query = f'site:{link} {exclusion_str} {inclusion_str})'

        # Run query
        job_links = []
        job_links.append(get_search_links(query, api_key, search_engine))
        print("Done.")

    # 3. Visit each result link
    with open('data/links.txt') as file:
        # Put links into an array
        links_arr = []
        for line in file:
            links_arr = line.split(' ')

        # Get unique keywords from each visited page
        keyword_arrays = [set()]
        for link in links_arr:
            keyword_arrays.append(process_html(get_html(link)))

        keywords_per_page = pd.DataFrame()

        # google.com: site:boards.greenhouse.io united states (intext:"Software Developer" OR intext:"Software Engineer")

run_keyword_analyzer()