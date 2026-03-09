import os
import time
import socket
import pandas as pd
from datetime import datetime

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import (
        TimeoutException,
        NoSuchElementException,
        StaleElementReferenceException,
        WebDriverException
    )
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

MAX_NETWORK_WAIT_SECONDS = 120
RETRY_ATTEMPTS = 3
RETRY_DELAY = 5

WEBSITES = [
    "https://chartink.com/screener/copy-nks-best-buy-stocks-for-intraday-2",
    "https://chartink.com/screener/potential-breakouts",
    "https://chartink.com/screener/perfect-sell-short",
    "https://chartink.com/screener/boss-scanner-for-btst",
    "https://chartink.com/screener/strong-stocks",
    # "https://chartink.com/screener/rsi-overbought-or-oversold-scan",
    # "https://chartink.com/screener/nr7-current-day",
    # "https://chartink.com/screener/copy-morning-scanner-for-buy-nr7-based-breakout-8",
    # "https://chartink.com/screener/stock-screener-open-high-open-low",
    # "https://chartink.com/screener/ichimoku-uptrend-cloud-crossover",
    # "https://chartink.com/screener/moving-average-bullish-strong-buy",
    # "https://chartink.com/screener/buy-entry-intraday",
    # "https://chartink.com/screener/morning-star-candlestick-pattern",
    # "https://chartink.com/screener/pure-bullish-trend-stocks",
    # "https://chartink.com/screener/ema-crossover-5-13-26-scan",
    # "https://chartink.com/screener/doji-2",
    # "https://chartink.com/screener/golden-cross-scan",
    # "https://chartink.com/screener/buy-open-equals-to-low",
    # "https://chartink.com/screener/positive-hammer-1",
    # "https://chartink.com/screener/high-volume-stocks",
    # "https://chartink.com/screener/bullish-momentum-stocks",
    # "https://chartink.com/screener/profit-jump-by-200",
    # "https://chartink.com/screener/breaking-days-high-5-mins",
    # "https://chartink.com/screener/nks-best-buy-stocks-for-intraday",
    # "https://chartink.com/screener/closing-3-up-since-3-days",
    # "https://chartink.com/screener/justfortraders-cpr-2",
    # "https://chartink.com/screener/nr7-896",
    # "https://chartink.com/screener/copy-001-49",
    # "https://chartink.com/screener/copy-hm-positional-buy-nk-sir-23",
    # "https://chartink.com/screener/nr7-nr4",
    # "https://chartink.com/screener/bullish-engulfing-pattern-1",
    # "https://chartink.com/screener/breakout-intraday",
    # "https://chartink.com/screener/my-intraday-buy-setup-adx",
    # "https://chartink.com/screener/copy-copy-bb-blast-15-min-3",
    # "https://chartink.com/screener/evening-star",
    # "https://chartink.com/screener/copy-nr7-fut-6",
    # "https://chartink.com/screener/sell-entry-intraday",
    # "https://chartink.com/screener/stockinsight-intraday-bullish-scanner",
    # "https://chartink.com/screener/santu-baba-trick-on-open-equal-low-with-1-higher-previous-close",
    # "https://chartink.com/screener/yesterday-bearish-engulifing",
    # "https://chartink.com/screener/supertrend-negative-breakout",
    # "https://chartink.com/screener/cpr-14",
    # "https://chartink.com/screener/short-term-hourly-ema-strategy-ema-15-30-50-macd-histogram-priyaram-bindiganavile-sharable",
    # "https://chartink.com/screener/javeed-hussain-intraday-buy-1",
    # "https://chartink.com/screener/day-low-high",
    # "https://chartink.com/screener/4-moving-average-crossover",
    # "https://chartink.com/screener/large-cap-stocks",
    # "https://chartink.com/screener/copy-stocks-near-52-week-high-by-25-575",
    # "https://chartink.com/screener/ohol-prb",
    # "https://chartink.com/screener/stocks-below-book-value",
    # "https://chartink.com/screener/inside-bar",
    # "https://chartink.com/screener/volume-shockers",
    # "https://chartink.com/screener/bullish-rsi-stochastic",
    # "https://chartink.com/screener/btst-scanner-stock-insight",
    # "https://chartink.com/screener/cpr-by-kgs-wcpr-for-tomorrow",
    # "https://chartink.com/screener/gap-up-by-3-with-3x-volume",
    # "https://chartink.com/screener/low-debt-companies",
    # "https://chartink.com/screener/rsi-crossed-above-80",
    # "https://chartink.com/screener/uptrend-stocks-2",
    # "https://chartink.com/screener/perfect",
    # "https://chartink.com/screener/copy-bullish-checklist-24",
    # "https://chartink.com/screener/cpr-by-kgs-s1-pdl-broken",
    # "https://chartink.com/screener/copy-hilega-milega-weekly-buy-setup-23",
    # "https://chartink.com/screener/15-min-candle-outside-bollinger-band",
    # "https://chartink.com/screener/monthly-rsi-above-50",
    # "https://chartink.com/screener/third-15-minutes-candle-breakout-impulse-technical",
    # "https://chartink.com/screener/copy-bullish-for-next-day-31",
    # "https://chartink.com/screener/volume-bo-from-range",
    # "https://chartink.com/screener/abc-4",
    # "https://chartink.com/screener/bullish-in-all-tf-1",
    # "https://chartink.com/screener/copy-novice-hedge-narrow-cpr-eod-195",
    # "https://chartink.com/screener/copy-amal-positional-rsi-extreme-bullish-strategy",
    # "https://chartink.com/screener/pious-volume-generator",
    # "https://chartink.com/screener/12-month-momentum",
    # "https://chartink.com/screener/gap-up-stocks",
    # "https://chartink.com/screener/stockinsight-intraday-bearish-scanner",
    # "https://chartink.com/screener/rsi-40-to-50-scan",
    # "https://chartink.com/screener/a-a-trading-blog1",
    # "https://chartink.com/screener/volume-spike-in-5-minutes",
    # "https://chartink.com/screener/copy-3-candles-hourly-bullish",
    # "https://chartink.com/screener/stockinsight-bollinger-band-squeeze-breakout-screener",
    # "https://chartink.com/screener/copy-chanakya-bearish-scanner-working-11",
    # "https://chartink.com/screener/the-active-trader-club-breakout-stocks-scanner",
    # "https://chartink.com/screener/supertrend-buy-with-adx-and-rsi",
    # "https://chartink.com/screener/chart-link",
    # "https://chartink.com/screener/macd-and-ema-12-26-crossover",
    # "https://chartink.com/screener/open-drive-by-pathik-trader",
    # "https://chartink.com/screener/btst-15-min",
    # "https://chartink.com/screener/nks-98-o-l-trick-24-11-2017",
    # "https://chartink.com/screener/52-week-low-3",
    # "https://chartink.com/screener/my-intraday-sell-setup-adx",
    # "https://chartink.com/screener/price-near-vwap",
    # "https://chartink.com/screener/uptrend-stocks",
    # "https://chartink.com/screener/weekly-rsi-overbought-oversold-scan",
    # "https://chartink.com/screener/morning-star-bullish-pattern",
    # "https://chartink.com/screener/sell-volume-change",
    # "https://chartink.com/screener/copy-novice-hedge-narrow-cpr-eod-1566",
    # "https://chartink.com/screener/bb-weelky-blast",
    # "https://chartink.com/screener/last-5-minute-stock-breakouts-from-support-resistance",
    # "https://chartink.com/screener/stocks-closing-daily-2-up-from-5-days-back-to-back",
    # "https://chartink.com/screener/nks-best-intraday-formula",
    # "https://chartink.com/screener/copy-camrilla-above-r3-r4-volume-buying-final-01-06-2021-9-00-pm-1",
    # "https://chartink.com/screener/orb-15-min-vwap-bo",
    # "https://chartink.com/screener/copy-breakout-scan-9",
    # "https://chartink.com/screener/rsi-ema-macd",
    # "https://chartink.com/screener/sanchit",
    # "https://chartink.com/screener/intraday-future-sell-with-supertrend-80-accuracy",
    # "https://chartink.com/screener/weekly-rsi-above-60-9",
    # "https://chartink.com/screener/bullish-engulf-3",
    # "https://chartink.com/screener/darvax-adx-combination-1",
    # "https://chartink.com/screener/copy-1000-buy-doji-bullish-engulfing-3",
    # "https://chartink.com/screener/rsi-40-scan-undervalued-companies",
    # "https://chartink.com/screener/virgin-cpr",
    # "https://chartink.com/screener/intraday-renko-long-trade-gainers-within-9-15-to-9-45",
    # "https://chartink.com/screener/bullish-pin-bar",
    # "https://chartink.com/screener/copy-52-week-high-low-rounded-no-22",
    # "https://chartink.com/screener/nifty-50-stocks",
    # "https://chartink.com/screener/rsi-oversold-scan",
    # "https://chartink.com/screener/copy-rsi-breakout-3",
    # "https://chartink.com/screener/moving-average-crossover-2",
    # "https://chartink.com/screener/short-term-breakout-g-v-k",
    # "https://chartink.com/screener/copy-cpr-by-kgs-ncpr-for-tomorrow-694",
    # "https://chartink.com/screener/bearish-engulfing-strong-1",
    # "https://chartink.com/screener/copy-1045-bound-19",
    # "https://chartink.com/screener/double-inside-candle",
    # "https://chartink.com/screener/stocks-trading-near-day-s-high-on-5-min-chart-with-volume-bo-intraday",
    # "https://chartink.com/screener/nks-future-trick-bb-part1",
    # "https://chartink.com/screener/copy-ha-stoch-rsi-4",
    # "https://chartink.com/screener/intraday-stocks-rising-with-increase-in-volume-on-15-minute-candles",
    # "https://chartink.com/screener/intraday-go-long",
    # "https://chartink.com/screener/stocks-near-day-high",
    # "https://chartink.com/screener/daily-breakout-8",
    # "https://chartink.com/screener/nks-positional-95-accuracy",
    # "https://chartink.com/screener/copy-nicholas-supertrend-positive-breakout-buy-intraday-1",
    # "https://chartink.com/screener/highest-earning-per-share-eps-stocks",
    # "https://chartink.com/screener/rishikesh-adx-scan-gsinghal",
    # "https://chartink.com/screener/3-supertrend-strategy",
    # "https://chartink.com/screener/intraday-mean-reversion",
    # "https://chartink.com/screener/volume-shockers-momentum-with-volume",
    # "https://chartink.com/screener/extreemcompression",
    # "https://chartink.com/screener/copy-nicholas-supertrend-negative-breakout-sell-intraday-10",
    # "https://chartink.com/screener/rsp-btst-intraday-rsibased",
    # "https://chartink.com/screener/rk-trading-supertrend-strategy",
    # "https://chartink.com/screener/small-cap-stocks",
    # "https://chartink.com/screener/copy-bullish-for-next-day-114",
    # "https://chartink.com/screener/insideday-23",
    # "https://chartink.com/screener/stocks-near-support-level-bearish-parimal-wadiwala",
    # "https://chartink.com/screener/ascending-triangle-screener",
    # "https://chartink.com/screener/nks-stocks-jackpot-buy-2",
    # "https://chartink.com/screener/sma-10-50",
    # "https://chartink.com/screener/top-stocks-with-the-lowest-pe-pricing-earnings",
    # "https://chartink.com/screener/vwap-crossover-1",
    # "https://chartink.com/screener/fake-paradise-by-pathik",
    # "https://chartink.com/screener/open-high-with-round-numbers-santu-baba-sir",
    # "https://chartink.com/screener/position-buy-seema",
    # "https://chartink.com/screener/testing-btst-bullish-engulfing",
    # "https://chartink.com/screener/5m-breakout-across-5-hours-with-4-times-volume-deva",
    # "https://chartink.com/screener/neeraj-joshi-intraday-hammer-candle-15-min",
    # "https://chartink.com/screener/twt-vc1",
    # "https://chartink.com/screener/copy-copy-nk-sir-s-uptrend-stocks-1178",
    # "https://chartink.com/screener/1st-15-min-outside-upper-bollinger-band",
    # "https://chartink.com/screener/copy-dp-2nd-15mins-candle-under-1st-min-candle-49",
    # "https://chartink.com/screener/nr4-intraday-6",
    # "https://chartink.com/screener/trend-reversal-sf",
    # "https://chartink.com/screener/boss-scanner-for-btst-440",
    # "https://chartink.com/screener/intraday-trading-strategy-200-sma",
    # "https://chartink.com/screener/pivot-r1-and-s1-breakout",
    # "https://chartink.com/screener/doji-and-near-doji-scan-btst-futures",
    # "https://chartink.com/screener/stock-screener-3400",
    # "https://chartink.com/screener/stocks-in-consolidation",
]


def check_internet_connection():
    try:
        socket.create_connection(("www.google.com", 80), timeout=5)
        return True
    except OSError:
        return False


def wait_for_network_recovery(log_fn, max_wait_seconds=120):
    start_time = datetime.now()
    wait_interval = 5
    log_fn(f"Network issue detected. Waiting up to {max_wait_seconds}s for recovery...")
    while (datetime.now() - start_time).total_seconds() < max_wait_seconds:
        if check_internet_connection():
            elapsed = (datetime.now() - start_time).total_seconds()
            log_fn(f"Network recovered after {elapsed:.0f} seconds")
            return True
        remaining = max_wait_seconds - (datetime.now() - start_time).total_seconds()
        log_fn(f"   Checking network... {remaining:.0f}s remaining")
        time.sleep(wait_interval)
    log_fn(f"Network did not recover within {max_wait_seconds} seconds.")
    return False


def extract_table_from_dom(driver, log_fn):
    """Read the results table directly from DOM — no clipboard needed."""
    table_selectors = [
        "#DataTables_Table_0",
        "table.table-striped",
        "table.dataTable",
        ".screener-result table",
        "table",
    ]

    for selector in table_selectors:
        try:
            tables = driver.find_elements(By.CSS_SELECTOR, selector)
            for table in tables:
                rows = table.find_elements(By.TAG_NAME, "tr")
                if len(rows) < 2:
                    continue

                # Extract headers
                header_row = rows[0]
                headers = [th.text.strip() for th in header_row.find_elements(By.TAG_NAME, "th")]
                if not headers:
                    headers = [td.text.strip() for td in header_row.find_elements(By.TAG_NAME, "td")]
                if not headers:
                    continue

                # Extract data rows
                data = []
                for row in rows[1:]:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if not cells:
                        continue
                    row_data = [c.text.strip() for c in cells]
                    if any(row_data):
                        data.append(row_data)

                if not data:
                    continue

                col_count = len(headers)
                padded = []
                for row in data:
                    if len(row) < col_count:
                        row += [""] * (col_count - len(row))
                    padded.append(row[:col_count])

                df = pd.DataFrame(padded, columns=headers)
                df = df.dropna(how="all")
                df = df[df.apply(lambda r: r.astype(str).str.strip().ne("").any(), axis=1)]

                if not df.empty:
                    log_fn(f"DOM table read via '{selector}' -> {len(df)} rows, {len(df.columns)} cols")
                    return df

        except Exception as e:
            log_fn(f"   Selector '{selector}' skipped: {str(e)[:60]}")
            continue

    return None


def wait_for_table_to_load(driver, wait_obj, log_fn):
    """Wait until at least one data row is visible in the table."""
    try:
        wait_obj.until(EC.presence_of_element_located((By.CSS_SELECTOR,
            "#DataTables_Table_0 tbody tr, table.dataTable tbody tr, table.table-striped tbody tr")))
        return True
    except TimeoutException:
        log_fn("Table wait timed out - attempting extraction anyway")
        return False


def scrape_chartink_page(driver, wait_obj, url, log_fn, stop_flag, retry_count=0):
    if stop_flag():
        return None
    if retry_count >= RETRY_ATTEMPTS:
        log_fn(f"Max retries ({RETRY_ATTEMPTS}) reached for {url}")
        return None

    screener_name = url.split("/")[-1]

    try:
        log_fn(f"Visiting {screener_name} (attempt {retry_count + 1}/{RETRY_ATTEMPTS})")
        driver.get(url)

        if stop_flag():
            return None

        # Try clicking a Run/Refresh button if it exists
        for sel in ["button.btn-success", "#run-screen", ".run-screen", "button[type='submit']"]:
            try:
                btn = driver.find_element(By.CSS_SELECTOR, sel)
                if btn.is_displayed() and btn.is_enabled():
                    btn.click()
                    log_fn(f"Clicked run button ({sel})")
                    break
            except Exception:
                continue

        if stop_flag():
            return None

        log_fn("Waiting for results table...")
        wait_for_table_to_load(driver, wait_obj, log_fn)

        if stop_flag():
            return None

        df = extract_table_from_dom(driver, log_fn)

        if df is None or df.empty:
            log_fn(f"No table data found on {screener_name}")
            log_fn(f"   Page title: {driver.title}")
            return None

        df.insert(0, "Screener", screener_name)
        log_fn(f"Successfully extracted {len(df)} rows from {screener_name}")
        return df

    except WebDriverException as e:
        err_str = str(e)
        if "net::" in err_str or "ERR_" in err_str or "timeout" in err_str.lower():
            log_fn(f"Network error: {err_str[:120]}")
            if not wait_for_network_recovery(log_fn, MAX_NETWORK_WAIT_SECONDS):
                log_fn("Network timeout exceeded.")
                return None
            return scrape_chartink_page(driver, wait_obj, url, log_fn, stop_flag, retry_count + 1)
        else:
            log_fn(f"WebDriver error: {err_str[:150]}")
            time.sleep(RETRY_DELAY)
            return scrape_chartink_page(driver, wait_obj, url, log_fn, stop_flag, retry_count + 1)

    except (TimeoutException, StaleElementReferenceException) as e:
        log_fn(f"Element error: {str(e)[:100]}")
        time.sleep(RETRY_DELAY)
        return scrape_chartink_page(driver, wait_obj, url, log_fn, stop_flag, retry_count + 1)

    except Exception as e:
        log_fn(f"Unexpected error: {str(e)[:200]}")
        import traceback
        log_fn(traceback.format_exc()[:500])
        time.sleep(RETRY_DELAY)
        return scrape_chartink_page(driver, wait_obj, url, log_fn, stop_flag, retry_count + 1)


def run_scraper(log_fn, progress_fn, stop_flag, output_dir):
    if not SELENIUM_AVAILABLE:
        log_fn("Selenium is not installed. Cannot run scraper.")
        return None

    log_fn("=" * 60)
    log_fn("CHARTINK WEB SCRAPER - Starting")
    log_fn("=" * 60)
    log_fn(f"Total screeners : {len(WEBSITES)}")
    log_fn(f"Network timeout : {MAX_NETWORK_WAIT_SECONDS}s")
    log_fn(f"Retries per URL : {RETRY_ATTEMPTS}")
    log_fn(f"Data method     : Direct DOM table extraction (no clipboard)")
    log_fn("=" * 60)

    if not check_internet_connection():
        log_fn("No internet connection at startup")
        if not wait_for_network_recovery(log_fn, MAX_NETWORK_WAIT_SECONDS):
            log_fn("Exiting: no network.")
            return None

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    driver = None
    output_file = None

    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        wait_obj = WebDriverWait(driver, 15)

        all_dataframes = []
        successful_scrapes = 0
        failed_scrapes = 0
        total = len(WEBSITES)

        for idx, url in enumerate(WEBSITES, 1):
            if stop_flag():
                log_fn("Stop requested by user.")
                break

            log_fn(f"\n{'─' * 50}")
            log_fn(f"Processing {idx}/{total}: {url.split('/')[-1]}")
            log_fn(f"{'─' * 50}")

            df = scrape_chartink_page(driver, wait_obj, url, log_fn, stop_flag)

            if df is not None:
                all_dataframes.append(df)
                successful_scrapes += 1
            else:
                failed_scrapes += 1

            progress_fn(idx, total)

            if not stop_flag():
                time.sleep(0.5)

        log_fn("\n" + "=" * 60)
        log_fn("SCRAPING COMPLETED")
        log_fn("=" * 60)
        log_fn(f"Successful : {successful_scrapes}/{total}")
        log_fn(f"Failed     : {failed_scrapes}/{total}")

        if all_dataframes:
            log_fn(f"\nCombining {len(all_dataframes)} dataframes...")
            merged_df = pd.concat(all_dataframes, ignore_index=True)

            original_rows = len(merged_df)
            merged_df = merged_df.drop_duplicates()
            duplicates_removed = original_rows - len(merged_df)

            log_fn(f"Rows before dedup  : {original_rows}")
            log_fn(f"Duplicates removed : {duplicates_removed}")
            log_fn(f"Final rows         : {len(merged_df)}")
            log_fn(f"Columns            : {list(merged_df.columns)}")

            # Always save as chartink.xlsx — replaces any previous run
            excel_name = "chartink.xlsx"
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, excel_name)

            # Remove old file first so it is cleanly replaced
            if os.path.exists(output_file):
                os.remove(output_file)
                log_fn("Replaced existing chartink.xlsx")

            with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
                merged_df.to_excel(writer, index=False, sheet_name="All Screeners")
                for screener_name, group_df in merged_df.groupby("Screener"):
                    sheet = screener_name[:31]
                    group_df.drop(columns=["Screener"]).to_excel(
                        writer, index=False, sheet_name=sheet
                    )

            log_fn(f"\nExcel saved: {excel_name}")
            log_fn(f"Sheets: 'All Screeners' + one sheet per screener")
            log_fn("=" * 60)
        else:
            log_fn("\nNo data extracted from any website")
            log_fn("=" * 60)

    except Exception as e:
        log_fn(f"\nCritical error: {e}")
        import traceback
        log_fn(traceback.format_exc())

    finally:
        if driver:
            log_fn("\nClosing browser...")
            try:
                driver.quit()
            except Exception:
                pass
            log_fn("Browser closed")

    return output_file