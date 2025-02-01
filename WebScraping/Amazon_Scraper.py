import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time

# File paths
#product_info_file = r"C:\Users\trams\OneDrive\Desktop\#Web-Scraping-Output\Product_Info_COSRX_AMAZON_FINAL.csv"
reviews_file = r"C:\Users\trams\OneDrive\Desktop\#Web-Scraping-Output\Reviews_NEUTROGENA.csv"

# Ensure product info file exists
# if not os.path.exists(product_info_file):
#     product_info_columns = ["Brand", "Product Name",  "Rating", "Total Ratings", "Product URL"]
#     pd.DataFrame(columns=product_info_columns).to_csv(product_info_file, index=False)
#     print(f"Created product info file at: {product_info_file}")

# Ensure reviews file exists
if not os.path.exists(reviews_file):
    review_columns = ["Brand Name", "Product Name",  "Review Rating", "Review Text"]
    pd.DataFrame(columns=review_columns).to_csv(reviews_file, index=False)
    print(f"Created reviews file at: {reviews_file}")

# Initialize WebDriver
path = r'C:\Users\trams\chromedriver\chromedriver.exe'
service = Service(path)
driver = webdriver.Chrome(service=service)

product_link = "https://www.amazon.eg/-/en/Neutrogena-Balancing-Facial-Wash-200ml/dp/B07P142JYW?th=1"
driver.get(product_link)
driver.maximize_window()

product_info = {}
time.sleep(8)

# Extract product information
try:
    product_info["Brand"] = 'Neutrogena' #driver.find_element(By.XPATH, "//*[@id='dpx-premium-sourced-badge-container']/div/div[1]").text.strip()
    product_info["Product Name"] = "Oil Balancing Facial Wash, With Lime, For Oily Skin, 200ml"
    #product_info["Price"] = "16.69"
    try:
        product_info["Rating"] = driver.find_element(By.XPATH, "//*[@id='acrPopover']").text.strip()
    except:
        product_info["Rating"] = "N/A"

    try:
        product_info["Total Ratings"] = driver.find_element(By.ID, "acrCustomerReviewText").text.strip()
    except:
        product_info["Total Ratings"] = "0 ratings"

    product_info["Product URL"] = product_link
except Exception as e:
    print(f"Error while extracting product information: {e}")

# # Save product information
# try:
#     df_product_info = pd.read_csv(product_info_file)
#     df_product_info = pd.concat([df_product_info, pd.DataFrame([product_info])], ignore_index=True)
#     df_product_info.to_csv(product_info_file, index=False)
#     print("Product info file has been updated.")
# except Exception as e:
#     print(f"Error while updating product info file: {e}")

# Navigate to reviews section
try:
    reviews_all = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, "//*[@id='reviews-medley-footer']/div[2]/a"))
    )
    reviews_all.click()
except Exception as e:
    print(f"Error while navigating to reviews: {e}")

email = WebDriverWait(driver, 5).until(
    EC.presence_of_element_located((By.XPATH, '//input[@autocomplete="username"]'))
)
email.send_keys("mishi12807@gmail.com")

next_button = WebDriverWait(driver, 5).until(
    EC.element_to_be_clickable((By.XPATH, '//*[@id="continue"]'))
)
next_button.click()

time.sleep(3) 
password = WebDriverWait(driver, 5).until(
    EC.presence_of_element_located((By.XPATH, '//input[@autocomplete ="current-password"]'))
)
password.send_keys("Rimi-5t5r")

login_button = driver.find_element(By.XPATH,'//*[@id="signInSubmit"]')
login_button.click()
time.sleep(5)
#Function to extract review data
def get_review_data(driver, rId):
    try:
        #r_date = driver.find_element(By.XPATH, f'//div[@id="{rId}"]//span[@class="a-size-base a-color-secondary review-date"]').text
        r_data = driver.find_element(By.XPATH, f'//div[@id="{rId}"]//div[@class="a-row a-spacing-small review-data"]').text
        r_star = driver.find_element(By.XPATH, f'//div[@id="{rId}"]//span[@class="a-icon-alt"]').get_attribute('textContent')

        return {
            #'Date': r_date,
            'Data': r_data,
            'Star': r_star
        }
    except Exception as e:
        print(f"Error extracting review {rId}: {e}")
        return None

# Scraping reviews by star rating
reviews = []
# translate_buttons = driver.find_elements(By.XPATH, "//*[@id='a-autoid-8-announce']")
# for button in translate_buttons:
#     try:
#         button.click()
#         time.sleep(5)  # Allow translation to complete
#     except:
#         print("Error while clicking translate button for a review.")
star_filters = [
    (1, "//*[@id='star-count-dropdown_5']"),  # 1 star
    (2, "//*[@id='star-count-dropdown_4']"),  # 2 stars
    (3, "//*[@id='star-count-dropdown_3']"),  # 3 stars
    (4, "//*[@id='star-count-dropdown_2']"),  # 4 stars
    (5, "//*[@id='star-count-dropdown_1']"),  # 5 stars
]

for stars, filter_xpath in star_filters:
    try:
        # Open the star filter dropdown
        star_filter = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="a-autoid-5-announce"]')))
        star_filter.click()
        time.sleep(2)

        # Click the desired star filter
        star_filter_value = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, filter_xpath)))
        star_filter_value.click()
        time.sleep(3)

        # Scrape reviews for the selected star filter
        while True:
            try:
                
                all_reviews_wrapper = driver.find_element(By.ID, "cm_cr-review_list")
                
                translate_buttons = driver.find_elements(By.XPATH, "//a[contains(text(), 'Translate all reviews to English')]")

                if translate_buttons:  # Checks if the list is not empty
                    translate_buttons[0].click()
                    time.sleep(5)

                
                all_reviews = all_reviews_wrapper.find_elements(By.XPATH, '//div[@class="a-section celwidget"]')

                # Collect review IDs on the current page
                r_id_list = [review.get_attribute('id') for review in all_reviews]

                # Extract review data
                for rId in r_id_list:
                    review_data = get_review_data(driver, rId)
                    if review_data:
                        review_dict = {
                            "Brand Name": product_info.get("Brand", "N/A"),
                            "Product Name": product_info.get("Product Name", "N/A"),
                            #"Date": review_data.get("Date", "N/A"),
                            "Review Rating": review_data.get("Star", "N/A"),
                            "Review Text": review_data.get("Data", "N/A"),
                        }
                        reviews.append(review_dict)

                # Navigate to the next page
                try:
                    next_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//ul[@class='a-pagination']/li[@class='a-last']/a"))
                    )
                    next_button.click()
                    time.sleep(5)
                except Exception:
                    print("No more pages of reviews for this star rating.")
                    break  # Exit loop if no more pages
            except Exception as e:
                print(f"Error during review scraping for star filter: {e}")
                break
    except Exception as e:
        print(f"Error clicking star filter: {e}")
        continue

# Save reviews to CSV
try:
    if reviews:
        df_reviews = pd.read_csv(reviews_file)
        new_reviews_df = pd.DataFrame(reviews)
        df_reviews = pd.concat([df_reviews, new_reviews_df], ignore_index=True)
        df_reviews.to_csv(reviews_file, index=False)
        print("Reviews file has been updated.")
    else:
        print("No reviews extracted to add to the CSV file.")
except Exception as e:
    print(f"Error while updating reviews file: {e}")

# Close the browser
driver.quit()
