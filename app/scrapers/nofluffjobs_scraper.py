import datetime
import json
import requests as req
from bs4 import BeautifulSoup
from app.enums import ExperienceLevel, WorkMode, ContractType
from app.schemas.job_offer import JobOfferCreate

CATEGORY_SLUGS = [
    "backend", "frontend", "fullstack", "mobile", "embedded", "testing",
    "devops", "architecture", "security", "game-dev", "artificial-intelligence",
    "data", "sys-administrator", "agile", "product-management", "project-manager",
    "business-intelligence", "business-analyst", "ux", "support", "erp",
    "javascript", ".net", "sql", "nosql", "java", "python", "react", "aws",
    "typescript", "html", "css", "angular", "azure", "php", "c%2B%2B",
    "android", "kotlin", "vue.js", "ios", "golang", "c", "hadoop", "spark",
    "ruby%20on%20rails", "flutter", "elixir", "c%23", "react%20native", "rust",
]

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

def build_offer_url_from_slug(offer_slug:str) -> str:
    url = f"https://nofluffjobs.com/pl/job/{offer_slug}"
    return url

def build_category_url_from_slug(category_slug:str) -> str:
    url = f"https://nofluffjobs.com/pl/{category_slug}"
    return url

def build_category_list(category_list:list) -> list[str]:
    category_urls = []
    for cat in category_list:
        category_urls.append(build_category_url_from_slug(cat))
    return category_urls

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

def find_list_of_offers(state:dict) -> list:
    for val in state.values():
        if isinstance(val,dict) and "postings" in val:
            return val["postings"]
    else:
        raise Exception(f"No posting data found in serverApp-state")

def get_offers_url_from_category(category_urls: list) -> list[str]:
    offers_url_list = []
    for url in category_urls:
        html_content = fetch_page(url)
        state = parse_state_transfer(html_content)
        postings_data = find_list_of_offers(state)
        for post in postings_data:
            offers_url_list.append(build_offer_url_from_slug(post["url"]))
    return list(set(offers_url_list))

def parse_company_name(parse_data:dict) -> str:
    company_name = parse_data["company"]["name"]
    return company_name

def parse_salary_UOP(parse_data:dict) -> list | None:
    type_of_stake = parse_data.get("essentials", {}).get("originalSalary", {}).get("types", {}).get("permanent", {}).get("period", None)
    if type_of_stake == "Hour":
        salary = parse_data.get("essentials", {}).get("convertedSalary", {}).get("types", {}).get("permanent", {}).get("range", None)
    elif type_of_stake == "Month":
        salary = parse_data.get("essentials", {}).get("originalSalary", {}).get("types", {}).get("permanent", {}).get("range",None)
    else:
        raise Exception(f"Unexpected type_of_stake: {type_of_stake}")

    return salary


def parse_salary_B2B(parse_data:dict) -> list | None:

    type_of_stake = parse_data.get("essentials", {}).get("originalSalary", {}).get("types", {}).get("b2b", {}).get("period",None)
    if type_of_stake == "Hour":
        salary = parse_data.get("essentials", {}).get("convertedSalary", {}).get("types", {}).get("b2b", {}).get("range",None)
    elif type_of_stake == "Month":
        salary = parse_data.get("essentials", {}).get("originalSalary", {}).get("types", {}).get("b2b", {}).get("range", None)
    else:
        raise Exception(f"Unexpected type_of_stake: {type_of_stake}")
    return salary

def parse_salary(parse_data:dict) -> list | None:
    uop_data = parse_data.get("essentials", {}).get("originalSalary",{}).get("types",{}).get("permanent",None)
    b2b_data = parse_data.get("essentials", {}).get("originalSalary",{}).get("types",{}).get("b2b",None)

    if uop_data is not None:
        return parse_salary_UOP(parse_data)
    elif b2b_data is not None:
        return parse_salary_B2B(parse_data)
    else:
        return None


def parse_tech(parse_data:dict) -> list:
    tech = []
    for item in parse_data["requirements"]["musts"]:
        tech.append(item["value"])

    for item in parse_data["requirements"]["nices"]:
        tech.append(item["value"])
    return tech

def parse_job_title(parse_data:dict) -> str:
    job_title = parse_data["title"]
    return job_title

def parse_expiration_date(parse_data:dict) -> datetime.date:
    date_obj = datetime.datetime.fromisoformat(parse_data["expiresAt"]).date()
    return date_obj

def parse_experience(parse_data:dict) -> str:
    experience = parse_data["basics"]["seniority"][0]
    return experience.title()

def map_experience_to_enum(parse_data: dict) -> ExperienceLevel:
    exp = parse_experience(parse_data)
    if exp == "Team Lider":
        level = ExperienceLevel("Senior")
    elif exp == "Expert":
        level = ExperienceLevel("Senior")
    else:
        try:
            level = ExperienceLevel(exp)
        except ValueError:
            raise Exception(f"No experience level found for {exp}")
    return level


def parse_mode_of_work_and_location(parse_data:dict) -> list:
    remote = parse_data.get("location",{}).get("remote",None)
    work_mode = None
    location = None
    if remote is not None:
        match remote:
            case 0:
                work_mode = "Stationary"
            case 1|2|3|4:
                work_mode = "Hybrid"
            case 5:
                work_mode = "Remote"
            case _:
                raise Exception(f"Unexpected remote value: {remote}")

    if work_mode is not None:
        if work_mode == "Remote":
            location = parse_data["location"]["places"][1]["country"]["name"]
        else:
            location = parse_data["location"]["places"][0]["city"]

    work_mode_enum = WorkMode(work_mode)
    return [work_mode_enum, location]


def parse_contract_type(parse_data:dict) -> str:
    contract_type = list(parse_data["essentials"]["originalSalary"]["types"].keys())
    if "permanent" in contract_type:
        return "permanent".title()
    elif "b2b" in contract_type:
        return "b2b".title()
    else:
        raise Exception(f"No contract type found for {contract_type}")

def map_contract_type_to_enum(parse_data:dict) -> ContractType:
    ct = parse_contract_type(parse_data)
    if ct == "Permanent":
        contract_type_enum = ContractType("UOP")
    elif ct == "B2B":
        contract_type_enum = ContractType("B2B")
    else:
        raise ValueError(f"Unexpected contract type: {ct}")
    return contract_type_enum

def create_JobOffer_from_scraped_data(parse_data:dict, url:str) -> JobOfferCreate | None:
    company_name = parse_company_name(parse_data)
    technologies = parse_tech(parse_data)
    job_title = parse_job_title(parse_data)
    experience_level = map_experience_to_enum(parse_data)
    contract_type = map_contract_type_to_enum(parse_data)
    mode_of_work_and_location = parse_mode_of_work_and_location(parse_data)
    mode_of_work = mode_of_work_and_location[0]
    location = mode_of_work_and_location[1]
    expiration_date = parse_expiration_date(parse_data)
    salary_range = parse_salary(parse_data)
    if salary_range is not None:
        min_salary = salary_range[0]
        max_salary = salary_range[1]
        return JobOfferCreate(
            company_name=company_name,
            technologies=technologies,
            job_title=job_title,
            experience=experience_level,
            type_of_contract= contract_type,
            mode_of_work=mode_of_work,
            location=location,
            publication_date=None,
            expiration_date=expiration_date,
            url_address=url,
            salary_min=min_salary,
            salary_max=max_salary)
    else:
        return None

def run_scraper() -> list:
    category_url_list = build_category_list(CATEGORY_SLUGS)
    offers_url_list = get_offers_url_from_category(category_url_list)
    scraped_offers_list = []
    for offer in offers_url_list:
        try:
            html_content = fetch_page(offer)
            state = parse_state_transfer(html_content)
            offer_slug = find_offer_slug(offer)
            posting_data = find_posting_data(state,offer_slug)
            job_offer = create_JobOffer_from_scraped_data(posting_data,offer)
            if job_offer is not None:
                scraped_offers_list.append(job_offer)
        except Exception as e:
            print(f"Unexpected exception: {e}")

    return scraped_offers_list






