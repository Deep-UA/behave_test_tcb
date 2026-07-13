import os
import re

import allure
from dotenv import load_dotenv

from base_definitions import ROOT_DIR
from lib.driver_wrapper import Driver
from lib.utilities import Utilities

# Local secrets (e.g. TCB_PHONE) live in the git-ignored .env file;
# explicitly set env vars still take precedence
load_dotenv()

TRACES_DIR = f'{ROOT_DIR}/traces'


def before_all(context):
    context.driver = Driver()
    context.driver.start_browser()


def before_scenario(context, scenario):
    # @mobile tag runs the scenario in an emulated mobile device context
    context.page = context.driver.new_page(mobile='mobile' in scenario.tags)


def after_scenario(context, scenario):
    trace_path = None
    if scenario.status in ('failed', 'error'):
        Utilities.get_screenshot(context.page)
        Utilities.get_html_source(context.page)
        os.makedirs(TRACES_DIR, exist_ok=True)
        scenario_slug = re.sub(r'\W+', '_', scenario.name).strip('_')
        trace_path = f'{TRACES_DIR}/{scenario_slug}.zip'
    context.driver.close_page(trace_path=trace_path)
    if trace_path:
        # Open with: playwright show-trace <file>
        allure.attach.file(trace_path, name='playwright_trace', extension='zip')


def after_all(context):
    Utilities.fix_properties(context.driver.browser)
    context.driver.stop()
    Utilities.generate_allure_report()
