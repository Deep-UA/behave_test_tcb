Feature: TCB site navigation

  Scenario: Redirection to the contact page
    Given Open TCB site
    When Go to the contact page via menu
    Then Check user is redirected to the contact page
