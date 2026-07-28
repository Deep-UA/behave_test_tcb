# behave creates given/when/then decorators dynamically, so pylint's
# static analysis flags them as not-callable — a known false positive
# pylint: disable=not-callable
from behave import given, then, when

from page_objects.tcb.tcb_api_client import TcbApiClient


@given('TCB API client')
def create_api_client(context):
    context.api = TcbApiClient()


@when('I request the maintenance status')
def request_maintenance(context):
    context.api.get_maintenance()


@when('I request the list of team filters')
def request_filters(context):
    context.api.get_filters()


@when('I request page "{page:d}" of reviews sorted "{sort_desc:d}"')
def request_reviews_page(context, page, sort_desc):
    context.api.get_reviews(page=page, sort_desc=sort_desc)


@when('I request the unknown endpoint "{path}"')
def request_unknown_endpoint(context, path):
    context.api.get_path(path)


@then('the response status code is "{expected_status:d}"')
def check_status_code(context, expected_status):
    actual = context.api.response.status_code
    assert actual == expected_status, \
        f'Expected status {expected_status}, got {actual} for {context.api.response.url}'


@then('the site is not in maintenance mode')
def check_not_in_maintenance(context):
    body = context.api.json()
    assert body['active'] is False, f'Expected maintenance mode to be off, got: {body}'


@then('the reported current page is "{expected_page:d}"')
def check_reported_page(context, expected_page):
    meta = context.api.json()['meta']
    assert meta['current_page'] == expected_page, \
        f'Expected current_page {expected_page}, got {meta["current_page"]}'
    assert len(context.api.json()['data']) <= meta['per_page'], \
        f'Page returned more items ({len(context.api.json()["data"])}) than per_page ({meta["per_page"]})'


@then('each filter has an id, slug and title')
def check_filters_shape(context):
    filters = context.api.json()['data']
    assert filters, 'Expected at least one team filter'
    for item in filters:
        for field in ('id', 'slug', 'title'):
            assert field in item, f'Filter item missing "{field}": {item}'
