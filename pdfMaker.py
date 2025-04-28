import os
import time
import functions
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait  
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Setup WebDriver
service = Service("/usr/local/bin/chromedriver")
driver = webdriver.Chrome(service=service)

# Output paths
output_folder = os.path.expanduser("~/Documents/CEE/CEE-DATA/ASIA/CHINA/GAOKAO/NATIONAL A/LANGUAGE")
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
    print(f"Created output folder: {output_folder}")

try:
    originalUrl = "https://gaokao.eol.cn/e_html/gk/gkst/2023st.shtml"
    driver.get(originalUrl)

    try:
        examVersionContainer = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'st1'))
        )
    except Exception as e:
        print("Error locating examVersionContainer:", e)
        driver.save_screenshot("error_examVersionContainer.png")
        driver.quit()
        exit()

    try:
        subjectsContainer = examVersionContainer.find_element(By.CLASS_NAME, 'sline')
        subjects = subjectsContainer.find_elements(By.TAG_NAME, 'li')
        print("Number of subjects found:", len(subjects))
    except Exception as e:
        print("Error locating subjects:", e)
        driver.save_screenshot("error_subjects.png")
        driver.quit()
        exit()

    try:
        Language = subjects[0]
        examQuestions = Language.find_element(By.XPATH, ".//a[1]")
        answers = Language.find_element(By.XPATH, ".//a[2]")
    except Exception as e:
        print("Error finding examQuestions or answers:", e)
        driver.save_screenshot("error_examQuestions.png")
        driver.quit()
        exit()

    try:
        url = examQuestions.get_attribute("href")
        print("Navigating to:", url)
        driver.get(url)
    except Exception as e:
        print("Error navigating to examQuestions URL:", e)
        driver.save_screenshot("error_navigate_to_examQuestions.png")
        driver.quit()
        exit()

    try:
        pagesContainer = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@id='perpage']"))
        )
        pages = pagesContainer.find_elements(By.TAG_NAME, "a")
        numericPages = [page for page in pages if page.text.isdigit()]
        pageNumbers = len(numericPages)
        print(f"Total numeric pages found: {pageNumbers}")
    except Exception as e:
        print("Error locating or filtering pages:", e)
        driver.save_screenshot("error_pages.png")
        driver.quit()
        exit()

    imagePaths = list()
    current_page = 1
    with tqdm(total=pageNumbers, desc="Scraping pages", unit="page") as pbar:
        while current_page <= pageNumbers:
            try:
                print(f"Scraping page {current_page}")

                try:
                    imageContainer = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'TRS_Editor'))
                    )
                    image = imageContainer.find_element(By.XPATH, './/img[1]')
                    imageSource = image.get_attribute('src')

                    tempImagePath = f"temp/{current_page}.jpg"
                    resizedImagePath = f"temp/resized_a4_{current_page}.png"

                    functions.download_image(imageSource, tempImagePath)
                    functions.resize_image(tempImagePath, "temp")
                    os.remove(tempImagePath)

                    imagePaths.append(resizedImagePath)

                    print(f"Page {current_page} scraped successfully.")

                except TimeoutException:
                    print(f"Timeout: No image found on page {current_page}, skipping...")
                    driver.save_screenshot(f"timeout_page_{current_page}.png")

                except Exception as scrape_e:
                    print(f"Error scraping page {current_page}:", scrape_e)
                    driver.save_screenshot(f"error_scraping_page_{current_page}.png")

                # Now move to next page if any
                if current_page < pageNumbers:
                    try:
                        pagesContainer = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, "//div[@id='perpage']"))
                        )
                        pages = pagesContainer.find_elements(By.TAG_NAME, "a")
                        numericPages = [page for page in pages if page.text.isdigit()]
                        
                        next_link = numericPages[current_page].get_attribute("href")
                        print(f"Navigating to page {current_page + 1}: {next_link}")
                        driver.get(next_link)
                        time.sleep(2)
                    except Exception as nav_e:
                        print(f"Error navigating to page {current_page + 1}:", nav_e)
                        driver.save_screenshot(f"error_navigate_page_{current_page + 1}.png")
                        break

                current_page += 1
                pbar.update(1)

            except Exception as e:
                print(f"Unknown error at page {current_page}:", e)
                driver.save_screenshot(f"unknown_error_page_{current_page}.png")
                break  # stop completely if scraping failed

    try:
        output_pdf_path = os.path.join(output_folder, "Language_Exam.pdf")
        functions.images_to_pdf(imagePaths, output_pdf_path)
        print(f"PDF successfully created: {output_pdf_path}")
    except Exception as e:
        print("Error creating PDF:", e)

    try:
        driver.get(originalUrl)
    except Exception as e:
        print("Error navigating back to original URL:", e)

finally:
    input("Press ENTER to quit and close the browser...")
    driver.quit()
