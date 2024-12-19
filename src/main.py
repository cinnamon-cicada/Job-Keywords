from ats_search import *
import numpy as np

def run_keyword_analyzer():
    # 1. Search ATS sites
    user_input = format_input('data/inputs.txt')
    ats_links, search_terms, days = user_input[0], user_input[1], user_input[2]

    env_input = format_input('.env')
    api_key, search_engine = env_input[0], env_input[1]

    # Visit each ATS site
    for link in ats_links:
        # Format query
        query = f'!google site:{link} united states -"jobs" -"careers" -"roles" ('
        for term in search_terms:
            query += f'intext:"{term}" OR '
        query = query[:-4] #TODO: check it's not cut too short
        query += ')'

        # Run query
        job_links = []
        job_links.append(api_search(query), api_key, search_engine)
        print("Done.")

    # 2. 
        f

        # google.com: site:boards.greenhouse.io united states (intext:"Software Developer" OR intext:"Software Engineer")

run_keyword_analyzer()