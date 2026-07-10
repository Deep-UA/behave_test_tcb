Feature: TCB by phone

   Scenario: Login with mobile phone
     Given Open TCB site
     When Click to the avatar icon
     And Put in my number and wait for SMS code screen
     And Logged in go to "Мій кабінет"
     Then Check that in "Мої дані" tab name="Попович Дмитро Ігорович"