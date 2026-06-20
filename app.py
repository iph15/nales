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
from datetime import datetime
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
    """Descarga los resultados actualizados de la Copa del Mundo 2026 desde GitHub."""
    url = "https://raw.githubusercontent.com/martj42/international_results/master/results.csv"
    try:
        df = pd.read_csv(url)
        df['date'] = pd.to_datetime(df['date'])
        # Filtrar partidos de la Copa del Mundo 2026
        df_wc = df[(df['tournament'] == 'FIFA World Cup') & (df['date'] >= pd.Timestamp('2026-06-11'))]
        
        online_results = []
        for _, row in df_wc.iterrows():
            home = pred.normalize_name(row['home_team'])
            away = pred.normalize_name(row['away_team'])
            
            # Buscar el grupo del partido
            group = None
            for g, teams in pred.WC2026_GROUPS.items():
                if home in [pred.normalize_name(t) for t in teams]:
                    group = g
                    break
                    
            online_results.append({
                'date': row['date'].strftime('%Y-%m-%d'),
                'home': home,
                'away': away,
                'home_score': int(row['home_score']),
                'away_score': int(row['away_score']),
                'group': group
            })
        
        if len(online_results) > 0:
            return online_results
    except Exception as e:
        pass
    
    return pred.WC2026_RESULTS

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

@st.cache_data(ttl=600)  # Caché por 10 minutos
def fetch_live_odds(api_key):
    """Obtiene cuotas reales de casas de apuestas usando The Odds API."""
    if not api_key:
        return {}
    
    url = "https://api.the-odds-api.com/v4/sports/soccer_fifa_world_cup/odds/"
    params = {
        'apiKey': api_key,
        'regions': 'eu',  # Europa (Bet365, Codere, Bwin, etc.)
        'markets': 'h2h',
        'oddsFormat': 'decimal'
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            odds_cache = {}
            for match in data:
                home = pred.normalize_name(match['home_team'])
                away = pred.normalize_name(match['away_team'])
                
                match_odds = {}
                for bm in match.get('bookmakers', []):
                    bm_name = bm['title']
                    for market in bm.get('markets', []):
                        if market['key'] == 'h2h':
                            odds = {}
                            for outcome in market['outcomes']:
                                team = pred.normalize_name(outcome['name'])
                                odds[team] = outcome['price']
                            
                            # Guardar cuotas de local, empate y visitante
                            match_odds[bm_name] = {
                                'home': odds.get(home, 1.0),
                                'draw': odds.get('Draw', 1.0),
                                'away': odds.get(away, 1.0)
                            }
                if len(match_odds) > 0:
                    odds_cache[(home, away)] = match_odds
                    # Guardar también en sentido inverso
                    odds_cache[(away, home)] = {
                        bm: {
                            'home': odds_cache[(home, away)][bm]['away'],
                            'draw': odds_cache[(home, away)][bm]['draw'],
                            'away': odds_cache[(home, away)][bm]['home']
                        } for bm in match_odds
                    }
            return odds_cache
    except Exception as e:
        pass
    return {}

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

def get_safest_bet(team_a, team_b, active_model_name):
    probs, _ = get_match_prediction(team_a, team_b, active_model_name)
    p_draw, p_win_a, p_win_b = probs[0], probs[1], probs[2]
    
    ta = pred.normalize_name(team_a)
    tb = pred.normalize_name(team_b)
    
    if p_win_a > p_win_b:
        fav = ta
        und = tb
        fav_prob = p_win_a
        is_a_fav = True
    else:
        fav = tb
        und = ta
        fav_prob = p_win_b
        is_a_fav = False
        
    lc = model_vars['lambda_cache'].get((ta, tb))
    lambda_total = 2.7
    lambda_a_val = 1.35
    lambda_b_val = 1.35
    if lc:
        lambda_a_val = lc['lambda_a']
        lambda_b_val = lc['lambda_b']
        lambda_total = lambda_a_val + lambda_b_val
        
    p_under_1_5 = math.exp(-lambda_total) * (1 + lambda_total)
    p_over_1_5 = 1 - p_under_1_5
    p_under_3_5 = math.exp(-lambda_total) * (1 + lambda_total + (lambda_total**2)/2 + (lambda_total**3)/6)
    p_both_score = (1 - math.exp(-lambda_a_val)) * (1 - math.exp(-lambda_b_val))
    p_both_score_no = 1 - p_both_score
    
    markets = [
        ('Doble Oportunidad (Gana/Empata Favorito)', fav_prob + p_draw),
        ('Menos de 3.5 Goles', p_under_3_5),
        ('Más de 1.5 Goles', p_over_1_5),
        ('Gana Favorito', fav_prob),
        ('Ambos marcan (NO)', p_both_score_no)
    ]
    
    safest_market, safest_prob = max(markets, key=lambda x: x[1])
    return safest_market, safest_prob, fav, und, is_a_fav

def check_bet_won(bet_type, is_a_fav, hs_a, hs_b):
    if is_a_fav:
        hs_fav, hs_und = hs_a, hs_b
    else:
        hs_fav, hs_und = hs_b, hs_a
        
    if "Doble Oportunidad" in bet_type:
        return hs_fav >= hs_und
    elif "Menos de 3.5" in bet_type:
        return (hs_fav + hs_und) <= 3
    elif "Más de 1.5" in bet_type:
        return (hs_fav + hs_und) >= 2
    elif "Gana Favorito" in bet_type:
        return hs_fav > hs_und
    elif "Ambos marcan (NO)" in bet_type:
        return hs_fav == 0 or hs_und == 0
    return False

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

if model_ready:
    # Sidebar: Selección del partido
    st.sidebar.markdown("### ⚙️ Panel de Control")
    
    mode = st.sidebar.radio(
        "Tipo de Simulación:",
        ["🏆 Fase de Grupos Oficial", "⚔️ Enfrentamiento Personalizado (Fantasía)"]
    )
    
    # Inicializar equipos seleccionados
    team_a, team_b = None, None
    is_played_match = False
    real_home_score, real_away_score = None, None
    selected_group_name = None
    
    if mode == "🏆 Fase de Grupos Oficial":
        groups = sorted(list(pred.WC2026_GROUPS.keys()))
        selected_group_name = st.sidebar.selectbox("Selecciona el Grupo:", groups)
        group_teams = pred.WC2026_GROUPS[selected_group_name]
        
        # Generar las 6 combinaciones de partidos del grupo
        group_matches = []
        for i in range(len(group_teams)):
            for j in range(i + 1, len(group_teams)):
                ta = pred.normalize_name(group_teams[i])
                tb = pred.normalize_name(group_teams[j])
                
                # Buscar si ya se ha jugado
                played_info = None
                for r in wc2026_results:
                    r_home = pred.normalize_name(r['home'])
                    r_away = pred.normalize_name(r['away'])
                    if (r_home == ta and r_away == tb) or (r_home == tb and r_away == ta):
                        played_info = r
                        break
                
                if played_info:
                    status = f"✅ {ta} vs {tb} (Jugado: {played_info['home_score']}-{played_info['away_score']})"
                else:
                    status = f"⏳ {ta} vs {tb} (Pendiente)"
                
                group_matches.append((ta, tb, status, played_info))
        
        match_options = [m[2] for m in group_matches]
        selected_match_idx = st.sidebar.selectbox("Selecciona el Partido:", range(len(match_options)), format_func=lambda x: match_options[x])
        
        team_a = group_matches[selected_match_idx][0]
        team_b = group_matches[selected_match_idx][1]
        played_info = group_matches[selected_match_idx][3]
        
        if played_info:
            is_played_match = True
            # Mantener orden correspondiente del marcador real
            if pred.normalize_name(played_info['home']) == team_a:
                real_home_score = played_info['home_score']
                real_away_score = played_info['away_score']
            else:
                real_home_score = played_info['away_score']
                real_away_score = played_info['home_score']
                # Invertir el orden para que coincida con el selector
                team_a, team_b = team_b, team_a
                
    else:
        # Modo Fantasía
        all_teams = sorted(pred.ALL_WC_TEAMS)
        team_a = st.sidebar.selectbox("Selecciona Equipo Local (A):", all_teams, index=0)
        # Filtrar equipo A del selector B
        remaining_teams = [t for t in all_teams if t != team_a]
        team_b = st.sidebar.selectbox("Selecciona Equipo Visitante (B):", remaining_teams, index=0)
        
    # Configuración de Inteligencia Artificial
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**🤖 Configuración de IA:**")
    
    # Selector de modelos
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
    st.sidebar.markdown(f"• **Partidos de Entrenamiento:** `3,760`")
    
    # Configuración de Cuotas en Vivo (Opcional)
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**🔑 API de Cuotas en Vivo (Opcional):**")
    odds_api_key = st.sidebar.text_input(
        "API Key (the-odds-api.com):",
        type="password",
        help="Introduce tu API Key gratuita de The Odds API para ver cuotas reales de Bet365, Codere, etc. en tiempo real."
    )
    
    # Cargar cuotas en vivo
    live_odds = fetch_live_odds(odds_api_key)

    # =============================================================================
    # PESTAÑAS PRINCIPALES DEL DASHBOARD
    # =============================================================================
    tab_prediction, tab_explain, tab_global, tab_betting = st.tabs([
        "📊 Predicción de Partido", 
        "💡 Explicabilidad y Comparativa", 
        "📈 Análisis Global del Torneo",
        "🎯 Consejos de Apuestas (Seguras)"
    ])
    
    # Ejecutar predicción
    probs, raw_features = get_match_prediction(team_a, team_b, selected_model_name)
    p_draw, p_win_a, p_win_b = probs[0], probs[1], probs[2]
    
    # Calcular marcador esperado
    elo_a = model_vars['elo'].get_rating(team_a)
    elo_b = model_vars['elo'].get_rating(team_b)
    fa = model_vars['features_cache'].get(team_a, {})
    fb = model_vars['features_cache'].get(team_b, {})
    
    lambda_a, lambda_b, expected_score, score_probs = calculate_expected_score(
        team_a, team_b
    )

    # -------------------------------------------------------------------------
    # TAB 1: PREDICCIÓN DE PARTIDO
    # -------------------------------------------------------------------------
    with tab_prediction:
        # Encabezado visual de enfrentamiento (Tarjetas de Equipos)
        col_team_a, col_vs, col_team_b = st.columns([4, 2, 4])
        
        color_a = get_team_color(team_a, "#2563EB")
        color_b = get_team_color(team_b, "#DC2626")
        
        sv_a = pred.get_squad_value(team_a)
        conf_a = pred.get_confederation(team_a)
        is_host_a = team_a in ['United States', 'Mexico', 'Canada']
        host_badge_a = "🇺🇸🇲🇽🇨🇦 Anfitrión" if is_host_a else ""
        
        with col_team_a:
            st.markdown(f"""
            <div class='card' style='border-top: 6px solid {color_a}; text-align: center;'>
                <div style='font-size: 4rem;'>🇺🇳</div>
                <div class='team-header-a' style='text-align: center; color: #F8FAFC;'>{team_a}</div>
                <div style='font-size: 0.9rem; color: #38BDF8; font-weight: 700; height: 20px;'>{host_badge_a}</div>
                <div style='margin-top: 15px; display: grid; grid-template-columns: 1fr 1fr; gap: 10px;'>
                    <div>
                        <div class='metric-label'>Ranking FIFA</div>
                        <div class='metric-value'>#{pred.FIFA_RANKINGS.get(team_a, {}).get('rank', 'N/A')}</div>
                    </div>
                    <div>
                        <div class='metric-label'>Rating ELO</div>
                        <div class='metric-value'>{elo_a:.0f}</div>
                    </div>
                    <div>
                        <div class='metric-label'>Valor Plantilla</div>
                        <div class='metric-value'>{sv_a:.1f} M€</div>
                    </div>
                    <div>
                        <div class='metric-label'>Confederación</div>
                        <div class='metric-value'>{conf_a}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_vs:
            st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
            st.markdown("<div class='vs-badge'>VS</div>", unsafe_allow_html=True)
            if is_played_match:
                st.markdown(f"""
                <div style='text-align: center; margin-top: 20px;'>
                    <span style='background-color: #059669; color: white; padding: 6px 12px; border-radius: 20px; font-weight: 800; font-size: 0.85rem;'>
                        JUGADO
                    </span>
                    <div style='font-size: 2.2rem; font-weight: 900; color: #10B981; margin-top: 5px;'>
                        {real_home_score} - {real_away_score}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            elif selected_group_name:
                st.markdown(f"""
                <div style='text-align: center; margin-top: 20px;'>
                    <span style='background-color: #3B82F6; color: white; padding: 6px 12px; border-radius: 20px; font-weight: 800; font-size: 0.85rem;'>
                        GRUPO {selected_group_name}
                    </span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style='text-align: center; margin-top: 20px;'>
                    <span style='background-color: #6366F1; color: white; padding: 6px 12px; border-radius: 20px; font-weight: 800; font-size: 0.85rem;'>
                        FANTASÍA
                    </span>
                </div>
                """, unsafe_allow_html=True)
            
        sv_b = pred.get_squad_value(team_b)
        conf_b = pred.get_confederation(team_b)
        is_host_b = team_b in ['United States', 'Mexico', 'Canada']
        host_badge_b = "🇺🇸🇲🇽🇨🇦 Anfitrión" if is_host_b else ""
        
        with col_team_b:
            st.markdown(f"""
            <div class='card' style='border-top: 6px solid {color_b}; text-align: center;'>
                <div style='font-size: 4rem;'>🇺🇳</div>
                <div class='team-header-b' style='text-align: center; color: #F8FAFC;'>{team_b}</div>
                <div style='font-size: 0.9rem; color: #38BDF8; font-weight: 700; height: 20px;'>{host_badge_b}</div>
                <div style='margin-top: 15px; display: grid; grid-template-columns: 1fr 1fr; gap: 10px;'>
                    <div>
                        <div class='metric-label'>Ranking FIFA</div>
                        <div class='metric-value'>#{pred.FIFA_RANKINGS.get(team_b, {}).get('rank', 'N/A')}</div>
                    </div>
                    <div>
                        <div class='metric-label'>Rating ELO</div>
                        <div class='metric-value'>{elo_b:.0f}</div>
                    </div>
                    <div>
                        <div class='metric-label'>Valor Plantilla</div>
                        <div class='metric-value'>{sv_b:.1f} M€</div>
                    </div>
                    <div>
                        <div class='metric-label'>Confederación</div>
                        <div class='metric-value'>{conf_b}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        
        # Probabilidades y Marcador Esperado
        col_left, col_right = st.columns([5, 5])
        
        with col_left:
            st.markdown("### 📊 Probabilidades de Resultado")
            
            # Gráfico de Plotly para probabilidades
            labels = [f"Victoria {team_a}", "Empate", f"Victoria {team_b}"]
            values = [p_win_a * 100, p_draw * 100, p_win_b * 100]
            colors_list = [color_a, '#64748B', color_b]
            
            fig = go.Figure(go.Bar(
                x=values,
                y=labels,
                orientation='h',
                marker_color=colors_list,
                text=[f"{v:.1f}%" for v in values],
                textposition='inside',
                textfont=dict(size=14, color='white', weight='bold'),
                hovertemplate='%{y}: <b>%{x:.2f}%</b><extra></extra>'
            ))
            
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=10, b=10),
                height=300,
                xaxis=dict(showgrid=True, gridcolor='#334155', range=[0, 105], title="Probabilidad (%)"),
                yaxis=dict(autorange="reversed", tickfont=dict(size=12, color='#F8FAFC'))
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Mensaje analítico en español
            fav = team_a if p_win_a > p_win_b else team_b
            max_prob = max(p_win_a, p_win_b)
            dif_ratio = abs(p_win_a - p_win_b) * 100
            
            if dif_ratio < 5:
                resumen_txt = f"⚖️ **Partido sumamente equilibrado**. El modelo no visualiza un claro favorito, dando un empate con un **{p_draw*100:.1f}%** o una victoria marginal para cualquiera de los dos lados."
            elif dif_ratio < 20:
                resumen_txt = f"📈 **Ligera ventaja para {fav}**. El modelo de IA le otorga un **{max_prob*100:.1f}%** de probabilidad de ganar frente a la otra selección."
            else:
                resumen_txt = f"🔥 **{fav} es claro favorito**. Las features recopiladas (Elo, Ranking yOdds) le otorgan una sólida probabilidad de victoria del **{max_prob*100:.1f}%**."
                
            st.info(resumen_txt)
            
            # Comparación con cuotas reales en vivo si hay API Key
            ia_odd_win_a = 1.0 / p_win_a if p_win_a > 0 else 99.0
            ia_odd_draw = 1.0 / p_draw if p_draw > 0 else 99.0
            ia_odd_win_b = 1.0 / p_win_b if p_win_b > 0 else 99.0
            
            matchup_odds = live_odds.get((team_a, team_b))
            if matchup_odds:
                st.markdown("##### 🎲 Comparación con Casas de Apuestas (En Vivo)")
                
                # Buscar Bet365 o usar la primera disponible
                bm_choice = 'Bet365' if 'Bet365' in matchup_odds else list(matchup_odds.keys())[0]
                bm_odds = matchup_odds[bm_choice]
                
                val_win_a = "🔥 VALOR (+EV)" if bm_odds['home'] > ia_odd_win_a else "Sin Valor"
                val_draw = "🔥 VALOR (+EV)" if bm_odds['draw'] > ia_odd_draw else "Sin Valor"
                val_win_b = "🔥 VALOR (+EV)" if bm_odds['away'] > ia_odd_win_b else "Sin Valor"
                
                comp_odds_data = {
                    'Resultado': [f"Gana {team_a}", "Empate", f"Gana {team_b}"],
                    'Probabilidad IA': [f"{p_win_a*100:.1f}%", f"{p_draw*100:.1f}%", f"{p_win_b*100:.1f}%"],
                    'Cuota Justa IA': [f"@{ia_odd_win_a:.2f}", f"@{ia_odd_draw:.2f}", f"@{ia_odd_win_b:.2f}"],
                    f'Cuota Real ({bm_choice})': [f"@{bm_odds['home']:.2f}", f"@{bm_odds['draw']:.2f}", f"@{bm_odds['away']:.2f}"],
                    'Valoración': [val_win_a, val_draw, val_win_b]
                }
                
                df_comp_odds = pd.DataFrame(comp_odds_data)
                st.dataframe(df_comp_odds.set_index('Resultado'), use_container_width=True)
                st.info(f"💡 **Valor (+EV):** Ocurre cuando la cuota real de la casa de apuestas es mayor que la cuota justa estimada por la IA, representando una oportunidad matemática rentable a largo plazo.")

        with col_right:
            st.markdown("### ⚽ Marcador Esperado (Poisson)")
            
            # Marcador destacado
            st.markdown(f"""
            <div style='background-color: #1E293B; border-radius: 12px; padding: 20px; border: 1px solid #334155; text-align: center; margin-bottom: 20px;'>
                <div style='font-size: 1.1rem; color: #94A3B8; text-transform: uppercase; font-weight: 700; letter-spacing: 0.1em;'>
                    Marcador Más Probable
                </div>
                <div style='font-size: 4rem; font-weight: 900; color: #38BDF8; margin: 10px 0;'>
                    {expected_score[0]} - {expected_score[1]}
                </div>
                <div style='font-size: 0.95rem; color: #64748B;'>
                    Tasa de goles esperada: <b>{team_a} ({lambda_a:.2f})</b> vs <b>{team_b} ({lambda_b:.2f})</b>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Generar matriz/heatmap de marcadores
            matrix_data = []
            for g_b in range(5): # Goles B en columnas
                row = []
                for g_a in range(5): # Goles A en filas
                    row.append(score_probs[(g_a, g_b)] * 100)
                matrix_data.append(row)
                
            fig_heat = go.Figure(data=go.Heatmap(
                z=matrix_data,
                x=[f"{g} Goles {team_a}" for g in range(5)],
                y=[f"{g} Goles {team_b}" for g in range(5)],
                colorscale='Viridis',
                text=[[f"{val:.1f}%" for val in r] for r in matrix_data],
                texttemplate="%{text}",
                hovertemplate=f"Goles {team_a}: %{{x}}<br>Goles {team_b}: %{{y}}<br>Probabilidad: <b>%{{z:.2f}}%</b><extra></extra>"
            ))
            
            fig_heat.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=10, b=10),
                height=300,
                xaxis=dict(tickangle=0),
                yaxis=dict(autorange="reversed")
            )
            
            st.plotly_chart(fig_heat, use_container_width=True)

    # -------------------------------------------------------------------------
    # TAB 2: EXPLICABILIDAD Y COMPARATIVA
    # -------------------------------------------------------------------------
    # TAB 2: EXPLICABILIDAD Y COMPARATIVA
    # -------------------------------------------------------------------------
    with tab_explain:
        st.markdown("### 💡 Explicabilidad del Modelo: ¿Por qué predice esto?")
        st.write("A continuación se muestra el **Balance de Ventajas**. Las barras hacia la **derecha** representan ventajas para **" + team_a + "**, y hacia la **izquierda** representan ventajas para **" + team_b + "**.")
        
        # Calcular ventajas normalizadas para el gráfico
        mom_a = compute_wc2026_momentum(team_a)
        mom_b = compute_wc2026_momentum(team_b)
        
        adv_features = {
            'Rating ELO': raw_features.get('elo_diff', 0.0) / 150.0, # Normalizado (1.0 = ventaja de 150 puntos)
            'Ranking FIFA': -raw_features.get('fifa_rank_diff', 0.0) / 15.0,
            'Probabilidad Apuestas': raw_features.get('odds_prob_diff', 0.0) * 8.0,
            'Valor de Plantilla': raw_features.get('squad_value_diff', 0.0) / 300.0,
            'Fuerza de Confederación': raw_features.get('conf_strength_diff', 0.0) / 2.0,
            'Efecto Localía / Anfitrión': raw_features.get('host_advantage_diff', 0.0) * 1.5,
            'Forma Reciente': raw_features.get('recent_form_diff', 0.0) * 3.0,
            'Historial H2H': (raw_features.get('h2h_win_rate', 0.5) - 0.5) * 4.0,
            'Capacidad Goleadora': raw_features.get('goals_scored_diff', 0.0) * 1.0,
            'Solidez Defensiva': -raw_features.get('goals_conceded_diff', 0.0) * 1.0, # Invertido (menos encajados es mejor)
            'Momentum del Mundial': (mom_a['wc26_points_per_game'] - mom_b['wc26_points_per_game']) * 0.5
        }
        
        categories = list(adv_features.keys())
        values_adv = list(adv_features.values())
        
        # Determinar colores para las barras (si es positivo color_a, si es negativo color_b)
        bar_colors = [color_a if v >= 0 else color_b for v in values_adv]
        
        fig_adv = go.Figure(go.Bar(
            x=values_adv,
            y=categories,
            orientation='h',
            marker_color=bar_colors,
            hovertemplate='Factor: <b>%{y}</b><br>Ventaja Relativa: <b>%{x:.2f}</b><extra></extra>'
        ))
        
        fig_adv.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=40, r=40, t=10, b=10),
            height=450,
            xaxis=dict(
                title=f"⬅️ Favorece a {team_b}  |  Favorece a {team_a} ➡️",
                showgrid=True,
                gridcolor='#334155',
                zeroline=True,
                zerolinecolor='#64748B',
                zerolinewidth=2
            ),
            yaxis=dict(tickfont=dict(size=12, color='#F8FAFC'))
        )
        
        st.plotly_chart(fig_adv, use_container_width=True)
        
        # Tabla detallada de comparación
        st.markdown("### 📋 Comparación Numérica Detallada")
        
        # Obtener confederaciones y squad values
        sv_a = pred.get_squad_value(team_a)
        sv_b = pred.get_squad_value(team_b)
        conf_a = pred.get_confederation(team_a)
        conf_b = pred.get_confederation(team_b)
        
        comp_data = {
            'Métrica': [
                'Confederación', 'Valor de Plantilla (M€)', 'Puntos Ranking FIFA', 'Rating ELO Actual', 'Odds de Apuestas (%)', 
                'Win Rate Histórico Ponderado', 'Goles Marcados Históricos (Med.)', 
                'Goles Recibidos Históricos (Med.)', 'Partidos en el Mundial Actual', 
                'Puntos por Partido (Mundial)'
            ],
            team_a: [
                conf_a,
                f"{sv_a:.1f} M€",
                f"{pred.FIFA_RANKINGS.get(team_a, {}).get('points', 0):.1f} (Rank #{pred.FIFA_RANKINGS.get(team_a, {}).get('rank', 0)})",
                f"{elo_a:.0f}",
                f"{pred.BETTING_ODDS.get(team_a, 0.001)*100:.2f}%",
                f"{fa.get('weighted_win_rate', 0)*100:.1f}%",
                f"{fa.get('weighted_goals_scored', 0):.2f}",
                f"{fa.get('weighted_goals_conceded', 0):.2f}",
                f"{mom_a['wc26_matches']}",
                f"{mom_a['wc26_points_per_game']:.2f}"
            ],
            team_b: [
                conf_b,
                f"{sv_b:.1f} M€",
                f"{pred.FIFA_RANKINGS.get(team_b, {}).get('points', 0):.1f} (Rank #{pred.FIFA_RANKINGS.get(team_b, {}).get('rank', 0)})",
                f"{elo_b:.0f}",
                f"{pred.BETTING_ODDS.get(team_b, 0.001)*100:.2f}%",
                f"{fb.get('weighted_win_rate', 0)*100:.1f}%",
                f"{fb.get('weighted_goals_scored', 0):.2f}",
                f"{fb.get('weighted_goals_conceded', 0):.2f}",
                f"{mom_b['wc26_matches']}",
                f"{mom_b['wc26_points_per_game']:.2f}"
            ]
        }
        
        st.table(pd.DataFrame(comp_data).set_index('Métrica'))

    # -------------------------------------------------------------------------
    # TAB 3: ANÁLISIS GLOBAL DEL TORNEO
    # -------------------------------------------------------------------------
    with tab_global:
        st.markdown("### 📈 Análisis Global del Torneo y Modelado")
        st.write("Esta sección presenta las visualizaciones generadas por el pipeline de entrenamiento del script principal de Machine Learning.")
        
        # Verificar si las imágenes pre-generadas existen en el directorio output
        output_dir = pred.OUTPUT_DIR
        
        img_winner = os.path.join(output_dir, 'winner_predictions.png')
        img_stages = os.path.join(output_dir, 'stage_progression.png')
        img_importance = os.path.join(output_dir, 'feature_importance.png')
        img_models = os.path.join(output_dir, 'model_comparison.png')
        
        col_g1, col_g2 = st.columns([5, 5])
        
        with col_g1:
            st.markdown("#### 🏆 Probabilidades de Ganar el Mundial 2026 (Top 20)")
            if os.path.exists(img_winner):
                st.image(img_winner, use_container_width=True)
            else:
                st.info("ℹ️ Ejecuta el script principal `wc2026_predictor.py` para generar la predicción completa del torneo.")
                
            st.markdown("#### 📊 Importancia de Variables en la IA")
            if os.path.exists(img_importance):
                st.image(img_importance, use_container_width=True)
            else:
                st.info("ℹ️ Imagen de importancia de variables no encontrada en 'output/'.")
                
        with col_g2:
            st.markdown("#### 📈 Progresión por Rondas de los Favoritos (Top 10)")
            if os.path.exists(img_stages):
                st.image(img_stages, use_container_width=True)
            else:
                st.info("ℹ️ Ejecuta la simulación completa del torneo para ver las probabilidades de progression.")
                
            st.markdown("#### 🤖 Comparación de Métricas de Modelos ML")
            if os.path.exists(img_models):
                st.image(img_models, use_container_width=True)
            else:
                st.info("ℹ️ Imagen de comparación de modelos no encontrada en 'output/'.")

    # -------------------------------------------------------------------------
    # TAB 4: CONSEJOS DE APUESTAS (SEGURAS)
    # -------------------------------------------------------------------------
    with tab_betting:
        st.markdown("### 🎯 Consejos y Pronósticos de Apuestas de Alta Probabilidad")
        st.write("Basado en 5,000 simulaciones completas de Monte Carlo del Mundial 2026 y la calibración de goles de la distribución de Poisson.")
        st.markdown("💡 *Los resultados reales de los partidos se obtienen online y en tiempo real desde GitHub. Los partidos pasados se marcan como biased porque sus características ya incluyen el resultado post-partido, mientras que los partidos pendientes son predicciones puras sin sesgo.*")
        
        # Calcular estadísticas globales de acierto para partidos jugados
        total_bets = 0
        won_bets = 0
        played_bets_data = []
        
        for r in wc2026_results:
            ta = pred.normalize_name(r['home'])
            tb = pred.normalize_name(r['away'])
            hs_a = r['home_score']
            hs_b = r['away_score']
            
            # Obtener apuesta recomendada
            bet_type, prob, fav, und, is_a_fav = get_safest_bet(ta, tb, selected_model_name)
            is_won = check_bet_won(bet_type, is_a_fav, hs_a, hs_b)
            
            total_bets += 1
            if is_won:
                won_bets += 1
                
            played_bets_data.append({
                'Grupo': f"Grupo {r.get('group', 'N/A')}",
                'Partido': f"{ta} vs {tb}",
                'Resultado Real': f"{hs_a} - {hs_b}",
                'Apuesta Realizada': f"{bet_type}",
                'Prob. Estimada': f"{prob*100:.1f}%",
                'Estado': "✅ ACERTADA" if is_won else "❌ FALLADA",
                'Tipo Evaluación': "⚠️ BIASED (A Posteriori)"
            })
            
        accuracy = (won_bets / total_bets * 100) if total_bets > 0 else 0.0
        
        # Renderizar Tarjetas de Estadísticas de Acierto
        col_acc_1, col_acc_2, col_acc_3 = st.columns(3)
        with col_acc_1:
            st.markdown(f"""
            <div style='background-color: #1E293B; border-radius: 12px; padding: 20px; border: 1px solid #334155; text-align: center;'>
                <div style='font-size: 0.85rem; color: #94A3B8; text-transform: uppercase; font-weight: 700; letter-spacing: 0.05em;'>Partidos Evaluados (API)</div>
                <div style='font-size: 2.2rem; font-weight: 900; color: #38BDF8;'>{total_bets}</div>
            </div>
            """, unsafe_allow_html=True)
        with col_acc_2:
            st.markdown(f"""
            <div style='background-color: #1E293B; border-radius: 12px; padding: 20px; border: 1px solid #334155; text-align: center;'>
                <div style='font-size: 0.85rem; color: #94A3B8; text-transform: uppercase; font-weight: 700; letter-spacing: 0.05em;'>Apuestas Acertadas</div>
                <div style='font-size: 2.2rem; font-weight: 900; color: #10B981;'>{won_bets}</div>
            </div>
            """, unsafe_allow_html=True)
        with col_acc_3:
            st.markdown(f"""
            <div style='background-color: #1E293B; border-radius: 12px; padding: 20px; border: 1px solid #334155; text-align: center;'>
                <div style='font-size: 0.85rem; color: #94A3B8; text-transform: uppercase; font-weight: 700; letter-spacing: 0.05em;'>Tasa de Acierto Global</div>
                <div style='font-size: 2.2rem; font-weight: 900; color: #10B981;'>{accuracy:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("---")
        
        # Obtener pendientes
        pending_bets = []
        for group_name, teams in pred.WC2026_GROUPS.items():
            for i in range(len(teams)):
                for j in range(i + 1, len(teams)):
                    ta = pred.normalize_name(teams[i])
                    tb = pred.normalize_name(teams[j])
                    
                    # Verificar si ya se jugó
                    played = False
                    for r in wc2026_results:
                        r_home = pred.normalize_name(r['home'])
                        r_away = pred.normalize_name(r['away'])
                        if (r_home == ta and r_away == tb) or (r_home == tb and r_away == ta):
                            played = True
                            break
                    
                    if not played:
                        bet_type, prob, fav, und, is_a_fav = get_safest_bet(ta, tb, selected_model_name)
                        pending_bets.append({
                            'group': group_name,
                            'match': f"{ta} vs {tb}",
                            'favorite': fav,
                            'underdog': und,
                            'bet_type': bet_type,
                            'prob': prob
                        })
                        
        pending_bets_sorted = sorted(pending_bets, key=lambda x: x['prob'], reverse=True)
        
        # --- NUEVA SECCIÓN: COMBINADAS RECOMENDADAS ---
        if len(pending_bets_sorted) >= 3:
            st.markdown("#### 🔗 Combinadas Recomendadas por la IA (Parlays)")
            st.write("Combinamos múltiples pronósticos de alta probabilidad para maximizar la cuota manteniendo un perfil de riesgo controlado.")
            
            # 1. Combinada Segura
            segura_items = pending_bets_sorted[:3]
            prob_segura = 1.0
            for b in segura_items:
                prob_segura *= b['prob']
            cuota_segura = 1.0 / prob_segura if prob_segura > 0 else 1.0
            
            # 2. Combinada Moderada
            moderada_items = pending_bets_sorted[3:6] if len(pending_bets_sorted) >= 6 else pending_bets_sorted[-3:]
            prob_moderada = 1.0
            for b in moderada_items:
                prob_moderada *= b['prob']
            cuota_moderada = 1.0 / prob_moderada if prob_moderada > 0 else 1.0
            
            col_parlay_1, col_parlay_2 = st.columns(2)
            
            with col_parlay_1:
                st.markdown(f"""
                <div style='background-color: #1E293B; border-radius: 12px; padding: 20px; border-left: 6px solid #10B981; margin-bottom: 20px; min-height: 280px; display: flex; flex-direction: column; justify-content: space-between;'>
                    <div>
                        <div style='display: flex; justify-content: space-between; align-items: center;'>
                            <span style='background-color: #10B981; color: white; font-weight: 800; font-size: 0.8rem; padding: 3px 10px; border-radius: 20px;'>RIESGO BAJO</span>
                            <span style='font-size: 0.9rem; color: #94A3B8;'>Prob: <b>{prob_segura*100:.1f}%</b></span>
                        </div>
                        <h4 style='color: #F8FAFC; margin-top: 10px; margin-bottom: 10px;'>🟢 La Combinada Segura (Cuota @{cuota_segura:.2f})</h4>
                        <div style='font-size: 0.85rem; color: #E2E8F0; line-height: 1.6;'>
                            • <b>{segura_items[0]['match']}</b>: {segura_items[0]['bet_type']} ({segura_items[0]['prob']*100:.1f}%)<br>
                            • <b>{segura_items[1]['match']}</b>: {segura_items[1]['bet_type']} ({segura_items[1]['prob']*100:.1f}%)<br>
                            • <b>{segura_items[2]['match']}</b>: {segura_items[2]['bet_type']} ({segura_items[2]['prob']*100:.1f}%)
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
            with col_parlay_2:
                st.markdown(f"""
                <div style='background-color: #1E293B; border-radius: 12px; padding: 20px; border-left: 6px solid #EAB308; margin-bottom: 20px; min-height: 280px; display: flex; flex-direction: column; justify-content: space-between;'>
                    <div>
                        <div style='display: flex; justify-content: space-between; align-items: center;'>
                            <span style='background-color: #EAB308; color: #0F172A; font-weight: 800; font-size: 0.8rem; padding: 3px 10px; border-radius: 20px;'>RIESGO MEDIO</span>
                            <span style='font-size: 0.9rem; color: #94A3B8;'>Prob: <b>{prob_moderada*100:.1f}%</b></span>
                        </div>
                        <h4 style='color: #F8FAFC; margin-top: 10px; margin-bottom: 10px;'>🟡 La Combinada de Valor (Cuota @{cuota_moderada:.2f})</h4>
                        <div style='font-size: 0.85rem; color: #E2E8F0; line-height: 1.6;'>
                            • <b>{moderada_items[0]['match']}</b>: {moderada_items[0]['bet_type']} ({moderada_items[0]['prob']*100:.1f}%)<br>
                            • <b>{moderada_items[1]['match']}</b>: {moderada_items[1]['bet_type']} ({moderada_items[1]['prob']*100:.1f}%)<br>
                            • <b>{moderada_items[2]['match']}</b>: {moderada_items[2]['bet_type']} ({moderada_items[2]['prob']*100:.1f}%)
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
            st.markdown("---")
            
        # Sub-pestañas para segmentar apuestas
        sub_tab_pending, sub_tab_history = st.tabs([
            "🔮 Apuestas para Partidos Restantes",
            "📜 Historial y Verificación de Resultados"
        ])
        
        with sub_tab_pending:
            st.markdown("#### 🔮 Pronósticos para los Próximos Partidos del Mundial 2026")
            st.write("A continuación se listan las apuestas recomendadas (las de mayor probabilidad) para cada uno de los partidos restantes de la fase de grupos.")
            
            if len(pending_bets_sorted) > 0:
                # Mostrar top 3 destacadas como tarjetas visuales
                st.markdown("##### ⭐ Top 3 Apuestas más Seguras (Sólidas)")
                col_top_1, col_top_2, col_top_3 = st.columns(3)
                top_cols = [col_top_1, col_top_2, col_top_3]
                
                for idx, bet in enumerate(pending_bets_sorted[:3]):
                    with top_cols[idx]:
                        st.markdown(f"""
                        <div style='background-color: #1E293B; border-radius: 12px; padding: 15px; border-top: 5px solid #38BDF8; margin-bottom: 15px;'>
                            <div style='font-size: 0.75rem; color: #94A3B8; text-transform: uppercase; font-weight: 700;'>Grupo {bet['group']}</div>
                            <div style='font-size: 1rem; font-weight: 700; color: #F8FAFC; margin: 5px 0;'>{bet['match']}</div>
                            <div style='font-size: 0.85rem; color: #38BDF8;'>👉 <b>{bet['bet_type']}</b></div>
                            <div style='font-size: 1.4rem; font-weight: 900; color: #10B981; margin-top: 5px;'>{bet['prob']*100:.1f}%</div>
                            <div style='font-size: 0.7rem; color: #64748B;'>Probabilidad de éxito</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Mostrar lista completa en tabla interactiva
                st.markdown("##### 📋 Listado Completo de Partidos Restantes")
                df_pending = pd.DataFrame([
                    {
                        'Grupo': f"Grupo {b['group']}",
                        'Partido': b['match'],
                        'Favorito': b['favorite'],
                        'Apuesta Recomendada': b['bet_type'],
                        'Confianza de la IA': f"{b['prob']*100:.1f}%",
                        'Evaluación': "🆕 NEW (Predicción Pura)"
                    } for b in pending_bets_sorted
                ])
                st.dataframe(df_pending, use_container_width=True, hide_index=True)
            else:
                st.info("🎉 ¡Fase de grupos completada! Todos los partidos ya han sido jugados.")
                
        with sub_tab_history:
            st.markdown("#### 📜 Historial de Apuestas y Resultados Obtenidos")
            st.write("Verificación detallada de los pronósticos realizados en los partidos ya completados.")
            
            if len(played_bets_data) > 0:
                df_played = pd.DataFrame(played_bets_data)
                st.dataframe(df_played, use_container_width=True, hide_index=True)
            else:
                st.info("⏳ Aún no se han registrado partidos jugados en la Copa del Mundo 2026.")
                
else:
    st.warning("⚠️ El modelo de Machine Learning no ha terminado de entrenarse o no está disponible. Inicializa el script primero.")
