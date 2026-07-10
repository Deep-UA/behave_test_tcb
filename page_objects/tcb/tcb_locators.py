class TcbLocators:
    # "Контакти" link lives inside the collapsed "Меню" dropdown in the header,
    # so the menu must be opened before the link is clickable
    MENU_BTN = 'header >> text=Меню'
    CONTACT_LINK = 'nav a[href="/contacts/"]'
    CONTACT_PAGE_TITLE = 'h1:has-text("Контакти"), h2:has-text("Контакти")'
    # Logged out: avatar opens the login modal; logged in the header renders a
    # different component whose button toggles the user dropdown
    AVATAR_ICON = 'button.user-button__login'
    LOGGED_IN_AVATAR = '.user-wrapper_button'
    LOGIN_MODAL = '.modal-wrapper'
    # Login modal
    INPUT_TEL = 'role=textbox[name="Телефон *"]'
    LOGIN_NEXT_BTN = 'role=button[name="Далі"]'
    # SMS confirmation: 4 single-digit inputs, all with accessible name "-"
    OTP_INPUT = 'role=textbox[name="-"]'
    # Logged-in cabinet
    BUTTON_BY_NAME = 'role=button[name="{}"]'
    LINK_BY_NAME = 'role=link[name="{}"]'
    HEADING_BY_NAME = 'role=heading[name="{}"]'
    MY_CABINET_BTN = 'role=button[name="Мій кабінет"]'
