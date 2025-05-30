import os
import time
from seleniumCore import functions
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import shutil

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

def fetch_image_paths(driver: webdriver.Chrome):
    pages_container = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'perpage'))
    )
    children = pages_container.find_elements(By.XPATH, "./*")
    total = int(children[-1].text.split()[1])
    print(f"Total pages: {total}")

    total_pages_scraped = 0
    image_paths = []
    current_page = 1

    def get_visible_page_links():
        pages = driver.find_element(By.ID, 'perpage').find_elements(By.TAG_NAME, "a")
        return {
            int(p.text): p.get_attribute("href")
            for p in pages if p.text.isdigit()
        }

    page_links = get_visible_page_links()

    # Check if the blank placeholder image exists
    if not os.path.exists("seleniumCore/assets/blank.jpeg"):
        raise FileNotFoundError("Blank placeholder image not found at seleniumCore/assets/blank.jpeg")

    while current_page <= total:
        temp = f"temp/{current_page}.jpg"
        try:
            print(f"\nScraping page {current_page}")

            image = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'TRS_Editor'))
            ).find_element(By.XPATH, './/img[1]')

            if image:
                src = image.get_attribute('src')
                print(f"Attempting to download image from: {src}")

                success = functions.download_image(src, temp)
                if success:
                    total_pages_scraped += 1
                    print(f"✅ Page {current_page} scraped successfully.")
                else:
                    print(f"❌ Failed to download image for page {current_page}. Using blank placeholder.")
                    shutil.copy("seleniumCore/assets/blank.jpeg", temp)
                    total_pages_scraped += 1  # Count as scraped since we have a placeholder

        except TimeoutException:
            print(f"⏰ Timeout: No image found on page {current_page}. Using blank placeholder.")
            shutil.copy("seleniumCore/assets/blank.jpeg", temp)
            total_pages_scraped += 1  # Count as scraped since we have a placeholder

        except Exception as e:
            print(f"⚠️ Error scraping page {current_page}: {e}. Using blank placeholder.")
            shutil.copy("seleniumCore/assets/blank.jpeg", temp)
            total_pages_scraped += 1  # Count as scraped since we have a placeholder

        image_paths.append(temp)

        # Update visible page links
        new_links = get_visible_page_links()
        for k, v in new_links.items():
            if k not in page_links:
                page_links[k] = v

        if current_page + 1 in page_links:
            next_link = page_links[current_page + 1]
            print(f"➡️ Navigating to page {current_page + 1}: {next_link}")
            driver.get(next_link)
            time.sleep(2)
        else:
            print(f"❌ No link for page {current_page + 1}, stopping.")
            break

        current_page += 1

    return image_paths, total, total_pages_scraped




def create_pdf(image_paths: list, output_folder: str, subject: str):
    output = os.path.join(output_folder, f"{translate_to_english[subject]}.pdf")
    
    # ✅ If PDF already exists, remove it
    if os.path.exists(output):
        print(f"PDF already exists. Replacing: {output}")
        os.remove(output)

    functions.images_to_pdf(image_paths, output)
    print(f"PDF successfully created: {output}")
    return output

def save_exam_to_db(data: Exam,output,total_pages, total_pages_scraped):
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
            total_pages_number= total_pages, 
            total_pages_scraped= total_pages_scraped

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
    images, total_pages, total_pages_scraped = fetch_image_paths(driver)
    output = create_pdf(images, folder, data.subject)
    save_exam_to_db(data,output,total_pages, total_pages_scraped)
  

    
    
        
