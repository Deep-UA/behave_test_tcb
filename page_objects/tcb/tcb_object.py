from page_objects.base_page import BasePage
from page_objects.tcb.tcb_locators import TcbLocators


class TcbPage(BasePage):
    def open_site(self):
        self.open()
        # The Vue app binds click handlers after the load event; without this
        # wait, early clicks (e.g. the avatar icon) land before hydration and do nothing
        self.page.wait_for_load_state('networkidle')

    def go_to_contact_page(self):
        self.click(TcbLocators.MENU_BTN)
        self.click(TcbLocators.CONTACT_LINK)

    def is_redirected_to_contact_page(self) -> bool:
        self.wait_current_url_contains_text('/contacts/')
        return ('/contacts/' in self.get_current_url()
                and self.is_element_visible(TcbLocators.CONTACT_PAGE_TITLE))

    def click_to_avatar_icon(self):
        self.click(TcbLocators.AVATAR_ICON)

    def check_telephone_input(self):
        return self.is_element_visible(TcbLocators.INPUT_TEL)

    def login_with_phone(self, phone_number: str, confirmation_wait_sec: int = 60):
        # Masked input ('(---) --- -- --'), so type digits instead of fill()
        self.type_without_clearing(phone_number, TcbLocators.INPUT_TEL)
        self.click(TcbLocators.LOGIN_NEXT_BTN)
        # Manual step: enter the SMS code in the opened browser window (run
        # headed). Instead of a blind sleep, wait until the logged-in state
        # ("Мій кабінет" button) appears
        self.wait_until_element_is_visible(TcbLocators.MY_CABINET_BTN, timeout=confirmation_wait_sec)

    def confirm_sms_code(self, code: str):
        """Fill the 4 one-digit SMS inputs, if the code is known programmatically"""
        self.wait_until_element_is_visible(TcbLocators.OTP_INPUT)
        for index, digit in enumerate(code):
            self.page.locator(self._selector(TcbLocators.OTP_INPUT)).nth(index).fill(digit)

    def go_to_user_menu_item(self, menu_item: str):
        self.click(self.get_parametrized_locator(TcbLocators.BUTTON_BY_NAME, [menu_item]))

    def open_tab(self, tab_name: str):
        self.click(self.get_parametrized_locator(TcbLocators.LINK_BY_NAME, [tab_name]))

    def is_name_in_profile(self, expected_name: str) -> bool:
        return self.is_element_visible(
            self.get_parametrized_locator(TcbLocators.HEADING_BY_NAME, [expected_name]))
