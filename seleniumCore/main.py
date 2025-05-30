
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from seleniumCore.exam_treatment import treat_exam, close_browser
from seleniumCore.solution_treatment import treat_solution, close_browser

from seleniumCore.english_translation import translate_to_english

from app.routes.exam import read_last_exam, partial_update_exam
from app.database import SessionLocal
from app.models import Exam, Solution
from app.schemas import ExamUpdate

# Configuration
examTypeContainer = ['st1', 'st2', 'st5', 'st6', 'st7']
originalUrl = "https://gaokao.eol.cn/e_html/gk/gkst/2023st.shtml"
CHROMEDRIVER_PATH = "/usr/local/bin/chromedriver"

def is_exam_already_processed(db, year, exam_type, subject):
    exam = db.query(Exam).filter_by(
        year=year, exam_type=exam_type, subject=subject, country='china'
    ).first()
    
    if not exam:
        return False, False  # exam not processed, solution not processed
    
    has_solution = db.query(Solution).filter_by(exam_id=exam.exam_id).first()  is not None and exam.answers
    return True, has_solution  # exam processed, solution status


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
    db = SessionLocal()
    for examType in examTypeContainer:
        print(examType)
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
            # Re-fetch elements
            safe_get(driver, originalUrl)
            container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, f"//div[@id='{examType}']"))
            )
            subject_elements = container.find_element(By.CLASS_NAME, 'sline') \
                                    .find_element(By.CSS_SELECTOR, ".gkzt-xueke.mtT_30.clearfix") \
                                    .find_elements(By.TAG_NAME, 'li')

            subj = subject_elements[i]
            name = subj.find_element(By.CLASS_NAME, 'word-xueke').text.split('\n')[0].strip()


            exam_processed, solution_processed = is_exam_already_processed(db, year, translate_to_english[type_text], translate_to_english[name])

            if exam_processed == False:

                exam_data = Exam(
                    year=year,
                    exam_type=type_text,
                    subject=name,
                    answers=True,
                    country='china'
                )
                treat_exam(driver, exam_data, subj)

                last_exam = read_last_exam(db)
                this_exam_id = last_exam.exam_id if last_exam else 0

                # Re-fetch to avoid stale elements
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

            elif exam_processed == True and solution_processed == False : 
                print("solution is missing")
                last_exam = read_last_exam(db)
                this_exam_id = last_exam.exam_id if last_exam else 0

                # Re-fetch to avoid stale elements
                safe_get(driver, originalUrl)
                try:
                    
                    container = WebDriverWait(driver, 15).until(
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
                except TimeoutException:
                    print('skipping solution - container not found')
                    # update the exam to have a solution set to false
                    partial_update_exam(this_exam_id, ExamUpdate(answers=False), db)
                    
            else:
                print("exam and its solution already exist")
                continue


    db.close()
    close_browser(driver, originalUrl)



if __name__ == '__main__':
    run()
