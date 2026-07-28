@api
Feature: TCB public API

  These hit the JSON API the TCB Vue frontend calls under /api/. It has no
  published docs/Swagger, but is public and unauthenticated.

  Scenario: Site is not in maintenance mode
    Given TCB API client
    When I request the maintenance status
    Then the response status code is "200"
    And the site is not in maintenance mode

  Scenario: Team filters are exposed
    Given TCB API client
    When I request the list of team filters
    Then the response status code is "200"
    And each filter has an id, slug and title

  Scenario Outline: Reviews list is paginated correctly
    Given TCB API client
    When I request page "<page>" of reviews sorted "<sort_desc>"
    Then the response status code is "200"
    And the reported current page is "<page>"

    Examples:
      | page | sort_desc |
      | 1    | 1         |
      | 2    | 1         |
      | 3    | 1         |
      | 1    | 0         |

  @negative
  Scenario: Unknown API endpoint returns 404
    Given TCB API client
    When I request the unknown endpoint "/promo/does-not-exist/"
    Then the response status code is "404"
