
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from seleniumCore.get_documents import getDocument, close_browser

from app import crud
from app.database import SessionLocal
from app.models import Exam, Solution

# Configuration
examTypeContainer = ['st1', 'st2', 'st5', 'st6', 'st7']
originalUrl = "https://gaokao.eol.cn/e_html/gk/gkst/2023st.shtml"
CHROMEDRIVER_PATH = "/usr/local/bin/chromedriver"

# Selenium setup
def create_driver(headless: bool = True) -> webdriver.Chrome:
    options = Options()
    options.add_argument("--headless")  # headless mode
    options.add_argument("--no-sandbox")  # recommended on Linux
    options.add_argument("--disable-dev-shm-usage")  # stability on CI

    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(originalUrl)
    return driver

# Core run loop
def run():
    driver = create_driver()
    try:
        for examType in examTypeContainer:
            try:
                container = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, f"//div[@id='{examType}']"))
                )
                type_text = container.find_element(By.CSS_SELECTOR, ".topline.clearfix .head-fl.clearfix span").text
                year = container.find_element(By.CSS_SELECTOR, ".topline.clearfix .head-fr.clearfix a").text
                subjects = container.find_element(By.CLASS_NAME, 'sline').find_element(
                By.CSS_SELECTOR,".gkzt-xueke.mtT_30.clearfix").find_elements(By.TAG_NAME, 'li')
                    

                print(f"Found {len(subjects)} subjects for {type_text} ({year})")
                for subj in subjects:
                    try:
                        name = subj.find_element(By.CLASS_NAME, 'word-xueke').text
                        exam_data = Exam(year=year, exam_type=type_text, subject=name, answers=True, country= 'china')
                        getDocument(driver, exam_data, subj, False)
                        #get the same id

                        db = SessionLocal()
                        this_exam_id = crud.get_exam(db, exam_data.exam_id)

                        driver.get(originalUrl)

                        container = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, f"//div[@id='{examType}']"))
                            )

                        getDocument(driver,  exam_data, subj, True)
                        new_exam_solution = Solution(this_exam_id)
                        
                        driver.get(originalUrl)
                    except Exception as err:
                        print(f"Subject error: {err}")
            except Exception as err:
                print(f"Exam type '{examType}' error: {err}")
    finally:
        close_browser(driver, originalUrl)

if __name__ == '__main__':
    run()
