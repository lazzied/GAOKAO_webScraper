
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from seleniumCore.exam_treatment import treat_exam, close_browser
from seleniumCore.solution_treatment import treat_solution, close_browser


from app.routes.exam import read_last_exam
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

def safe_get(driver, url, timeout=20):
    try:
        driver.set_page_load_timeout(timeout)
        driver.get(url)
    except TimeoutException:
        driver.execute_script("window.stop();")

# Core run loop
def run():
    driver = create_driver()
    
    for examType in examTypeContainer:
        safe_get(driver, originalUrl)

        container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f"//div[@id='{examType}']"))
        )

        type_text = container.find_element(By.CSS_SELECTOR, ".topline.clearfix .head-fl.clearfix span").text
        year = container.find_element(By.CSS_SELECTOR, ".topline.clearfix .head-fr.clearfix a").text

        subject_elements = container.find_element(By.CLASS_NAME, 'sline') \
                            .find_element(By.CSS_SELECTOR, ".gkzt-xueke.mtT_30.clearfix") \
                            .find_elements(By.TAG_NAME, 'li')

        print(f"Found {len(subject_elements)} subjects for {type_text} ({year})")

        for i in range(len(subject_elements)):
            # Re-fetch page and subject list to prevent stale elements
            safe_get(driver, originalUrl)

            container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, f"//div[@id='{examType}']"))
            )
            subject_elements = container.find_element(By.CLASS_NAME, 'sline') \
                                .find_element(By.CSS_SELECTOR, ".gkzt-xueke.mtT_30.clearfix") \
                                .find_elements(By.TAG_NAME, 'li')

            subj = subject_elements[i]  # fresh WebElement
            name = subj.find_element(By.CLASS_NAME, 'word-xueke').text.split('\n')[0].strip()

            exam_data = Exam(
                year=year,
                exam_type=type_text,
                subject=name,
                answers=True,
                country='china'
            )
            treat_exam(driver, exam_data, subj)

            db = SessionLocal()
            last_exam = read_last_exam(db) 
            this_exam_id = last_exam.exam_id if last_exam else 0
            db.close()

            # Again re-fetch to avoid stale elements
            safe_get(driver, originalUrl)
            container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, f"//div[@id='{examType}']"))
            )
            all_li = container.find_elements(
                By.CSS_SELECTOR, ".gkzt-xueke.mtT_30.clearfix li"
            )

            matched = next(
                li for li in all_li
                if li.find_element(By.CLASS_NAME, "word-xueke").text.split('\n')[0].strip() == name
            )

            solution_data = Solution(exam_id=this_exam_id)
            treat_solution(driver, solution_data, matched)

            print("moving to next exam")

    close_browser(driver, originalUrl)


if __name__ == '__main__':
    run()
