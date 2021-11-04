from extraction import extract
from scraper import Scraper
from analyzer import Analyzer


def main():
    # Initialise
    scraper = Scraper()

    # Scrape
    scraper.go()

    # Access data
    # scraper.applications
    # This is a dictionary with the following format
    # {
    #   'application_name': {
    #       'question': 'answer',
    #       'question1': 'answer1'
    #   },
    #   'application_name1': {
    #       'question': 'answer',
    #       'question1': 'answer1'
    #   }
    # }

    question_list = []
    for app, questions in scraper.applications.items():
        for question, answer in questions.items():
            question_list.append(answer)

    analyzer = Analyzer()
    analyzer.analyze(question_list)

    # Access results of analyzer in analyzer.result (Dict with property called 'documents')
    extract(analyzer.result["documents"])

    # Create excel doc
    scraper.write_to_excel()


if __name__ == "__main__":
    main()

