import datetime
from unittest import mock
import pytest
from fastapi.testclient import TestClient
from app.main import app as api_app
from unittest.mock import MagicMock
from datetime import date
from app.models import Company
from app.models.job_offer import JobOffer
from app.enums import ContractType, OfferStatus, ExperienceLevel, WorkMode
from app.repositories import job_offer_repository
from app.services import job_offer_service
from app.api import job_offers
from app.api import stats

client = TestClient(api_app)
test_company = Company(company_id=1,name="Test Company")

test_offer = JobOffer(
        offer_id=1,
        company_id=1,
        type_of_contract=ContractType.B2B,
        salary_min=20000,
        salary_max=30000,
        status=OfferStatus.ACTIVE,
        experience=ExperienceLevel.SENIOR,
        location="Remote",
        mode_of_work=WorkMode.REMOTE,
        publication_date=date(2026, 8, 1),
        expiration_date=date(2026, 9, 1),
        last_seen_at=date(2026, 8, 5),
        url_address="https://example.com/job/python-developer",
        job_title="Senior Python Developer",
        company=test_company)

#====JobOffers====
def test_get_offer_when_exists(monkeypatch):
    fake_return_by_id = MagicMock(return_value=test_offer)
    monkeypatch.setattr(job_offer_repository, "get_by_id", fake_return_by_id)
    response = client.get("/offers/1")
    assert response.status_code == 200
    assert response.json()["offer_id"] == 1
    assert response.json()["job_title"] == "Senior Python Developer"
    fake_return_by_id.assert_called_once()

def test_get_offer_when_not_exists(monkeypatch):
    fake_return_by_id = MagicMock(return_value=None)
    monkeypatch.setattr(job_offer_repository, "get_by_id", fake_return_by_id)
    response = client.get("/offers/-1")
    assert response.status_code == 404
    assert response.json() == {"detail": "Offer not found"}
    fake_return_by_id.assert_called_once_with(db=mock.ANY,offer_id=-1)

def test_delete_offer_when_exist(monkeypatch):
    fake_return_by_id = MagicMock(return_value=test_offer)
    fake_return_delete_record_by_id = MagicMock(return_value=None)
    monkeypatch.setattr(job_offer_repository, "get_by_id", fake_return_by_id)
    monkeypatch.setattr(job_offer_service, "delete_record_by_id", fake_return_delete_record_by_id)
    response = client.delete("/offers/1")
    assert response.status_code == 204
    fake_return_by_id.assert_called_once_with(db=mock.ANY,offer_id=1)
    fake_return_delete_record_by_id.assert_called_once_with(db=mock.ANY,offer_id=1)

def test_delete_offer_when_not_exists(monkeypatch):
    fake_return_by_id = MagicMock(return_value=None)
    monkeypatch.setattr(job_offer_repository, "get_by_id", fake_return_by_id)
    response = client.delete("/offers/-1")
    assert response.status_code == 404
    assert response.json() == {"detail": "Offer not found"}
    fake_return_by_id.assert_called_once_with(db=mock.ANY,offer_id=-1)

def test_get_offers(monkeypatch):
    fake_return_search = MagicMock(return_value=[test_offer])
    monkeypatch.setattr(job_offer_repository, "search", fake_return_search)
    response = client.get("/offers")
    assert response.status_code == 200
    assert response.json()[0]["job_title"] == "Senior Python Developer"
    fake_return_search.assert_called_once()

def test_create_offer_success(monkeypatch):
    fake_fetch_page = MagicMock(return_value='<script id="serverApp-state" type="application/json">{"TestKey":"TestVal"}</script>')
    fake_parse_state_transfer = MagicMock(return_value={"TestKey1": "TestVal1", "TestKey2": {"TestKey21": "TestVal21"},"/posting/TestSlug": {"TestKey3": "TestVal3"}})
    fake_find_slug = MagicMock(return_value="TestSlug")
    fake_find_posting_data = MagicMock(return_value={"TestKey3": "TestVal3"})
    fake_create_job_offer_from_scraped_data = MagicMock(return_value={"company_name": "TestCompany","technologies": ["Python","Docker"],"job_title": "Senior Python Developer","experience": ExperienceLevel.SENIOR,"type_of_contract": ContractType.UOP,"mode_of_work": WorkMode.STATIONARY,"location": "Gliwice","publication_date": None,"expiration_date": datetime.date(2026,12,31),"url_address": "https://example.com/job/python-developer","salary_min": 15_000,"salary_max": 20_000,})
    fake_process_scraped_offer = MagicMock(return_value=test_offer)
    monkeypatch.setattr(job_offers,"fetch_page",fake_fetch_page)
    monkeypatch.setattr(job_offers,"parse_state_transfer",fake_parse_state_transfer)
    monkeypatch.setattr(job_offers,"find_offer_slug",fake_find_slug)
    monkeypatch.setattr(job_offers,"find_posting_data",fake_find_posting_data)
    monkeypatch.setattr(job_offers,"create_JobOffer_from_scraped_data",fake_create_job_offer_from_scraped_data)
    monkeypatch.setattr(job_offers,"process_scraped_offer",fake_process_scraped_offer)
    response = client.post("/offers/", json={"url_address": "https://example.com/job/python-developer"})
    assert response.status_code == 201
    assert response.json()["job_title"] == "Senior Python Developer"
    fake_fetch_page.assert_called_once()
    fake_parse_state_transfer.assert_called_once()
    fake_find_slug.assert_called_once()
    fake_find_posting_data.assert_called_once()
    fake_create_job_offer_from_scraped_data.assert_called_once()
    fake_process_scraped_offer.assert_called_once()

def test_create_offer_fail(monkeypatch):
    fake_fetch_page = MagicMock(return_value='<script id="serverApp-state" type="application/json">{"TestKey":"TestVal"}</script>')
    fake_parse_state_transfer = MagicMock(return_value={"TestKey1": "TestVal1", "TestKey2": {"TestKey21": "TestVal21"},"/posting/TestSlug": {"TestKey3": "TestVal3"}})
    fake_find_slug = MagicMock(return_value="TestSlug")
    fake_find_posting_data = MagicMock(return_value={"TestKey3": "TestVal3"})
    fake_create_job_offer_from_scraped_data = MagicMock(return_value=None)
    monkeypatch.setattr(job_offers,"fetch_page",fake_fetch_page)
    monkeypatch.setattr(job_offers,"parse_state_transfer",fake_parse_state_transfer)
    monkeypatch.setattr(job_offers,"find_offer_slug",fake_find_slug)
    monkeypatch.setattr(job_offers,"find_posting_data",fake_find_posting_data)
    monkeypatch.setattr(job_offers,"create_JobOffer_from_scraped_data",fake_create_job_offer_from_scraped_data)
    response = client.post("/offers/", json={"url_address": "https://example.com/job/python-developer"})
    assert response.status_code == 422
    fake_fetch_page.assert_called_once()
    fake_parse_state_transfer.assert_called_once()
    fake_find_slug.assert_called_once()
    fake_find_posting_data.assert_called_once()
    fake_create_job_offer_from_scraped_data.assert_called_once()

#====Stats====
@pytest.mark.parametrize("count_function_url, name_of_function_to_mocked",[
    ("/stats/offers_by_experience", "count_offers_by_experience"),
    ("/stats/offers_by_tech", "count_offers_by_technology"),
    ("/stats/offers_by_work_mode", "count_offers_by_work_mode"),
    ("/stats/offers_by_contract_type", "count_offers_by_contract"),
    ("/stats/offers_by_location", "count_offers_by_location")
])
def test_stats_count_endpoints(monkeypatch,count_function_url, name_of_function_to_mocked):
    monkeypatch.setattr(stats,name_of_function_to_mocked,MagicMock(return_value=[("Junior", 5)]))
    response = client.get(count_function_url)
    assert response.status_code == 200
    assert response.json() == [{"group_name": "Junior", "number_of_offers": 5}]

@pytest.mark.parametrize("avg_salary_function_url, name_of_function_to_mocked",[
    ("/stats/avg_salary_by_tech_and_contract", "avg_salary_by_tech_and_contract"),
    ("/stats/avg_salary_by_experience_and_contract", "avg_salary_by_experience_and_contract"),
    ("/stats/avg_salary_by_work_mode_and_contract", "avg_salary_by_mode_of_work_and_contract"),
    ("/stats/avg_salary_by_location_and_contract", "avg_salary_by_location_and_contract"),
])
def test_stats_avg_salary_endpoints(monkeypatch,avg_salary_function_url, name_of_function_to_mocked):
    monkeypatch.setattr(stats,name_of_function_to_mocked,MagicMock(return_value=[("Python", ContractType.UOP, 15_000.0, 5)]))
    response = client.get(avg_salary_function_url)
    assert response.status_code == 200
    assert response.json() == [{"avg_salary":15_000.0,"contract_type": "UOP", "group_name": "Python", "number_of_offers": 5}]
















































