# DOS Applications

Project to parse the DOS applications to identify specific technologies and skills 
used by previous case studies.

### Requirements
- Python3
- Digital marketplace login
- Azure text analysis service

### Quickstart
Insert the url and key for your text analysis service into `conf.json`.

To install the required python dependencies:\
`python -m pip install -r requirements.txt`

To run the scripts:\
`python run.py`

This will do the following:
- Prompt you to login
- Scrape applications and answers from the DOS site
- Request analysis on each answer through the text analysis service
- Write analysis results to a csv `results.csv`
- Write the applications and answers to an excel sheet `DOSExport.xlsx`

You can run `python scraper.py` alone to just login, scrape and write to excel.

