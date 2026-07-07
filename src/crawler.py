import datetime
import random
import re
import time
import urllib.parse
import os
import requests
from bs4 import BeautifulSoup
import moment

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class LinkedInCrawler:
    def __init__(self, account_manager, logger, publisher, client_id: int):
        self.account_manager = account_manager
        self.logger = logger
        self.publisher = publisher
        self.client_id = client_id
        
        self.driver = None
        self.current_username = None
        self.start_time = time.time()
        self.debug_dir = "debug_image"
        
    def init_driver(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-impl-side-painting')
        chrome_options.add_argument('--disable-gpu-sandbox')
        chrome_options.add_argument('--disable-accelerated-2d-canvas')
        chrome_options.add_argument('--disable-accelerated-jpeg-decoding')
        chrome_options.add_argument('--test-type=ui')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--allow-running-insecure-content')
        chrome_options.add_argument('--window-size=1024x800')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        self.driver = webdriver.Chrome(options=chrome_options)

    def close_driver(self):
        if self.driver:
            try:
                self.driver.close()
                self.driver.quit()
            except Exception as e:
                print(f"[WARNING] Error closing driver: {e}")
            self.driver = None

    def dummy_wait(self, wait_time: int):
        print(f"[INFO] Waiting for {wait_time} second...")
        try:
            wait = WebDriverWait(self.driver, wait_time)
            wait.until(EC.visibility_of_element_located((By.XPATH, "ul")))
        except Exception:
            pass

    def logout(self) -> str:
        try:
            self.driver.get("https://www.linkedin.com/m/logout/")
        except Exception as e:
            print("[INFO] Logout failed", e)
            pass
        return str(self.driver.page_source)

    def login(self) -> int:
        available_account = None
        try:
            available_account = self.account_manager.get_available_account()
            print(f"[INFO] Available Account: {available_account}")
        except Exception as e:
            print("[ERROR] Failed to read local account file. Please check accounts.json")
            self.logger.generate_log(
                4601,
                "Failed to read local account file.",
                "login",
                {
                    "client_id": str(self.client_id),
                    "error": str(e)
                },
                self.start_time
            )
            return 0

        if available_account is None:
            print("[INFO] No available account or cookie for use")
            self.logger.generate_log(
                4401,
                "No available account or cookie for use.",
                "login",
                {
                    "client_id": str(self.client_id),
                },
                self.start_time
            )
            return 0

        self.current_username = available_account['username']
        # Set account in use
        accounts = self.account_manager.load_accounts()
        for acc in accounts:
            if acc.get("username") == self.current_username:
                acc["in_use"] = True
        self.account_manager.save_accounts(accounts)

        try:
            print(f"[INFO] Start login with username: {self.current_username}")
            self.driver.get("https://www.linkedin.com/login")
            self.dummy_wait(5)
            print("[INFO] Insert username and password")
        except Exception as e:
            print(f"[DEBUG] Error pas isi form: {e}")

        # Polling for login success (redirected to feed or global-nav present)
        timeout = 300
        start_wait = time.time()
        logged_in = False
        print("[INFO] Waiting for user to complete login/captcha in the browser...")
        
        while time.time() - start_wait < timeout:
            current_url = self.driver.current_url
            if "linkedin.com/feed" in current_url:
                logged_in = True
                break
            try:
                # global-nav is only visible when logged in
                self.driver.find_element(By.CLASS_NAME, 'global-nav')
                logged_in = True
                break
            except Exception:
                pass
            
            elapsed = int(time.time() - start_wait)
            if elapsed % 10 == 0:
                print(f"[INFO] Waiting for login/captcha completion... ({elapsed}s elapsed)")
            time.sleep(2)
            
        if logged_in:
            print("[INFO] Login success detected!")
        else:
            print("[WARNING] Login timeout reached.")

        self.driver.get("https://www.linkedin.com/")
        self.dummy_wait(3)
        print("[DEBUG] ========================= RENDER TEST")
        page = self.driver.find_element(By.XPATH, "//html").get_attribute("innerText")
        print(page)
        print("[DEBUG] ========================= RENDER TEST")

        found = None
        try:
            found = self.driver.find_element(By.CLASS_NAME, 'nav__button-secondary').text
            print("[INFO] Found =>", found)
        except Exception:
            pass

        if found is None:
            status = 1
            print("[INFO] Finish login")
        else:
            status = 0
            print("[INFO] Failed to login, please check the account.")
            self.logger.generate_log(
                4504,
                "Failed to login, please check the account.",
                "login",
                {
                    "client_id": str(self.client_id),
                    "username": self.current_username
                },
                self.start_time
            )
            self.kill_service("Failed to login, please check the account.")

        return status

    def check_login_status(self) -> dict:
        print("[INFO] Check login status")
        self.driver.get("http://www.linkedin.com")

        is_login = True
        found = None
        try:
            found = self.driver.find_element(By.CLASS_NAME, 'nav__button-secondary').text
        except Exception:
            pass

        if found is not None:
            is_login = False

        result = {"is_login": is_login}

        if not is_login:
            self.logger.generate_log(
                4502,
                "Access failed - The status of the search page may be logged out, immediately check the status of the account being used.",
                "login",
                {
                    "client_id": str(self.client_id),
                    "username": self.current_username,
                    "cookies": None,
                },
                self.start_time
            )
            self.kill_service("Access failed - The status of the search page may be logged out, immediately check the status of the account being used.")

        return result

    def do_check_login(self):
        check = self.check_login_status()
        if not check['is_login']:
            try:
                print("[INFO] Relogin..")
                do_login = self.login()
                print(f"[INFO] Do relogin again {do_login}")
                time.sleep(3)
            except Exception as e:
                print("[ERROR] Failed login:", e)

    def extract_update_urns_from_dom(self, post_urls: list, seen: set) -> int:
        added = 0
        src = self.driver.page_source or ""

        ugc_patterns = [
            r'userGeneratedContentId=(\d{19})',
            r'urn:li:ugcPost:(\d{19})',
            r'userGeneratedContentPostUrn=UserGeneratedContentPostUrn\(userGeneratedContentId=(\d{19})\)',
        ]

        share_patterns = [
            r'shareId=(\d{19})',
            r'urn:li:share:(\d{19})',
            r'ShareUrn\(shareId=(\d{19})\)',
        ]

        ugc_ids = set()
        share_ids = set()

        for pattern in ugc_patterns:
            ugc_ids.update(re.findall(pattern, src))

        for pattern in share_patterns:
            share_ids.update(re.findall(pattern, src))

        for ugc_id in ugc_ids:
            raw_post_id = f"urn:li:ugcPost:{ugc_id}"
            url = f"https://www.linkedin.com/feed/update/{raw_post_id}/"

            if url not in seen:
                seen.add(url)
                post_urls.append(url)
                added += 1

        for share_id in share_ids:
            raw_post_id = f"urn:li:share:{share_id}"
            url = f"https://www.linkedin.com/feed/update/{raw_post_id}/"

            if url not in seen:
                seen.add(url)
                post_urls.append(url)
                added += 1

        return added

    def save_debug_screenshot(self, name: str):
        os.makedirs(self.debug_dir, exist_ok=True)
        path = os.path.join(self.debug_dir, name)
        self.driver.save_screenshot(path)
        print(f"[DEBUG] Saved screenshot: {path}")

    def scroll_search_results(self) -> bool:
        moved = False
        try:
            workspace = self.driver.find_element(By.ID, "workspace")
            before = self.driver.execute_script("return arguments[0].scrollTop", workspace)
            self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollTop + 1200;", workspace)
            after = self.driver.execute_script("return arguments[0].scrollTop", workspace)
            moved = after > before
        except Exception as e:
            print(f"[DEBUG] workspace scroll failed: {e}")

        try:
            buttons = self.driver.find_elements(
                By.XPATH,
                "//button[contains(., 'Load more') or contains(., 'Muat lebih banyak')]"
            )
            for btn in buttons:
                try:
                    if btn.is_displayed() and btn.is_enabled():
                        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
                        self.driver.execute_script("arguments[0].click();", btn)
                        return True
                except Exception as e:
                    print(f"[DEBUG] failed clicking one Load more button: {e}")
        except Exception as e:
            print(f"[DEBUG] Load more lookup failed: {e}")

        return moved

    def crawling(self, keyword: str, scroll: bool, server_ip: str, git_commit_id: str):
        self.check_login_status()
        post_urls = []
        max_pagination = 10
        page_count = 0
        seen = set()

        print(f"[INFO] Search Query: {urllib.parse.unquote(keyword)}")

        while True:
            page_count += 1
            search_url = (
                "https://www.linkedin.com/search/results/content/?keywords="
                + keyword
                + "&page="
                + str(page_count)
                + "&sortBy=\"date_posted\"&datePosted=\"past-24h\""
            )
            print(f"[INFO] Search URL: {search_url}")

            try:
                self.driver.get(search_url)
                time.sleep(5)

                added = self.extract_update_urns_from_dom(post_urls, seen)
                print(f"[INFO] Added {added} urls (initial), total unique={len(post_urls)}")

                scroll_times = random.randint(5, 10)
                print(f"[INFO] Randomly decided to scroll {scroll_times} times.")

                for i in range(scroll_times):
                    try:
                        moved = self.scroll_search_results()
                        time.sleep(random.uniform(4, 10))

                        added = self.extract_update_urns_from_dom(post_urls, seen)
                        print(
                            f"[INFO] Scroll {i+1}/{scroll_times}: "
                            f"moved={moved}, added {added}, total unique={len(post_urls)}"
                        )
                    except Exception as e:
                        print("[ERROR] Failed to scroll the page:", e)
                        break

            except Exception as e:
                print("[ERROR] Failed to crawl:", e)
                break

            if not scroll:
                break
            if page_count == max_pagination:
                break

        print(f"[INFO] Finish collecting post URL for keyword: {urllib.parse.unquote(keyword)}")
        print("=" * 90)

        total_data = 0
        print("[INFO] Start crawling post url.")
        for url in post_urls:
            print(f"[INFO] Post URL: {url}")
            try:
                datetime_crawling_ms = int(datetime.datetime.now().timestamp() * 1000)
                created_time = datetime.datetime.now().isoformat()
                updated_time = None
                hashtag = []
                raw_html = requests.get(url=url).text

                if "telescopeScope" in raw_html:
                    print("\033[33m[INFO] Private post found.\033[0m")
                    print("\033[33m[INFO] Starting to get URL with driver.\033[0m")
                    self.driver.get(url)
                    self.dummy_wait(5)
                    soup = BeautifulSoup(str(self.driver.page_source), 'html.parser')
                    mode = "selenium"
                else:
                    soup = BeautifulSoup(raw_html, 'html.parser')
                    mode = "requests"

                print("[INFO] Crawling mode:", mode)
                post_id = url.split(":")[-1].split("?")[0].strip("/")

                # REQUESTS
                if mode == "requests":
                    try:
                        content_str = soup.find(class_="attributed-text-segment-list__container relative mt-1 mb-1.5 babybear:mt-0 babybear:mb-0.5").text
                    except Exception:
                        content_str = None

                    if content_str is None:
                        try:
                            content_str = soup.find(attrs={"data-tracking-control-name": "public_post_feed-article-content"}).text
                        except Exception:
                            content_str = None
                    try:
                        comment_count = int(soup.find(attrs={"data-tracking-control-name": "public_post_social-actions-comments"}).text.replace(" Comments", "").replace(" Comment", "").replace("\n", "").replace(",", "").strip())
                    except Exception:
                        comment_count = 0

                    try:
                        for x in soup.find_all(attrs={"data-tracking-control-name": "	"}):
                            if "#" in x.text:
                                hashtag.append(x.text)
                    except Exception:
                        hashtag = []

                    try:
                        reaction_count = int(soup.find(attrs={"data-test-id": "social-actions__reaction-count"}).text.replace(",", ""))
                    except Exception:
                        reaction_count = 0

                    try:
                        post_owner_name = soup.find(attrs={"data-tracking-control-name": "public_post_feed-actor-name"}).text.replace("\n ", "").replace("\n", "").strip()
                    except Exception:
                        post_owner_name = None

                    try:
                        post_owner_url = soup.find(attrs={"data-tracking-control-name": "public_post_feed-actor-name"}).get("href").split("?")[0]
                    except Exception:
                        post_owner_url = None

                    try:
                        post_owner_headline = soup.find(class_="share-update-card__actor-headline").text.replace("\n", "").strip()
                    except Exception:
                        post_owner_headline = None

                    try:
                        post_owner_pic = soup.find(attrs={"data-ghost-classes": "bg-color-entity-ghost-background"}).get("data-delayed-url")
                    except Exception:
                        post_owner_pic = None

                    try:
                        post_time_str = soup.find("time").text.split("·")[0].replace("\n", "").replace(" ", "").replace("Edited", "").strip()
                    except Exception:
                        post_time_str = None

                    try:
                        if "m" in post_time_str:
                            post_time_datetime = moment.date(post_time_str.replace("m", "minutes ago"))
                        elif "h" in post_time_str:
                            post_time_datetime = moment.date(post_time_str.replace("h", "hours ago"))
                        elif "d" in post_time_str:
                            post_time_datetime = moment.date(post_time_str.replace("d", "days ago"))
                        else:
                            post_time_datetime = moment.date(post_time_str)
                    except Exception as e:
                        post_time_datetime = None
                        print("[ERROR] Failed to get post time:", e)
                    try:
                        post_time_datetimems = int(post_time_datetime.datetime.timestamp() * 1000)
                    except Exception:
                        post_time_datetimems = None

                # SELENIUM
                elif mode == "selenium":
                    content_str = None
                    limited_content = ""
                    def print_blue(text):
                        print("\033[34m" + text + "\033[0m")

                    try:
                        content_str = self.driver.find_element(By.XPATH, "//*[contains(@class, 'update-components-text')]").text.strip()
                        content_str = content_str.replace("Tagar", "").strip()
                        words = content_str.split()[:20]
                        limited_content = ' '.join(words) + "..."
                    except Exception as e:
                        print("[ERROR] Failed to get content:", e)
                    print_blue(f"[DEBUG] Post content: {limited_content}")

                    try:
                        comment_count = self.driver.find_element(By.XPATH, "//li[contains(@class, 'social-details-social-counts__comments')]//button//span[@aria-hidden='true']").text.replace(" Comments", "").replace(" Comment", "").replace(" Komentar", "").replace("\n", "").replace(",", "").strip()
                    except Exception:
                        comment_count = 0
                    print_blue(f"[DEBUG] Post comments: {comment_count}")

                    try:
                        hashtag = re.findall(r"#\w+", content_str)
                        hashtag.extend(hashtag)
                    except Exception:
                        hashtag = []
                    print_blue(f"[DEBUG] Post hashtags: {hashtag[:6]}")

                    try:
                        reaction_count = self.driver.find_element(By.XPATH, "//*[contains(@class, 'social-details-social-counts__reactions-count')]").text
                    except Exception:
                        reaction_count = 0
                    print_blue(f"[DEBUG] Post reactions: {reaction_count}")

                    try:
                        post_owner_name = self.driver.find_element(By.XPATH, "//*[contains(@class, 'update-components-actor__single-line-truncate')]").text.replace("\n", "").strip()
                    except Exception:
                        post_owner_name = None
                    print_blue(f"[DEBUG] Post owner name: {post_owner_name}")

                    try:
                        post_owner_url = self.driver.find_element(By.XPATH, "//a[contains(@class, 'update-components-actor__meta-link')]").get_attribute("href")
                    except Exception:
                        post_owner_url = self.driver.find_element(By.XPATH, "//a[contains(@class, 'update-components-actor__image')]").get_attribute("href")
                    print_blue(f"[DEBUG] Post owner url: {post_owner_url}")

                    try:
                        post_owner_headline = self.driver.find_element(By.XPATH, "//*[contains(@class, 'update-components-actor__description') and contains(@class, 'text-body-xsmall')]").text.replace("\n", "").strip()
                        if "•" in post_owner_headline:
                            post_owner_headline = None
                    except Exception:
                        post_owner_headline = None
                    print_blue(f"[DEBUG] Post owner headline: {post_owner_headline}")

                    try:
                        post_owner_pic = self.driver.find_element(By.XPATH, "//span[@class='js-update-components-actor__avatar']//img").get_attribute("src")
                    except Exception:
                        post_owner_pic = None
                    print_blue(f"[DEBUG] Post owner pic: {post_owner_pic}")

                    try:
                        post_time_str = self.driver.find_element(By.XPATH, "//*[contains(@class, 'update-components-actor__sub-description') and contains(@class, 'text-body-xsmall')]").text.split(" •")[0].replace(" • Edited •   ", "").replace(" • Diedit •   ", "").replace("\n", "").strip()
                    except Exception:
                        post_time_str = None
                    print_blue(f"[DEBUG] Post date: {post_time_str}")

                    try:
                        if "mnt" in post_time_str:
                            post_time_datetime = moment.date(post_time_str.replace("mnt", "minutes ago"))
                        elif "jam" in post_time_str:
                            post_time_datetime = moment.date(post_time_str.replace("jam", "hours ago"))
                        elif "hr" in post_time_str:
                            post_time_datetime = moment.date(post_time_str.replace("hr", "days ago"))
                        elif "mgg" in post_time_str:
                            post_time_datetime = moment.date(post_time_str.replace("mgg", "weeks ago"))
                        else:
                            post_time_datetime = moment.date(post_time_str)
                    except Exception as e:
                        post_time_datetime = None
                        print("[ERROR] Failed to get post_time_datetime:", e)

                    try:
                        post_time_datetimems = int(post_time_datetime.datetime.timestamp() * 1000)
                    except Exception:
                        post_time_datetimems = None

                total_data += 1
                print(f"[DEBUG] [{total_data}] {post_id} | {post_time_str}")

                # Metadata Crawling
                metadata = {
                    "crawler": {
                        "server_ip": server_ip,
                        "git_commit_id": git_commit_id,
                        "account": {
                            "user": self.current_username,
                            "token": None
                        },
                        "type": "login",
                        "search": urllib.parse.unquote(keyword),
                        "client_id": int(self.client_id),
                        "platform": "Media Intelligence",
                        "crawling_mode": mode,
                        "author": "macan"
                    }
                }

                # Insert Data LinkedIn Post
                insert_data = {
                    "post_id": post_id,
                    "url": url,
                    "datetime_crawling_ms": datetime_crawling_ms,
                    "owner": {
                        "name": post_owner_name,
                        "url": post_owner_url,
                        "headline": post_owner_headline,
                        "avatar": post_owner_pic
                    },
                    "post": {
                        "content_str": content_str
                    },
                    "post_time": {
                        "post_time_str": post_time_str,
                        "post_time_datetime": str(post_time_datetime.date) if post_time_datetime else None,
                        "post_time_datetimems": post_time_datetimems
                    },
                    "datetime_ms": post_time_datetimems,
                    "hashtag": hashtag,
                    "comment_count": comment_count,
                    "reaction_count": reaction_count,
                    "metadata": metadata,
                    "created_time": created_time,
                    "updated_time": updated_time
                }

                # Send data
                self.publisher.produce_message(post_id, insert_data)

            except Exception as e:
                print("[ERROR] Reason:", e)
            time.sleep(2)

        self.logger.generate_log(
            0000,
            "Crawling finished for this loop. Please check the data to review total results.",
            "crawling summary",
            {
                "username": self.current_username,
                "client_id": self.client_id,
                "total_data": total_data,
                "keyword": keyword,
                "ip_server": server_ip
            },
            self.start_time
        )

        return 1

    def kill_service(self, message: str):
        print(message)
        if self.current_username:
            self.account_manager.release_account(self.current_username)
            self.account_manager.mark_account_failed(self.current_username)
            
        import multiprocessing
        import sys
        for prc in multiprocessing.active_children():
            prc.terminate()
        self.close_driver()
        sys.exit(0)
