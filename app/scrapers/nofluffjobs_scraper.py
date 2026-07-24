import datetime
import json
import re
import requests as req
from bs4 import BeautifulSoup
from app.enums import ExperienceLevel, WorkMode, ContractType
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
    #salary = parse_data["essentials"]["originalSalary"]["types"]["permanent"]["range"]

def parse_salary_B2B(parse_data:dict) -> list | None:
    #type_of_stake = parse_data["essentials"]["originalSalary"]["types"]["b2b"]["period"]
    type_of_stake = parse_data.get("essentials", {}).get("originalSalary", {}).get("types", {}).get("b2b", {}).get("period",None)
    if type_of_stake == "Hour":
        #salary = parse_data["essentials"]["convertedSalary"]["types"]["b2b"]["range"]
        salary = parse_data.get("essentials", {}).get("convertedSalary", {}).get("types", {}).get("b2b", {}).get("range",None)
    elif type_of_stake == "Month":
        #salary = parse_data["essentials"]["originalSalary"]["types"]["b2b"]["range"]
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
    return experience

def map_experience_to_enum(exp:str) -> ExperienceLevel:
    exp = exp.title()
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
    elif ct == "B2b":
        contract_type_enum = ContractType("B2B")
    else:
        raise ValueError(f"Unexpected contract type: {ct}")
    return contract_type_enum



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

