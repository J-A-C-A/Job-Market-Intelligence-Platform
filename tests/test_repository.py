import datetime
import pytest
from unittest.mock import MagicMock
from app.repositories.company_repository import get_by_name, create_company
from app.repositories.technology_repository import get_by_name,create_technology
from app.repositories.job_offer_repository import get_by_id, get_by_url, delete_by_id, create_job_offer, search
from app.repositories.offer_history_repository import get_by_offer_id, create_change
from app.repositories.stats_repository import count_offers_by_experience,count_offers_by_technology,count_offers_by_location, count_offers_by_contract, count_offers_by_work_mode, avg_salary_by_tech_and_contract, avg_salary_by_experience_and_contract, avg_salary_by_mode_of_work_and_contract,avg_salary_by_location_and_contract

#====Company====
def test_get_by_name_company():
    fake_db = MagicMock()
    fake_db.execute.return_value.scalar_one_or_none.return_value = "test"
    result = get_by_name(fake_db, "test")
    assert result == "test"

def test_create_company():
    fake_db = MagicMock()
    result = create_company(fake_db, "test")
    passed_object = fake_db.add.call_args[0][0]
    assert passed_object.name == "test"
    fake_db.commit.assert_called_once()
    fake_db.refresh.assert_called_once()
    assert result.name == "test"


#====Tech====
def test_get_by_name_tech():
    fake_db = MagicMock()
    fake_db.execute.return_value.scalar_one_or_none.return_value = "test"
    result = get_by_name(fake_db, "test")
    assert result == "test"

def test_create_tech():
    fake_db = MagicMock()
    result = create_technology(fake_db, "test")
    passed_object = fake_db.add.call_args[0][0]
    assert passed_object.name == "test"
    fake_db.commit.assert_called_once()
    fake_db.refresh.assert_called_once()
    assert result.name == "test"

#====JobOffer====
def test_get_job_offer_by_url():
    fake_db = MagicMock()
    fake_db.execute.return_value.scalar_one_or_none.return_value = "test"
    result = get_by_url(fake_db, "test")
    assert result == "test"

def test_get_job_offer_by_id():
    fake_db = MagicMock()
    fake_db.execute.return_value.scalar_one_or_none.return_value = 1
    result = get_by_id(fake_db, 1)
    assert result == 1

def test_create_job_offer():
    fake_db = MagicMock()
    fake_company = MagicMock()
    fake_technology = [MagicMock()]
    fake_offer_data = {"job_title": "test"}
    result = create_job_offer(db= fake_db,offer_data= fake_offer_data ,company=fake_company, technologies=fake_technology)
    passed_object = fake_db.add.call_args[0][0]
    assert passed_object.job_title == "test"

def test_delete_job_offer_by_id():
    fake_db = MagicMock()
    delete_by_id(fake_db, 1)
    fake_db.execute.assert_called_once()

def test_search():
    fake_db = MagicMock()
    fake_db.execute.return_value.scalars.return_value.all.return_value = ["test1","test2"]
    result = search(fake_db)
    assert result == ["test1", "test2"]

#====OfferHistory====
def test_get_by_offer_id():
    fake_db = MagicMock()
    fake_db.execute.return_value.scalars.return_value.all.return_value = 1
    result = get_by_offer_id(fake_db, 1)
    assert result == 1

def test_create_change():
    fake_db = MagicMock()
    fake_field = "test_field"
    fake_date = datetime.date(2026,8,4)
    fake_old_val = "test_val1"
    fake_new_val = "test_val2"
    result = create_change(db=fake_db,offer_id= 1, field_changed= fake_field,change_at= fake_date, old_value= fake_old_val,new_value= fake_new_val)
    passed_object = fake_db.add.call_args[0][0]
    assert passed_object.field_changed == "test_field"
    fake_db.commit.assert_called_once()
    fake_db.refresh.assert_called_once()

#====Stats====
@pytest.mark.parametrize("stats_function",[
    count_offers_by_experience,
    count_offers_by_technology,
    count_offers_by_location,
    count_offers_by_contract,
    count_offers_by_work_mode,
    avg_salary_by_tech_and_contract,
    avg_salary_by_experience_and_contract,
    avg_salary_by_mode_of_work_and_contract,
    avg_salary_by_location_and_contract
])
def test_stats_function(stats_function):
    fake_db = MagicMock()
    fake_db.execute.return_value.all.return_value = [("test",1)]
    result = stats_function(fake_db)
    assert result == [("test",1)]
