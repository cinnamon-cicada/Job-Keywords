# (Search) Keyword Analyzer

## About
There are a hundred different platforms out there, and a thousand different technologies. As an aspiring SWE, I have to ask: where do I begin? Where do any of us? Hence this app: a tool to find the top 20 skills mentioned in any job. 

## Setup
1. Install libraries
```
pip install requests
pip install numpy
pip install pandas
pip install google-api-python-client
pip install beautifulsoup4
pip install nltk
```
2. Get a Google Cloud Console project API key 

## Workflow
0. Inputs: search keyword, API key
1. Google Search Engine API: get first 
    1. ATS sites
        1. lever, recruiterbox, greenhouse, success factors
        2. with logins: workday.wd5.myworkdayjobs.com, icims.com, taleo.net
2. Open URLs -> Get HTML
    1. BeautifulSoup?
3. Clean HTML (More BeautifulSoup?)
    1. Remove HTML formatting
    2. Remove duplicates (>99% similarity)
4. Extract keywords
    1. Extract **skills**
    2. Make unique per job posting
5. Find most common keywords
    1. Go through all words, keeping track of each unique word?
    2. Or: compile everything, sort alphabetically by word, search for longest repeated sequence.

## File Structure
JobKeywords/
├── src/
│   ├──main.py: File to run.
│   ├──ats_search.py
│   ├──get_keywords.py: Retrieve URL's HTML code, clean it, and extract keywords
│   ├──analysis.py
├── data/
│   ├──inputs.txt
│   ├──ats_results.txt: All searched links
│   ├──keywords.txt
│   ├──analysis.csv: Top 20 skill keywords, with count (% of job postings in which it appeared)


## Technology
- Python
- Google Programmable Search Engine API

## Extension Ideas
- Specify search time window
- Automated daily run of project -> Track keywords over time