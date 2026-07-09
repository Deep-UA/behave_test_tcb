import os

from playwright.sync_api import Page, sync_playwright

from configuration.config_parse import (
    BROWSER,
    HEADLESS,
    MOBILE_DEVICE,
    NAVIGATION_TIMEOUT_SEC,
    TIMEOUT_SEC,
    VIEWPORT_HEIGHT,
    VIEWPORT_WIDTH,
)

# Selenium-era browser names mapped to Playwright engines, so the existing
# `BROWSER` values keep working
_BROWSER_ENGINES = {
    'chrome': 'chromium',
    'chromium': 'chromium',
    'firefox': 'firefox',
    'safari': 'webkit',
    'webkit': 'webkit',
}


class Driver:
    """One browser per run, one isolated context+page per scenario."""

    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def start_browser(self):
        engine = _BROWSER_ENGINES.get(BROWSER, 'chromium')
        # CI has no display, so it always runs headless
        headless = HEADLESS or bool(os.getenv('DOCKER_RUN')) or bool(os.getenv('GITHUB_RUN'))
        launch_args = ['--no-sandbox', '--disable-dev-shm-usage'] if engine == 'chromium' and headless else []
        self.playwright = sync_playwright().start()
        self.browser = getattr(self.playwright, engine).launch(headless=headless, args=launch_args)
        return self.browser

    def new_page(self, mobile: bool = False) -> Page:
        """Fresh incognito-like context per scenario: clean cookies and storage"""
        if mobile:
            self.context = self.browser.new_context(**self.playwright.devices[MOBILE_DEVICE])
        else:
            self.context = self.browser.new_context(
                viewport={'width': VIEWPORT_WIDTH, 'height': VIEWPORT_HEIGHT}
            )
        self.context.tracing.start(screenshots=True, snapshots=True, sources=True)
        self.page = self.context.new_page()
        self.page.set_default_timeout(TIMEOUT_SEC * 1000)
        self.page.set_default_navigation_timeout(NAVIGATION_TIMEOUT_SEC * 1000)
        return self.page

    def close_page(self, trace_path: str = None):
        """Close the scenario context; pass trace_path to save the trace (on failure)"""
        if self.context:
            self.context.tracing.stop(path=trace_path)
            self.context.close()
            self.context = None
            self.page = None

    def stop(self):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
