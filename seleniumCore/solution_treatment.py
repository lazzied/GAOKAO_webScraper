import os
import time
from seleniumCore import functions
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


from app.routes.exam import read_exam
from app.routes.solution import create_solution

from app.schemas import SolutionCreate
from seleniumCore.exam_treatment import fetch_image_paths
from app.database import SessionLocal
from app.models import Exam,Solution


import os

def setup_output_folder(data) -> str:
    output_folder = os.path.expanduser(
        f"~/Documents/CEE/CEE-DATA/ASIA/CHINA/GAOKAO/{data.year}/{data.exam_type.strip()}/{data.subject.strip()}/Solution"
    )
    os.makedirs(output_folder, exist_ok=True)
    print(f"Using output folder: {output_folder}")
    return output_folder



def navigate_to_subject(driver: webdriver.Chrome,container: str):
        
        links = container.find_element(By.XPATH,".//*[@class='xueke-a']").find_elements(By.TAG_NAME, 'a')
        target = links[1]
        url = target.get_attribute("href")
        print("Navigating to:", url)
        driver.get(url)
        return



def create_pdf(image_paths: list, output_folder: str, subject: str):
    output = os.path.join(output_folder, f"{subject}.pdf")
    functions.images_to_pdf(image_paths, output)
    print(f"PDF successfully created: {output}")
    return output


def save_solution_to_db(data: Solution, total_pages, total_pages_scraped):
    db = SessionLocal()
    try:
        # Build a Pydantic input object:
        sol_in = SolutionCreate(
            exam_id=data.exam_id,
            total_pages_number=total_pages, 
            total_pages_scraped=total_pages_scraped
            )

        # Pass the schema into your crud
        record = create_solution(sol_in,db)
        print(
            f"Created Solution with ID: {record.solution_id}, "
            f"related to Exam {record.exam_id}"
        )
    except Exception as e:
        db.rollback()
        print(f"Database error: {e}")
    finally:
        db.close()

def close_browser(driver: webdriver.Chrome, Url: str):
    try:
        input("pless enter to quit")
        driver.quit()
    except Exception as e:
        print("Error quitting", e)
    

def treat_solution(driver, data: Solution, container):
    if not isinstance(driver, webdriver.Chrome):
        raise TypeError("driver must be a Chrome WebDriver instance.")
    db = SessionLocal()
    solution_exam_data = read_exam(data.exam_id,db)
    folder = setup_output_folder(solution_exam_data)
    
    navigate_to_subject(driver, container)
    images, total_pages, total_pages_scraped = fetch_image_paths(driver)
    create_pdf(images, folder, solution_exam_data.subject)
    save_solution_to_db(data,total_pages, total_pages_scraped)

    
    
        
