import json, csv, re

def extract(documents):
    with open('tech_terms.txt', 'r') as f:
        tech_terms = [x for x in f.read().strip().split(',')]
    with open('non_tech_terms.txt', 'r') as f:
        non_tech_terms = [x for x in f.read().strip().split(',')]

    results = []
    for doc in documents:
        categories = {}
        for item in doc["entities"]:
            # Dont include netcompany
            if item['text'].lower() != 'netcompany':
                category = item['category']
                # Move technologies from organisation to skill
                if category == 'Organization':
                    for term in tech_terms:
                        if term in item['text'].lower():
                            category = 'Skill'
                            break
                if category == 'Skill' or category == 'Product':
                    non_tech = False
                    for term in non_tech_terms:
                        if term == item['text'].lower():
                            non_tech = True
                            break
                    if non_tech:
                        continue
                categories[category] = categories.setdefault(category, set())
                categories[category].add(item['text'])
        results.append(categories)

    grouped_results = {}
    date_regex = ['\d{4}', 'last \d years']
    header = ['Client','Year','Skill']
    with open('results.csv', 'w',encoding='utf-8',newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header) 
        for doc in sorted(results, key=lambda x: ''.join(x.setdefault('Organization', ''))):
            orgs = ' | '.join(doc.setdefault('Organization', ''))
            #find the 4 digits for the year and place them in a list
            dates = []
            for datetime in doc.setdefault('DateTime',[]):
                for regex in date_regex:
                    dates += re.findall(regex, datetime)
            #joined skills and product together and if they are empty an empyt list is used
            skills = (doc.setdefault('Skill', set()) | doc.setdefault('Product', set()))
            for skill in skills:
                # pipes to delimit list of values
                row = [orgs, ' | '.join(dates), skill]
                writer.writerow(row)

            # populate object with results grouped by orgs
            grouped_results[orgs] = grouped_results.setdefault(orgs, { 'dates': [], 'skills': [] })
            grouped_results[orgs]['skills'] += skills
            grouped_results[orgs]['dates'] += dates

    with open('grouped_results.csv', 'w',encoding='utf-8',newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header) 
        for org, val in grouped_results.items():
            skills = ' | '.join(set(val.setdefault('skills', [])))
            dates = ' | '.join(set(val.setdefault('dates', [])))
            writer.writerow([org, dates, skills])

    print('\nWritten analyser results.')

