import re
import time
from datetime import datetime, timedelta
from typing import List, Optional

import allure
from playwright.sync_api import Locator, Page, TimeoutError as PlaywrightTimeoutError, expect

from configuration.config_parse import MAIN_UI_URL, TIMEOUT_SEC

# Selenium By strategies mapped to Playwright selector syntax, so legacy
# (By.XPATH, '//a') locator tuples keep working during the migration
_BY_TO_SELECTOR = {
    'css selector': '{}',
    'xpath': 'xpath={}',
    'id': 'id={}',
    'name': '[name="{}"]',
    'class name': '.{}',
    'tag name': '{}',
    'link text': 'text="{}"',
    'partial link text': 'text={}',
}


class BasePage:
    timeout_sec = TIMEOUT_SEC

    def __init__(self, page: Page, base_url: str = MAIN_UI_URL):
        self.page = page
        self.base_url = base_url
        self._start_log_capture()

    # -> LOCATORS

    @staticmethod
    def _selector(*locator) -> str:
        """Accepts a Playwright selector string, a legacy (By.X, value) tuple, or the same tuple unpacked"""
        if len(locator) == 1:
            if isinstance(locator[0], (tuple, list)):
                return BasePage._selector(*locator[0])
            return locator[0]
        by, value = locator
        return _BY_TO_SELECTOR[by].format(value)

    def element(self, *locator) -> Locator:
        """Build a Locator; nothing is queried until an action or assertion runs on it"""
        return self.page.locator(self._selector(*locator)).first

    def find_element(self, *locator, timeout: float = timeout_sec) -> Locator:
        element = self.element(*locator)
        element.wait_for(state='attached', timeout=timeout * 1000)
        return element

    # Find array of elements on page (useful for table, lists, dropdowns etc.)
    def find_elements(self, *locator, timeout: float = timeout_sec, wait: bool = True) -> List[Locator]:
        if wait:
            self.find_element(*locator, timeout=timeout)
        return self.page.locator(self._selector(*locator)).all()

    @staticmethod
    def get_parametrized_locator(locator, parameter):
        if isinstance(locator, (tuple, list)):
            return locator[0], locator[1].format(*parameter)
        return locator.format(*parameter)

    # -> NAVIGATION

    @allure.step('Open page - {url}')
    def open(self, url: str = ""):
        self.page.goto(self.base_url + url)

    @allure.step('Redirect by url - {url}')
    def go_to_exact_url(self, url: str = ""):
        self.page.goto(url)

    # Focus recently opened tab
    def focus_active_tab(self) -> Page:
        self.page = self.page.context.pages[-1]
        self.page.bring_to_front()
        return self.page

    def scroll_page_up(self, count: int = 3):
        for _ in range(count):
            self.page.keyboard.press('PageUp')

    def scroll_page_down(self, count: int = 3):
        for _ in range(count):
            self.page.keyboard.press('PageDown')

    @staticmethod
    def scroll_element_to_center_by_js(element: Locator):
        element.evaluate("el => el.scrollIntoView({block: 'center'})")

    # -> ACTIONS

    # Playwright auto-waits for visibility/stability and scrolls into view itself,
    # so no JS-click or scroll fallbacks are needed
    @allure.step('Click on element - {locator}')
    def click(self, *locator, timeout: float = timeout_sec):
        self.element(*locator).click(timeout=timeout * 1000)

    @allure.step('Click last element - {locator}')
    def click_last_element(self, *locator, timeout: float = timeout_sec):
        self.page.locator(self._selector(*locator)).last.click(timeout=timeout * 1000)

    # Click on web element and check that another element appear
    def click_and_check(self, click_locator, check_locator, timeout: float = timeout_sec):
        self.click(click_locator, timeout=timeout)
        for _ in range(3):
            if self.is_element_visible(check_locator, timeout=timeout / 2):
                return
            self.click(click_locator, timeout=timeout)
        raise AssertionError(f'Element - "{check_locator}" did not appear after clicking "{click_locator}"')

    # Click on web element and check that element missed
    def click_and_wait_for_element_to_be_hidden(self, *locator, timeout: float = timeout_sec):
        self.click(*locator, timeout=timeout)
        for _ in range(3):
            if self.is_element_invisible(*locator, timeout=timeout):
                return
            self.click(*locator, timeout=timeout)
        raise AssertionError(f'Element - "{locator}" did not disappear after clicking')

    def click_and_wait_for_other_element_to_be_hidden(self, click_locator, check_locator,
                                                      timeout: float = timeout_sec):
        self.click(click_locator, timeout=timeout)
        for _ in range(3):
            if self.is_element_invisible(check_locator, timeout=timeout):
                return
            self.click(click_locator, timeout=timeout)
        raise AssertionError(f'Element - "{check_locator}" did not disappear after clicking - "{click_locator}"')

    # Click on web element only if it's visible
    def click_if_element_visible(self, *locator, timeout: float = timeout_sec):
        if self.is_element_visible(*locator, timeout=timeout):
            self.click(*locator)

    def click_child_element(self, parent_element: Locator, child_locator):
        parent_element.locator(self._selector(child_locator)).first.click()

    @allure.step('Hover on element - {locator}')
    def hover(self, *locator):
        self.element(*locator).hover()

    # Scroll to web element
    def move_to_element(self, *locator):
        self.element(*locator).hover()

    @allure.step('Type text "{text}" into element - {locator}')
    def type(self, text: str, *locator):
        # fill() clears the field first
        self.element(*locator).fill(text)

    @allure.step('Type text "{text}" into element - {locator} without clearing')
    def type_without_clearing(self, text, locator):
        self.element(locator).press_sequentially(text)

    @allure.step('Upload file "{filename}" into element - {locator}')
    def upload_file(self, filename: str, *locator):
        self.element(*locator).set_input_files(filename)

    def clear(self, *locator):
        self.element(*locator).clear()

    @allure.step('Press TAB into element - {locator}')
    def defocus_element(self, *locator):
        self.element(*locator).press('Tab')

    # Hit "ENTER" button on web element
    def press_enter(self, *locator):
        self.element(*locator).press('Enter')

    @allure.step('Drag element {source_element} to {destination_element}')
    def drag_element_to_element(self, source_element, destination_element):
        self.element(source_element).drag_to(self.element(destination_element))

    # Remove web element using JS
    def remove_web_item(self, *locator):
        self.element(*locator).evaluate('el => el.remove()')

    # Playwright auto-dismisses dialogs; call this BEFORE the action that
    # triggers the alert to accept it instead
    def close_alert(self):
        self.page.once('dialog', lambda dialog: dialog.accept())

    # -> SELECT

    @allure.step('Select value "{value}" by value in selector - {locator}')
    def select_by_value(self, value, *locator):
        self.element(*locator).select_option(value=value)

    @allure.step('Select value "{text}" by text in selector - {locator}')
    def select_by_text(self, text, *locator):
        self.element(*locator).select_option(label=text)

    @allure.step('Select value "{index}" by index in selector - {locator}')
    def select_by_index(self, index, *locator):
        self.element(*locator).select_option(index=index)

    # -> CHECKERS

    def is_element_selected(self, *locator) -> bool:
        return self.element(*locator).is_checked()

    def is_checked_checkbox(self, *locator) -> bool:
        return self.element(*locator).is_checked()

    def is_element_enabled(self, *locator, timeout: float = timeout_sec) -> bool:
        return self.find_element(*locator, timeout=timeout).is_enabled()

    # Check that web element is present on the page
    def is_element_present(self, *locator, timeout: float = timeout_sec) -> bool:
        try:
            self.element(*locator).wait_for(state='attached', timeout=timeout * 1000)
        except PlaywrightTimeoutError:
            return False
        return True

    def is_element_visible(self, *locator, timeout: float = timeout_sec) -> bool:
        try:
            self.element(*locator).wait_for(state='visible', timeout=timeout * 1000)
        except PlaywrightTimeoutError:
            return False
        return True

    def is_element_invisible(self, *locator, timeout: float = timeout_sec) -> bool:
        try:
            self.element(*locator).wait_for(state='hidden', timeout=timeout * 1000)
        except PlaywrightTimeoutError:
            return False
        return True

    def is_popup_present(self, locator, timeout: float = timeout_sec) -> bool:
        return self.is_element_present(locator, timeout=timeout)

    # Check if file downloaded after clicking the element
    def check_if_file_downloaded(self, *locator) -> bool:
        try:
            with self.page.expect_download(timeout=self.timeout_sec * 1000) as download_info:
                self.click(*locator)
            return download_info.value is not None
        except PlaywrightTimeoutError:
            return False

    # -> GETTERS

    @allure.step('Get page title')
    def get_title(self) -> str:
        return self.page.title()

    def get_current_url(self) -> str:
        return self.page.url

    @allure.step('Get text of element - {locator}')
    def get_text(self, *locator, wait: bool = True, timeout: float = timeout_sec) -> Optional[str]:
        if not wait and not self.is_element_visible(*locator, timeout=timeout):
            return None
        return self.element(*locator).inner_text(timeout=timeout * 1000)

    @allure.step('Get text of many elements - {locator}')
    def get_text_of_many_elements(self, *locator, wait: bool = True, timeout: float = timeout_sec) -> list:
        if wait:
            self.find_element(*locator, timeout=timeout)
        return self.page.locator(self._selector(*locator)).all_inner_texts()

    @allure.step('Get attribute "{attribute}" value of element - {locator}')
    def get_attribute_value(self, attribute: str, *locator, timeout: float = timeout_sec) -> str:
        return self.find_element(*locator, timeout=timeout).get_attribute(attribute)

    @allure.step('Get options in the dropdown with the lazy loading')
    def get_all_options_from_lazy_loading_select(self, options_locator, wait: bool = True) -> List[str]:
        # For animation
        time.sleep(1)
        options = []
        previous_texts = None
        while True:
            visible_options = self.find_elements(options_locator, wait=wait)
            texts = [option.inner_text() for option in visible_options if option.inner_text()]
            options += texts
            # To check that list is still scrollable
            if texts == previous_texts:
                return list(set(options))
            previous_texts = texts
            self.scroll_element_to_center_by_js(visible_options[-1])

    @allure.step('Scroll lazy loading selector to the top')
    def scroll_lazy_loading_selector_to_the_top(self, options_locator):
        self._scroll_lazy_loading_selector(options_locator, to_bottom=False)

    @allure.step('Scroll lazy loading selector to the bottom')
    def scroll_lazy_loading_selector_to_the_bottom(self, options_locator):
        self._scroll_lazy_loading_selector(options_locator, to_bottom=True)

    def _scroll_lazy_loading_selector(self, options_locator, to_bottom: bool):
        previous_texts = None
        while True:
            visible_options = self.find_elements(options_locator)
            texts = [option.inner_text() for option in visible_options]
            if texts == previous_texts:
                break
            previous_texts = texts
            self.scroll_element_to_center_by_js(visible_options[-1 if to_bottom else 0])

    # -> WAITERS

    def wait_current_url_contains_text(self, text: str):
        try:
            self.page.wait_for_url(re.compile(f'.*{re.escape(text)}.*'), timeout=5000)
        except PlaywrightTimeoutError:
            pass

    def wait_until_element_is_present(self, *locator, timeout: float = timeout_sec):
        try:
            self.element(*locator).wait_for(state='attached', timeout=timeout * 1000)
        except PlaywrightTimeoutError:
            raise AssertionError(f'Element "{locator}" not present in DOM after {timeout} seconds')

    def wait_until_element_is_visible(self, *locator, timeout: float = timeout_sec):
        try:
            self.element(*locator).wait_for(state='visible', timeout=timeout * 1000)
        except PlaywrightTimeoutError:
            raise AssertionError(f'Element "{locator}" not visible after {timeout} seconds')

    def wait_until_element_is_hidden(self, *locator, timeout: float = timeout_sec):
        try:
            self.element(*locator).wait_for(state='hidden', timeout=timeout * 1000)
        except PlaywrightTimeoutError:
            raise AssertionError(f'Element "{locator}" was present for too long. '
                                 f'It takes more than {timeout} sec to hide an element')

    def wait_until_element_is_clickable(self, *locator, timeout: float = timeout_sec):
        try:
            expect(self.element(*locator)).to_be_enabled(timeout=timeout * 1000)
        except AssertionError:
            raise AssertionError(
                f'Element "{locator}" not clickable. It takes more than {timeout} sec to load an element')

    def wait_until_element_is_disabled(self, *locator, timeout: float = timeout_sec):
        try:
            expect(self.element(*locator)).to_be_disabled(timeout=timeout * 1000)
        except AssertionError:
            raise AssertionError(f'Element {locator} has not been disabled during {timeout} seconds')

    # -> LOGS

    # Network/console events are collected via listeners, so capture starts
    # when the first page object is created
    def _start_log_capture(self):
        if hasattr(self.page, 'captured_network_events'):
            return
        self.page.captured_network_events = []
        self.page.captured_console_messages = []
        self.page.on('request', lambda r: self.page.captured_network_events.append(
            {'type': 'request', 'url': r.url, 'method': r.method, 'time': time.time()}))
        self.page.on('response', lambda r: self.page.captured_network_events.append(
            {'type': 'response', 'url': r.url, 'status': r.status, 'time': time.time()}))
        self.page.on('console', lambda m: self.page.captured_console_messages.append(f'{m.type}: {m.text}'))

    def get_network_logs(self, event_type: str = 'request', seconds: int = 10) -> List[dict]:
        events = [e for e in self.page.captured_network_events if e['type'] == event_type]
        if event_type == 'request':
            cutoff = datetime.now() - timedelta(seconds=seconds)
            events = [e for e in events if datetime.fromtimestamp(e['time']) > cutoff]
        return events

    def get_console_log(self) -> str:
        return '; \n'.join(self.page.captured_console_messages)
