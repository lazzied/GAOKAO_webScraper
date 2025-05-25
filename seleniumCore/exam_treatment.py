import os
import time
from seleniumCore import functions
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


from app.routes.exam import create_exam
from app.schemas import ExamCreate
from app.database import SessionLocal
from app.models import Exam
from seleniumCore.english_translation import translate_to_english


def setup_output_folder(data: Exam) -> str:
    print("here's the subject" , data.subject)
    output_folder = os.path.expanduser(
        f"~/Documents/CEE/CEE-DATA/ASIA/CHINA/GAOKAO/{data.year}/{translate_to_english[data.exam_type.strip()]}/{translate_to_english[data.subject.strip()]}/Exam"
    )
    os.makedirs(output_folder, exist_ok=True)
    print(f"Using output folder: {output_folder}")
    return output_folder

def navigate_to_subject(driver: webdriver.Chrome, container: str):
        
        links = container.find_element(By.XPATH,".//*[@class='xueke-a']").find_elements(By.TAG_NAME, 'a')
        target =links[0]
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
    output = os.path.join(output_folder, f"{translate_to_english[subject]}.pdf")
    functions.images_to_pdf(image_paths, output)
    print(f"PDF successfully created: {output}")
    return output

def save_exam_to_db(data: Exam,output):
    db = SessionLocal()
    answers_path = f"~/Documents/CEE/CEE-DATA/ASIA/CHINA/GAOKAO/{data.year}/{translate_to_english[data.exam_type.strip()]}/{translate_to_english[data.subject.strip()]}/Solution"
    try:
        # Build a Pydantic input schema instead of a SQLAlchemy model:
        exam_input = ExamCreate(
            year         = data.year,
            exam_type    = translate_to_english[data.exam_type],
            subject      = translate_to_english[data.subject],
            exam_path    = output,
            answers_path = answers_path,
            answers      = True,
            country      = "china",
            # omit exam_id—Pydantic won’t include it
        )
        record = create_exam(exam_input,db)
        print(f"Created Exam with ID: {record.exam_id}")
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
    

def treat_exam(driver, data, container):
    if not isinstance(driver, webdriver.Chrome):
        raise TypeError("driver must be a Chrome WebDriver instance.")

    folder = setup_output_folder( data )
    
    navigate_to_subject(driver, 
     container)
    images = fetch_image_paths(driver)
    output = create_pdf(images, folder, data.subject)
    save_exam_to_db(data,output)
  

    
    
        
