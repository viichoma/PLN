📊 Análise de Poemas em Português com NLP
📌 Descrição do Projeto

Este projeto realiza uma análise textual de poemas em português utilizando técnicas de Processamento de Linguagem Natural (NLP).

O foco principal é explorar e comparar diferentes abordagens de representação de texto, incluindo:

Frequência de termos (TF)
TF-IDF
Stemming
Lematização

Além disso, o projeto investiga padrões linguísticos entre autores e mede similaridade entre poemas.

🎯 Objetivos
Explorar a estrutura do dataset de poemas
Aplicar técnicas de pré-processamento textual
Comparar texto original, stem e lemma
Identificar termos mais relevantes
Visualizar padrões com WordCloud
Medir similaridade entre poemas
📁 Dataset

O dataset utilizado é:

poems-in-portuguese

Obtido via:

kagglehub.dataset_download("oliveirasp6/poems-in-portuguese")
⚙️ Tecnologias Utilizadas
Python 3.x
Pandas / NumPy
Matplotlib / Seaborn
NLTK
spaCy
Scikit-learn
WordCloud
KaggleHub
📦 Instalação
1. Clonar o repositório
git clone <seu-repositorio>
cd <seu-repositorio>
2. Criar ambiente virtual (opcional, recomendado)
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
3. Instalar dependências
pip install -r requirements.txt
⬇️ Downloads adicionais
NLTK

Executar no Python:

import nltk
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('rslp')
spaCy
python -m spacy download pt_core_news_sm
▶️ Como Executar

Execute o notebook ou script principal:

python main.py

ou no Jupyter:

jupyter notebook
🔄 Pipeline do Projeto
1. Análise Exploratória
Verificação de nulos e duplicados
Contagem de autores
Distribuição de poemas
2. Pré-processamento
Lowercase
Remoção de pontuação
Remoção de números
Tokenização
Remoção de stopwords
3. Normalização Linguística

Comparação entre:

Texto limpo
Stemming (RSLP)
Lematização (spaCy)
4. Vetorização
TF (Term Frequency)
Frequência absoluta de termos
TF-IDF
Importância relativa dos termos
5. Visualizações
Gráficos de frequência
Histogramas
WordClouds:
Por autor
TF vs TF-IDF
Comparação: original vs stem vs lemma
6. Similaridade
Cálculo com cosine similarity
Identificação de poemas mais similares
📊 Resultados

O projeto permite observar:

Redução significativa de tokens após limpeza
Diferenças entre stemming e lematização:
Stemming: mais agressivo
Lemma: mais interpretável
TF destaca termos frequentes
TF-IDF destaca termos relevantes
Padrões distintos entre autores
📁 Saídas Geradas

O projeto gera automaticamente:

📊 Gráficos (.png)
☁️ WordClouds (.png)
📈 Distribuições
📄 Sumário final no console

Todos com alta resolução (dpi ≥ 150)

⚠️ Tratamento de Erros

O código inclui boas práticas como:

Remoção de valores nulos
Verificação de tamanho de textos antes de gerar gráficos
Uso de .copy() para evitar warnings
Controle de listas vazias
🔁 Reprodutibilidade

Para reproduzir os resultados:

Instalar dependências
Baixar recursos (NLTK + spaCy)
Executar o código

Todos os resultados serão gerados automaticamente.