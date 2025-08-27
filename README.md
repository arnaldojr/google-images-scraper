# Google Images Dataset Downloader

**Script Python para baixar imagens do Google Images e criar datasets para Deep Learning**

Ferramenta automatizada que busca, baixa e organiza imagens do Google Images em estrutura de pastas pronta para treinamento de modelos de machine learning.

## Requisitos

### Dependências Python
```bash
pip install selenium requests pillow
```

### Instalação do ChromeDriver

**Ubuntu/Debian:**
```bash
sudo apt-get install chromium-chromedriver
```

**MacOS:**
```bash
brew install chromedriver
```

**Windows:**
1. Baixe de https://chromedriver.chromium.org/
2. Adicione ao PATH do sistema

## 🛠 Instalação

1. **Clone o repositório**
```bash
git clone <seu-repositorio>
cd google-images-downloader
```

2. **Crie ambiente virtual (recomendado)**
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate     # Windows
```

3. **Instale dependências**
```bash
pip install -r requirements.txt
```

## Como Usar

### Uso Básico
```bash
python google_images_scraper.py --terms "gato" "cachorro" --images 50
```

### Uso Avançado
```bash
python google_images_scraper.py \
  --terms "golden retriever" "labrador" "bulldog" \
  --images 50 \
  --output dogs_dataset \
  --delay 0.5 \
  --headless
```

## Parâmetros

| Parâmetro | Descrição | Padrão |
|-----------|-----------|---------|
| `--terms` | Termos de busca (obrigatório) | - |
| `--images` | Número de imagens por termo | 50 |
| `--output` | Diretório de saída | `dataset` |
| `--delay` | Delay entre downloads (segundos) | 1.0 |
| `--headless` | Executa sem interface gráfica | False |

###  **Otimização de Velocidade**
```bash
# Modo rápido (menor delay)
--delay 0.5

# Modo conservador (maior delay, menos falhas)  
--delay 2.0

# Modo batch (muitas imagens)
--images 500 --delay 1.0

# exemplo
python google_images_scraper.py --terms "gato" --images 10 --delay 0.5
```

### **Debugging e Testes**
```bash
# Ver navegador funcionando modo verbose (sem headless)
python google_images_scraper.py --terms "gato" --images 10

# Sem Ver navegador funcionando (headless)
python google_images_scraper.py --terms "gato" --images 10 --delay 0.5 --headless
```

## Estrutura de Saída

O dataset é organizado automaticamente:

```
dataset/
├── gato/
│   ├── gato_001_abc123.jpg
│   ├── gato_002_def456.jpg
│   └── gato_003_ghi789.jpg
├── cachorro/
│   ├── cachorro_001_jkl012.jpg
│   ├── cachorro_002_mno345.jpg
│   └── cachorro_003_pqr678.jpg
└── passaro/
    ├── passaro_001_stu901.jpg
    └── passaro_002_vwx234.jpg
```

