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

    # Format criteria portion of query
    criteria = make_google_format(search_terms, exclusions)

    # Comment out if necessary
    # nltk.download("punkt")
    # nltk.download("wordnet")
    # nltk.download("stopwords")

    # 2. Visit each ATS site
    for link in ats_links:
        #TODO: check it's not cut too short
        query = f'site:{link} {criteria})'
        
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

        keywords_per_page = pd.DataFrame(keyword_arrays)
        keywords_per_page.to_csv('data/keywords.csv') #TODO: delete; keywords saved to avoid excess scraping

        # Get keyword count
        keywords_df = pd.Series(keywords_per_page.values.ravel()).value_counts()
        keywords_df.to_csv('data/analysis.csv') 


# Call analyzing method
run_keyword_analyzer()