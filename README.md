# Job Keywords Analyzer

## About
As a sophomore studying CS, I've been feeling lost as to what technologies I should focus on. Hence this app: a tool to find the top 20 skills mentioned in any job. Hope it helps all of us find some direction in our lives!

## Setup
1. Install libraries
```
pip install requests
pip install numpy
pip install selenium
```

## Workflow
0. Inputs: search keyword
1. Selenium API: Retrieve ATS postings as links
    1. ATS sites
        1. lever, recruiterbox, greenhouse, success factors
        2. logins: workday, iCIMS, taleo
    2. "Click" each subsequent page
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