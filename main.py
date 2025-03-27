from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import time

options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

url = "https://www.tgju.org/profile/price_eur/history"
driver.get(url)

wait = WebDriverWait(driver, 10)

# Gregorian calendar
# start_date = datetime(2022, 5, 1)
# end_date = datetime(2025, 3, 1)
# dates = pd.date_range(start=start_date, end=end_date, freq='MS')  # MS = Month Start

dates = []

for year in range(1401, 1404):
    for month in range(1, 13):
        if year == 1403 and month > 12:
            break

        month_str = f"{month:02d}"
        date_str = f"{year}/{month_str}/12"
        dates.append(date_str)

data = []

for d in dates:
    # from_str = to_str = d.strftime("%Y/%m/%d")
    from_str = to_str = d

    try:
        from_input = wait.until(EC.presence_of_element_located((By.ID, "history-from")))
        to_input = driver.find_element(By.ID, "history-to")

        from_input.clear()
        from_input.send_keys(from_str)
        to_input.clear()
        to_input.send_keys(to_str)

        apply_btn = driver.find_element(By.XPATH, "//button[text()='انتخاب']")
        apply_btn.click()

        time.sleep(1.5)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        table = soup.find("table")
        rows = table.find_all("tr")[1:]

        if not rows:
            print(f"Data for {from_str} didn't found.")
            continue

        cols = rows[0].find_all("td")
        date_str = cols[6].text.strip()
        price_str = cols[3].text.strip().replace(",", "")

        price = int(price_str)
        # data.append((d.strftime("%Y-%m"), price))
        # print(f"{d.strftime('%Y-%m')} → {price}")
        
        price = int(price_str)
        price_short = round(price / 10000)
        data.append((d, date_str, price, price_short))
        print(f"{d} ({date_str}) → {price} → {price_short} Hezar Toman")

    except Exception as e:
        data.append((d, "", "", ""))
        print(f"Error for {from_str}: {e}")

driver.quit()

df = pd.DataFrame(data, columns=["JMonth", "GMonth", "Price", "Price(Hezar Toman)"])
df.to_csv("euro_monthly_representative_price.csv", index=False)
print("✅ Saved.")
