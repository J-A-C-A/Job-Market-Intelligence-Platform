import json
import re
import requests as req
from bs4 import BeautifulSoup
PATTERN = r"\s"
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
def fetch_page(url:str) -> str:
    response = req.get(url,headers=HEADERS)
    if response.status_code == 200:
        html_content = response.text
        return html_content
    else:
        raise Exception(f"Failed to fetch page, status code: {response.status_code}")

def find_offer_slug(url:str) -> str:
    offer_slug = url.split("/")[-1]
    return offer_slug

def parse_state_transfer(html:str) -> dict:
    soup = BeautifulSoup(html, 'html.parser')
    tag = soup.find("script", {"id": "serverApp-state"})
    if tag is None:
        raise Exception(f"No state transfer found in serverApp-state")
    else:
        data = json.loads(tag.string)
        return data

def find_posting_data(state:dict, offer_slug:str) -> dict:
    for item in state.keys():
        if item.startswith("/posting/") and offer_slug in item:
            return state[item]
    else:
        raise Exception(f"No posting data found in serverApp-state")

#====STARE ROZWIĄZANIE====
def parse_job_posting_jsonld(html:str) -> dict:
    soup = BeautifulSoup(html, 'html.parser')
    tag = soup.find("script", {"type": "application/ld+json"})
    json_dict = json.loads(tag.string)
    for item in json_dict["@graph"]:
        if item["@type"] == "JobPosting":
            return item
    else:
        raise Exception(f"No JobPosting found in JSON-LD")

def parse_monthly_salary(html:str) -> tuple[float,float] | None:
    soup = BeautifulSoup(html, 'html.parser')
    salary_div = soup.find("div", {"class": "salary"})
    if salary_div is None:
        return None
    else:
        h4_tag = salary_div.find("h4")
        raw_text = h4_tag.text
        text_without_pln = raw_text.replace("PLN", "")
        text_without_space = text_without_pln.strip()
        strings = text_without_space.split("–")
        float1 = float(re.sub(PATTERN, "", strings[0]))
        float2 = float(re.sub(PATTERN, "", strings[1]))
        return (float1, float2)

