from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time

# 1. Configuración
chrome_options = Options()
# chrome_options.add_argument("--headless") 

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    # 2. Abrir la URL
    url = "https://app.powerbi.com/view?r=eyJrIjoiMzUxMDFjMmEtZGNhNC00Y2NhLThhZTItZTBmMTllNzZkNDhkIiwidCI6IjJmZjI1NWUxLWFlMDAtNDRiYy05Nzg3LWZhOGY4MDYxYmY2OCIsImMiOjR9"
    driver.get(url)
    wait = WebDriverWait(driver, 30)

    print("Buscando el reporte de Power BI...")
    try:
        iframe = wait.until(EC.presence_of_element_condition((By.TAG_NAME, "iframe")))
        driver.switch_to.frame(iframe)
    except:
        print("Continuando en la página base...")

    # 3. Clic para mostrar la tabla
    xpath_boton = '//*[@id="1"]' 
    print("Haciendo clic para desplegar la tabla...")
    boton = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_boton)))
    driver.execute_script("arguments[0].click();", boton)

    print("Esperando 8 segundos a que la tabla cargue...")
    time.sleep(8) 

    # --- EXTRAER ENCABEZADOS DE TU IMAGEN ---
    html_inicial = driver.page_source
    soup_inicial = BeautifulSoup(html_inicial, 'html.parser')
    
    encabezados = []
    column_headers = soup_inicial.find_all('div', role='columnheader')
    for header in column_headers:
        texto = header.get_text(strip=True)
        # Filtramos para evitar encabezados vacíos o basura visual
        if texto and texto not in encabezados: 
            encabezados.append(texto)
            
    print(f"Encabezados detectados: {encabezados}")

    # --- SCROLL Y EXTRACCIÓN DE DATOS ---
    datos_completos = []
    filas_vistas = set() 
    
    intentos_sin_nuevas_filas = 0
    max_intentos = 3 

    print("Iniciando scroll hacia abajo para extraer todos los datos...")
    
    while intentos_sin_nuevas_filas < max_intentos:
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        filas_visibles = soup.find_all('div', role='row')
        
        nuevas_filas_en_esta_vuelta = 0
        
        for fila in filas_visibles:
            celdas = fila.find_all('div', role='gridcell')
            if celdas:
                datos_fila = tuple(celda.get_text(strip=True) for celda in celdas)
                
                # Verificamos que la fila tenga datos y no sea repetida
                if datos_fila and any(datos_fila) and datos_fila not in filas_vistas:
                    filas_vistas.add(datos_fila)
                    datos_completos.append(list(datos_fila))
                    nuevas_filas_en_esta_vuelta += 1
                    
        print(f"Total de registros copiados hasta ahora: {len(datos_completos)}")
        
        if nuevas_filas_en_esta_vuelta == 0:
            intentos_sin_nuevas_filas += 1
        else:
            intentos_sin_nuevas_filas = 0 
            
        # Acción de Scroll
        elementos_fila_selenium = driver.find_elements(By.XPATH, "//div[@role='row']")
        if elementos_fila_selenium:
            ultima_fila = elementos_fila_selenium[-1]
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", ultima_fila)
            except:
                pass 
                
        time.sleep(2) 

    # --- EXPORTAR A CSV ---
    if datos_completos:
        # Aseguramos que la cantidad de columnas coincida con los encabezados
        num_columnas = len(datos_completos[0])
        encabezados_finales = encabezados[:num_columnas] if encabezados else None
        
        df = pd.DataFrame(datos_completos, columns=encabezados_finales)
        
        # Guardar en CSV con soporte para español (utf-8-sig)
        nombre_archivo = "datos_transacciones.csv"
        df.to_csv(nombre_archivo, index=False, encoding='utf-8-sig', sep=',') 
        
        print("\n✅ ¡Éxito! Tu tabla ha sido extraída.")
        print(f"Archivo guardado como: {nombre_archivo}")
        print("\nPrimeras filas del archivo:")
        print(df.head())
        
    else:
        print("No se encontraron datos. Verifica el clic o el tiempo de espera.")

except Exception as e:
    print(f"Ocurrió un error: {e}")

finally:
    driver.quit()