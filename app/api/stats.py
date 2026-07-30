from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.stats import CountFunction, AverageFunction
from app.repositories.stats_repository import count_offers_by_experience, count_offers_by_location, count_offers_by_technology, count_offers_by_work_mode,count_offers_by_contract, avg_salary_by_tech_and_contract,avg_salary_by_experience_and_contract,avg_salary_by_mode_of_work_and_contract,avg_salary_by_location_and_contract

router = APIRouter(prefix="/stats", tags=["stats"])

@router.get("/offers_by_experience",response_model=list[CountFunction])
def get_number_of_offers_by_experience(db: Session = Depends(get_db)):
    results = count_offers_by_experience(db)
    list_of_objects = []
    for experience,count in results:
        list_of_objects.append(CountFunction(group_name=experience,number_of_offers=count ))
    return list_of_objects


@router.get("/offers_by_tech",response_model=list[CountFunction])
def get_number_of_offers_by_tech(db: Session = Depends(get_db)):
    results = count_offers_by_technology(db)
    list_of_objects = []
    for tech, count in results:
        list_of_objects.append(CountFunction(group_name=tech, number_of_offers=count))
    return list_of_objects

@router.get("/offers_by_work_mode",response_model=list[CountFunction])
def get_number_of_offers_by_work_mode(db: Session = Depends(get_db)):
    results = count_offers_by_work_mode(db)
    list_of_objects = []
    for mode, count in results:
        list_of_objects.append(CountFunction(group_name=mode, number_of_offers=count))
    return list_of_objects

@router.get("/offers_by_contract_type",response_model=list[CountFunction])
def get_number_of_offers_by_contract_type(db: Session = Depends(get_db)):
    results = count_offers_by_contract(db)
    list_of_objects = []
    for contract, count in results:
        list_of_objects.append(CountFunction(group_name=contract, number_of_offers=count))
    return list_of_objects

@router.get("/offers_by_location",response_model=list[CountFunction])
def get_number_of_offers_by_location(db: Session = Depends(get_db)):
    results = count_offers_by_location(db)
    list_of_objects = []
    for location, count in results:
        list_of_objects.append(CountFunction(group_name=location, number_of_offers=count))
    return list_of_objects

@router.get("/avg_salary_by_tech_and_contract",response_model=list[AverageFunction])
def get_avg_salary_by_tech(db: Session = Depends(get_db)):
    results = avg_salary_by_tech_and_contract(db)
    list_of_objects = []
    for tech, contract, salary, count in results:
        list_of_objects.append(AverageFunction(avg_salary=salary, contract_type=contract, group_name=tech, number_of_offers=count))
    return list_of_objects

@router.get("/avg_salary_by_experience_and_contract",response_model=list[AverageFunction])
def get_avg_salary_by_experience(db: Session = Depends(get_db)):
    results = avg_salary_by_experience_and_contract(db)
    list_of_objects = []
    for experience, contract, salary, count in results:
        list_of_objects.append(
            AverageFunction(avg_salary=salary, contract_type=contract, group_name=experience, number_of_offers=count))
    return list_of_objects

@router.get("/avg_salary_by_work_mode_and_contract",response_model=list[AverageFunction])
def get_avg_salary_by_work_mode(db: Session = Depends(get_db)):
    results = avg_salary_by_mode_of_work_and_contract(db)
    list_of_objects = []
    for mode, contract, salary, count in results:
        list_of_objects.append(
            AverageFunction(avg_salary=salary, contract_type=contract, group_name=mode,
                            number_of_offers=count))
    return list_of_objects

@router.get("/avg_salary_by_location_and_contract",response_model=list[AverageFunction])
def get_avg_salary_by_location(db: Session = Depends(get_db)):
    results = avg_salary_by_location_and_contract(db)
    list_of_objects = []
    for location, contract, salary, count in results:
        list_of_objects.append(
            AverageFunction(avg_salary=salary, contract_type=contract, group_name=location,
                            number_of_offers=count))
    return list_of_objects