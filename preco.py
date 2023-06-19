import csv
import re
import requests
from bs4 import BeautifulSoup
from tabulate import tabulate

def normalize_string(text):
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text

def extract_price_from_text(price_text):
    price_text = re.sub(r'[^\d,.]', '', price_text)
    try:
        price = float(price_text.replace(',', '.'))
        return price
    except ValueError:
        return None

def search_product_price(product_name):
    search_url = f"https://www.amazon.com.br/s?k={product_name.replace(' ', '+')}"
    for _ in range(10):
        response = requests.get(search_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        price_elements = soup.find_all('span', class_='a-offscreen')
        for price_element in price_elements:
            price_text = price_element.get_text()
            price = extract_price_from_text(price_text)
            if price is not None:
                return price
    return None

def read_products_from_csv(file_path):
    products = []
    with open(file_path, 'r', newline='', encoding='utf-8-sig') as file:
        reader = csv.reader(file)
        next(reader)  # Ignora o cabeçalho do arquivo CSV
        for row in reader:
            product_name = row[0].strip()
            if product_name:
                normalized_name = normalize_string(product_name)
                products.append(normalized_name)
    return products

def get_product_prices(products):
    results = []
    for product_name in products:
        lowest_price = search_product_price(product_name)
        if lowest_price is None:
            lowest_price = "Preço não encontrado"
        else:
            lowest_price = f"R${lowest_price:.2f}"
        results.append([product_name, lowest_price])
    return results

def display_results(results):
    table_headers = ["Produto", "Preço na Amazon"]
    print(tabulate(results, headers=table_headers, tablefmt="grid"))

# Solicita ao usuário o caminho do arquivo CSV
csv_file_path = input("Digite o caminho do arquivo CSV: ")

# Lê os produtos do arquivo CSV
product_names = read_products_from_csv(csv_file_path)

# Realiza a busca de preços para cada produto
results = get_product_prices(product_names)

# Exibe os resultados em uma tabela
display_results(results)
