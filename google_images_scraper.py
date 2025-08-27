#!/usr/bin/env python3
import os
import requests
import time
import json
import re
from urllib.parse import urlparse, unquote
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import hashlib
from PIL import Image
import argparse

class GoogleImagesDownloader:
    def __init__(self, headless=True, delay=1):
        """
        Inicializa o downloader
        
        Args:
            headless: Se True, executa o Chrome sem interface gráfica
            delay: Delay entre downloads (segundos)
        """
        self.delay = delay
        self.setup_driver(headless)
        
    def setup_driver(self, headless):
        """Configura o driver do Chrome"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        except Exception as e:
            print(f"Erro ao inicializar Chrome driver: {e}")
            print("Certifique-se de que o ChromeDriver está instalado!")
            raise
    
    def search_images(self, query, max_images=100):
        """
        Busca imagens no Google Images
        
        Args:
            query: Termo de busca
            max_images: Número máximo de imagens para coletar URLs
        """
        print(f"Buscando imagens para: {query}")
        
        # Monta a URL de busca
        search_url = f"https://www.google.com/search?q={query}&tbm=isch&hl=pt-BR"
        self.driver.get(search_url)
        
        # Aguarda o carregamento
        time.sleep(3)
        
        image_urls = set()  # Usar set para evitar duplicatas
        scroll_pause_time = 2
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        print("Coletando URLs das imagens...")
        
        while len(image_urls) < max_images:
            # Coleta URLs das imagens visíveis
            images = self.driver.find_elements(By.CSS_SELECTOR, 'img[jsaction]')
            
            for img in images:
                try:
                    # Clica na imagem para abrir o painel lateral
                    self.driver.execute_script("arguments[0].click();", img)
                    time.sleep(0.5)
                    
                    # Tenta encontrar a imagem em alta resolução
                    try:
                        # Aguarda a imagem em alta resolução carregar
                        high_res_img = WebDriverWait(self.driver, 3).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, 'img[src*="gstatic"], img[src*="googleusercontent"], img[src*="ggpht"]'))
                        )
                        src = high_res_img.get_attribute('src')
                    except:
                        # Fallback para a imagem original
                        src = img.get_attribute('src')
                    
                    if src and src.startswith('http') and 'data:image' not in src:
                        image_urls.add(src)
                        print(f"  Encontradas: {len(image_urls)}/{max_images}", end='\r')
                        
                        if len(image_urls) >= max_images:
                            break
                            
                except Exception as e:
                    continue
            
            if len(image_urls) >= max_images:
                break
            
            # Scroll para baixo para carregar mais imagens
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause_time)
            
            # Tenta clicar no botão "Mostrar mais resultados"
            try:
                show_more_button = self.driver.find_element(By.CSS_SELECTOR, 'input[value*="mais"], input[value*="more"], .mye4qd')
                if show_more_button.is_displayed():
                    show_more_button.click()
                    time.sleep(3)
            except:
                pass
            
            # Verifica se chegou ao fim da página
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        
        print(f"\nEncontradas {len(image_urls)} URLs de imagens")
        return list(image_urls)[:max_images]
    
    def search_images_alternative(self, query, max_images=100):
        """
        Método alternativo usando busca por data-src e outros atributos
        """
        print(f"Método alternativo para: {query}")
        
        search_url = f"https://www.google.com/search?q={query}&tbm=isch&hl=pt-BR"
        self.driver.get(search_url)
        time.sleep(3)
        
        image_urls = set()
        
        # Scroll e coleta de URLs
        for scroll in range(5):  # Limita scrolls para evitar loops infinitos
            # Busca por diferentes seletores de imagem
            selectors = [
                'img[data-src]',
                'img[src]:not([src*="data:image"])',
                '.rg_i img',
                '.isv-r img'
            ]
            
            for selector in selectors:
                images = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for img in images:
                    try:
                        src = img.get_attribute('data-src') or img.get_attribute('src')
                        if src and src.startswith('http') and len(src) > 50:
                            image_urls.add(src)
                    except:
                        continue
            
            print(f"  URLs coletadas: {len(image_urls)}", end='\r')
            
            if len(image_urls) >= max_images:
                break
                
            # Scroll
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
        
        print(f"\nMétodo alternativo encontrou {len(image_urls)} URLs")
        return list(image_urls)[:max_images]
    
    def download_image(self, url, filepath):
        """
        Baixa uma imagem da URL
        
        Args:
            url: URL da imagem
            filepath: Caminho onde salvar a imagem
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
                'Referer': 'https://www.google.com/'
            }
            
            response = requests.get(url, headers=headers, timeout=15, stream=True)
            response.raise_for_status()
            
            # Verifica se é realmente uma imagem
            content_type = response.headers.get('content-type', '').lower()
            if not content_type.startswith('image/'):
                return False
            
            # Salva a imagem
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Valida e processa a imagem
            try:
                with Image.open(filepath) as img:
                    # Verifica tamanho mínimo
                    if img.size[0] < 100 or img.size[1] < 100:
                        os.remove(filepath)
                        return False
                    
                    # Converte para RGB se necessário
                    if img.mode in ('RGBA', 'P', 'L'):
                        rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        if img.mode == 'RGBA':
                            rgb_img.paste(img, mask=img.split()[-1])
                        elif img.mode == 'L':
                            rgb_img.paste(img)
                        rgb_img.save(filepath, 'JPEG', quality=90)
                    elif img.mode != 'RGB':
                        img.convert('RGB').save(filepath, 'JPEG', quality=90)
                        
            except Exception as e:
                if os.path.exists(filepath):
                    os.remove(filepath)
                return False
                
            return True
            
        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            return False
    
    def create_dataset(self, search_terms, images_per_term=100, output_dir="dataset"):
        """
        Cria um dataset baixando imagens para múltiplos termos de busca
        
        Args:
            search_terms: Lista de termos de busca ou dicionário {termo: num_imagens}
            images_per_term: Número de imagens por termo (se search_terms for lista)
            output_dir: Diretório de saída
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Normaliza search_terms para dicionário
        if isinstance(search_terms, list):
            search_dict = {term: images_per_term for term in search_terms}
        else:
            search_dict = search_terms
        
        total_downloaded = 0
        
        for search_term, num_images in search_dict.items():
            print(f"\n{'='*50}")
            print(f"Processando: {search_term}")
            print(f"{'='*50}")
            
            # Cria diretório para a classe
            class_dir = os.path.join(output_dir, search_term.replace(" ", "_"))
            os.makedirs(class_dir, exist_ok=True)
            
            # Tenta primeiro método, depois alternativo
            image_urls = self.search_images(search_term, num_images * 3)
            
            if len(image_urls) < num_images // 2:  # Se muito poucas URLs
                print("Tentando método alternativo...")
                alt_urls = self.search_images_alternative(search_term, num_images * 2)
                image_urls.extend(alt_urls)
                image_urls = list(set(image_urls))  # Remove duplicatas
            
            downloaded_count = 0
            failed_count = 0
            
            for i, url in enumerate(image_urls):
                if downloaded_count >= num_images:
                    break
                    
                # Gera nome do arquivo usando hash da URL
                url_hash = hashlib.md5(url.encode()).hexdigest()[:10]
                filename = f"{search_term.replace(' ', '_')}_{downloaded_count+1:03d}_{url_hash}.jpg"
                filepath = os.path.join(class_dir, filename)
                
                # Pula se já existe
                if os.path.exists(filepath):
                    continue
                
                print(f"Baixando {downloaded_count + 1}/{num_images}: {filename}")
                
                if self.download_image(url, filepath):
                    downloaded_count += 1
                    total_downloaded += 1
                    print(f"  ✓ Sucesso")
                else:
                    failed_count += 1
                    print(f"  ✗ Falhou")
                
                # Delay entre downloads
                time.sleep(self.delay)
            
            print(f"✓ Baixadas {downloaded_count} imagens para '{search_term}' (falhas: {failed_count})")
        
        print(f"\n{'='*50}")
        print(f"CONCLUÍDO! Total de imagens baixadas: {total_downloaded}")
        print(f"Dataset salvo em: {output_dir}")
        print(f"{'='*50}")
    
    def close(self):
        """Fecha o driver"""
        if hasattr(self, 'driver'):
            self.driver.quit()

def main():
    parser = argparse.ArgumentParser(description="Baixa imagens do Google Images para criar dataset")
    parser.add_argument('--terms', nargs='+', required=True, 
                       help='Termos de busca (ex: --terms "gato" "cachorro" "pássaro")')
    parser.add_argument('--images', type=int, default=50, 
                       help='Número de imagens por termo (padrão: 50)')
    parser.add_argument('--output', default='dataset', 
                       help='Diretório de saída (padrão: dataset)')
    parser.add_argument('--delay', type=float, default=1.0, 
                       help='Delay entre downloads em segundos (padrão: 1.0)')
    parser.add_argument('--headless', action='store_true', 
                       help='Executa sem interface gráfica')
    
    args = parser.parse_args()
    
    downloader = GoogleImagesDownloader(headless=args.headless, delay=args.delay)
    
    try:
        downloader.create_dataset(
            search_terms=args.terms,
            images_per_term=args.images,
            output_dir=args.output
        )
    finally:
        downloader.close()

if __name__ == "__main__":
    # para teste
    if len(os.sys.argv) == 1:  # Se não há argumentos da linha de comando
        print("teste...")
        search_terms = ["golden retriever", "persian cat", "eagle bird"]
        downloader = GoogleImagesDownloader(headless=False, delay=1)  # headless=False para debug
        
        try:
            downloader.create_dataset(
                search_terms=search_terms,
                images_per_term=10,  # Número menor para teste
                output_dir="test_dataset"
            )
        finally:
            downloader.close()
    else:
        main()