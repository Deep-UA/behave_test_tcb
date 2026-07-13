import glob
import os
import shutil
import subprocess
import time
from importlib.metadata import version

import allure
from playwright.sync_api import Browser, Error as PlaywrightError, Page

from base_definitions import ROOT_DIR
from configuration.config_parse import BROWSER, GITHUB, OS_VERSION


class Utilities:
    @staticmethod
    def get_screenshot(page: Page):
        if not page:
            return
        try:
            allure.attach(page.screenshot(), name='screenshot', attachment_type=allure.attachment_type.PNG)
        except PlaywrightError:
            pass  # Page/browser already closed

    @staticmethod
    def get_html_source(page: Page):
        if not page:
            return
        try:
            html = page.content()
            if html:
                allure.attach(html, name='html_source', attachment_type=allure.attachment_type.HTML)
            # Console messages are collected by BasePage listeners
            console_log = getattr(page, 'captured_console_messages', None)
            if console_log:
                allure.attach('\n\n'.join(console_log), name='console_log',
                              attachment_type=allure.attachment_type.TEXT)
        except PlaywrightError:
            pass  # Page/browser already closed

    @staticmethod
    def generate_allure_report():
        """Regenerate allure-report after the run and feed its history back into
        allure-results so the Trend widget accumulates a point per run.
        Skipped in CI and when the allure CLI is not installed."""
        if os.getenv('GITHUB_RUN') or not shutil.which('allure'):
            return
        results_dir = f'{ROOT_DIR}/allure-results'
        report_dir = f'{ROOT_DIR}/allure-report'
        subprocess.run(['allure', 'generate', results_dir, '-o', report_dir, '--clean'],
                       check=False, capture_output=True)
        os.makedirs(f'{results_dir}/history', exist_ok=True)
        for history_file in glob.glob(f'{report_dir}/history/*.json'):
            shutil.copy(history_file, f'{results_dir}/history/')

    @staticmethod
    def fix_properties(browser_instance: Browser):
        browser = BROWSER.upper()
        properties_path = f'{ROOT_DIR}/allure-results/environment.properties'
        if os.path.isdir(f"{ROOT_DIR}/allure-results"):
            if os.path.exists(properties_path):
                remove_cycles = 10
                wait_interval = 1
                for _ in range(remove_cycles):
                    try:
                        os.remove(properties_path)
                        break
                    except FileNotFoundError:
                        time.sleep(wait_interval)  # will be useful in parallel mode
        else:
            os.mkdir(f"{ROOT_DIR}/allure-results")
        with open(properties_path, "w+") as file:
            file.write(f"Environment {os.getenv('ENVIRONMENT', '').upper()}\n")
            file.write(f"Browser {browser}\n")
            file.write(f"{browser}_VERSION {browser_instance.version}\n")
            file.write(f"Git {GITHUB}\n")
            file.write(f"OS_VERSION {OS_VERSION}\n")
            file.write(f"PLAYWRIGHT_VERSION {version('playwright')}\n")
            file.write(f"HEADLESS {os.getenv('HEADLESS')}\n")
