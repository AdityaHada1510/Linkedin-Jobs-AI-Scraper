# scraper/linkedin_browser.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

def get_driver():
    options = Options()
    # options.add_argument("--headless=new")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def close_sign_in_modal(driver):
    try:
        # Wait for modal close button to become present and clickable
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "contextual-sign-in-modal__modal-dismiss"))
        )

        close_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "contextual-sign-in-modal__modal-dismiss"))
        )

        driver.execute_script("arguments[0].click();", close_button)  # JS click is more reliable
        print("✅ Modal closed with JavaScript click.")
        time.sleep(1)  # small buffer

    except Exception as e:
        print("⚠️ Modal not found or failed to close:", e)



def scrape_linkedin_jobs_from_url(url: str, max_jobs=5):
    driver = get_driver()
    driver.get(url)
    time.sleep(3)  # let page load
    close_sign_in_modal(driver)

    jobs_data = []
    job_cards = driver.find_elements(By.CLASS_NAME, "base-card")

    scraped_urls = set()

    i = 0
    while i < max_jobs:
        try:
            # Re-fetch job cards every time
            job_cards = driver.find_elements(By.CLASS_NAME, "base-card")

            if i >= len(job_cards):
                print("⚠️ No more job cards to process.")
                break

            card = job_cards[i]

            driver.execute_script("arguments[0].scrollIntoView(true);", card)
            time.sleep(1)

            # Get current job description element to check for staleness
            try:
                old_desc = driver.find_element(By.CLASS_NAME, "show-more-less-html__markup")
            except:
                old_desc = None

            card.click()

            if old_desc:
                WebDriverWait(driver, 10).until(EC.staleness_of(old_desc))

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "show-more-less-html__markup"))
            )

            soup = BeautifulSoup(driver.page_source, "html.parser")
            title = soup.find("h2", class_="top-card-layout__title")
            company = soup.find("span", class_="topcard__flavor")
            location = soup.find("span", class_="topcard__flavor topcard__flavor--bullet")
            job_desc = soup.find("div", class_="show-more-less-html__markup")
            job_url = driver.current_url

            # De-duplication
            if job_url in scraped_urls:
                i += 1
                continue

            jobs_data.append({
                "Job Title": title.get_text(strip=True) if title else None,
                "Company": company.get_text(strip=True) if company else None,
                "Location": location.get_text(strip=True) if location else None,
                "Description": job_desc.get_text(" ", strip=True) if job_desc else None,
                "URL": job_url
            })

            scraped_urls.add(job_url)
            print(f"✅ Scraped job {i + 1}: {title.get_text(strip=True) if title else 'Unknown Title'}")

        except Exception as e:
            print(f"❌ Error scraping job {i+1}: {e}")
        finally:
            i += 1


    driver.quit()
    return jobs_data
