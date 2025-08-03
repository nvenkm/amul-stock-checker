from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import sys
import os
import logging
from datetime import datetime
import argparse
import json
import requests
from config import PRODUCT_URL, PINCODE, STATUS_FILE, NTFY_TOPIC
from notifier import send_ntfy_notification

class AmulStockChecker:
    def __init__(self, headless=True, log_file=None):
        """Initialize the web scraper with Chrome options"""
        self.setup_logging(log_file)
        self.clean_cron_log_file()
        self.setup_driver(headless)
        self.wait = WebDriverWait(self.driver, 15)
        self.pincode = PINCODE

        self.product_url = PRODUCT_URL
        # self.product_url = "https://shop.amul.com/en/product/amul-organic-bajra-flour-500-g"
        self.status_file = STATUS_FILE
        self.ntfy_topic = NTFY_TOPIC
        self.ntfy_url = f"https://ntfy.sh/{self.ntfy_topic}"
        
    def setup_logging(self, log_file=None):
        """Setup logging configuration"""
        if log_file is None:
            log_file = f"amul_stock_checker_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_driver(self, headless):
        """Setup Chrome driver with appropriate options"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.logger.info("✓ Chrome driver initialized successfully")
        except Exception as e:
            self.logger.error(f"✗ Failed to initialize Chrome driver: {e}")
            self.logger.error("Make sure ChromeDriver is installed and in PATH")
            sys.exit(1)
    
    def navigate_to_product(self):
        """Navigate to the product page"""
        try:
            self.logger.info(f"🌐 Navigating to: {self.product_url}")
            self.driver.get(self.product_url)
            
            # Wait for page to load
            self.wait.until(EC.presence_of_element_located((By.ID, "search")))
            self.logger.info("✓ Product page loaded successfully")
            return True
            
        except TimeoutException:
            self.logger.error("✗ Failed to load product page - timeout")
            return False
        except Exception as e:
            self.logger.error(f"✗ Error navigating to product: {e}")
            return False
    
    def handle_pincode_popup(self):
        """Handle the pincode popup and enter the pincode"""
        try:
            self.logger.info("🔍 Looking for pincode input popup...")
            
            # Wait for the pincode input to appear
            # pincode_input = self.wait.until(
            #     EC.element_to_be_clickable((By.ID, "search"))
            # )
            for _ in range(10):
                try:
                    pincode_input = self.driver.find_element(By.ID, "search")
                    if pincode_input.is_displayed() and pincode_input.is_enabled():
                        break
                except:
                    pass
                time.sleep(1)
            else:
                self.logger.error("✗ Pincode input field not interactable after retries")
                return False

            self.logger.info("✓ Found pincode input field")
            
            # Clear and enter pincode
            pincode_input.clear()
            pincode_input.send_keys(self.pincode)
            self.logger.info(f"✓ Entered pincode: {self.pincode}")
            
            # Wait for debouncing to complete
            self.logger.info("⏳ Waiting for search results (debouncing)...")
            time.sleep(2)
            
            return True
            
        except TimeoutException:
            self.logger.error("✗ Pincode input field not found - timeout")
            return False
        except Exception as e:
            self.logger.error(f"✗ Error handling pincode popup: {e}")
            return False
    
    def select_pincode_from_dropdown(self):
        """Select the pincode from the dropdown results"""
        try:
            self.logger.info("🔍 Looking for pincode in dropdown...")
            
            # Wait for the dropdown item to appear and be clickable
            dropdown_item = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.searchitem-name"))
            )
            
            # Verify it contains our pincode
            pincode_text = dropdown_item.find_element(By.CSS_SELECTOR, "p.item-name").text
            if self.pincode in pincode_text:
                self.logger.info(f"✓ Found pincode option: {pincode_text}")
                dropdown_item.click()
                self.logger.info("✓ Clicked on pincode option")
                return True
            else:
                self.logger.error(f"✗ Expected pincode {self.pincode} but found {pincode_text}")
                return False
                
        except TimeoutException:
            self.logger.error("✗ Pincode dropdown option not found - timeout")
            return False
        except Exception as e:
            self.logger.error(f"✗ Error selecting pincode from dropdown: {e}")
            return False
    
    def check_stock_status(self):
        """Check if the product is in stock or sold out based on the sold out div"""
        try:
            self.logger.info("⏳ Waiting for new page to load...")
            
            # Wait a bit for page transition
            time.sleep(3)
            
            # Wait for the page content to load properly
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # Check specifically for the sold out div
            try:
                sold_out_div = self.driver.find_element(
                    By.CSS_SELECTOR, "div.alert.alert-danger.mt-3"
                )
                
                # Verify the div contains "Sold Out" text
                if sold_out_div.is_displayed() and "Sold Out" in sold_out_div.text:
                    self.logger.info("❌ Product Status: SOLD OUT")
                    self.logger.info(f"Found sold out div: {sold_out_div.text.strip()}")
                    return "SOLD_OUT"
                    
            except NoSuchElementException:
                # If the sold out div is not found, product is in stock
                self.logger.info("✅ Product Status: IN STOCK")
                self.logger.info("Sold out div not found - product is available")

                # Fix: Get the text from the WebElement first
                product_name_element = self.driver.find_element(By.CLASS_NAME, "product-name")
                product_name_string = product_name_element.text  # Get the text content
                
                # Now you can use string methods
                if "," in product_name_string:
                    product_name = product_name_string[:product_name_string.index(",")]
                else:
                    product_name = product_name_string  # Use full text if no comma found
                
                # Send notification for stock availability
                send_ntfy_notification(
                    logger=self.logger,
                    ntfy_url=self.ntfy_url,
                    message=f"🚨 {product_name} is IN STOCK! Check now: {self.product_url}",
                    ntfy_topic=self.ntfy_topic
                )
                return "IN_STOCK"
            
            # If we found the div but it doesn't contain "Sold Out", check its content
            if sold_out_div:
                self.logger.warning(f"⚠️ Found alert div but unexpected content: {sold_out_div.text.strip()}")
                return "UNKNOWN"
                
        except TimeoutException:
            self.logger.error("✗ Page failed to load properly - timeout")
            return "ERROR"
        except Exception as e:
            self.logger.error(f"✗ Error checking stock status: {e}")
            return "ERROR"
    
    def save_status(self, status):
        """Save the current stock status to a JSON file"""
        try:
            status_data = {
                "timestamp": datetime.now().isoformat(),
                "status": status,
                "pincode": self.pincode,
                "product_url": self.product_url
            }
            
            with open(self.status_file, "w") as f:
                json.dump(status_data, f, indent=2)
            
            self.logger.info(f"💾 Status saved to {self.status_file}")
            
        except Exception as e:
            self.logger.error(f"✗ Error saving status: {e}")
    
    def load_previous_status(self):
        """Load the previous stock status from JSON file"""
        try:
            if os.path.exists(self.status_file):
                with open(self.status_file, "r") as f:
                    return json.load(f)
            return None
        except Exception as e:
            self.logger.error(f"✗ Error loading previous status: {e}")
            return None
    
    def send_notification(self, status, previous_status=None):
        """Send notification if status changed from SOLD_OUT to IN_STOCK"""
        if previous_status and previous_status.get("status") == "SOLD_OUT" and status == "IN_STOCK":
            self.logger.info("🚨 STOCK ALERT: Product is now IN STOCK! 🚨")
            # Here you can add email, SMS, or other notification methods
            # For example, you could integrate with Twilio, SendGrid, etc.
            
            # Simple desktop notification (works on Linux/macOS)
            try:
                os.system(f'notify-send "Amul Stock Alert" "Product is now IN STOCK for pincode {self.pincode}!"')
            except:
                pass
        elif status != previous_status.get("status") if previous_status else None:
            self.logger.info(f"📊 Status changed from {previous_status.get('status') if previous_status else 'N/A'} to {status}")
    
    def run_stock_check(self):
        """Run the complete stock checking process"""
        self.logger.info("🚀 Starting Amul Product Stock Check")
        self.logger.info("=" * 50)
        
        # Load previous status for comparison
        previous_status = self.load_previous_status()
        
        try:
            # Step 1: Navigate to product page
            if not self.navigate_to_product():
                return False
            
            # Step 2: Handle pincode popup
            if not self.handle_pincode_popup():
                return False
            
            # Step 3: Select pincode from dropdown
            if not self.select_pincode_from_dropdown():
                return False
            
            # Step 4: Check stock status
            status = self.check_stock_status()
            
            # Step 5: Save status and send notifications
            # self.save_status(status)
            # self.send_notification(status, previous_status)
            
            self.logger.info("=" * 50)
            self.logger.info(f"🎯 FINAL RESULT: {status}")
            
            return status != "ERROR"
            
        except Exception as e:
            self.logger.error(f"✗ Unexpected error during stock check: {e}")
            return False
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        try:
            self.driver.quit()
            print("🧹 Browser closed successfully \n\n")
        except Exception as e:
            print(f"⚠️ Error during cleanup: {e}")

    def cleanup(self):
        """Clean up resources"""
        try:
            self.driver.quit()
            self.logger.info("🧹 Browser closed successfully \n\n")
        except Exception as e:
            self.logger.error(f"⚠️ Error during cleanup: {e}")

    def clean_cron_log_file(self):
        """Clean the cron log file if it exceeds size of 500Kbs """
        # Log file path --> log/amul-log.log
        log_file_path = os.path.join(os.path.dirname(__file__), 'log', 'amul-log.log')
        if os.path.exists(log_file_path) and os.path.getsize(log_file_path) > 500 * 1024:
            try:
                with open(log_file_path, 'w') as log_file:
                    log_file.write("")  # Clear the file content
                self.logger.info("🗑️ Cron log file cleaned successfully")
            except Exception as e:
                self.logger.error(f"⚠️ Error cleaning cron log file: {e}")
        else:
            self.logger.info("🗑️ Cron log file size is within limits, no cleaning needed")
