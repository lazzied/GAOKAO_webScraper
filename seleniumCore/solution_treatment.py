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

def fetch_image_paths(driver: webdriver.Chrome) -> list:
    pages_container = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'perpage'))
    )
    pages = pages_container.find_elements(By.TAG_NAME, "a")
    numeric = [p for p in pages if p.text.isdigit()]
    total = len(numeric)
    print(f"Total numeric pages found: {total}")
    pages_container = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, "//*[@id='perpage']")))
    pages = pages_container.find_elements(By.TAG_NAME, "a")
    numeric = [p for p in pages if p.text.isdigit()]
    page_links = [p.get_attribute("href") for p in numeric]


    image_paths = []
    for current in tqdm(range(1, total + 1), desc="Scraping pages", unit="page"):
        try:
            print(f"Scraping page {current}")
            image = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'TRS_Editor'))
            ).find_element(By.XPATH, './/img[1]')
            src = image.get_attribute('src')

            temp = f"temp/{current}.jpg"
            resized = f"temp/resized_a4_{current}.png"

            functions.download_image(src, temp)
            functions.resize_image(temp, "temp")
            os.remove(temp)

            image_paths.append(resized)
            print(f"Page {current} scraped successfully.")

        except TimeoutException:
            print(f"Timeout: No image found on page {current}, skipping...")
        except Exception as e:
            print(f"Error scraping page {current}:", e)

        if current < total:
            try:
                

                next_link = page_links[current]
                print(f"Navigating to page {current+1}: {next_link}")
                driver.get(next_link)
                time.sleep(2)
            except Exception as e:
                print(f"Error navigating to page {current+1}:", e)
                break
    return image_paths

def create_pdf(image_paths: list, output_folder: str, subject: str):
    output = os.path.join(output_folder, f"{subject}.pdf")
    functions.images_to_pdf(image_paths, output)
    print(f"PDF successfully created: {output}")
    return output


def save_solution_to_db(data: Solution):
    db = SessionLocal()
    try:
        # Build a Pydantic input object:
        sol_in = SolutionCreate(exam_id=data.exam_id)

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
    images = fetch_image_paths(driver)
    create_pdf(images, folder, solution_exam_data.subject)
    save_solution_to_db(data)

    
    
        
