Feature: TCB by phone

   Scenario: Login with mobile phone
     Given Open TCB site
     When Click to the avatar icon
     And Put in login telephone input field my number and wait 10 sec
     And Logged in go to "Мій кабінет"
     Then Check that in "Мої дані" tab name="Попович Дмитро Ігорович"