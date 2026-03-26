## Análise de Poemas em Português com NLP - Task 02

### 📌 Descrição do Projeto
Este projeto realiza uma análise textual de poemas em português, focando na comparação entre técnicas de Stemming e Lematização. O estudo utiliza Processamento de Linguagem Natural (NLP) para entender como o pré-processamento impacta a dimensionalidade do vocabulário e a preservação do sentido em textos literários.

### 🎯 Objetivos
- Exploração: Analisar a estrutura do dataset poems-in-portuguese;
- Pré-processamento: Aplicar limpeza (lowercase, remoção de pontuação e números);
- Filtragem: Avaliar a eficiência da remoção de stopwords;
- Comparação Técnica: Contrastar resultados entre Stemming (RSLP) e Lematização (spaCy);
- Desempenho: Medir a velocidade computacional entre as bibliotecas NLTK e spaCy.

### 🛠 Tecnologias Utilizadas
- Python
- Pandas & NumPy: Manipulação de dados;
- NLTK: Tokenização e Stemming (RSLP);
- spaCy (pt_core_news_sm): Lematização e análise morfossintática;
- Matplotlib & Seaborn: Visualização de dados e gráficos de frequência;
- Scikit-learn: Vetorização (TF-IDF) e Similaridade de Cosseno;
- WordCloud: Geração de nuvens de palavras para visualização de termos.

### 🔄 Pipeline de Processamento
- Limpeza Inicial: Conversão para minúsculas e remoção de caracteres não alfabéticos.
- Remoção de Stopwords: Filtragem de artigos, preposições e conjunções.
- Normalização:
    - Stemming: Redução ao radical (ex: "correndo" -> "corr").
    - Lematização: Redução à forma canônica (ex: "correndo" -> "correr").
- Análise Quantitativa: Contagem de tokens e cálculo de redução de vocabulário.
- Vetorização: Aplicação de TF e TF-IDF para identificar termos relevantes.

### 📊 Principais Resultados
- Redução de Ruído: A remoção de stopwords gerou uma taxa de redução de 58,2% no volume de tokens
- Trade-off de Performance: O NLTK foi aproximadamente 3,2 vezes mais rápido que o spaCy em textos curtos
- Qualidade Linguística: A lematização mostrou-se superior para análise semântica por preservar palavras válidas, enquanto o stemming foi mais agressivo e gerou radicais inexistentes
- Inconsistência de Dados: Foi detectada a presença de termos em inglês no dataset original, como "the" e "of"

### 📦 Instalação e Execução
**1. Clonar o repositório:**
```bash
git clone https://github.com/viichoma/PLN.git
cd (pasta desejada)
```

**2. Instalar dependências:**
```bash
pip install -r requirements.txt
```

**3. Downloads Adicionais (Necessário):**
```bash
python -m spacy download pt_core_news_sm
python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt'); nltk.download('rslp')"
```

**4. Execução:**

Abra o notebook `Task02.ipynb` em seu ambiente Jupyter ou VS Code e execute todas as células para gerar os gráficos e análises.
