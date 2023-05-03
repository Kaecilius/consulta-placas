import os
from time import sleep
from anticaptchaofficial.recaptchav2proxyless import *
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By


def main():
    apikey = os.getenv("apikey") # apikey for anticaptcha
    driver = webdriver.Chrome(ChromeDriverManager().install())
    url = "https://www.sunarp.gob.pe/consulta-vehicular.html"

    page = driver.get(url)
    sleep(5)
    sitekey = driver.find_element(By.XPATH, '//*[@id="ReCaptchContainer"]/div/div/iframe').get_attribute('outerHTML')
    sitekey_clean = sitekey.split(";")[1].split("k=")[1][:40]
    print( sitekey_clean )


    solver = recaptchaV2Proxyless()
    solver.set_verbose(1)
    solver.set_key(apikey)
    solver.set_website_url(url)
    solver.set_website_key(sitekey_clean)
    

    g_response = solver.solve_and_return_solution()

    if g_response!=0:
        print("g_response: "+ g_response)
    else:
        print("error: "+ solver.error_code)

    driver.execute_script('var element=document.getElementById("g-recaptcha-response"); element.style.display="";')
    driver.execute_script("""document.getElementById("g-recaptcha-response").innerHTML = arguments[0]""", g_response)
    driver.execute_script('var element=document.getElementById("g-recaptcha-response"); element.style.display="none";')

    driver.find_element(By.XPATH, '//*[@id="MainContent_btnSearch"]').click()
    

if __name__ == "__main__":
    main()