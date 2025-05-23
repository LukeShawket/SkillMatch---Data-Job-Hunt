from bs4 import BeautifulSoup
import requests
import pdf_picker
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time

URL = 'https://www.linkedin.com/jobs/search?keywords=Data%20Analyst&location=United%20States&geoId=103644278&trk=public_jobs_jobs-search-bar_search-submit&position=1&pageNum=0'
URL2 = "https://www.linkedin.com/jobs/search?keywords=Data%20Engineer&location=United%20States&geoId=103644278&trk=public_jobs_jobs-search-bar_search-submit&position=1&pageNum=0"
URL3 = "https://www.linkedin.com/jobs/search?keywords=Data%20Scientist&location=United%20States&geoId=103644278&trk=public_jobs_jobs-search-bar_search-submit&position=1&pageNum=0"
URL4 = "https://www.linkedin.com/jobs/search?keywords=Business%20Analyst&location=United%20States&geoId=103644278&trk=public_jobs_jobs-search-bar_search-submit&position=1&pageNum=0"

# Set up WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)


driver.get(URL4)

last_height = driver.execute_script("return document.body.scrollHeight")
scroll_count = 0
unchanged_scrolls = 0

driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_DOWN)
time.sleep(2)  # Give time for new content

# Scroll down multiple times
while True:
    driver.execute_script("window.scrollBy(0, document.body.scrollHeight);")
    time.sleep(2)

    try:
        see_more_button = driver.find_element(By.XPATH, "//button[contains(text(), 'See more jobs')]")
        see_more_button.click()
        time.sleep(2)
    except:
        pass 

    new_height = driver.execute_script("return document.body.scrollHeight")

    if new_height == last_height:
        unchanged_scrolls += 1
        if unchanged_scrolls > 20:  # Ensure it remains unchanged for multiple attempts
            print("Scrolling stopped after multiple unchanged attempts. Ending process.")
            break
    else:
        unchanged_scrolls = 0

    last_height = new_height
    scroll_count += 1


# Get full page source after scrolling
html = driver.page_source
driver.quit()



headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
}

def retrieve_job_urls():

    soup = BeautifulSoup(html, 'html.parser')

    job_links = []
    all_url_elements = soup.select("[data-tracking-control-name=\"public_jobs_jserp-result_search-card\"]")
    for url in all_url_elements:
        job_links.append(url["href"])

    return job_links


def scrape_job(job_url):
    response = requests.get(job_url, headers=headers)
    web_html = response.text
    soup = BeautifulSoup(web_html, 'html.parser')

    website_element = soup.select_one("[data-tracking-control-name=\"public_jobs_topcard_logo\"]")
    if website_element:
        website = website_element["href"]
    else:
        website = "Unknown"

    title_element = soup.select_one('h1')
    if title_element:
        title = title_element.text.strip()
    else:
        title = "Unknown"

    company_element = soup.find("span", "topcard__flavor")
    if company_element:
        company_name = company_element.text.strip()
    else:
        company_name = "Unknown"

    location_element = soup.find("span", "topcard__flavor topcard__flavor--bullet")
    if location_element:
        location = location_element.text.strip()
    else:
        location = "Unknown"

    salary_element = soup.find("div", "salary compensation__salary")
    if salary_element:
        salary = salary_element.text.strip()
    else:
        salary = "Unknown"

    description_element = soup.find("div", "description__text description__text--rich")
    if description_element:
        description = description_element.text
        skills = pdf_picker.parse_skills(description)
        if skills:
            pass
        else:
            skills = ""
    else:
        skills = ""


    # Collect the scraped data and return it
    jobs = {
        "url": website,
        "title": title,
        "company": company_name,
        "location": location,
        "salary": salary,
        "required_skills": list(skills)
    }

    return jobs

all_data = {}
key = 0
for url in retrieve_job_urls():
    print(scrape_job(url))
    all_data[key] = scrape_job(url)
    key += 1

# Writing JSON to a file
with open("data4.json", "w") as json_file:
    json.dump(all_data, json_file, indent=4)

