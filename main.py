from selenium.webdriver.chrome.options import Options
from selenium.webdriver import Chrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as Exp_Cond
from selenium.webdriver.common.by import By
import json

options = Options()
options.page_load_strategy = 'none'
browser_emulator = Chrome(options=options)
browser_emulator.get("https://spb.hh.ru/search/vacancy?area=1&area=2&search_field=name&search_field=company_name&search_field=description&text=python&enable_snippets=false&only_with_salary=true")

default_window = browser_emulator.current_window_handle

def wait_elements(by, value, desired_amount = 50):
    # вынужден делать так, а не просто WebDriverWait, потому что он возвращал не все обьекты, а только 20 штук, а этот подход гарантирует нужное количество
    while True:
        list_elements = browser_emulator.find_elements(by, value)
        if len(list_elements) < desired_amount:
            continue
        else:
            return list_elements

def wait_element(by, value, last_wait = False):
    if last_wait == True:
        return WebDriverWait(browser_emulator, 5).until(Exp_Cond.presence_of_all_elements_located((by, value)))
    else:
        return WebDriverWait(browser_emulator, 5).until(Exp_Cond.presence_of_element_located((by, value)))

def get_elements():
    list_links = []
    salary = []
    company_titles = []
    cities = []
    max_count_pages = int(wait_elements(By.XPATH, "//a[@data-qa='pager-page']", 5)[4].text)

    for x in range(0, max_count_pages):
        if x == max_count_pages - 1:
            list_title_links = wait_element(By.XPATH, "//span/a[@class='bloko-link' and @target='_blank']", True)
            list_links.extend([link.get_attribute("href") for link in list_title_links])

            list_salary = wait_element(By.CLASS_NAME, "bloko-header-section-2", True)
            salary.extend([salary.text for salary in list_salary])

            list_company_titles = wait_element(By.CLASS_NAME, "vacancy-serp-item__meta-info-company", True)
            company_titles.extend([company_title.text for company_title in list_company_titles])

            list_cities = wait_element(By.XPATH, "//div[@data-qa='vacancy-serp__vacancy-address']", True)
            cities.extend([city.text for city in list_cities])
        else:
            list_title_links = wait_elements(By.XPATH, "//span/a[@class='bloko-link' and @target='_blank']")
            list_links.extend([link.get_attribute("href") for link in list_title_links])

            list_salary = wait_elements(By.CLASS_NAME, "bloko-header-section-2")
            salary.extend([salary.text for salary in list_salary])

            list_company_titles = wait_elements(By.CLASS_NAME, "vacancy-serp-item__meta-info-company")
            company_titles.extend([company_title.text for company_title in list_company_titles])

            list_cities = wait_elements(By.XPATH, "//div[@data-qa='vacancy-serp__vacancy-address']")
            cities.extend([city.text for city in list_cities])

            next_button = wait_element(By.XPATH, "//a[@data-qa='pager-next']")
            coords = next_button.get_attribute("offsetTop")
            browser_emulator.execute_script("window.scrollTo(0," + coords + ");")
            browser_emulator.get(next_button.get_attribute("href"))
        
    return sort_elements(list_links, salary, company_titles, cities)

def sort_elements(links: list, salary: list, company_titles: list, cities: list):
    vacancy_dict = {
        "vacancies": [],
    }
    for index, link in enumerate(links):
        if salary[index].find("$") != -1:
            browser_emulator.switch_to.new_window('tab')
            browser_emulator.get(link)
            description = wait_element(By.XPATH, "//div[@data-qa='vacancy-description']").text.upper()
            if description.find("DJANGO") != -1 or description.find("FLASK") != -1:
                vacancy_dict.get("vacancies").append(
                    {
                        "link": link,
                        "salary": salary[index].replace("\u202f", ''),
                        "company_title": company_titles[index],
                        "city": cities[index],
                    }
                )
            browser_emulator.close()
            browser_emulator.switch_to.window(default_window)

    return vacancy_dict

def write_data_to_json(dict):
    with open("vacancies.json", "w", encoding="utf-8") as json_file:
        json.dump(dict, json_file, ensure_ascii = False, indent=2)

if __name__ == "__main__":
    hh_elements = get_elements()
    write_data_to_json(hh_elements)