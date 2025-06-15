import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from streamlit_folium import folium_static
from folium.plugins import HeatMap
import datetime

# Configuração da página
st.set_page_config(
    page_title="Dashboard - Análise do Mercado Imobiliário",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Função para formatar valores monetários
def format_currency(value):
    if value >= 1e6:
        return f"${value/1e6:.1f}M"
    elif value >= 1e3:
        return f"${value/1e3:.1f}K"
    else:
        return f"${value:.2f}"

# Função para carregar os dados
@st.cache_data
def load_data():
    df = pd.read_csv('././kc_house_data.csv')
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['season'] = df['month'].apply(lambda x: 'Spring' if x in [3,4,5] 
                                   else 'Summer' if x in [6,7,8]
                                   else 'Fall' if x in [9,10,11]
                                   else 'Winter')
    
    # Calculando métricas derivadas
    df['price_per_sqft'] = df['price'] / df['sqft_living']
    df['age'] = 2025 - df['yr_built']
    df['renovation_age'] = df.apply(lambda x: 2025 - x['yr_renovated'] if x['yr_renovated'] > 0 else x['age'], axis=1)
    df['total_bathrooms'] = df['bathrooms'].astype(int)
    df['price_category'] = pd.qcut(df['price'], q=5, labels=['Muito Baixo', 'Baixo', 'Médio', 'Alto', 'Muito Alto'])
    
    return df

# Carregando os dados
df = load_data()

# Estilo CSS personalizado
st.markdown("""
    <style>
        .big-font {
            font-size:24px !important;
            font-weight: bold;
        }
        .metric-card {
            background-color: #f0f2f6;
            padding: 15px;
            border-radius: 10px;
            margin: 10px;
            text-align: center;
            border-left: 5px solid #0f4c81;
        }
        .stMetric {
            background-color: #ffffff;
            padding: 15px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .stMetric label {
            color: #0f4c81;
            font-weight: 500;
        }
        .stMetric .metric-value {
            color: #2c3e50;
            font-size: 24px;
            font-weight: bold;
        }
        .highlight {
            background-color: #e8f4f8;
            padding: 20px;
            border-radius: 10px;
            margin: 10px 0;
        }
        .small-font {
            font-size: 12px;
            color: #666;
        }
        div[data-testid="stMetricDelta"] {
            background-color: #f8f9fa;
            padding: 3px 10px;
            border-radius: 15px;
        }
    </style>
""", unsafe_allow_html=True)

# Título do Dashboard
st.title("🏠 Dashboard - Análise do Mercado Imobiliário")
st.markdown("""
    <div class='small-font'>
        Última atualização: {}
    </div>
""".format(datetime.datetime.now().strftime("%d/%m/%Y %H:%M")), unsafe_allow_html=True)
st.markdown("---")

# Tabs para diferentes análises
tab1, tab2, tab3 = st.tabs(["📊 Visão Geral", "🗺️ Análise Geográfica", "📈 Análise Detalhada"])

with tab1:
    # Filtros laterais
    with st.sidebar:
        st.header("Filtros")
        
        # Filtro de data
        date_range = st.date_input(
            "Período de Análise",
            value=(df['date'].min(), df['date'].max()),
            min_value=df['date'].min(),
            max_value=df['date'].max()
        )
        
        # Filtro de preço
        price_range = st.slider(
            'Faixa de Preço (USD)',
            float(df['price'].min()),
            float(df['price'].max()),
            (float(df['price'].min()), float(df['price'].max())),
            format="$%d"
        )
        
        # Filtro de área
        living_area = st.slider(
            'Área Habitável (sqft)',
            float(df['sqft_living'].min()),
            float(df['sqft_living'].max()),
            (float(df['sqft_living'].min()), float(df['sqft_living'].max()))
        )
        
        # Filtros avançados
        with st.expander("Filtros Avançados"):
            # Grade (qualidade)
            grades = sorted(df['grade'].unique())
            selected_grades = st.multiselect(
                'Grade (Qualidade)',
                grades,
                default=grades
            )
            
            # Condição
            conditions = sorted(df['condition'].unique())
            selected_conditions = st.multiselect(
                'Condição',
                conditions,
                default=conditions
            )
            
            # Vista
            views = sorted(df['view'].unique())
            selected_views = st.multiselect(
                'Vista',
                views,
                default=views
            )

    # Aplicando filtros
    filtered_df = df[
        (df['date'].dt.date.between(date_range[0], date_range[1])) &
        (df['price'].between(price_range[0], price_range[1])) &
        (df['sqft_living'].between(living_area[0], living_area[1])) &
        (df['grade'].isin(selected_grades)) &
        (df['condition'].isin(selected_conditions)) &
        (df['view'].isin(selected_views))
    ]

    # Row 1: KPIs principais com comparações
    st.subheader("Métricas Principais")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        current_avg_price = filtered_df['price'].mean()
        overall_avg_price = df['price'].mean()
        price_delta = (current_avg_price / overall_avg_price - 1) * 100
        
        st.metric(
            "Preço Médio",
            format_currency(current_avg_price),
            delta=f"{price_delta:.1f}% vs. média geral"
        )

    with col2:
        current_median_price = filtered_df['price'].median()
        overall_median_price = df['price'].median()
        median_delta = (current_median_price / overall_median_price - 1) * 100
        
        st.metric(
            "Preço Mediano",
            format_currency(current_median_price),
            delta=f"{median_delta:.1f}% vs. mediana geral"
        )

    with col3:
        avg_price_sqft = filtered_df['price_per_sqft'].mean()
        overall_price_sqft = df['price_per_sqft'].mean()
        sqft_delta = (avg_price_sqft / overall_price_sqft - 1) * 100
        
        st.metric(
            "Preço/m² Médio",
            format_currency(avg_price_sqft),
            delta=f"{sqft_delta:.1f}% vs. média geral"
        )

    with col4:
        total_volume = filtered_df['price'].sum()
        count_deals = len(filtered_df)
        
        st.metric(
            "Volume Total",
            format_currency(total_volume),
            delta=f"{count_deals} negócios"
        )

    # Row 2: Análise Temporal e Distribuição
    col1, col2 = st.columns(2)

    with col1:
        # Evolução temporal dos preços com tendência
        st.subheader("Evolução dos Preços")
        price_time = filtered_df.groupby(['date'])['price'].agg(['mean', 'count']).reset_index()
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Linha de preço médio
        fig.add_trace(
            go.Scatter(
                x=price_time['date'],
                y=price_time['mean'],
                name="Preço Médio",
                line=dict(color='#0f4c81', width=3)
            ),
            secondary_y=False
        )
        
        # Linha de tendência
        z = np.polyfit(range(len(price_time)), price_time['mean'], 1)
        p = np.poly1d(z)
        fig.add_trace(
            go.Scatter(
                x=price_time['date'],
                y=p(range(len(price_time))),
                name="Tendência",
                line=dict(color='red', dash='dash')
            ),
            secondary_y=False
        )
        
        # Volume de vendas
        fig.add_trace(
            go.Bar(
                x=price_time['date'],
                y=price_time['count'],
                name="Volume",
                marker_color='rgba(15, 76, 129, 0.3)'
            ),
            secondary_y=True
        )
        
        fig.update_layout(
            title="Evolução do Preço Médio e Volume de Vendas",
            hovermode='x unified',
            plot_bgcolor='white'
        )
        
        fig.update_yaxes(
            title_text="Preço Médio ($)",
            secondary_y=False,
            gridcolor='lightgray'
        )
        fig.update_yaxes(
            title_text="Volume de Vendas",
            secondary_y=True
        )
        
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Box plot dos preços por categoria
        st.subheader("Distribuição dos Preços")
        fig = go.Figure()
        
        fig.add_trace(go.Box(
            x=filtered_df['price_category'],
            y=filtered_df['price'],
            name='Preço',
            marker_color='#0f4c81'
        ))
        
        fig.update_layout(
            title="Distribuição dos Preços por Categoria",
            xaxis_title="Categoria de Preço",
            yaxis_title="Preço ($)",
            plot_bgcolor='white',
            boxmode='group',
            showlegend=False
        )
        
        fig.update_yaxes(gridcolor='lightgray')
        
        st.plotly_chart(fig, use_container_width=True)

    # Row 3: Análises Complementares
    st.subheader("Análises de Valor")
    col1, col2, col3 = st.columns(3)

    with col1:
        # Correlação entre área e preço com linha de tendência
        fig = px.scatter(
            filtered_df,
            x="sqft_living",
            y="price",
            color="grade",
            trendline="ols",
            title="Correlação: Área vs Preço",
            color_continuous_scale="Viridis"
        )
        
        fig.update_layout(
            xaxis_title="Área Habitável (sqft)",
            yaxis_title="Preço ($)",
            plot_bgcolor='white'
        )
        
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Preço médio por sazonalidade
        seasonal_avg = filtered_df.groupby('season')['price'].mean().reset_index()
        seasonal_avg['season'] = pd.Categorical(seasonal_avg['season'], 
                                              categories=['Spring', 'Summer', 'Fall', 'Winter'])
        seasonal_avg = seasonal_avg.sort_values('season')
        
        fig = go.Figure(data=[
            go.Bar(
                x=seasonal_avg['season'],
                y=seasonal_avg['price'],
                marker_color='#0f4c81'
            )
        ])
        
        fig.update_layout(
            title="Preço Médio por Estação",
            xaxis_title="Estação",
            yaxis_title="Preço Médio ($)",
            plot_bgcolor='white'
        )
        
        st.plotly_chart(fig, use_container_width=True)

    with col3:
        # Composição do valor por características
        features = ['bedrooms', 'bathrooms', 'grade', 'condition']
        importance_data = []
        
        for feature in features:
            correlation = filtered_df['price'].corr(filtered_df[feature])
            importance_data.append({
                'feature': feature,
                'correlation': abs(correlation)
            })
        
        importance_df = pd.DataFrame(importance_data)
        
        importance_df = importance_df.sort_values('correlation', ascending=True)
        
        fig = go.Figure(data=[
            go.Bar(
                y=importance_df['feature'],
                x=importance_df['correlation'],
                orientation='h',
                marker_color='#0f4c81'
            )
        ])
        
        fig.update_layout(
            title="Impacto das Características no Preço",
            xaxis_title="Correlação Absoluta",
            yaxis_title="Característica",
            plot_bgcolor='white'
        )
        
        st.plotly_chart(fig, use_container_width=True)

    # Row 4: Métricas de Valor Agregado
    st.subheader("Métricas de Valor Agregado")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Valor total por grade
        value_by_grade = filtered_df.groupby('grade')['price'].agg(['mean', 'sum', 'count']).reset_index()
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig.add_trace(
            go.Bar(
                x=value_by_grade['grade'],
                y=value_by_grade['sum'],
                name="Valor Total",
                marker_color='#0f4c81'
            ),
            secondary_y=False
        )
        
        fig.add_trace(
            go.Scatter(
                x=value_by_grade['grade'],
                y=value_by_grade['mean'],
                name="Preço Médio",
                line=dict(color='red', width=3)
            ),
            secondary_y=True
        )
        
        fig.update_layout(
            title="Valor Total e Médio por Grade",
            xaxis_title="Grade",
            plot_bgcolor='white'
        )
        
        fig.update_yaxes(title_text="Valor Total ($)", secondary_y=False)
        fig.update_yaxes(title_text="Preço Médio ($)", secondary_y=True)
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Distribuição do valor por faixa de preço
        price_dist = pd.qcut(filtered_df['price'], q=10)
        price_summary = filtered_df.groupby(price_dist)['price'].agg(['count', 'mean']).reset_index()
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=price_summary['price'].astype(str),
            y=price_summary['count'],
            name='Quantidade',
            marker_color='#0f4c81'
        ))
        
        fig.add_trace(go.Scatter(
            x=price_summary['price'].astype(str),
            y=price_summary['mean'],
            name='Preço Médio',
            yaxis='y2',
            line=dict(color='red', width=3)
        ))
        
        fig.update_layout(
            title='Distribuição e Média por Faixa de Preço',
            yaxis=dict(title='Quantidade de Imóveis'),
            yaxis2=dict(title='Preço Médio ($)', overlaying='y', side='right'),
            plot_bgcolor='white',
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Análise Geográfica de Preços")
    
    # Filtros específicos para o mapa
    col1, col2 = st.columns(2)
    
    with col1:
        price_filter = st.select_slider(
            'Faixa de Preço para Visualização',
            options=['Todos'] + list(df['price_category'].unique()),
            value='Todos'
        )
    
    with col2:
        map_style = st.selectbox(
            'Estilo de Visualização',
            ['Clusters', 'Heatmap', 'Scatter']
        )
    
    # Filtrando dados para o mapa
    if price_filter != 'Todos':
        map_data = filtered_df[filtered_df['price_category'] == price_filter]
    else:
        map_data = filtered_df
    
    # Criando o mapa base
    m = folium.Map(
        location=[map_data['lat'].mean(), map_data['long'].mean()],
        zoom_start=10,
        tiles='cartodbpositron'
    )
    
    if map_style == 'Heatmap':
        # Heatmap
        heat_data = [[row['lat'], row['long'], row['price']] for index, row in map_data.iterrows()]
        HeatMap(heat_data).add_to(m)
    elif map_style == 'Scatter':
        # Scatter plot no mapa
        for idx, row in map_data.iterrows():
            folium.CircleMarker(
                location=[row['lat'], row['long']],
                radius=5,
                color='blue',
                fill=True,
                popup=f"Preço: ${row['price']:,.2f}<br>"
                      f"Grade: {row['grade']}<br>"
                      f"Quartos: {row['bedrooms']}<br>"
                      f"Área: {row['sqft_living']} sqft",
            ).add_to(m)
    else:
        # Clusters
        from folium.plugins import MarkerCluster
        marker_cluster = MarkerCluster().add_to(m)
        for idx, row in map_data.iterrows():
            folium.Marker(
                location=[row['lat'], row['long']],
                popup=f"Preço: ${row['price']:,.2f}<br>"
                      f"Grade: {row['grade']}<br>"
                      f"Quartos: {row['bedrooms']}<br>"
                      f"Área: {row['sqft_living']} sqft",
            ).add_to(marker_cluster)
    
    # Exibindo o mapa
    folium_static(m, width=1200)
    
    # Análises geográficas complementares
    col1, col2 = st.columns(2)
    
    with col1:
        # Preço médio por região (zipcode)
        zip_prices = map_data.groupby('zipcode')['price'].mean().reset_index()
        
        fig = px.bar(
            zip_prices.sort_values('price', ascending=False).head(10),
            x='zipcode',
            y='price',
            title='Top 10 Regiões mais Valorizadas',
            color='price',
            color_continuous_scale='Viridis'
        )
        
        fig.update_layout(plot_bgcolor='white')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Densidade de preços por região
        fig = px.density_heatmap(
            map_data,
            x='zipcode',
            y='price_category',
            title='Densidade de Preços por Região',
            color_continuous_scale='Viridis'
        )
        
        fig.update_layout(plot_bgcolor='white')
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Análise Detalhada de Valor")
    
    # Seletor de análise
    analysis_type = st.selectbox(
        "Tipo de Análise",
        ["Características do Imóvel", "Tendências Temporais", "Análise de Renovações"]
    )
    
    if analysis_type == "Características do Imóvel":
        # Matriz de correlação interativa
        features = ['price', 'sqft_living', 'grade', 'bathrooms', 'bedrooms', 'view', 'condition']
        corr_matrix = filtered_df[features].corr()
        
        fig = px.imshow(
            corr_matrix,
            title="Matriz de Correlação",
            color_continuous_scale='RdBu',
            aspect='auto'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Análise detalhada por característica
        feature = st.selectbox(
            "Selecione uma característica para análise detalhada",
            features[1:]  # Excluindo 'price' da lista
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Scatter plot com linha de tendência
            fig = px.scatter(
                filtered_df,
                x=feature,
                y='price',
                trendline="ols",
                title=f"Correlação: {feature} vs Preço"
            )
            
            fig.update_layout(plot_bgcolor='white')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Box plot
            fig = px.box(
                filtered_df,
                x=feature,
                y='price',
                title=f"Distribuição de Preços por {feature}"
            )
            
            fig.update_layout(plot_bgcolor='white')
            st.plotly_chart(fig, use_container_width=True)
    
    elif analysis_type == "Tendências Temporais":
        # Análise de tendências
        col1, col2 = st.columns(2)
        
        with col1:
            # Tendência anual
            yearly_trend = filtered_df.groupby('year')['price'].agg(['mean', 'median', 'std']).reset_index()
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=yearly_trend['year'],
                y=yearly_trend['mean'],
                name='Média',
                line=dict(color='#0f4c81', width=3)
            ))
            
            fig.add_trace(go.Scatter(
                x=yearly_trend['year'],
                y=yearly_trend['median'],
                name='Mediana',
                line=dict(color='red', width=3)
            ))
            
            fig.update_layout(
                title='Tendência Anual de Preços',
                plot_bgcolor='white'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Sazonalidade
            seasonal_trend = filtered_df.groupby(['year', 'season'])['price'].mean().reset_index()
            
            fig = px.line(
                seasonal_trend,
                x='year',
                y='price',
                color='season',
                title='Tendência Sazonal de Preços'
            )
            
            fig.update_layout(plot_bgcolor='white')
            st.plotly_chart(fig, use_container_width=True)
    
    else:  # Análise de Renovações
        # Impacto das renovações
        renovated = filtered_df[filtered_df['yr_renovated'] > 0]
        not_renovated = filtered_df[filtered_df['yr_renovated'] == 0]
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Comparação de preços
            fig = go.Figure()
            
            fig.add_trace(go.Box(
                y=renovated['price'],
                name='Renovado',
                boxpoints='outliers',
                marker_color='#0f4c81'
            ))
            
            fig.add_trace(go.Box(
                y=not_renovated['price'],
                name='Não Renovado',
                boxpoints='outliers',
                marker_color='red'
            ))
            
            fig.update_layout(
                title='Distribuição de Preços: Renovados vs Não Renovados',
                plot_bgcolor='white'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # ROI das renovações
            renovation_data = renovated.copy()
            renovation_data['years_since_renovation'] = 2025 - renovation_data['yr_renovated']
            renovation_data['price_per_year'] = renovation_data['price'] / renovation_data['years_since_renovation']
            
            fig = px.scatter(
                renovation_data,
                x='years_since_renovation',
                y='price_per_year',
                title='Retorno sobre Renovação ao Longo do Tempo',
                trendline="ols"
            )
            
            fig.update_layout(plot_bgcolor='white')
            st.plotly_chart(fig, use_container_width=True)

# Rodapé com informações e links úteis
st.markdown("---")
st.markdown("""
    <div style='text-align: center'>
        <p>Dashboard desenvolvido com Streamlit e Plotly | Dados: King County House Sales</p>
        <p class='small-font'>Última atualização: {}</p>
    </div>
""".format(datetime.datetime.now().strftime("%d/%m/%Y %H:%M")), unsafe_allow_html=True)
