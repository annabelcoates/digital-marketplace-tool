from xlsxwriter import Workbook
from twill.commands import *
from twill.errors import TwillAssertionError
from lxml import html
import tkinter as tk
from tkinter import messagebox
import os



class App(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack(padx=5, pady=5)
        self.create_widgets()
        self.links = []
        redirect_output(os.devnull)

    def create_widgets(self):
        top = tk.Frame(self)
        tk.Label(top, text='URL: ').pack(side=tk.LEFT)
        self.url_entry = tk.Entry(top, width=100)
        self.url_entry.pack(side=tk.LEFT, padx=5)
        self.url_entry.focus()
        tk.Button(top, text='Go', command=self.go).pack(side=tk.RIGHT)
        top.pack(side=tk.TOP)

        self.list_frame = tk.Frame(self)

        bottom = tk.Frame(self)
        tk.Button(bottom, text="View", command=self.view_chosen).grid(row=0, column=0)
        tk.Button(bottom, text="Save", command=self.write_to_excel).grid(row=0, column=1, padx=5)
        tk.Button(bottom, text="Close", command=self.master.destroy).grid(row=0, column=2)
        bottom.pack(side=tk.BOTTOM)

    def go(self):
        url = self.url_entry.get()
        if (not url.startswith('https://www.digitalmarketplace.service.gov.uk/digital-outcomes-and-specialists/opportunities')):
            messagebox.showinfo(message='Your URL sucks!')
        else:
            self.list_frame.destroy()
            self.list_frame = tk.Frame(self)

            go(url)

            elements = html.fromstring(show()).xpath("//div[@id='js-dm-live-search-results']/ul/li/h2/a")
            for i, element in enumerate(elements):
                tk.Button(self.list_frame, text='Add', command=lambda e = element: self.add_chosen(e)).grid(column=0, row=i)
                tk.Label(self.list_frame, text=element.text_content()).grid(column=1, row=i, sticky='W')
            self.list_frame.pack(side=tk.TOP, pady=5)

    def add_chosen(self, element):
        self.links.append((element.text_content(), element.get('href')))

    def remove_chosen(self, index):
        del self.links[index]
        self.view_chosen()

    def view_chosen(self):
        self.list_frame.destroy()
        self.list_frame = tk.Frame(self)
        for i, link in enumerate(self.links):
            tk.Button(self.list_frame, text='Remove', command=lambda i=i: self.remove_chosen(i)).grid(column=0, row=i)
            tk.Label(self.list_frame, text=link[0]).grid(column=1, row=i, sticky='W')
        self.list_frame.pack(side=tk.TOP, pady=5)

    def write_to_excel(self):
        filepath = 'DOSExport.xlsx'
        workbook = Workbook(filepath)
        worksheet = workbook.add_worksheet()

#       worksheet.set_column(0, 0, 30)
#       worksheet.set_column(1, 1, 60)
        _format = workbook.add_format({'bold': True, 'bottom': 1})

        headers = [
            'Title',
            'Link',
            'Published',
            'Deadline for asking questions',
            'Closing date for applications',
            'Latest start date',
            'Expected contract length',
            'Location',
            'Organisation the work is for',
            'Budget range',
            'Maximum day rate'
        ]
        for col, h in enumerate(headers):
            worksheet.write(0, col, h, _format)

        r = 1
        for title, url in self.links:
            link = 'https://www.digitalmarketplace.service.gov.uk/' + url
            app = dict.fromkeys(headers)
            app['Title'] = title
            app['Link'] = link
            go(link)

            tables = html.fromstring(show()).xpath('//dl')
            for table in tables[:2]:
                for row in table.xpath('./div'):
                    key = row.xpath('./dt')[0].text_content().strip()
                    val = row.xpath('./dd')[0].text_content().strip()
                    app[key] = val
            for i in range(len(headers)):
                worksheet.write(r, i, app[headers[i]])
            r += 1

        messagebox.showinfo(title='Written', message='Applications scraped and written to: ' + filepath)
        workbook.close()


if __name__ == "__main__":
    root = tk.Tk()
    app = App(master=root)
    app.mainloop()

