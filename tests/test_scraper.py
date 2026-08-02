import datetime

import pytest
import requests as req
from app.scrapers.nofluffjobs_scraper import map_experience_to_enum, map_contract_type_to_enum, parse_salary_UOP, \
    parse_salary_B2B, parse_mode_of_work_and_location, parse_salary, find_list_of_offers, find_posting_data, fetch_page, \
    parse_state_transfer, create_JobOffer_from_scraped_data
from app.enums import ExperienceLevel, ContractType, WorkMode


@pytest.mark.parametrize("seniority_input, expected", [
    ("Junior", ExperienceLevel.JUNIOR),
    ("Mid", ExperienceLevel.MID),
    ("Senior", ExperienceLevel.SENIOR),
    ("Team Lider", ExperienceLevel.SENIOR),
    ("Expert", ExperienceLevel.SENIOR)
])
def test_map_experience_to_enum(seniority_input, expected):
    parse_data = {"basics": {"seniority": [seniority_input]}}
    result = map_experience_to_enum(parse_data)
    assert result == expected

def test_map_experience_to_enum_raises_for_unknown_value():
    parse_data = {"basics": {"seniority": ["Nieznana wartość"]}}
    with pytest.raises(Exception):
        map_experience_to_enum(parse_data)


@pytest.mark.parametrize("contract_input, expected", [
    ("permanent", ContractType.UOP),
    ("b2b", ContractType.B2B),])
def test_map_contract_type_to_enum(contract_input, expected):
    parse_data = {"essentials": {"originalSalary":{"types":{contract_input:{}}}}}
    result = map_contract_type_to_enum(parse_data)
    assert result == expected

def test_map_contract_type_to_enum_raises_for_unknown_value():
    parse_data = {"essentials": {"originalSalary":{"types":{"Nieznana wartość":{}}}}}
    with pytest.raises(Exception):
        map_contract_type_to_enum(parse_data)

#====UOP====
def test_parse_salary_uop_pln_month():
  parse_data =  {'essentials': {'originalSalary': {'currency': 'PLN', 'types': {'permanent': {'period': 'Month', 'range': [10_000, 15_000]}}}}}
  result = parse_salary_UOP(parse_data)
  assert result == [10_000, 15_000]

def test_parse_salary_uop_pln_hour():
    parse_data = {'essentials': {
        'originalSalary': {'currency': 'PLN', 'types': {'permanent': {'period': 'Hour', 'range': [100, 150]}}},
        'convertedSalary':{'currency': 'PLN', 'types':{'permanent': {'period': 'Month', 'range': [10_000, 15_000]}}}}}
    result = parse_salary_UOP(parse_data)
    assert result == [10_000, 15_000]

def test_parse_salary_uop_huf_month():
    parse_data = {'essentials': {'originalSalary': {'currency': 'HUF', 'types': {'permanent': {'period': 'Month', 'range': [1_000_000, 1_500_000]}}}, 'convertedSalary':{'currency': 'PLN', 'types':{'permanent': {'period': 'Month', 'range': [10_000, 15_000]}}}}}
    result = parse_salary_UOP(parse_data)
    assert result == [10_000, 15_000]

def test_parse_salary_uop_pln_raises_for_unknown_stake():
    parse_data = {'essentials': {'originalSalary': {'currency': 'PLN', 'types': {'permanent': {'period': 'Week', 'range': [10_000, 15_000]}}}}}
    with pytest.raises(Exception):
        parse_salary_UOP(parse_data)

def test_parse_salary_uop_huf_raises_for_lack_of_convertedSalary():
    parse_data = {'essentials': {'originalSalary': {'currency': 'HUF', 'types': {'permanent': {'period': 'Month', 'range': [1_000_000, 1_500_000]}}}}}
    with pytest.raises(Exception):
        parse_salary_UOP(parse_data)

#====B2B====
def test_parse_salary_b2b_pln_month():
  parse_data =  {'essentials': {'originalSalary': {'currency': 'PLN', 'types': {'b2b': {'period': 'Month', 'range': [10_000, 15_000]}}}}}
  result = parse_salary_B2B(parse_data)
  assert result == [10_000, 15_000]

def test_parse_salary_b2b_pln_hour():
    parse_data = {'essentials': {
        'originalSalary': {'currency': 'PLN', 'types': {'b2b': {'period': 'Hour', 'range': [100, 150]}}},
        'convertedSalary': {'currency': 'PLN', 'types': {'b2b': {'period': 'Month', 'range': [10_000, 15_000]}}}}}
    result = parse_salary_B2B(parse_data)
    assert result == [10_000, 15_000]


def test_parse_salary_b2b_huf_month():
    parse_data = {'essentials': {'originalSalary': {'currency': 'HUF', 'types': {'b2b': {'period': 'Month', 'range': [1_000_000, 1_500_000]}}}, 'convertedSalary':{'currency': 'PLN', 'types':{'b2b': {'period': 'Month', 'range': [10_000, 15_000]}}}}}
    result = parse_salary_B2B(parse_data)
    assert result == [10_000, 15_000]

def test_parse_salary_b2b_pln_raises_for_unknown_stake():
    parse_data = {'essentials': {'originalSalary': {'currency': 'PLN', 'types': {'b2b': {'period': 'Week', 'range': [10_000, 15_000]}}}}}
    with pytest.raises(Exception):
        parse_salary_B2B(parse_data)

def test_parse_salary_b2b_huf_raises_for_lack_of_convertedSalary():
    parse_data = {'essentials': {'originalSalary': {'currency': 'HUF', 'types': {'b2b': {'period': 'Month', 'range': [1_000_000, 1_500_000]}}}}}
    with pytest.raises(Exception):
        parse_salary_B2B(parse_data)

def test_parse_mode_of_work_and_location_stationary():
    parse_data = {"location": {"places": [{'country': {'code': 'POL', 'name': 'Poland'},
'city': 'Gliwice',}], "remote": 0}}
    result = parse_mode_of_work_and_location(parse_data)
    assert result == [WorkMode.STATIONARY, "Gliwice"]

def test_parse_mode_of_work_and_location_remote():
    parse_data = {"location": {"places": [{"city":"Remote"},{'country': {'code': 'POL', 'name': 'Poland'}, 'city': 'Kraków'}], "remote": 5}}
    result = parse_mode_of_work_and_location(parse_data)
    assert result == [WorkMode.REMOTE, "Poland"]

@pytest.mark.parametrize("remote_input, expected", [
    (1, WorkMode.HYBRID),
    (2, WorkMode.HYBRID),
    (3, WorkMode.HYBRID),
    (4, WorkMode.HYBRID), ])
def test_parse_mode_of_work_and_location_hybrid(remote_input, expected):
    parse_data = {"location": {"places": [{'country': {'code': 'POL', 'name': 'Poland'},
                                           'city': 'Gliwice', }], "remote": remote_input}}
    result = parse_mode_of_work_and_location(parse_data)
    assert result == [expected, "Gliwice"]

def test_parse_mode_of_work_and_location_for_unknown_remote():
    parse_data = {"location": {"places": [{'country': {'code': 'POL', 'name': 'Poland'},
                                           'city': 'Gliwice', }], "remote": 6}}
    with pytest.raises(Exception):
        parse_mode_of_work_and_location(parse_data)

def test_parse_mode_of_work_and_location_for_lack_of_remote():
    parse_data = {"location": {"places": [{'country': {'code': 'POL', 'name': 'Poland'},
                                           'city': 'Gliwice', }]}}
    with pytest.raises(Exception):
        parse_mode_of_work_and_location(parse_data)

def test_parse_salary_for_uop():
    parse_data = {'essentials': {
        'originalSalary': {'currency': 'PLN', 'types': {'permanent': {'period': 'Month', 'range': [10_000, 15_000]}}}}}
    result = parse_salary(parse_data)
    assert result == [10_000, 15_000]

def test_parse_salary_for_b2b():
    parse_data = {'essentials': {
        'originalSalary': {'currency': 'PLN', 'types': {'b2b': {'period': 'Month', 'range': [10_000, 15_000]}}}}}
    result = parse_salary(parse_data)
    assert result == [10_000, 15_000]

def test_parse_salary_for_lock_of_uop_and_b2b():
    parse_data = {'essentials': {
        'originalSalary': {'currency': 'PLN', 'types': {'umowa_o_dzieło': {'period': 'Month', 'range': [10_000, 15_000]}}}}}
    result = parse_salary(parse_data)
    assert result is None

def test_find_list_of_offers():
    state= {"TestKey1": "TestVal1", "TestKey2": {"TestKey21": "TestVal21"},"HashKey": {"postings":"postingsVal"}}
    offers = find_list_of_offers(state)
    assert offers == "postingsVal"

def test_find_list_of_offers_raises_when_not_found():
    state= {"TestKey1": "TestVal1", "TestKey2": {"TestKey21": "TestVal21"},"HashKey": {"NotPostings":"postingsVal"}}
    with pytest.raises(Exception):
        find_list_of_offers(state)

def test_find_posting_data():
    offer_slug = "TestSlug"
    state = {"TestKey1": "TestVal1", "TestKey2": {"TestKey21": "TestVal21"},"/posting/TestSlug": {"TestKey3": "TestVal3"}}
    result = find_posting_data(state, offer_slug)
    assert result == {"TestKey3": "TestVal3"}

def test_find_posting_data_raises_when_slug_is_different():
    offer_slug = "TestSlug"
    state = {"TestKey1": "TestVal1", "TestKey2": {"TestKey21": "TestVal21"},"/posting/OtherSlug": {"TestKey3": "TestVal3"}}
    with pytest.raises(Exception):
        find_posting_data(state, offer_slug)

def test_find_posting_data_raises_when_posting_is_not_found():
    offer_slug = "TestSlug"
    state = {"TestKey1": "TestVal1", "TestKey2": {"TestKey21": "TestVal21"},"/other/TestSlug": {"TestKey3": "TestVal3"}}
    with pytest.raises(Exception):
        find_posting_data(state, offer_slug)

def test_parse_state_transfer():
    html = '<script id="serverApp-state" type="application/json">{"TestKey":"TestVal"}</script>'
    result = parse_state_transfer(html)
    assert result == {"TestKey": "TestVal"}

def test_parse_state_transfer_raises_when_tag_missing():
    html = "<html><body>test</body></html>"
    with pytest.raises(Exception):
        parse_state_transfer(html)

def test_create_JobOffer():
    SAMPLE_PARSE_DATA = {
        "title": "Senior Python Developer",
        "company": {"name": "TestCompany"},
        "expiresAt": "2026-12-31T23:59:59",
        "requirements": {
            "musts": [{"value": "Python", "type": "main"}],
            "nices": [{"value": "Docker", "type": "nice"}],
        },
        "basics": {"seniority": ["Senior"]},
        "location": {
            "places": [{"country": {"code": "POL", "name": "Poland"}, "city": "Gliwice"}],
            "remote": 0,
        },
        "essentials": {
            "originalSalary": {
                "currency": "PLN",
                "types": {"permanent": {"period": "Month", "range": [15000, 20000]}},
            },
        },
    }
    URL = "https://nofluffjobs.com/pl/job/senior-python-developer-testcompany"

    result = create_JobOffer_from_scraped_data(SAMPLE_PARSE_DATA,URL)
    assert result.company_name == "TestCompany"
    assert result.technologies == ["Python", "Docker"]
    assert result.job_title == "Senior Python Developer"
    assert result.experience == ExperienceLevel.SENIOR
    assert result.type_of_contract == ContractType.UOP
    assert result.mode_of_work == WorkMode.STATIONARY
    assert result.location == "Gliwice"
    assert result.publication_date is None
    assert result.expiration_date == datetime.date(2026,12,31)
    assert result.url_address == URL
    assert result.salary_min == 15000
    assert result.salary_max == 20000


# company_name = company_name,
# technologies = technologies,
# job_title = job_title,
# experience = experience_level,
# type_of_contract = contract_type,
# mode_of_work = mode_of_work,
# location = location,
# publication_date = None,
# expiration_date = expiration_date,
# url_address = url,
# salary_min = min_salary,
# salary_max = max_salary

#====MonkeyPatch====
def test_fetch_page(monkeypatch):
    class FakeResponse:
        status_code = 200
        text = "<html>Test</html>"
    def fake_get(url, headers=None):
            return FakeResponse()

    monkeypatch.setattr(req, "get",fake_get)

    result = fetch_page("http://example.com")
    assert result == "<html>Test</html>"

def test_fetch_page_raises_for_bad_status(monkeypatch):
    class FakeResponse:
        status_code = 404
        text = "<html>Test</html>"
    def fake_get(url, headers=None):
        return FakeResponse()

    monkeypatch.setattr(req, "get",fake_get)
    with pytest.raises(Exception):
        fetch_page("http://example.com")