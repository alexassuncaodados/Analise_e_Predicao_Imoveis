# Dashboard - Análise do Mercado Imobiliário

Este diretório contém a aplicação do dashboard desenvolvida com Streamlit para análise do mercado imobiliário.



## Principais Funcionalidades

### 1. Visão Geral (📊)
- Métricas principais (preço médio, mediano, etc.)
- Análises temporais de vendas
- Distribuição de preços por características do imóvel
- Estatísticas de mercado

### 2. Análise Geográfica (🗺️)
- Mapa de calor de preços
- Distribuição geográfica dos imóveis
- Análises por região

### 3. Análise Detalhada (📈)
- Correlações entre variáveis
- Tendências de mercado
- Análises específicas por características do imóvel

## Filtros Disponíveis

- Período de análise
- Faixa de preço
- Área habitável
- Filtros avançados:
  - Grade (qualidade do imóvel)
  - Condição
  - Vista

## Tecnologias Utilizadas

- Python
- Streamlit
- Pandas
- Plotly
- Folium
- Numpy

## Como Executar

1. Certifique-se de ter todas as dependências instaladas do projeto no ambiente virtual.:
```bash
pip install -r requirements.txt
```

2. Execute o dashboard:
```bash
streamlit run src/dashboard/app.py
```

3. Acesse o dashboard através do navegador (normalmente em http://localhost:8501)

## Estrutura de Dados

O dashboard utiliza o arquivo `kc_house_data.csv` localizado na raiz do projeto e realiza as seguintes transformações nos dados:

- Conversão de datas
- Cálculo de métricas derivadas (preço por pé quadrado, idade do imóvel, etc.)
- Categorização de preços
- Cálculos de métricas sazonais

## Customização

O dashboard inclui estilos CSS personalizados para melhorar a experiência do usuário e a apresentação visual dos dados. As personalizações incluem:
- Cards de métricas estilizados
- Fontes personalizadas
- Layout responsivo
- Esquema de cores consistente
