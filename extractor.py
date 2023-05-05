import os
from time import sleep
from anticaptchaofficial.recaptchav2proxyless import *
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import io, base64
from PIL import Image
import uuid
import pandas as pd

def main():

    # Chrome Options
    options = Options()
    options.add_experimental_option("detach", True)

    # start chrome browser
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    url = "https://www.sunarp.gob.pe/consulta-vehicular.html"

    page = driver.get(url)

    apikey = os.getenv("apikey") # apikey for anticaptcha
    sleep(1)

    # list of placas : TEST !
    df_placas = pd.read_csv("input/muestra_placa_rv.txt")
    placas = df_placas.loc[:200, "PLACA"].to_list()

    for placa in placas:
        print(placa)
        # insert placa to search
        input_text = driver.find_element(By.ID, "MainContent_txtNoPlaca")
        input_text.send_keys(placa)

        # find key captcha to resolve
        sitekey = driver.find_element(By.XPATH, '//*[@id="ReCaptchContainer"]/div/div/iframe').get_attribute('outerHTML')
        sitekey_clean = sitekey.split(";")[1].split("k=")[1][:40]
        print( sitekey_clean )

        # resolve captcha
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

        # set captcha response 
        driver.execute_script('var element=document.getElementById("g-recaptcha-response"); element.style.display="";')
        driver.execute_script("""document.getElementById("g-recaptcha-response").innerHTML = arguments[0]""", g_response)
        driver.execute_script('var element=document.getElementById("g-recaptcha-response"); element.style.display="none";')
        driver.find_element(By.XPATH, '//*[@id="MainContent_btnSearch"]').click()
        sleep(.5)

        # save image
        try:
            driver.find_element(By.ID, "MainContent_imgPlateCar")
            print("placa valida!")
            file_name =  uuid.uuid4()
            img = driver.find_element(By.ID, "MainContent_imgPlateCar")
            imgb64 = img.get_attribute("src").split(",")[1]
            # download image
            dwl_img = Image.open(io.BytesIO(base64.decodebytes(bytes(imgb64, "utf-8"))))
            dwl_img.save(f"files/{placa}_{file_name}.png")
        except NoSuchElementException as exec:
            print("no existe la placa!")

        driver.delete_all_cookies()
        driver.refresh()

if __name__ == "__main__":
    main()