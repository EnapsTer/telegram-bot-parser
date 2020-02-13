from bs4 import BeautifulSoup
import requests
from config import *

class HHParser():

    def __init__(self, url):

        #sent vacancies in one message
        self.posts_cnt = 20
        #vacancies that have already been sent
        self.current_posts = 0
        #all vacancies found
        self.all_vacancies = 0
        #page list
        self.page = 0
        #area location
        self.area = 1
        # hh.ru url
        self.url = url
        #url to parse
        self.parse_url = ''
        #text
        self.text = ''

    def set_url(self,page=None, area=None, text=None):
        if page:
            self.page += 1 if page == 1 and int(self.all_vacancies) // 20 <= page else -1 if self.page > 0 else 0
        else:
            self.page = 0

        if area or area == 0:
            self.area = area

        if text:
            self.text = text.replace(' ', '+')
        self.parse_url = self.url+f'page={self.page}'+f'&area={self.area}'+f'&text={self.text}'

    def parse(self):
        with requests.Session() as session:
            print(self.parse_url)
            response = session.get(self.parse_url, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')

            vacancy_items = soup.select('.vacancy-serp-item')
            for item in vacancy_items:
                vacancy_adress = item.find('span', attrs={'data-qa':"vacancy-serp__vacancy-address"})
                vacancy_name = item.find('a', attrs={'class': 'HH-LinkModifier'})
                vacancy_link = vacancy_name['href']
                vacancy_salary = item.find('div', attrs={'data-qa': 'vacancy-serp__vacancy-compensation'})
                employer = item.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-employer'})
                vacancy_description = item.find('div',
                                                attrs={'data-qa': 'vacancy-serp__vacancy_snippet_responsibility'})
                vacancy_requirement = item.find('div', attrs={'data-qa': 'vacancy-serp__vacancy_snippet_requirement'})
                try:
                    yield (vacancy_name.text, vacancy_salary.text if vacancy_salary else 'Не указано',employer.text),\
                          (vacancy_description.text, vacancy_requirement.text,
                           vacancy_link if vacancy_link else 'https://hh.ru/', vacancy_adress.text)
                except AttributeError:
                    continue

    def get_area(self):
        with requests.Session() as session:
            response = session.get(self.parse_url, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            area = soup.select('.clusters-value__name')
            print(area[0].text)
            return area[0].text

    #parse all vacancies count
    def get_title(self):
        with requests.Session() as session:
            pre_response = session.get(self.parse_url, headers=headers)
            soup = BeautifulSoup(pre_response.content, 'html.parser')
            title = soup.find('h1', attrs={'data-qa': 'page-title'})
            all_vacancies = ''
            for item in title.text.split():
                if item.isdigit():
                    all_vacancies += item
                else:
                    continue
            self.all_vacancies = all_vacancies
            return all_vacancies
