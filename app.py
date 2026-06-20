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

# =============================================================================
# CÁRGA DE DATOS Y MODELO (CON CACHÉ)
# =============================================================================
@st.cache_resource(show_spinner=False)
def load_pretrained_assets():
    """Carga los assets pre-entrenados del modelo para Streamlit."""
    import pickle
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
    for r in pred.WC2026_RESULTS:
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
                for r in pred.WC2026_RESULTS:
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

    # =============================================================================
    # PESTAÑAS PRINCIPALES DEL DASHBOARD
    # =============================================================================
    tab_prediction, tab_explain, tab_global = st.tabs([
        "📊 Predicción de Partido", 
        "💡 Explicabilidad y Comparativa", 
        "📈 Análisis Global del Torneo"
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
                
else:
    st.warning("⚠️ El modelo de Machine Learning no ha terminado de entrenarse o no está disponible. Inicializa el script primero.")
