from bs4 import BeautifulSoup
from IPython import embed
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import codecs
import re
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import numpy as np
from termcolor import colored

df = pd.read_excel('cidade_dir.xlsx')

index = 0
val="https://resultados.tse.jus.br/oficial/app/index.html#/divulga/votacao-nominal;e=545;cargo=1;uf=zz;mu=29254"

while index < 181:
    try:
        driver = webdriver.Chrome()
        driver.get(val)

        elem = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".scrollable-content")) #This is a dummy element
        )

        legenda = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "app-legenda-votacao.mx-4.mt-12")) #This is a dummy element
        )

        svg_arc = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "app-grafico-votacao")) #This is a dummy element
        )

        soup = BeautifulSoup(elem.get_attribute("innerHTML"), features="lxml")
        divs = soup.find_all("div", class_="py-2")

        cidade = divs[0].text.split(",")[0].strip()
        lula_voto = divs[1].text.split("·")[0].split("Votação")[1].strip().replace(".", "")
        lula_pct = divs[1].text.split("·")[1].strip().replace(",", ".").replace("%",'')
        bolsonaro_voto = divs[2].text.split("·")[0].split("Votação")[1].strip().replace(".", "")
        bolsonaro_pct = divs[2].text.split("·")[1].strip().replace(",", ".").replace("%",'')

        df.loc[df["website_name"] == cidade, 'lula_votos_2o'] = lula_voto
        df.loc[df["website_name"] == cidade, 'lula_pct_2o'] = lula_pct
        df.loc[df["website_name"] == cidade, 'bolsonaro_votos_2o'] = bolsonaro_voto
        df.loc[df["website_name"] == cidade, 'bolsonaro_pct_2o'] = bolsonaro_pct

        arc = BeautifulSoup(legenda.get_attribute("innerHTML"), features="lxml")
        concorrentes_pct = arc.find("h2", class_="text-center").text.split("·")[1].strip().replace(",", ".").replace("%",'')
        grid = arc.find_all("div", class_="legenda-grid")
        df.loc[df["website_name"] == cidade, 'concorrentes_pct'] = bolsonaro_pct

        votos_total = svg_arc.text.split("\n")[0].replace(".", "")
        votos_validos = grid[0].find_all("div", class_="font-bold")[0].text.strip().replace(".", "")
        anulados = grid[0].find_all("div", class_="font-bold")[1].text.strip().replace(".", "")
        anulados_sub_judice = grid[0].find_all("div", class_="font-bold")[2].text.strip().replace(".", "")
        df.loc[df["website_name"] == cidade, 'votos_total'] = votos_total
        df.loc[df["website_name"] == cidade, 'votos_validos'] = votos_validos
        df.loc[df["website_name"] == cidade, 'anulados'] = anulados
        df.loc[df["website_name"] == cidade, 'anulados_sub_judice'] = anulados_sub_judice

        nulos = grid[1].find_all("div", class_="font-bold")[0].text.split('·')[0].strip().replace(".", "")
        nulos_pct = grid[1].find_all("div", class_="font-bold")[0].text.split('·')[1].strip().replace(",", ".").replace("%",'')

        em_branco = grid[1].find_all("div", class_="font-bold")[1].text.strip().split('·')[0].strip().replace(".", "")
        em_branco_pct = grid[1].find_all("div", class_="font-bold")[1].text.strip().split('·')[1].strip().replace(",", ".").replace("%",'')

        anulados_e_apurados = grid[1].find_all("div", class_="font-bold")[2].text.strip().split('·')[0].strip().replace(".", "")
        anulados_e_apurados_pct = grid[1].find_all("div", class_="font-bold")[2].text.strip().split('·')[1].strip().replace(",", ".").replace("%",'')

        df.loc[df["website_name"] == cidade, 'nulos'] = nulos
        df.loc[df["website_name"] == cidade, 'nulos_pct'] = nulos_pct
        df.loc[df["website_name"] == cidade, 'em_branco'] = em_branco
        df.loc[df["website_name"] == cidade, 'em_branco_pct'] = em_branco_pct
        df.loc[df["website_name"] == cidade, 'anulados_e_apurados'] = anulados_e_apurados
        df.loc[df["website_name"] == cidade, 'anulados_e_apurados_pct'] = anulados_e_apurados_pct

        # cidade_match = df.loc[df["website_name"] == cidade, "city_pt"] == cidade

        # df.loc[df["website_name"] == cidade, 'name_match'] = cidade_match

        if df.loc[df["website_name"] == cidade, "city_loc2"].isnull().bool():
            df.loc[df["website_name"] == cidade, 'city_loc2'] = ''
            df.loc[df["website_name"] == cidade, 'country_loc2'] = ''

        index += 1

        driver.find_element(By.CSS_SELECTOR, "img[src='assets/navegacao/icone.svg']").click()

        cidade_dropdown = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".mat-form-field.ng-tns-c73-8")) #This is a dummy element
        )

        cidade_dropdown.click()

        cidades_list = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#cdk-overlay-0")) #This is a dummy element
        )

        cidades = driver.find_elements(By.CSS_SELECTOR, "#cdk-overlay-0 .mat-option")
        flag = df["flag"].loc[df["website_name"] == cidade].values[0]

        if lula_pct > bolsonaro_pct:
            resultado = colored(' Lula! ', 'white', 'on_red')
            score = lula_pct
            votos = lula_voto

        elif lula_pct < bolsonaro_pct:
            resultado = resultado = colored(" Fuckão :( ", 'white', 'on_blue')
            score = bolsonaro_pct
            votos = bolsonaro_voto

        else:
            if lula_pct == "0.00":
                resultado = "Nada"
                score = 0
                votos = 0
            else:
                resultado = "Tie"
                score = lula_pct
                votos = lula_voto


        print(str(index) + '. ' + cidade + ' ' + flag + '   ' + resultado + ' (' + str(score) + '%, ' + str(votos) + ' votos)')
        if index < len(cidades):
            next_cidade = cidades[index].text
            cidades[index].click()

            consultar = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "ion-button[type='submit']")) #This is a dummy element
            )

            consultar.click()

            WebDriverWait(driver, 10).until(
                EC.text_to_be_present_in_element((By.CSS_SELECTOR, 'virtual-scroller .font-bold.text-3xl'), next_cidade + ', ZZ') #This is a dummy element
            )

            val = driver.current_url

    finally:
        driver.quit()

with open('data.csv', 'w') as csv_file:
    df.to_csv(index=False, path_or_buf=csv_file)
