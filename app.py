#!/usr/bin/env python3
"""
🏆 APLICACIÓN INTERACTIVA: PREDICTOR COPA DEL MUNDO FIFA 2026 🏆
Plataforma interactiva para predecir partidos de la fase de grupos
y enfrentamientos personalizados utilizando Inteligencia Artificial.
"""

import os
import sys
import math
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import requests

# Asegurar encoding UTF-8 en Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Importar lógica del predictor existente
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    import wc2026_predictor as pred
except ImportError:
    st.error("❌ No se pudo importar 'wc2026_predictor.py'. Asegúrate de que el archivo existe en el mismo directorio.")
    st.stop()

# =============================================================================
# CONFIGURACIÓN DE PÁGINA Y ESTILOS
# =============================================================================
st.set_page_config(
    page_title="NaleScore 🏆",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo CSS personalizado para look premium
st.markdown("""
<style>
    /* Color de fondo y texto global */
    .stApp {
        background-color: #0F172A;
        color: #F8FAFC;
    }
    
    /* Encabezados */
    h1, h2, h3 {
        font-family: 'Outfit', 'Inter', sans-serif;
        font-weight: 800;
        letter-spacing: -0.025em;
    }
    
    .main-title {
        background: linear-gradient(135deg, #38BDF8, #818CF8, #F43F5E);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem !important;
        text-align: center;
        margin-bottom: 0.5rem;
        font-weight: 900;
    }
    
    .subtitle {
        text-align: center;
        color: #94A3B8;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    
    /* Contenedores y Tarjetas */
    .card {
        background-color: #1E293B;
        border-radius: 16px;
        padding: 24px;
        border: 1px solid #334155;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
        margin-bottom: 20px;
    }
    
    .team-header-a {
        text-align: right;
        font-size: 2.2rem;
        font-weight: 800;
    }
    
    .team-header-b {
        text-align: left;
        font-size: 2.2rem;
        font-weight: 800;
    }
    
    .vs-badge {
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #F43F5E, #E11D48);
        color: white;
        font-weight: 900;
        font-size: 1.5rem;
        border-radius: 50%;
        width: 60px;
        height: 60px;
        margin: 0 auto;
        border: 4px solid #0F172A;
        box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.3);
    }
    
    /* Métricas */
    .metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #F8FAFC;
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Botones y pestañas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #1E293B;
        padding: 6px;
        border-radius: 12px;
        border: 1px solid #334155;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 8px;
        color: #94A3B8;
        font-weight: 600;
        border: none;
        transition: all 0.2s;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #38BDF8 !important;
        color: #0F172A !important;
        font-weight: 700;
    }
    
    /* Alertas */
    .stAlert {
        border-radius: 12px;
        background-color: #1E293B !important;
        border: 1px solid #334155 !important;
    }
</style>
""", unsafe_allow_html=True)

# Colores de Equipos para personalizar la visualización
TEAM_COLORS = {
    'Argentina': '#75AADB',      # Celeste
    'Spain': '#C60B1E',          # Rojo
    'France': '#002395',         # Azul
    'England': '#132257',        # Marino
    'Portugal': '#006600',       # Verde oscuro
    'Brazil': '#FEDD00',         # Amarillo
    'Morocco': '#C1272D',        # Rojo marroquí
    'Netherlands': '#F36C21',    # Naranja
    'Belgium': '#E30613',        # Rojo belga
    'Germany': '#000000',        # Negro
    'Croatia': '#FF0000',        # Rojo cuadros
    'Colombia': '#FCD116',       # Amarillo colombiano
    'Mexico': '#006847',         # Verde mexicano
    'Senegal': '#00853F',        # Verde Senegal
    'Uruguay': '#43A1D5',        # Celeste Uruguay
    'United States': '#002868',  # Azul USA
    'Japan': '#00005F',          # Samurái Blue
    'Switzerland': '#D52B1E',    # Rojo suizo
    'Iran': '#239F40',           # Verde Irán
    'Ecuador': '#FFDD00',        # Amarillo Ecuador
    'Australia': '#FFCD00',      # Oro australiano
    'Turkey': '#E30A17',         # Rojo Turquía
    'South Korea': '#CD2E3A',    # Rojo coreano
    'Austria': '#ED2939',        # Rojo Austria
    'Sweden': '#006AA7',         # Azul sueco
    'Egypt': '#C1272D',          # Rojo Egipto
    'Norway': '#EF2B2D',         # Rojo noruego
    'Scotland': '#0065BF',       # Azul Escocia
    'Algeria': '#006233',        # Verde Argelia
    'Tunisia': '#E01A22',         # Rojo Túnez
    'Paraguay': '#D52B1E',       # Rojo Paraguay
    'Ivory Coast': '#FF8200',    # Naranja Costa de Marfil
    'Czech Republic': '#11457E', # Azul checo
    'Saudi Arabia': '#006C35',   # Verde saudí
    'Ghana': '#FFD100',          # Amarillo Ghana
    'Canada': '#FF0000',         # Rojo Canadá
    'Panama': '#DA121A',         # Rojo Panamá
    'Iraq': '#007A3D',           # Verde Irak
    'Jordan': '#E01A22',         # Rojo Jordania
    'Qatar': '#8A1538',          # Granate Qatar
    'Uzbekistan': '#0099B8',     # Azul Uzbekistán
    'Bosnia and Herzegovina': '#002F6C', # Azul Bosnia
    'South Africa': '#007C59',   # Verde Sudáfrica
    'DR Congo': '#007FFF',       # Azul Congo
    'New Zealand': '#000000',    # Negro All Blacks
    'Cape Verde': '#002A8F',     # Azul Cabo Verde
    'Haiti': '#00209F',          # Azul de Haití
    'Curacao': '#002B7F',        # Azul Curaçao
}

def get_team_color(team, default='#1e293b'):
    """Retorna el color primario de una selección nacional."""
    return TEAM_COLORS.get(team, default)

# Cargar resultados en tiempo real con caching
@st.cache_data(ttl=3600)  # Caché por 1 hora
def fetch_online_results():
    """Descarga los resultados actualizados de la Copa del Mundo 2026 desde GitHub y los combina con los locales sin duplicados."""
    # Empezar con una copia de los resultados locales
    results_map = {}
    for r in pred.WC2026_RESULTS:
        h = pred.normalize_name(r['home'])
        a = pred.normalize_name(r['away'])
        key = (min(h, a), max(h, a))
        results_map[key] = {
            'date': r['date'],
            'home': h,
            'away': a,
            'home_score': int(r['home_score']),
            'away_score': int(r['away_score']),
            'group': r['group']
        }

    url = "https://raw.githubusercontent.com/martj42/international_results/master/results.csv"
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            df = pd.read_csv(StringIO(response.text))
            df['date'] = pd.to_datetime(df['date'])
            # Filtrar partidos de la Copa del Mundo 2026
            df_wc = df[(df['tournament'] == 'FIFA World Cup') & (df['date'] >= pd.Timestamp('2026-06-11'))]
            # Eliminar filas sin marcador (partidos no jugados aún)
            df_wc = df_wc.dropna(subset=['home_score', 'away_score'])
            
            for _, row in df_wc.iterrows():
                home = pred.normalize_name(row['home_team'])
                away = pred.normalize_name(row['away_team'])
                key = (min(home, away), max(home, away))
                
                # Buscar el grupo del partido
                group = None
                for g, teams in pred.WC2026_GROUPS.items():
                    if home in [pred.normalize_name(t) for t in teams]:
                        group = g
                        break
                        
                results_map[key] = {
                    'date': row['date'].strftime('%Y-%m-%d'),
                    'home': home,
                    'away': away,
                    'home_score': int(row['home_score']),
                    'away_score': int(row['away_score']),
                    'group': group
                }
    except Exception as e:
        pass
    
    return list(results_map.values())

wc2026_results = fetch_online_results()

# =============================================================================
# CÁRGA DE DATOS Y MODELO (CON CACHÉ)
# =============================================================================
@st.cache_resource(show_spinner=False)
def load_pretrained_assets():
    """Carga los assets pre-entrenados del modelo para Streamlit."""
    import pickle
    import sys
    # Registrar EloSystem y default_rating en __main__ para evitar fallos de pickle
    sys.modules['__main__'].EloSystem = pred.EloSystem
    sys.modules['__main__'].default_rating = pred.default_rating
    
    assets_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", "model_assets.pkl")
    if not os.path.exists(assets_path):
        assets_path = os.path.join(os.getcwd(), "output", "model_assets.pkl")
    
    with open(assets_path, 'rb') as f:
        assets = pickle.load(f)
        
    model_data = {
        'models': assets['fitted_models'],
        'model_name': assets['best_model_name'],
        'scaler': assets['scaler'],
        'elo': assets['elo'],
        'features_cache': assets['team_features_cache'],
        'selected_features': assets['selected_features'],
        'model_metrics': assets['model_results'],
        'prob_cache_by_model': assets['prob_cache_by_model'],
        'feature_cache': assets['feature_cache'],
        'lambda_cache': assets['lambda_cache'],
        'winner_probs': assets['winner_probs'],
        'stage_counts': assets['stage_counts'],
        'n_simulations': assets['n_simulations'],
        'qualified': assets['qualified']
    }
    return model_data



# Mostrar pantalla de carga interactiva
with st.spinner("🧠 Cargando assets pre-entrenados del modelo de IA... Esto será instantáneo."):
    try:
        model_vars = load_pretrained_assets()
        model_ready = True
    except Exception as e:
        st.error(f"❌ Error al cargar los assets del modelo: {e}")
        model_ready = False

# =============================================================================
# LOGICA DE PREDICCIÓN Y MARCADORES (PRECOMPUTADO / POISSON)
# =============================================================================
def compute_wc2026_momentum(team):
    """Calcula el momentum del Mundial 2026 a partir de los partidos jugados."""
    tn = pred.normalize_name(team)
    matches_played = 0
    points = 0
    for r in wc2026_results:
        home = pred.normalize_name(r['home'])
        away = pred.normalize_name(r['away'])
        if home == tn:
            matches_played += 1
            hs, as_ = r['home_score'], r['away_score']
            if hs > as_:
                points += 3
            elif hs == as_:
                points += 1
        elif away == tn:
            matches_played += 1
            hs, as_ = r['home_score'], r['away_score']
            if as_ > hs:
                points += 3
            elif hs == as_:
                points += 1
    
    ppg = points / matches_played if matches_played > 0 else 0.0
    return {
        'wc26_matches': matches_played,
        'wc26_points_per_game': ppg
    }

def get_match_prediction(team_a, team_b, active_model_name):
    """Predice el resultado de un partido utilizando el modelo seleccionado."""
    if not model_ready:
        return np.array([0.33, 0.34, 0.33]), {}
    
    ta = pred.normalize_name(team_a)
    tb = pred.normalize_name(team_b)
    
    # Obtener el cache de probabilidades para el modelo activo
    pc = model_vars['prob_cache_by_model'].get(active_model_name, {})
    probs = pc.get((ta, tb), np.array([0.33, 0.34, 0.33]))
    
    # Obtener las features precalculadas para este enfrentamiento
    fc = model_vars['feature_cache']
    features = fc.get((ta, tb), {})
    
    return probs, features



def calculate_expected_score(team_a, team_b):
    """
    Calcula el marcador más probable y su matriz de probabilidad usando
    los lambdas precomputados de Poisson.
    """
    ta = pred.normalize_name(team_a)
    tb = pred.normalize_name(team_b)
    
    lc = model_vars['lambda_cache'].get((ta, tb))
    if lc is None:
        lambda_a = 1.35
        lambda_b = 1.35
    else:
        lambda_a = lc['lambda_a']
        lambda_b = lc['lambda_b']
    
    # Generar matriz de distribución de Poisson hasta 5 goles
    score_probs = {}
    for g_a in range(6):
        for g_b in range(6):
            prob_a = (math.exp(-lambda_a) * (lambda_a ** g_a)) / math.factorial(g_a)
            prob_b = (math.exp(-lambda_b) * (lambda_b ** g_b)) / math.factorial(g_b)
            score_probs[(g_a, g_b)] = prob_a * prob_b
    # Obtener el marcador con mayor probabilidad
    best_score = max(score_probs.items(), key=lambda x: x[1])
    most_likely_score = best_score[0]  # (goles_a, goles_b)
    
    return lambda_a, lambda_b, most_likely_score, score_probs

# =============================================================================
# ESTRUCTURA DE LA INTERFAZ USUARIO (STREAMLIT)
# =============================================================================
st.markdown("<div class='main-title'>🏆 NaleScore - Mundial 2026</div>", unsafe_allow_html=True)

# Helper flag emojis and date formatter
FLAGS = {
    'Argentina': '🇦🇷', 'Spain': '🇪🇸', 'France': '🇫🇷', 'England': '🏴󠁧󠁢󠁥󠁮󠁧󠁿',
    'Portugal': '🇵🇹', 'Brazil': '🇧🇷', 'Morocco': '🇲🇦', 'Netherlands': '🇳🇱',
    'Belgium': '🇧🇪', 'Germany': '🇩🇪', 'Croatia': '🇭🇷', 'Colombia': '🇨🇴',
    'Mexico': '🇲🇽', 'Senegal': '🇸🇳', 'Uruguay': '🇺🇾', 'United States': '🇺🇸',
    'Japan': '🇯🇵', 'Switzerland': '🇨🇭', 'Iran': '🇮🇷', 'Ecuador': '🇪🇨',
    'Australia': '🇦🇺', 'Turkey': '🇹🇷', 'South Korea': '🇰🇷', 'Austria': '🇦🇹',
    'Sweden': '🇸🇪', 'Egypt': '🇪🇬', 'Norway': '🇳🇴', 'Scotland': '🏴󠁧󠁢󠁳󠁣󠁴󠁿',
    'Algeria': '🇩🇿', 'Tunisia': '🇹🇳', 'Paraguay': '🇵🇾', 'Ivory Coast': '🇨🇮',
    'Czech Republic': '🇨🇿', 'Saudi Arabia': '🇸🇦', 'Ghana': '🇬🇭', 'Canada': '🇨🇦',
    'Panama': '🇵🇦', 'Iraq': '🇮🇶', 'Jordan': '🇯🇴', 'Qatar': '🇶🇦',
    'Uzbekistan': '🇺🇿', 'DR Congo': '🇨🇩', 'South Africa': '🇿🇦',
    'Bosnia and Herzegovina': '🇧🇦', 'New Zealand': '🇳🇿', 'Cape Verde': '🇨🇻',
    'Haiti': '🇭🇹', 'Curacao': '🇨🇼'
}

def get_flag(team):
    return FLAGS.get(pred.normalize_name(team), '🏳️')

def format_date_es(date_str):
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        months = ['Jun', 'Jul']
        month_idx = dt.month - 6
        return f"{dt.day} {months[month_idx]}"
    except:
        return date_str

def generate_official_schedule():
    group_offsets = {
        'A': 0, 'B': 1, 'C': 2, 'D': 2,
        'E': 3, 'F': 3, 'G': 4, 'H': 4,
        'I': 5, 'J': 5, 'K': 6, 'L': 6
    }
    times = ['18:00', '21:00', '00:00', '03:00']
    schedule = []
    for r in [1, 2, 3]:
        if r == 1:
            start_date = datetime(2026, 6, 11)
        elif r == 2:
            start_date = datetime(2026, 6, 18)
        else:
            start_date = datetime(2026, 6, 24)
            
        for g, teams in pred.WC2026_GROUPS.items():
            offset = group_offsets[g]
            match_date = start_date + timedelta(days=offset)
            date_str = match_date.strftime('%Y-%m-%d')
            g_idx = list(pred.WC2026_GROUPS.keys()).index(g)
            
            t1, t2, t3, t4 = teams[0], teams[1], teams[2], teams[3]
            if r == 1:
                schedule.append({'group': g, 'round': r, 'home': t1, 'away': t2, 'date': date_str, 'time': times[(g_idx * 2) % 4]})
                schedule.append({'group': g, 'round': r, 'home': t3, 'away': t4, 'date': date_str, 'time': times[(g_idx * 2 + 1) % 4]})
            elif r == 2:
                schedule.append({'group': g, 'round': r, 'home': t1, 'away': t3, 'date': date_str, 'time': times[(g_idx * 2 + 1) % 4]})
                schedule.append({'group': g, 'round': r, 'home': t4, 'away': t2, 'date': date_str, 'time': times[(g_idx * 2) % 4]})
            elif r == 3:
                schedule.append({'group': g, 'round': r, 'home': t1, 'away': t4, 'date': date_str, 'time': times[(g_idx * 2) % 4]})
                schedule.append({'group': g, 'round': r, 'home': t3, 'away': t2, 'date': date_str, 'time': times[(g_idx * 2 + 1) % 4]})
    return schedule

def display_match_details(team_a, team_b, real_home_score=None, real_away_score=None):
    # Execute prediction
    probs, raw_features = get_match_prediction(team_a, team_b, selected_model_name)
    p_draw, p_win_a, p_win_b = probs[0], probs[1], probs[2]
    
    # Expected score
    lambda_a, lambda_b, expected_score, score_probs = calculate_expected_score(team_a, team_b)
    
    col_left, col_right = st.columns([5, 5])
    
    with col_left:
        st.markdown("##### 📊 Probabilidades de Resultado (1X2)")
        labels = [f"Gana {team_a}", "Empate", f"Gana {team_b}"]
        values = [p_win_a * 100, p_draw * 100, p_win_b * 100]
        color_a = get_team_color(team_a, "#2563EB")
        color_b = get_team_color(team_b, "#DC2626")
        colors_list = [color_a, '#64748B', color_b]
        
        fig = go.Figure(go.Bar(
            x=values,
            y=labels,
            orientation='h',
            marker_color=colors_list,
            text=[f"{v:.1f}%" for v in values],
            textposition='inside',
            textfont=dict(size=13, color='white', weight='bold'),
            hovertemplate='%{y}: <b>%{x:.2f}%</b><extra></extra>'
        ))
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=10, r=10, t=10, b=10),
            height=200,
            xaxis=dict(showgrid=True, gridcolor='#334155', range=[0, 105]),
            yaxis=dict(autorange="reversed", tickfont=dict(size=12, color='#F8FAFC'))
        )
        st.plotly_chart(fig, use_container_width=True)
        


    with col_right:
        st.markdown("##### ⚽ Marcador Esperado & Matriz de Goles")
        st.markdown(f"""
        <div style='background-color: #1E293B; border-radius: 10px; padding: 12px; border: 1px solid #334155; text-align: center; margin-bottom: 10px;'>
            <span style='font-size: 0.8rem; color: #94A3B8; text-transform: uppercase; font-weight: 700;'>Marcador más probable</span>
            <div style='font-size: 2.2rem; font-weight: 900; color: #38BDF8;'>{expected_score[0]} - {expected_score[1]}</div>
            <div style='font-size: 0.8rem; color: #64748B;'>Lambdas: {team_a} ({lambda_a:.2f}) vs {team_b} ({lambda_b:.2f})</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Heatmap matrix
        matrix_data = []
        for g_b in range(5):
            row = []
            for g_a in range(5):
                row.append(score_probs[(g_a, g_b)] * 100)
            matrix_data.append(row)
            
        fig_heat = go.Figure(data=go.Heatmap(
            z=matrix_data,
            x=[f"{g} gol(es) {team_a}" for g in range(5)],
            y=[f"{g} gol(es) {team_b}" for g in range(5)],
            colorscale='Viridis',
            text=[[f"{val:.1f}%" for val in r] for r in matrix_data],
            texttemplate="%{text}",
            hovertemplate=f"Goles {team_a}: %{{x}}<br>Goles {team_b}: %{{y}}<br>Probabilidad: <b>%{{z:.2f}}%</b><extra></extra>"
        ))
        fig_heat.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=10, r=10, t=10, b=10),
            height=200,
            xaxis=dict(tickangle=0, tickfont=dict(size=10, color='#94A3B8')),
            yaxis=dict(autorange="reversed", tickfont=dict(size=10, color='#94A3B8'))
        )
        st.plotly_chart(fig_heat, use_container_width=True)

if model_ready:
    # Sidebar: Selección del partido
    st.sidebar.markdown("### ⚙️ Panel de Control")
    
    simulation_mode = st.sidebar.radio(
        "Ver en la interfaz:",
        ["🏆 Calendario Mundial 2026", "⚔️ Enfrentamiento Fantasía (Personalizado)"]
    )
    
    # Selector de modelos
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**🤖 Configuración de IA:**")
    available_models = list(model_vars['models'].keys())
    default_idx = available_models.index(model_vars['model_name']) if model_vars['model_name'] in available_models else 0
    selected_model_name = st.sidebar.selectbox(
        "Modelo Activo:",
        available_models,
        index=default_idx,
        help="Elige qué clasificador de IA utilizar para predecir las probabilidades del partido."
    )
    
    # Informar sobre el modelo seleccionado
    metrics = model_vars['model_metrics'][selected_model_name]
    st.sidebar.markdown(f"• **Precisión (CV):** `{metrics['accuracy_mean']*100:.2f}%` (+/- `{metrics['accuracy_std']*100:.1f}%`)")
    st.sidebar.markdown(f"• **F1-Score Macro:** `{metrics['f1_mean']:.3f}`")
    st.sidebar.markdown(f"• **Log Loss:** `{metrics['log_loss_mean']:.3f}`")
    st.sidebar.markdown(f"• **Partidos de Entrenamiento:** `3,768`")
    


    # Main Content
    if simulation_mode == "🏆 Calendario Mundial 2026":
        # Filters and Search
        col_f1, col_f2 = st.columns([6, 4])
        with col_f1:
            category_filter = st.radio(
                "Categoría del Partido:",
                ["Todos", "⏳ Próximos / Pendientes", "✅ Jugados"],
                horizontal=True
            )
        with col_f2:
            search_query = st.text_input("🔍 Buscar selección...", "").strip().lower()
            
        # Get schedule
        schedule = generate_official_schedule()
        
        st.markdown("---")
        
        matches_rendered = 0
        for m in schedule:
            home_norm = pred.normalize_name(m['home'])
            away_norm = pred.normalize_name(m['away'])
            
            # Check if match is played in real-time
            played_info = None
            for r in wc2026_results:
                r_home = pred.normalize_name(r['home'])
                r_away = pred.normalize_name(r['away'])
                if (r_home == home_norm and r_away == away_norm) or (r_home == away_norm and r_away == home_norm):
                    played_info = r
                    break
                    
            # Determine status and scores
            is_played = played_info is not None
            real_h_score, real_a_score = None, None
            if is_played:
                if pred.normalize_name(played_info['home']) == home_norm:
                    real_h_score = played_info['home_score']
                    real_a_score = played_info['away_score']
                else:
                    real_h_score = played_info['away_score']
                    real_a_score = played_info['home_score']
            
            # Apply category filter
            if category_filter == "⏳ Próximos / Pendientes" and is_played:
                continue
            if category_filter == "✅ Jugados" and not is_played:
                continue
                
            # Apply search filter
            if search_query:
                if search_query not in home_norm.lower() and search_query not in away_norm.lower():
                    continue
            
            # Get expected score
            _, _, expected_score, _ = calculate_expected_score(home_norm, away_norm)
            exp_h_score, exp_a_score = expected_score[0], expected_score[1]
            
            # Build Expander Title
            date_es = format_date_es(m['date'])
            home_flag = get_flag(home_norm)
            away_flag = get_flag(away_norm)
            
            status_text = ""
            
            if is_played:
                status_text = f"✅ Real: {real_h_score} - {real_a_score} | IA Esperado: {exp_h_score} - {exp_a_score}"
                
                # Check outcome hit
                probs, _ = get_match_prediction(home_norm, away_norm, selected_model_name)
                p_draw, p_win_a, p_win_b = probs[0], probs[1], probs[2]
                
                # Calculate real vs predicted outcome
                if real_h_score > real_a_score:
                    real_out = 1
                elif real_h_score == real_a_score:
                    real_out = 0
                else:
                    real_out = 2
                    
                if p_win_a > p_win_b and p_win_a > p_draw:
                    pred_out = 1
                elif p_win_b > p_win_a and p_win_b > p_draw:
                    pred_out = 2
                else:
                    pred_out = 0
                    
                if real_h_score == exp_h_score and real_a_score == exp_a_score:
                    status_text += "  ⭐ ¡MARCADOR EXACTO!"
                elif real_out == pred_out:
                    status_text += "  🎯 ¡ACERTADO (1X2)!"
                else:
                    status_text += "  ❌ NO ACERTADO"
            else:
                status_text = f"⏳ IA Esperado: {exp_h_score} - {exp_a_score}"
                
            header_title = f"{date_es} {m['time']} ({m['group']})  |  {home_flag} {home_norm} vs {away_norm} {away_flag}  |  {status_text}"
            
            with st.expander(header_title):
                display_match_details(home_norm, away_norm, real_h_score, real_a_score)
                
            matches_rendered += 1
            
        if matches_rendered == 0:
            st.info("No se encontraron partidos para los filtros aplicados.")
            
    else:
        # Enfrentamiento Fantasía (Personalizado)
        st.markdown("### ⚔️ Enfrentamiento Personalizado (Fantasía)")
        st.write("Configura un partido amistoso personalizado entre cualquier selección mundialista para ver la predicción de la IA.")
        
        all_teams = sorted(pred.ALL_WC_TEAMS)
        col_sel_a, col_sel_b = st.columns(2)
        with col_sel_a:
            team_a = st.selectbox("Selecciona Equipo Local (A):", all_teams, index=0)
        with col_sel_b:
            remaining_teams = [t for t in all_teams if t != team_a]
            team_b = st.selectbox("Selecciona Equipo Visitante (B):", remaining_teams, index=0)
            
        st.markdown("---")
        
        # Display team metrics summary
        color_a = get_team_color(team_a, "#2563EB")
        color_b = get_team_color(team_b, "#DC2626")
        elo_a = model_vars['elo'].get_rating(team_a)
        elo_b = model_vars['elo'].get_rating(team_b)
        sv_a = pred.get_squad_value(team_a)
        sv_b = pred.get_squad_value(team_b)
        conf_a = pred.get_confederation(team_a)
        conf_b = pred.get_confederation(team_b)
        
        col_card_a, col_card_vs, col_card_b = st.columns([4, 2, 4])
        with col_card_a:
            st.markdown(f"""
            <div class='card' style='border-top: 6px solid {color_a}; text-align: center;'>
                <div style='font-size: 3rem;'>{get_flag(team_a)}</div>
                <div style='font-size: 1.8rem; font-weight: 800;'>{team_a}</div>
                <div style='margin-top: 10px; display: grid; grid-template-columns: 1fr 1fr; gap: 8px;'>
                    <div><div class='metric-label'>Ranking FIFA</div><div class='metric-value'>#{pred.FIFA_RANKINGS.get(team_a, {}).get('rank', 'N/A')}</div></div>
                    <div><div class='metric-label'>Rating ELO</div><div class='metric-value'>{elo_a:.0f}</div></div>
                    <div><div class='metric-label'>Plantilla</div><div class='metric-value'>{sv_a:.1f}M€</div></div>
                    <div><div class='metric-label'>Confed.</div><div class='metric-value'>{conf_a}</div></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col_card_vs:
            st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
            st.markdown("<div class='vs-badge'>VS</div>", unsafe_allow_html=True)
        with col_card_b:
            st.markdown(f"""
            <div class='card' style='border-top: 6px solid {color_b}; text-align: center;'>
                <div style='font-size: 3rem;'>{get_flag(team_b)}</div>
                <div style='font-size: 1.8rem; font-weight: 800;'>{team_b}</div>
                <div style='margin-top: 10px; display: grid; grid-template-columns: 1fr 1fr; gap: 8px;'>
                    <div><div class='metric-label'>Ranking FIFA</div><div class='metric-value'>#{pred.FIFA_RANKINGS.get(team_b, {}).get('rank', 'N/A')}</div></div>
                    <div><div class='metric-label'>Rating ELO</div><div class='metric-value'>{elo_b:.0f}</div></div>
                    <div><div class='metric-label'>Plantilla</div><div class='metric-value'>{sv_b:.1f}M€</div></div>
                    <div><div class='metric-label'>Confed.</div><div class='metric-value'>{conf_b}</div></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        display_match_details(team_a, team_b)
        
else:
    st.warning("⚠️ El modelo de Machine Learning no ha terminado de entrenarse o no está disponible. Inicializa el script primero.")
