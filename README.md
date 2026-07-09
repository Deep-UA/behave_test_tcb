# behave practice
Just a python [behave](https://behave.readthedocs.io/en/stable/index.html) test runner practice

As usual I don't like BDD frameworks at all, cause you need to support additional layer of logic and map all the steps 
to the text feature files.

To be honest, I didn't have a troubles to start this PoC. Allure report integrated easily, setup/teardown logic also 
setup without any troubles, but write separate methods with text decorators for each step is so annoying.

## Playwright + Behave conventions

The suite runs on [Playwright](https://playwright.dev/python/) (migrated from Selenium).

### Running

```bash
pip install -r requirements.txt
playwright install                # download browser binaries (once)
behave                            # run everything, headed
HEADLESS=true behave              # headless
BROWSER=firefox behave            # chrome (default) | firefox | safari/webkit
```

### Configuration

All defaults live in `configuration/configs.yaml` under `browser_settings`
(browser, headless, viewport, navigation timeout, mobile device). Any value
can be overridden by an env var with the same name uppercased, e.g.
`VIEWPORT_WIDTH=1366 behave`.

### Isolation

The browser launches once per run; every scenario gets a **fresh browser
context** (clean cookies/storage) via `before_scenario`. Never rely on state
left by a previous scenario.

Tag a scenario with `@mobile` to run it in an emulated mobile device
(configured by `mobile_device` in configs.yaml) instead of the desktop viewport.

### Debugging failures

On failure the Allure report gets a screenshot, the HTML source, console log
and a **Playwright trace**. Traces are also written to `traces/` — open them
with `playwright show-trace traces/<scenario>.zip` for a full time-travel
recording (DOM snapshots, network, console for every action).

### Writing locators

- Locators are plain Playwright selector strings in `*_locators.py` files:
  CSS by default, `xpath=...` for XPath, `text=...` for text.
- Prefer user-facing selectors (text, roles, stable attributes like `[name=]`,
  `[title=]`) over style-coupled CSS classes — they survive redesigns.
- Page objects expose *user intent* methods (`register_account()`), steps
  never touch selectors directly, and `Then` steps assert on booleans returned
  by `is_*` page-object methods.