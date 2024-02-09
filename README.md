This is a sample CTF challenge for transfering funds from the admin account to your account abusing a XSS and CSRF vulnerability.

Credit to the original repo I copied from: https://github.com/Team-Probably/WebCTF/tree/master/csrf
Updates were made so using a selenium webdriver to automatically grab the feedback and execute any payloads left in the feedback for the admin user. More updates such as limiting transfer to 1000 and clearing stored payloads after viewing. 
