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

def append_blank(df, cidade, zona_num, secao_num):
    pd.concat([df, pd.Series({
        'cidade':cidade,
        'municipo':'',
        'zona':zona_num,
        'secao':secao_num,
        'polling_place':'',
        'lula_voto':'',
        'lula_pct':'',
        'bolsonaro_voto':'',
        'bolsonaro_pct':'',
        'eligible_voters':'',
        'attending_voters':'',
        'noshow_voters':'',
        'turnout_pct':'',
        'valid_votes':'',
        'valid_pct':'',
        'votos_legenda':'',
        'blank_votes':'',
        'null_votes':'',
        'votes_counted':'',
        'machine_type':''
    })], ignore_index = True)

df = pd.read_excel('cidade_dir.xlsx')

index = 0
secao_index = 1
val="https://resultados.tse.jus.br/oficial/app/index.html#/eleicao;uf=zz;ufbu=zz/dados-de-urna;e=e545/boletim-de-urna"
df = pd.DataFrame(columns=['cidade', 'municipo', 'zona', 'secao', 'polling_place','lula_voto', 'lula_pct', 'bolsonaro_voto', 'bolsonaro_pct', 'eligible_voters', 'attending_voters','noshow_voters','turnout_pct','valid_votes','valid_pct','votos_legenda','blank_votes','null_votes','votes_counted','machine_type'])

while index < 181:
    try:
        driver = webdriver.Chrome()
        driver.get(val)

        modal_select = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'app-selecionar-localidade2'))
        )

        modal_select.click()

        cidades_list = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#cdk-overlay-0"))
        )

        cidades = driver.find_elements(By.CSS_SELECTOR, "#cdk-overlay-0 .mat-option")

        cidade = cidades[index].text
        cidades[index].click()

        confirmar = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '.p-5 ion-button'))
        )
        confirmar.click()

        zona = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'mat-form-field.ng-tns-c73-0'))
        )

        zona.click()
        zonas = driver.find_elements(By.CSS_SELECTOR, ".mat-select-panel mat-option")
        zonas[1].click()

        secao = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'mat-form-field:nth-child(2)'))
        )

        secao.click()
        secaos = driver.find_elements(By.CSS_SELECTOR, ".mat-select-panel mat-option")
        secaos_length = len(secaos) - 1

        if secao_index <= secaos_length:
            secaos[secao_index].click()

            pesquisar = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.bg-yellow-500'))
            )
            pesquisar.click()


            if secao_index == 1:
                rdv = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "li.mr-5:nth-child(2) a")) #This is a dummy element
                )
                rdv.click()

                ng_component = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "ng-component")) #This is a dummy element
                )

                if "Não foi possível completar a operação" in ng_component.text:
                    df = append_blank(df, cidade, zona_num, secao_num)
                    index += 1
                    secao_index = 1
                    driver.quit()
                else:
                    boletim_de_urna = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "li.mr-5:nth-child(1) a")) #This is a dummy element
                    )
                    boletim_de_urna.click()

            grid_cols = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".grid-cols-3"))
            )

            elem = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "app-boletim-de-urna")) #This is a dummy element
            )



            soup = BeautifulSoup(elem.get_attribute("innerHTML"), features="lxml")
            cidade = soup.find("div", class_="leading-tight").text.replace(', ZZ', '').strip()
            zona_secao = soup.find_all("div", class_="mat-select-value")
            zona_num = zona_secao[0].text.split(' ')[1].strip()
            secao_num = zona_secao[1].text.split(' ')[1].strip()

            print(cidade + ': Zona ' + zona_num + ', Seção ' + secao_num + ' - ' + str(secao_index) + " do " + str(secaos_length))

            if "Situação da Seção:\nTotalizada" in grid_cols.text:
                urno_stats = soup.find_all("div", class_="mb-4")[1].find_all("div", class_="mb-2")
                urno_type = urno_stats[0].find("p", class_="font-bold").text.strip()

                topline_stats = soup.find("div", class_="grid-cols-4").find_all("div", class_="mb-2")
                if urno_type == 'Urna eletrônica':
                    municipo = topline_stats[0].find("p", class_="font-bold").text.strip()
                    polling_place = topline_stats[3].find("p", class_="font-bold").text.strip()
                    aptos = topline_stats[4].find("p", class_="font-bold").text.strip()
                    comparecimento = topline_stats[5].find("p", class_="font-bold").text.strip()
                    faltosos = topline_stats[6].find("p", class_="font-bold").text.strip()
                else:
                    municipo = topline_stats[0].find("p", class_="font-bold").text.strip()
                    polling_place = ''
                    aptos = topline_stats[6].find("p", class_="font-bold").text.strip()
                    comparecimento = topline_stats[7].find("p", class_="font-bold").text.strip()
                    faltosos = topline_stats[8].find("p", class_="font-bold").text.strip()

                candidatos_div = soup.find_all("div", class_="mt-5")[2].find_all("div", class_="pb-4")

                candidatos = (map(lambda x: x.text.split('Votação'), candidatos_div))

                lula_voto = 0
                bolsonaro_voto = 0

                for c in candidatos:
                    if c[0] == '13':
                        lula_voto = c[1]
                    elif c[0] == '22':
                        bolsonaro_voto = c[1]

                bottom_stats = soup.find_all("div", class_="mb-4")[2].find_all('div', class_='mb-2')
                votos_nominais = bottom_stats[2].find("p", class_="font-bold").text.strip()
                de_legenda = bottom_stats[3].find("p", class_="font-bold").text.strip()
                branco = bottom_stats[4].find("p", class_="font-bold").text.strip()
                nulos = bottom_stats[5].find("p", class_="font-bold").text.strip()
                apurado = bottom_stats[6].find("p", class_="font-bold").text.strip()


                lula_pct = int(lula_voto) / int(votos_nominais)
                bolsonaro_pct = int(bolsonaro_voto) / int(votos_nominais)
                df = pd.concat([df, pd.Series({
                    'cidade':cidade,
                    'municipo':municipo,
                    'zona':zona_num,
                    'secao':secao_num,
                    'polling_place':polling_place,
                    'lula_voto':int(lula_voto),
                    'lula_pct':lula_pct,
                    'bolsonaro_voto':int(bolsonaro_voto),
                    'bolsonaro_pct':bolsonaro_pct,
                    'eligible_voters':int(aptos),
                    'attending_voters':int(comparecimento),
                    'noshow_voters':int(faltosos),
                    'turnout_pct':int(comparecimento)/int(aptos),
                    'valid_votes':int(votos_nominais),
                    'valid_pct':int(votos_nominais)/int(comparecimento),
                    'votos_legenda':int(de_legenda),
                    'blank_votes':int(branco),
                    'null_votes':int(nulos),
                    'votes_counted':int(apurado),
                    'machine_type':urno_type
                })], ignore_index = True)

            else:
                df = append_blank(df, cidade, zona_num, secao_num)


        if secao_index <= secaos_length:
            secao_index += 1
        else:
            index += 1
            secao_index = 1
            driver.quit()

    finally:
        driver.quit()

with open('data-2o-urno.csv', 'w') as csv_file:
    df.to_csv(index=False, path_or_buf=csv_file)
