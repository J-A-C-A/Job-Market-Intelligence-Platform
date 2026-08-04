import datetime
from unittest.mock import MagicMock
import app.services.company_service as company_service
import app.services.technology_service as technology_service
import app.services.scraper_services as scraper_services
import app.services.job_offer_service as job_offer_service
from app.enums import ContractType, WorkMode, ExperienceLevel
from app.models import Company, Technology
from app.repositories import job_offer_repository
from app.schemas.job_offer import JobOfferCreate


#====Company====
def test_get_or_create_company_when_company_exists(monkeypatch):
    fake_db = MagicMock()
    fake_get = MagicMock(return_value="Company exists")
    monkeypatch.setattr(company_service, 'get_by_name', fake_get)
    result = company_service.get_or_create_company(fake_db,"test")
    assert result == "Company exists"
    fake_get.assert_called_once()

def test_get_or_create_company_when_company_not_exist(monkeypatch):
    fake_db = MagicMock()
    fake_get = MagicMock(return_value= None)
    fake_create = MagicMock(return_value="Company created")
    monkeypatch.setattr(company_service, 'get_by_name', fake_get)
    monkeypatch.setattr(company_service, 'create_company', fake_create)
    result = company_service.get_or_create_company(fake_db,"test")
    assert result == "Company created"
    fake_create.assert_called_once()
    fake_get.assert_called_once()

#====Tech====
def test_get_or_create_technology_when_technology_exists(monkeypatch):
    fake_db = MagicMock()
    fake_get = MagicMock(return_value="Technology exists")
    monkeypatch.setattr(technology_service, 'get_by_name', fake_get)
    result = technology_service.get_or_create_tech(fake_db,"test")
    assert result == "Technology exists"
    fake_get.assert_called_once()

def test_get_or_create_technology_when_technology_not_exist(monkeypatch):
    fake_db = MagicMock()
    fake_get = MagicMock(return_value= None)
    fake_create = MagicMock(return_value="Technology created")
    monkeypatch.setattr(technology_service, 'get_by_name', fake_get)
    monkeypatch.setattr(technology_service, 'create_technology', fake_create)
    result = technology_service.get_or_create_tech(fake_db,"test")
    assert result == "Technology created"
    fake_get.assert_called_once()
    fake_create.assert_called_once()

#====Scraper====
def test_scrape_and_save_offers_all_succeed(monkeypatch):
    fake_db = MagicMock()
    fake_offers = MagicMock(return_value=["Offer1", "Offer2", "Offer3"])
    fake_process = MagicMock()
    monkeypatch.setattr(scraper_services, 'run_scraper', fake_offers)
    monkeypatch.setattr(scraper_services, 'process_scraped_offer', fake_process)
    scraper_services.scrape_and_save_offers(fake_db)
    assert fake_process.call_count == 3

def test_scrape_and_save_offers_one_fail(monkeypatch):
    fake_db = MagicMock()
    fake_offers = MagicMock(return_value=["Offer1", "Offer2", "Offer3"])
    fake_process = MagicMock(side_effect=[None, Exception("test error"),None])
    monkeypatch.setattr(scraper_services, 'run_scraper', fake_offers)
    monkeypatch.setattr(scraper_services, 'process_scraped_offer', fake_process)
    scraper_services.scrape_and_save_offers(fake_db)
    assert fake_process.call_count == 3

#====JobOffer====
def test_create_job_offer(monkeypatch):
    sample_offer = JobOfferCreate(
        company_name="TestCompany",
        technologies=["Python", "Docker"],
        job_title="Senior Python Developer",
        url_address="https://nofluffjobs.com/pl/job/senior-python-developer-testcompany",
        salary_min=15000,
        salary_max=20000,
        type_of_contract=ContractType.UOP,
        experience=ExperienceLevel.SENIOR,
        mode_of_work=WorkMode.STATIONARY,
        location="Gliwice",
        publication_date=None,
        expiration_date=datetime.date(2026, 8, 4),
    )
    fake_db = MagicMock()
    fake_comp = MagicMock(return_value="TestCompany")
    fake_tech = MagicMock(return_value=["tech1", "tech2"])
    fake_create = MagicMock(return_value="Created")
    monkeypatch.setattr(job_offer_service, 'get_or_create_company', fake_comp)
    monkeypatch.setattr(job_offer_service, 'get_or_create_tech', fake_tech)
    monkeypatch.setattr(job_offer_service.job_offer_repository, 'create_job_offer', fake_create)
    result = job_offer_service.create_job_offer_from_scraped_data(fake_db, sample_offer)
    assert result == "Created"
    assert fake_tech.call_count == 2
    fake_comp.assert_called_once()
    fake_create.assert_called_once()
    fake_db.commit.assert_called_once()
    fake_db.refresh.assert_called_once()

def test_delete_record_by_id(monkeypatch):
    fake_db = MagicMock()
    fake_id = 1
    fake_process = MagicMock()
    monkeypatch.setattr(job_offer_service.job_offer_repository,"delete_by_id",fake_process)
    job_offer_service.delete_record_by_id(fake_db, fake_id)
    fake_process.assert_called_once()
    fake_db.commit.assert_called_once()

def test_detect_and_record_change(monkeypatch):
    fake_db = MagicMock()
    fake_old_val = MagicMock(salary_min=15000, salary_max=20000,type_of_contract= None, experience= None, mode_of_work= None, expiration_date= None, location= None)
    fake_new_val = MagicMock(salary_min=18000, salary_max=20000, type_of_contract= None, experience= None, mode_of_work= None, expiration_date= None, location= None)
    fake_process = MagicMock(return_value="Offer changed")
    monkeypatch.setattr(job_offer_service.offer_history_repository, 'create_change', fake_process)
    job_offer_service.detect_and_record_change(db=fake_db, old_offer=fake_old_val, new_offer=fake_new_val)
    fake_process.assert_called_once()
    fake_db.commit.assert_called_once()
    fake_db.refresh.assert_called_once()

def test_process_scraped_new_offer(monkeypatch):
    fake_db = MagicMock()
    fake_url = MagicMock(return_value=None)
    fake_create = MagicMock(return_value="Created")
    fake_data = MagicMock()
    fake_detect = MagicMock(return_value="Not detected")
    monkeypatch.setattr(job_offer_service.job_offer_repository, 'get_by_url', fake_url)
    monkeypatch.setattr(job_offer_service, "create_job_offer_from_scraped_data", fake_create)
    monkeypatch.setattr(job_offer_service, "detect_and_record_change", fake_detect)
    job_offer_service.process_scraped_offer(fake_db, fake_data)
    fake_url.assert_called_once()
    fake_create.assert_called_once()
    fake_detect.assert_not_called()

def test_process_scraped_old_offer(monkeypatch):
    fake_db = MagicMock()
    fake_url = MagicMock(return_value="TestUrl")
    fake_create = MagicMock(return_value="Not created")
    fake_data = MagicMock()
    fake_detect = MagicMock(return_value="Detected")
    monkeypatch.setattr(job_offer_service.job_offer_repository, 'get_by_url', fake_url)
    monkeypatch.setattr(job_offer_service, "create_job_offer_from_scraped_data", fake_create)
    monkeypatch.setattr(job_offer_service, "detect_and_record_change", fake_detect)
    job_offer_service.process_scraped_offer(fake_db, fake_data)
    fake_url.assert_called_once()
    fake_create.assert_not_called()
    fake_detect.assert_called_once()





