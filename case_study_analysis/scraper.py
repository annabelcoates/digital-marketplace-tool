from xlsxwriter import Workbook
from twill.commands import *
from twill.errors import TwillAssertionError
from lxml import html

class Scraper:
    def __init__(self):
        self.url = 'https://www.digitalmarketplace.service.gov.uk/suppliers/opportunities/frameworks/digital-outcomes-and-specialists-5/'
        #self.url = getinput('Need a ride? Where do you want to go? ')
        #print('Climb in back and we\'ll be off.')
        self.username = getinput('\nUsername: ')
        self.password = getpassword('Password: ')
        self.applications = {}

    def go(self):
        redirect_output('log.txt')
        go(self.url)
        sleep()

        # Will be redirected to login then forwarded to correct page
        formvalue(1, 'email_address', self.username)
        formvalue(1, 'password', self.password)
        submit()

        reset_output()
        try:
            code(200)
            print('\nLogin Successful.')
        except TwillAssertionError:
            print('\nLogin Failed.')
            exit(1)

        # Get links for completed responses
        redirect_output('log.txt')
        elements = html.fromstring(show()).xpath('(//tbody)[2]/tr/td/a')
        reset_output()
        print('\nChecking ' + str(len(elements)) + ' applications each one will take a second...')
        redirect_output('log.txt')
        for element in elements:
            title = element.text_content()
            link = element.get('href')

            # To be less intrusive
            sleep()
            # Collect questions from application
            go('https://www.digitalmarketplace.service.gov.uk' + link)

            self.applications[title] = {}
            rows = html.fromstring(show()).xpath('//tbody/tr')
            for row in rows:
                cells = row.xpath('td')
                self.applications[title][cells[0].text_content()] = cells[1].text_content()

        reset_output()
        print('\nScraped data.')

    def write_to_excel(self):
        # Create excel doc
        workbook = Workbook('DOSExport.xlsx')
        worksheet = workbook.add_worksheet()

        _format = workbook.add_format({'text_wrap': True})
        worksheet.set_default_row(100)
        worksheet.set_column(0, 0, 30, _format)
        worksheet.set_column(1, 1, 60, _format)
        worksheet.set_column(2, 2, 150, _format)

        row = 0
        for name, questions in self.applications.items():
            for q, a in questions.items():
                worksheet.write(row, 0, name)
                worksheet.write(row, 1, q)
                worksheet.write(row, 2, a)
                row += 1
            # Add a gap between applications
            row += 1

        workbook.close()
        print('Written excel sheet.')

if __name__ == "__main__":
    scraper = Scraper()
    scraper.go()
    scraper.write_to_excel()

