from ats_search import *
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import os
from googleapiclient.discovery import build
import pandas as pd
from sentence_transformers import SentenceTransformer, util # pip install -U sentence-transformers
import nltk

# API-independent functions
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
            if line[0] != '#':
                # More than one input
                if line.count(',') > 0:
                    formatted.append(line.split(': ')[1].split(','))
                    for i in range(len(formatted[-1])):
                        formatted[-1][i] = formatted[-1][i].strip()
                # One input
                else:
                    formatted.append(line.split(': ')[1].strip())

    return formatted

# Filter words only for those related to topic_words
# NOTE: wn similarity functions return !=0 ONLY for solid IS-A relationships

'''Alternative ideas:
- Exclude keywords found in non-CS job descriptions + TF-IDF
- word embedding library/methods -- what's so different between that and the below??

'''
def filter_keywords(df, df_compare, n=5, topic_words = ['coding', 'programming language', 'computer science', 'software', 'hardware', 'agile'], sim_threshold=0.4):
    df[df.columns[1]] = df[df.columns[1]].astype(int)
    keywords = df[df.n > n].iloc[:, 0] # Remove uncommon words

    # Get keywords to compare to + exclude
    e = './data/analysis_cmp.csv'
    if(not(os.path.exists(e))):
        a = './data/inputs_cmp.txt'
        b = './.env'
        c = './data/links_cmp.txt'
        d = './data/keywords_cmp.csv'
        run_keyword_analyzer(a, b, c, d, e, 0)
    exclude_keywords = pd.read_csv(e)['word']     # First column holds keywords; Second column holds counts
    print(len(exclude_keywords), ' ', len(exclude_keywords.unique()), '; ', len(keywords), ' ', len(keywords.unique())) # TODO: remove. Series + set length should be equal
    exclude_keywords = set(exclude_keywords.unique())
    keywords = set(keywords.unique())

    # Exclude non-target keywords
    # TODO: try tf-idf
    kept_keywords = keywords - exclude_keywords
    df = df[df.word.isin(kept_keywords)]
    df.sort_values(by='n', ascending=False)

    # Sort by descending similarity
    return df

def archive_links(links_to_visit, archived_links):
    """
    Appends all contents from links_to_visit.txt to archived_links.txt
    """
    try:
        with open(links_to_visit, 'r') as source:
            with open(archived_links, 'a') as target:
                target.write(source.read())
        os.remove(links_to_visit)
    except FileNotFoundError:
        with open(links_to_visit, 'r') as source:
            with open(archived_links, 'w') as target:
                target.write(source.read())
        os.remove(links_to_visit)
    except Exception as e:
        print(f"An error occurred while archiving links: {e}")

# Filter links to exclude non-job descriptions
# n: number of links scraped this session
def filter_links(links, n):
    patterns = [
            r'https://jobs\.lever\.co/[^/]+/\d+',
            r'https://boards\.greenhouse\.io/[^/]+/jobs/\d+',
            r'https://[^/]+\.icims\.com/jobs/\d+',
            r'https://[^/]+\.taleo\.net/careersection/[^/]+/jobdetail\.ftl\?job=\d+',
            r'https://[^/]+\.myworkdayjobs\.com/[^/]+/job/[^/]+/[^_]+_[a-zA-Z0-9]+',
            r'https://career\d+\.successfactors\.eu/career\?company=[^&]+&.*?jobId=\d+',
            r'https://[^/]+\.recruiterbox\.com/(apply|jobs)/\d+'
        ]
    for link in links:
        return any(re.match(pattern, link) for pattern in patterns)

# Define main analyzer method
def run_keyword_analyzer(api_input = './data/inputs.txt', env_input = './.env', links_to_visit = './data/links.txt', keywords_out = './data/keywords.csv', analysis_out = './data/analysis.csv', num_links=10): 
    # 1. Get inputs
    user_input = format_input(api_input)
    ats_links, search_terms, days, exclusions, inclusions = user_input[0], user_input[1], user_input[2], user_input[3], user_input[4]

    if type(ats_links) is not list:
        ats_links = [ats_links]

    env_input = format_input(env_input)
    api_key, search_engine, engine_id = env_input[0], env_input[1], env_input[2]
    api = search_wrapper(search_engine) #TODO: search wrapper not defined... prob due to circular dependencies

    # Format criteria portion of query
    criteria = api.make_api_format(search_terms, exclusions, inclusions)
    criteria = "(site:" + " OR site:".join(ats_links) + ") AND (" + criteria + ")"

    # Comment out if necessary
    # nltk.download("punkt")
    # nltk.download("wordnet")
    # nltk.download("stopwords")
    # nltk.download('averaged_perceptron_tagger_eng')

    # 2. Visit each ATS site
    if(not(os.path.exists(links_to_visit))):
        api.get_search_links(criteria, api_key, links_to_visit, search_engine, engine_id, num_links)
    else:
        archive_file = "archived_links_cmp.txt" if "cmp" in links_to_visit else "archived_links.txt"
        archive_links(links_to_visit, archive_file)
        api.get_search_links(criteria, api_key, links_to_visit, search_engine, engine_id, num_links)

    # 3. Visit each result link
    with open(links_to_visit) as file:
        # Record number of links
        n_links = 0
        # Put links into an array
        links_arr = []
        for line in file:
            links_arr.append(line.strip())
            n_links += 1

    # Get unique keywords from each visited page
    keywords_csv = keywords_out
    if(not(os.path.exists(keywords_csv))):
        keyword_arrays = []
        for link in links_arr:
            keyword_arrays.append(api.process_html(api.get_html(link), platform=link))

        keywords_per_page = pd.DataFrame(keyword_arrays)
        keywords_per_page.to_csv(keywords_csv) #TODO: delete; keywords saved to avoid excess scraping
    else:
        keyword_df = pd.read_csv(keywords_csv)
        new_keywords = []
        for link in links_arr:
            new_keywords.append(api.process_html(api.get_html(link), platform=link))

        new_keywords = pd.DataFrame(new_keywords)
        keywords_per_page = pd.concat([keyword_df, new_keywords], ignore_index=True, axis=0)
        keywords_per_page.to_csv(keywords_csv)

    # Run keyword analysis on ALL webpages scraped thus far.
    # Get keyword count
    keywords_per_page = pd.read_csv(keywords_csv)
    keywords_df = pd.Series(keywords_per_page.values.ravel()).value_counts()
    keywords_df = pd.DataFrame({'word': keywords_df.index, 'n': keywords_df.values})
    if not 'cmp' in api_input:
        keywords_df = filter_keywords(keywords_df, n_links/5)
    keywords_df.to_csv(analysis_out) 