import os
import time

from behave import *

from page_objects.tcb.tcb_object import TcbPage


@given('Open TCB site')
def open_tcb_site(context):
    context.tcb_page = TcbPage(context.page)
    context.tcb_page.open_site()


@when('Go to the contact page via menu')
def go_to_contact_page(context):
    context.tcb_page.go_to_contact_page()


@then('Check user is redirected to the contact page')
def check_redirected_to_contact_page(context):
    assert context.tcb_page.is_redirected_to_contact_page(), \
        f'User was not redirected to the contact page, current url: {context.tcb_page.get_current_url()}'

@when('Click to the avatar icon')
def click_to_avatar_icon(context):
    context.tcb_page.click_to_avatar_icon()

@then('Check if login modal opened and has telephone input field')
def check_login_modal_opened(context):
    time.sleep(3)
    assert context.tcb_page.check_telephone_input()


@when('Put in login telephone input field my number and wait 10 sec')
def put_in_phone_number(context):
    phone = os.getenv('TCB_PHONE')
    assert phone, ('Phone number is not set. Run with TCB_PHONE env var, '
                   'e.g.: TCB_PHONE=0671234567 behave features/tcb_login_by_phone.feature')
    context.tcb_page.login_with_phone(phone)


@when('Logged in go to "{menu_item}"')
def go_to_user_menu_item(context, menu_item):
    context.tcb_page.go_to_user_menu_item(menu_item)


@then('Check that in "{tab}" tab name="{expected_name}"')
def check_name_in_profile_tab(context, tab, expected_name):
    context.tcb_page.open_tab(tab)
    assert context.tcb_page.is_name_in_profile(expected_name), \
        f'Name "{expected_name}" not found in "{tab}" tab, url: {context.tcb_page.get_current_url()}'