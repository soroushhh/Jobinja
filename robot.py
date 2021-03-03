import json
import requests
from pathlib import Path
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
}
# to store all the scraped data
ads = {"data": []}
URL_PATH = "https://jobinja.ir/jobs?filters%5Bkeywords%5D%5B0%5D=&filters%5Blocations%5D%5B0%5D=&filters%5Bjob_categories%5D%5B0%5D=%D9%88%D8%A8%D8%8C%E2%80%8C+%D8%A8%D8%B1%D9%86%D8%A7%D9%85%D9%87%E2%80%8C%D9%86%D9%88%DB%8C%D8%B3%DB%8C+%D9%88+%D9%86%D8%B1%D9%85%E2%80%8C%D8%A7%D9%81%D8%B2%D8%A7%D8%B1"


def send_requests_and_parse(url_path, **kwargs):
    """ Takes a url_path as an input, return the html page ready to parse """
    r = requests.get(url_path, **kwargs)
    soup = BeautifulSoup(r.text, "lxml")
    return soup


def extract_links(html_page):
    """ Takes the html page that contains list of job ads and returns a list contains each ads link """

    # to find the <ul> tag that contains every job ad basic info
    jobs_list = html_page.find("ul", class_="o-listView__list")

    # iterate over every job recruiment to get it's link
    demo = list()
    for job_add in jobs_list.find_all("li", class_="o-listView__item"):
        link = job_add.find("a", class_="c-jobListView__titleLink")
        demo.append(link.get("href", None))

    return demo


def extract_data(html_page):
    """To parse and extract the wanted data from the html_page and return a dictionay of overall info as an output"""

    # store every ads info in a key, value pair
    container = {}

    # to find the job recruiment title , then add it to dictionary
    title = html_page.find("div", class_="c-jobView__titleText").get_text(strip=True)
    container["title"] = title

    # find the list that contains the wanted data, do iteration and extract its data
    elements = html_page.find_all("ul", class_="c-infoBox")
    for element in elements:
        for info in element.find_all("li"):

            # assign the wanted objects to key value pair in order to store them in a dict, but first we noralize the keys
            txt = info.h4.get_text(strip=True)
            key = normalize_keys(txt)
            value = find_value(info.find("div", class_="tags"))
            container[key] = value

    return container


def normalize_keys(txt):
    """ To transform persian characters into English """

    combos = [
        ("دسته\u200cبندی شغلی", "Type"),
        ("موقعیت مکانی", "Provience/City"),
        ("نوع همکاری", "Colab Type"),
        ("حداقل سابقه کار", "Min of year Exp"),
        ("حقوق", "Salary"),
        ("مهارت\u200cهای مورد نیاز", "Skills"),
        ("جنسیت", "Gender"),
        ("وضعیت نظام وظیفه", "Military Service"),
        ("حداقل مدرک تحصیلی", "Degree"),
    ]

    for combo in combos:
        # check for matching combinations
        if txt == combo[0]:
            txt = combo[1]
    return txt


def find_value(tag):
    """
    A function to extract the wanted data from every <div> tag with class "tags"
    Input Parameter (bs4.tag.Element) ---> <div> tag
    the <div> tag include one/multiple <span> tags that contain the wanted data
    Return type (list/string) ---> based on number of <span> tags
    """
    values = []

    for value in tag.find_all("span"):
        txt = value.get_text(strip=True)
        values.append(txt)

    if len(values) == 1:
        return ("").join(values)
    return values


if __name__ == "__main__":
    # iterate over number of pages include ads
    for i in range(1, 150):
        params = {"page": i}
        html_page = send_requests_and_parse(URL_PATH, headers=headers, params=params)

        links = extract_links(html_page)
        for link in links:
            ads_html_page = send_requests_and_parse(link, headers=headers)
            data = extract_data(ads_html_page)

            ads["data"].append(data)

    with Path("jobinja_demo.json").open("w", encoding="utf-8") as output_file:
        json.dump(ads, output_file, indent=3, ensure_ascii=False)
