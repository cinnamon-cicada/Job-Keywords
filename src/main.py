from ats_search import *
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import nltk

def run_keyword_analyzer(): 
    # 1. Get inputs
    user_input = format_input('data/inputs.txt')
    ats_links, search_terms, days, exclusions, inclusions = user_input[0], user_input[1], user_input[2], user_input[3], user_input[4]

    if type(ats_links) is not list:
        ats_links = [ats_links]

    env_input = format_input('.env')
    api_key, search_engine, engine_id = env_input[0], env_input[1], env_input[2]
    api = search_wrapper(search_engine)

    # Format criteria portion of query
    criteria = api.make_api_format(search_terms, exclusions, inclusions)

    # Comment out if necessary
    # nltk.download("punkt")
    nltk.download("wordnet")
    # nltk.download("stopwords")

    # # 2. Visit each ATS site
    # for link in ats_links:
    #     #TODO: check it's not cut too short
    #     query = 'site:' + link + ' ' + criteria
        
    #     # Run query
    #     api.get_search_links(query, api_key, search_engine, engine_id, 10)
    #     print("Done.")

    # 3. Visit each result link
    with open('data/links.txt') as file:
        # Put links into an array
        links_arr = []
        for line in file:
            links_arr = line.split('\n')

        # Get unique keywords from each visited page
        keyword_arrays = [set()]
        for link in links_arr:
            keyword_arrays.append(api.process_html(api.get_html(link), platform=link))

        keywords_per_page = pd.DataFrame(keyword_arrays)
        keywords_per_page.to_csv('data/keywords.csv') #TODO: delete; keywords saved to avoid excess scraping

        # Get keyword count
        keywords_df = pd.Series(keywords_per_page.values.ravel()).value_counts()
        keywords_df.to_csv('data/analysis.csv') 


# Call analyzing method
run_keyword_analyzer()