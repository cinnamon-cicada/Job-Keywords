from ats_search import *
import numpy as np

# 1. Search ATS sites
ats_links, search_terms, days = format_input()

# Visit each ATS site
for link in ats_links:
    # Format query
    query = f'!google site:{link} united states ('
    for term in search_terms:
        query += f'intext:"{term}" OR '
    query = query[:-4] #TODO: check it's not cut too short
    query += ')'
    

    # Run query
    job_links = []
    job_links.append(search_searxng(query))
    print("Done.")
# 2. 


    # !google site:boards.greenhouse.io united states (intext:"Software Developer" OR intext:"Software Engineer")
