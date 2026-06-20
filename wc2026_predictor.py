#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════╗
║           🏆  PREDICTOR COPA DEL MUNDO FIFA 2026  🏆               ║
║                                                                      ║
║  Pipeline completo de ML para predecir el ganador del Mundial 2026   ║
║  • Scraping de datos históricos (49,000+ partidos)                   ║
║  • Rankings FIFA, Elo ratings, odds de apuestas                      ║
║  • Feature engineering con decaimiento temporal                      ║
║  • Selección de features (MI, correlación, importancia)              ║
║  • Comparación de 5 modelos ML con cross-validation                  ║
║  • Simulación completa del torneo                                    ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import warnings
warnings.filterwarnings('ignore')

import os
import sys

# Fix encoding para consola Windows (cp1252 → UTF-8)
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import math
import random
import requests
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

from datetime import datetime, timedelta
from collections import defaultdict
from io import StringIO

from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import (accuracy_score, log_loss, f1_score,
                             roc_auc_score, classification_report,
                             confusion_matrix)
from sklearn.feature_selection import mutual_info_classif
from sklearn.pipeline import Pipeline

try:
    from xgboost import XGBClassifier
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False
    print("⚠️  XGBoost no instalado. Se usará GradientBoosting de sklearn como alternativa.")

# =============================================================================
# CONFIGURACIÓN GLOBAL
# =============================================================================
RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)
random.seed(RANDOM_STATE)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Fecha de referencia (hoy)
REFERENCE_DATE = datetime(2026, 6, 20)

# =============================================================================
# SECCIÓN 1: DATOS EMBEBIDOS
# =============================================================================

# --- 48 equipos y sus grupos ---
WC2026_GROUPS = {
    'A': ['Mexico', 'South Africa', 'South Korea', 'Czech Republic'],
    'B': ['Canada', 'Bosnia and Herzegovina', 'Qatar', 'Switzerland'],
    'C': ['Brazil', 'Morocco', 'Haiti', 'Scotland'],
    'D': ['United States', 'Paraguay', 'Australia', 'Turkey'],
    'E': ['Germany', 'Curacao', 'Ivory Coast', 'Ecuador'],
    'F': ['Netherlands', 'Japan', 'Sweden', 'Tunisia'],
    'G': ['Belgium', 'Egypt', 'Iran', 'New Zealand'],
    'H': ['Spain', 'Cape Verde', 'Saudi Arabia', 'Uruguay'],
    'I': ['France', 'Senegal', 'Iraq', 'Norway'],
    'J': ['Argentina', 'Algeria', 'Austria', 'Jordan'],
    'K': ['Portugal', 'DR Congo', 'Uzbekistan', 'Colombia'],
    'L': ['England', 'Croatia', 'Ghana', 'Panama'],
}

ALL_WC_TEAMS = []
for teams in WC2026_GROUPS.values():
    ALL_WC_TEAMS.extend(teams)

# --- Ranking FIFA (11 junio 2026) ---
FIFA_RANKINGS = {
    'Argentina': {'rank': 1, 'points': 1877.27},
    'Spain': {'rank': 2, 'points': 1874.71},
    'France': {'rank': 3, 'points': 1870.70},
    'England': {'rank': 4, 'points': 1828.02},
    'Portugal': {'rank': 5, 'points': 1767.85},
    'Brazil': {'rank': 6, 'points': 1765.86},
    'Morocco': {'rank': 7, 'points': 1755.10},
    'Netherlands': {'rank': 8, 'points': 1753.57},
    'Belgium': {'rank': 9, 'points': 1742.24},
    'Germany': {'rank': 10, 'points': 1735.77},
    'Croatia': {'rank': 11, 'points': 1714.87},
    'Colombia': {'rank': 13, 'points': 1698.35},
    'Mexico': {'rank': 14, 'points': 1687.48},
    'Senegal': {'rank': 15, 'points': 1684.07},
    'Uruguay': {'rank': 16, 'points': 1673.07},
    'United States': {'rank': 17, 'points': 1671.23},
    'Japan': {'rank': 18, 'points': 1661.58},
    'Switzerland': {'rank': 19, 'points': 1650.06},
    'Iran': {'rank': 20, 'points': 1619.58},
    'Ecuador': {'rank': 21, 'points': 1614.00},
    'Australia': {'rank': 22, 'points': 1610.00},
    'Turkey': {'rank': 23, 'points': 1605.00},
    'South Korea': {'rank': 24, 'points': 1600.00},
    'Austria': {'rank': 25, 'points': 1595.00},
    'Sweden': {'rank': 26, 'points': 1590.00},
    'Egypt': {'rank': 27, 'points': 1585.00},
    'Norway': {'rank': 29, 'points': 1575.00},
    'Scotland': {'rank': 30, 'points': 1570.00},
    'Algeria': {'rank': 31, 'points': 1565.00},
    'Tunisia': {'rank': 32, 'points': 1560.00},
    'Paraguay': {'rank': 33, 'points': 1555.00},
    'Ivory Coast': {'rank': 34, 'points': 1550.00},
    'Czech Republic': {'rank': 35, 'points': 1545.00},
    'Saudi Arabia': {'rank': 36, 'points': 1540.00},
    'Ghana': {'rank': 37, 'points': 1535.00},
    'Canada': {'rank': 38, 'points': 1530.00},
    'Panama': {'rank': 39, 'points': 1520.00},
    'Iraq': {'rank': 40, 'points': 1515.00},
    'Jordan': {'rank': 41, 'points': 1510.00},
    'Qatar': {'rank': 42, 'points': 1505.00},
    'Uzbekistan': {'rank': 43, 'points': 1500.00},
    'Bosnia and Herzegovina': {'rank': 44, 'points': 1495.00},
    'South Africa': {'rank': 45, 'points': 1490.00},
    'DR Congo': {'rank': 46, 'points': 1485.00},
    'New Zealand': {'rank': 47, 'points': 1470.00},
    'Cape Verde': {'rank': 48, 'points': 1450.00},
    'Haiti': {'rank': 49, 'points': 1420.00},
    'Curacao': {'rank': 50, 'points': 1400.00},
}

# --- Odds de apuestas (probabilidades implícitas, junio 2026) ---
# Convertidas de odds americanas a probabilidades implícitas
BETTING_ODDS = {
    'France': 0.20, 'Spain': 0.155, 'England': 0.145, 'Argentina': 0.12,
    'Portugal': 0.095, 'Brazil': 0.083, 'Germany': 0.071, 'Netherlands': 0.05,
    'Belgium': 0.04, 'Colombia': 0.03, 'Croatia': 0.025, 'Uruguay': 0.022,
    'Mexico': 0.019, 'United States': 0.018, 'Japan': 0.015, 'Morocco': 0.014,
    'South Korea': 0.010, 'Switzerland': 0.009, 'Sweden': 0.008, 'Senegal': 0.007,
    'Ecuador': 0.006, 'Australia': 0.005, 'Turkey': 0.005, 'Austria': 0.004,
    'Iran': 0.004, 'Norway': 0.004, 'Egypt': 0.003, 'Algeria': 0.003,
    'Scotland': 0.003, 'Tunisia': 0.002, 'Paraguay': 0.002, 'Ivory Coast': 0.002,
    'Czech Republic': 0.002, 'Saudi Arabia': 0.002, 'Ghana': 0.002,
    'Canada': 0.002, 'Panama': 0.001, 'Iraq': 0.001, 'Jordan': 0.001,
    'Qatar': 0.001, 'Uzbekistan': 0.001, 'Bosnia and Herzegovina': 0.001,
    'South Africa': 0.001, 'DR Congo': 0.001, 'New Zealand': 0.0005,
    'Cape Verde': 0.0005, 'Haiti': 0.0003, 'Curacao': 0.0002,
}

# --- Resultados ya jugados del Mundial 2026 ---
WC2026_RESULTS = [
    # Jornada 1
    {'date': '2026-06-11', 'home': 'Mexico', 'away': 'South Africa', 'home_score': 2, 'away_score': 0, 'group': 'A'},
    {'date': '2026-06-11', 'home': 'South Korea', 'away': 'Czech Republic', 'home_score': 2, 'away_score': 1, 'group': 'A'},
    {'date': '2026-06-12', 'home': 'Canada', 'away': 'Bosnia and Herzegovina', 'home_score': 1, 'away_score': 1, 'group': 'B'},
    {'date': '2026-06-12', 'home': 'United States', 'away': 'Paraguay', 'home_score': 4, 'away_score': 1, 'group': 'D'},
    {'date': '2026-06-13', 'home': 'Qatar', 'away': 'Switzerland', 'home_score': 1, 'away_score': 1, 'group': 'B'},
    {'date': '2026-06-13', 'home': 'Brazil', 'away': 'Morocco', 'home_score': 1, 'away_score': 1, 'group': 'C'},
    {'date': '2026-06-13', 'home': 'Haiti', 'away': 'Scotland', 'home_score': 0, 'away_score': 1, 'group': 'C'},
    {'date': '2026-06-13', 'home': 'Australia', 'away': 'Turkey', 'home_score': 2, 'away_score': 0, 'group': 'D'},
    {'date': '2026-06-14', 'home': 'Germany', 'away': 'Curacao', 'home_score': 7, 'away_score': 1, 'group': 'E'},
    {'date': '2026-06-14', 'home': 'Ivory Coast', 'away': 'Ecuador', 'home_score': 1, 'away_score': 0, 'group': 'E'},
    {'date': '2026-06-14', 'home': 'Netherlands', 'away': 'Japan', 'home_score': 2, 'away_score': 2, 'group': 'F'},
    {'date': '2026-06-14', 'home': 'Sweden', 'away': 'Tunisia', 'home_score': 5, 'away_score': 1, 'group': 'F'},
    {'date': '2026-06-15', 'home': 'Belgium', 'away': 'Egypt', 'home_score': 1, 'away_score': 1, 'group': 'G'},
    {'date': '2026-06-15', 'home': 'Iran', 'away': 'New Zealand', 'home_score': 2, 'away_score': 2, 'group': 'G'},
    {'date': '2026-06-15', 'home': 'Spain', 'away': 'Cape Verde', 'home_score': 0, 'away_score': 0, 'group': 'H'},
    {'date': '2026-06-15', 'home': 'Saudi Arabia', 'away': 'Uruguay', 'home_score': 1, 'away_score': 1, 'group': 'H'},
    {'date': '2026-06-16', 'home': 'France', 'away': 'Senegal', 'home_score': 3, 'away_score': 1, 'group': 'I'},
    {'date': '2026-06-16', 'home': 'Norway', 'away': 'Iraq', 'home_score': 4, 'away_score': 1, 'group': 'I'},
    {'date': '2026-06-16', 'home': 'Argentina', 'away': 'Algeria', 'home_score': 3, 'away_score': 0, 'group': 'J'},
    {'date': '2026-06-17', 'home': 'Portugal', 'away': 'DR Congo', 'home_score': 1, 'away_score': 1, 'group': 'K'},
    {'date': '2026-06-17', 'home': 'England', 'away': 'Croatia', 'home_score': 4, 'away_score': 2, 'group': 'L'},
    # Jornada 2 (parcial)
    {'date': '2026-06-18', 'home': 'Czech Republic', 'away': 'South Africa', 'home_score': 1, 'away_score': 1, 'group': 'A'},
    {'date': '2026-06-18', 'home': 'Switzerland', 'away': 'Bosnia and Herzegovina', 'home_score': 4, 'away_score': 1, 'group': 'B'},
    {'date': '2026-06-18', 'home': 'Canada', 'away': 'Qatar', 'home_score': 6, 'away_score': 0, 'group': 'B'},
    {'date': '2026-06-19', 'home': 'United States', 'away': 'Australia', 'home_score': 2, 'away_score': 0, 'group': 'D'},
]

# --- Mapeo de nombres alternativos ---
NAME_MAPPING = {
    'USA': 'United States',
    'US': 'United States',
    'Korea Republic': 'South Korea',
    'Korea DPR': 'North Korea',
    'Türkiye': 'Turkey',
    'Turkiye': 'Turkey',
    'Czechia': 'Czech Republic',
    'Cote d\'Ivoire': 'Ivory Coast',
    'Côte d\'Ivoire': 'Ivory Coast',
    'Congo DR': 'DR Congo',
    'Dem. Rep. of the Congo': 'DR Congo',
    'DR Congo': 'DR Congo',
    'Bosnia-Herzegovina': 'Bosnia and Herzegovina',
    'Republic of Ireland': 'Ireland',
    'Cabo Verde': 'Cape Verde',
    'Curaçao': 'Curacao',
    'Korea': 'South Korea',
    'Holland': 'Netherlands',
    'Eire': 'Ireland',
    'IR Iran': 'Iran',
    'Chinese Taipei': 'Taiwan',
}


def normalize_name(name):
    """Normaliza el nombre de un equipo."""
    name = str(name).strip()
    return NAME_MAPPING.get(name, name)


# =============================================================================
# SECCIÓN 2: DESCARGA DE DATOS HISTÓRICOS
# =============================================================================

def download_historical_data():
    """Descarga el dataset de resultados internacionales desde GitHub."""
    print("\n📥 Descargando datos históricos de partidos internacionales...")
    url = "https://raw.githubusercontent.com/martj42/international_results/master/results.csv"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        df = pd.read_csv(StringIO(response.text))
        print(f"   ✅ Descargados {len(df):,} partidos históricos ({df['date'].min()} → {df['date'].max()})")
        return df
    except Exception as e:
        print(f"   ⚠️  Error descargando datos: {e}")
        print("   ℹ️  Intentando URL alternativa...")
        try:
            alt_url = "https://raw.githubusercontent.com/martj42/international_results/refs/heads/master/results.csv"
            response = requests.get(alt_url, timeout=30)
            response.raise_for_status()
            df = pd.read_csv(StringIO(response.text))
            print(f"   ✅ Descargados {len(df):,} partidos (URL alternativa)")
            return df
        except Exception as e2:
            print(f"   ❌ No se pudo descargar: {e2}")
            print("   ℹ️  Generando dataset sintético mínimo para demostración...")
            return generate_synthetic_data()


def generate_synthetic_data():
    """Genera datos sintéticos mínimos si no se puede descargar el dataset real."""
    print("   🔄 Generando datos sintéticos basados en rankings...")
    records = []
    teams = ALL_WC_TEAMS.copy()
    
    for year in range(2018, 2026):
        for month in range(1, 13):
            for _ in range(20):
                t1, t2 = random.sample(teams, 2)
                r1 = FIFA_RANKINGS.get(t1, {}).get('rank', 50)
                r2 = FIFA_RANKINGS.get(t2, {}).get('rank', 50)
                
                strength_diff = (r2 - r1) / 50.0
                p_home_win = 1 / (1 + 10 ** (-strength_diff))
                
                rng = random.random()
                if rng < p_home_win * 0.45:
                    hs, as_ = random.randint(1, 4), random.randint(0, 2)
                    if hs <= as_: hs = as_ + 1
                elif rng < p_home_win * 0.45 + 0.28:
                    s = random.randint(0, 2)
                    hs, as_ = s, s
                else:
                    hs, as_ = random.randint(0, 2), random.randint(1, 4)
                    if as_ <= hs: as_ = hs + 1
                
                records.append({
                    'date': f'{year}-{month:02d}-{random.randint(1,28):02d}',
                    'home_team': t1,
                    'away_team': t2,
                    'home_score': hs,
                    'away_score': as_,
                    'tournament': random.choice(['Friendly', 'FIFA World Cup qualification',
                                                  'UEFA Euro qualification', 'Copa América']),
                    'city': 'Unknown',
                    'country': t1,
                    'neutral': random.choice([True, False]),
                })
    
    return pd.DataFrame(records)


# =============================================================================
# SECCIÓN 3: CÁLCULO DE ELO RATINGS
# =============================================================================

class EloSystem:
    """Sistema de ratings Elo para selecciones de fútbol."""
    
    def __init__(self, k_base=30, home_advantage=100):
        self.ratings = defaultdict(lambda: 1500)
        self.k_base = k_base
        self.home_advantage = home_advantage
        self.history = defaultdict(list)  # {team: [(date, rating), ...]}
    
    def get_k_factor(self, tournament):
        """Factor K variable según importancia del torneo."""
        tournament = str(tournament).lower()
        if 'world cup' in tournament and 'qualif' not in tournament:
            return self.k_base * 2.0  # 60
        elif 'continental' in tournament or 'euro' in tournament or 'copa' in tournament:
            return self.k_base * 1.5  # 45
        elif 'qualif' in tournament or 'nations league' in tournament:
            return self.k_base * 1.2  # 36
        else:
            return self.k_base  # 30 (amistosos)
    
    def expected_score(self, rating_a, rating_b):
        """Probabilidad esperada de victoria de A."""
        return 1.0 / (1.0 + 10 ** ((rating_b - rating_a) / 400.0))
    
    def get_actual_score(self, goals_a, goals_b):
        """Resultado real: 1 = victoria, 0.5 = empate, 0 = derrota."""
        if goals_a > goals_b:
            return 1.0
        elif goals_a == goals_b:
            return 0.5
        else:
            return 0.0
    
    def goal_diff_multiplier(self, goal_diff):
        """Multiplicador basado en diferencia de goles."""
        goal_diff = abs(goal_diff)
        if goal_diff <= 1:
            return 1.0
        elif goal_diff == 2:
            return 1.5
        elif goal_diff == 3:
            return 1.75
        else:
            return 1.75 + (goal_diff - 3) * 0.1
    
    def update(self, home_team, away_team, home_score, away_score,
               tournament='Friendly', date=None, neutral=False):
        """Actualiza los ratings tras un partido."""
        ra = self.ratings[home_team]
        rb = self.ratings[away_team]
        
        # Ventaja de local (reducida si es terreno neutral)
        ha = self.home_advantage * (0.3 if neutral else 1.0)
        
        ea = self.expected_score(ra + ha, rb)
        eb = 1.0 - ea
        
        sa = self.get_actual_score(home_score, away_score)
        sb = 1.0 - sa
        
        k = self.get_k_factor(tournament)
        gdm = self.goal_diff_multiplier(home_score - away_score)
        
        self.ratings[home_team] = ra + k * gdm * (sa - ea)
        self.ratings[away_team] = rb + k * gdm * (sb - eb)
        
        if date:
            self.history[home_team].append((date, self.ratings[home_team]))
            self.history[away_team].append((date, self.ratings[away_team]))
    
    def process_matches(self, df):
        """Procesa todos los partidos del DataFrame para calcular Elo."""
        df_sorted = df.sort_values('date').reset_index(drop=True)
        
        for _, row in df_sorted.iterrows():
            home = normalize_name(row['home_team'])
            away = normalize_name(row['away_team'])
            neutral = row.get('neutral', False)
            
            self.update(
                home_team=home,
                away_team=away,
                home_score=int(row['home_score']),
                away_score=int(row['away_score']),
                tournament=row.get('tournament', 'Friendly'),
                date=row['date'],
                neutral=neutral
            )
    
    def get_rating(self, team):
        """Obtiene el rating actual de un equipo."""
        return self.ratings[normalize_name(team)]


# =============================================================================
# SECCIÓN 4: FEATURE ENGINEERING
# =============================================================================

def time_decay_weight(match_date, reference_date=None, half_life_years=3):
    """
    Peso de decaimiento temporal exponencial.
    Un partido de hace `half_life_years` años tiene peso 0.5.
    """
    if reference_date is None:
        reference_date = REFERENCE_DATE
    
    if isinstance(match_date, str):
        match_date = datetime.strptime(match_date[:10], '%Y-%m-%d')
    if isinstance(reference_date, str):
        reference_date = datetime.strptime(reference_date[:10], '%Y-%m-%d')
    
    days_diff = (reference_date - match_date).days
    if days_diff < 0:
        return 1.0
    
    half_life_days = half_life_years * 365.25
    return 0.5 ** (days_diff / half_life_days)


def tournament_weight(tournament):
    """Peso según importancia del torneo."""
    tournament = str(tournament).lower()
    if 'world cup' in tournament and 'qualif' not in tournament:
        return 3.0
    elif 'euro' in tournament and 'qualif' not in tournament:
        return 2.0
    elif 'copa am' in tournament or 'african cup' in tournament or 'asian cup' in tournament:
        return 2.0
    elif 'nations league' in tournament:
        return 1.5
    elif 'qualif' in tournament:
        return 1.3
    elif 'confederations' in tournament:
        return 1.8
    else:
        return 1.0  # Amistosos


def compute_team_features(df, team, n_recent=10):
    """
    Calcula features para un equipo basado en su historial.
    Aplica decaimiento temporal y pesos por torneo.
    """
    team_n = normalize_name(team)
    
    # Filtrar partidos del equipo
    mask = (df['home_team_n'] == team_n) | (df['away_team_n'] == team_n)
    team_df = df[mask].sort_values('date', ascending=False).copy()
    
    if len(team_df) == 0:
        return {
            'weighted_win_rate': 0.33,
            'weighted_draw_rate': 0.34,
            'weighted_goals_scored': 1.0,
            'weighted_goals_conceded': 1.0,
            'recent_win_rate': 0.33,
            'recent_goals_scored': 1.0,
            'recent_goals_conceded': 1.0,
            'official_win_rate': 0.33,
            'consistency': 0.5,
            'matches_played': 0,
            'wc_experience': 0,
        }
    
    # Calcular resultados y pesos
    results = []
    for _, row in team_df.iterrows():
        is_home = row['home_team_n'] == team_n
        gs = row['home_score'] if is_home else row['away_score']
        gc = row['away_score'] if is_home else row['home_score']
        
        if gs > gc:
            result = 'W'
        elif gs == gc:
            result = 'D'
        else:
            result = 'L'
        
        tw = time_decay_weight(row['date'])
        tourney_w = tournament_weight(row.get('tournament', 'Friendly'))
        combined_weight = tw * tourney_w
        
        is_official = 'friendly' not in str(row.get('tournament', '')).lower()
        is_wc = 'world cup' in str(row.get('tournament', '')).lower() and 'qualif' not in str(row.get('tournament', '')).lower()
        
        results.append({
            'result': result,
            'goals_scored': gs,
            'goals_conceded': gc,
            'weight': combined_weight,
            'time_weight': tw,
            'is_official': is_official,
            'is_wc': is_wc,
        })
    
    results_df = pd.DataFrame(results)
    
    # --- Features con pesos temporales ---
    total_weight = results_df['weight'].sum()
    if total_weight > 0:
        weighted_wins = results_df[results_df['result'] == 'W']['weight'].sum()
        weighted_draws = results_df[results_df['result'] == 'D']['weight'].sum()
        weighted_win_rate = weighted_wins / total_weight
        weighted_draw_rate = weighted_draws / total_weight
        weighted_gs = (results_df['goals_scored'] * results_df['weight']).sum() / total_weight
        weighted_gc = (results_df['goals_conceded'] * results_df['weight']).sum() / total_weight
    else:
        weighted_win_rate = 0.33
        weighted_draw_rate = 0.34
        weighted_gs = 1.0
        weighted_gc = 1.0
    
    # --- Forma reciente (últimos N partidos) ---
    recent = results_df.head(n_recent)
    if len(recent) > 0:
        recent_wins = (recent['result'] == 'W').sum()
        recent_win_rate = recent_wins / len(recent)
        recent_gs = recent['goals_scored'].mean()
        recent_gc = recent['goals_conceded'].mean()
    else:
        recent_win_rate = 0.33
        recent_gs = 1.0
        recent_gc = 1.0
    
    # --- Rendimiento en partidos oficiales ---
    official = results_df[results_df['is_official']]
    if len(official) > 0:
        off_tw = official['weight'].sum()
        if off_tw > 0:
            official_win_rate = official[official['result'] == 'W']['weight'].sum() / off_tw
        else:
            official_win_rate = 0.33
    else:
        official_win_rate = 0.33
    
    # --- Consistencia (inversa de la varianza de goles marcados) ---
    if len(results_df) >= 5:
        consistency = 1.0 / (1.0 + results_df['goals_scored'].std())
    else:
        consistency = 0.5
    
    # --- Experiencia en mundiales ---
    wc_matches = results_df[results_df['is_wc']]
    wc_experience = len(wc_matches)
    
    return {
        'weighted_win_rate': weighted_win_rate,
        'weighted_draw_rate': weighted_draw_rate,
        'weighted_goals_scored': weighted_gs,
        'weighted_goals_conceded': weighted_gc,
        'recent_win_rate': recent_win_rate,
        'recent_goals_scored': recent_gs,
        'recent_goals_conceded': recent_gc,
        'official_win_rate': official_win_rate,
        'consistency': consistency,
        'matches_played': len(results_df),
        'wc_experience': wc_experience,
    }


def compute_h2h_features(df, team_a, team_b):
    """Calcula features del historial directo entre dos equipos."""
    ta = normalize_name(team_a)
    tb = normalize_name(team_b)
    
    mask = ((df['home_team_n'] == ta) & (df['away_team_n'] == tb)) | \
           ((df['home_team_n'] == tb) & (df['away_team_n'] == ta))
    h2h = df[mask].copy()
    
    if len(h2h) == 0:
        return {'h2h_win_rate_a': 0.5, 'h2h_matches': 0, 'h2h_goal_diff': 0}
    
    wins_a = 0
    total_weight = 0
    total_gd = 0
    
    for _, row in h2h.iterrows():
        w = time_decay_weight(row['date'])
        is_a_home = row['home_team_n'] == ta
        
        if is_a_home:
            ga, gb = row['home_score'], row['away_score']
        else:
            ga, gb = row['away_score'], row['home_score']
        
        if ga > gb:
            wins_a += w
        elif ga == gb:
            wins_a += w * 0.5
        
        total_weight += w
        total_gd += (ga - gb) * w
    
    return {
        'h2h_win_rate_a': wins_a / total_weight if total_weight > 0 else 0.5,
        'h2h_matches': len(h2h),
        'h2h_goal_diff': total_gd / total_weight if total_weight > 0 else 0,
    }


def compute_wc2026_momentum(team):
    """Calcula el momentum del equipo en el Mundial 2026 actual."""
    team_n = normalize_name(team)
    
    points = 0
    goals_scored = 0
    goals_conceded = 0
    matches = 0
    
    for result in WC2026_RESULTS:
        if normalize_name(result['home']) == team_n:
            gs, gc = result['home_score'], result['away_score']
        elif normalize_name(result['away']) == team_n:
            gs, gc = result['away_score'], result['home_score']
        else:
            continue
        
        matches += 1
        goals_scored += gs
        goals_conceded += gc
        
        if gs > gc:
            points += 3
        elif gs == gc:
            points += 1
    
    if matches == 0:
        return {
            'wc26_points_per_game': 0.0,
            'wc26_goals_scored_avg': 0.0,
            'wc26_goals_conceded_avg': 0.0,
            'wc26_goal_diff': 0.0,
            'wc26_matches': 0,
        }
    
    return {
        'wc26_points_per_game': points / matches,
        'wc26_goals_scored_avg': goals_scored / matches,
        'wc26_goals_conceded_avg': goals_conceded / matches,
        'wc26_goal_diff': (goals_scored - goals_conceded) / matches,
        'wc26_matches': matches,
    }


def build_match_features(df, elo_system, team_a, team_b, team_features_cache):
    """
    Construye el vector de features para un enfrentamiento team_a vs team_b.
    """
    ta = normalize_name(team_a)
    tb = normalize_name(team_b)
    
    # Obtener features de cada equipo (con caché)
    if ta not in team_features_cache:
        team_features_cache[ta] = compute_team_features(df, ta)
    if tb not in team_features_cache:
        team_features_cache[tb] = compute_team_features(df, tb)
    
    fa = team_features_cache[ta]
    fb = team_features_cache[tb]
    
    # Rankings y puntos FIFA
    rank_a = FIFA_RANKINGS.get(ta, {'rank': 60, 'points': 1400})
    rank_b = FIFA_RANKINGS.get(tb, {'rank': 60, 'points': 1400})
    
    # Elo
    elo_a = elo_system.get_rating(ta)
    elo_b = elo_system.get_rating(tb)
    
    # Odds
    odds_a = BETTING_ODDS.get(ta, 0.001)
    odds_b = BETTING_ODDS.get(tb, 0.001)
    
    # H2H
    h2h = compute_h2h_features(df, ta, tb)
    
    # Momentum WC2026
    mom_a = compute_wc2026_momentum(ta)
    mom_b = compute_wc2026_momentum(tb)
    
    features = {
        # --- Diferencias de rating/ranking ---
        'fifa_rank_diff': rank_a['rank'] - rank_b['rank'],  # Negativo = A mejor
        'fifa_points_diff': rank_a['points'] - rank_b['points'],
        'elo_diff': elo_a - elo_b,
        'odds_prob_diff': odds_a - odds_b,
        
        # --- Features del equipo A (relativas) ---
        'win_rate_diff': fa['weighted_win_rate'] - fb['weighted_win_rate'],
        'draw_rate_diff': fa['weighted_draw_rate'] - fb['weighted_draw_rate'],
        'goals_scored_diff': fa['weighted_goals_scored'] - fb['weighted_goals_scored'],
        'goals_conceded_diff': fa['weighted_goals_conceded'] - fb['weighted_goals_conceded'],
        
        # --- Forma reciente ---
        'recent_form_diff': fa['recent_win_rate'] - fb['recent_win_rate'],
        'recent_attack_diff': fa['recent_goals_scored'] - fb['recent_goals_scored'],
        'recent_defense_diff': fb['recent_goals_conceded'] - fa['recent_goals_conceded'],  # Invertido
        
        # --- Rendimiento oficial ---
        'official_wr_diff': fa['official_win_rate'] - fb['official_win_rate'],
        
        # --- Consistencia ---
        'consistency_diff': fa['consistency'] - fb['consistency'],
        
        # --- Experiencia ---
        'wc_exp_diff': fa['wc_experience'] - fb['wc_experience'],
        'matches_played_diff': fa['matches_played'] - fb['matches_played'],
        
        # --- H2H ---
        'h2h_win_rate': h2h['h2h_win_rate_a'],
        'h2h_goal_diff': h2h['h2h_goal_diff'],
        
        # --- Momentum WC2026 ---
        'wc26_ppg_diff': mom_a['wc26_points_per_game'] - mom_b['wc26_points_per_game'],
        'wc26_gd_diff': mom_a['wc26_goal_diff'] - mom_b['wc26_goal_diff'],
        
        # --- Absolutas combinadas ---
        'avg_elo': (elo_a + elo_b) / 2,
        'avg_fifa_points': (rank_a['points'] + rank_b['points']) / 2,
        'combined_odds': odds_a + odds_b,
    }
    
    return features


def build_training_dataset(df, elo_system):
    """
    Construye el dataset de entrenamiento a partir de partidos históricos.
    Solo usa partidos recientes (últimos 8 años) y de equipos relevantes.
    """
    print("\n🔧 Construyendo dataset de entrenamiento...")
    
    # Filtrar partidos recientes (2018+)
    df_recent = df[df['date'] >= '2018-01-01'].copy()
    print(f"   📊 Partidos desde 2018: {len(df_recent):,}")
    
    # Normalizar nombres
    df_recent['home_team_n'] = df_recent['home_team'].apply(normalize_name)
    df_recent['away_team_n'] = df_recent['away_team'].apply(normalize_name)
    
    # Filtrar solo partidos donde al menos un equipo está en el Mundial
    wc_teams_set = set(normalize_name(t) for t in ALL_WC_TEAMS)
    mask = df_recent['home_team_n'].isin(wc_teams_set) | df_recent['away_team_n'].isin(wc_teams_set)
    df_filtered = df_recent[mask].copy()
    print(f"   📊 Partidos con equipos del Mundial: {len(df_filtered):,}")
    
    # Construir features para cada partido
    team_features_cache = {}
    X_rows = []
    y_rows = []
    
    for idx, row in df_filtered.iterrows():
        home = normalize_name(row['home_team'])
        away = normalize_name(row['away_team'])
        
        try:
            features = build_match_features(df_recent, elo_system, home, away, team_features_cache)
            X_rows.append(features)
            
            # Target: 0 = empate, 1 = gana equipo A (home), 2 = gana equipo B (away)
            if row['home_score'] > row['away_score']:
                y_rows.append(1)  # Win A
            elif row['home_score'] == row['away_score']:
                y_rows.append(0)  # Draw
            else:
                y_rows.append(2)  # Win B
        except Exception as e:
            continue
    
    X = pd.DataFrame(X_rows)
    y = np.array(y_rows)
    
    print(f"   ✅ Dataset construido: {X.shape[0]} partidos, {X.shape[1]} features")
    print(f"   📊 Distribución: Win A={sum(y==1)} | Draw={sum(y==0)} | Win B={sum(y==2)}")
    
    return X, y, team_features_cache


# =============================================================================
# SECCIÓN 5: SELECCIÓN DE FEATURES
# =============================================================================

def feature_selection(X, y):
    """
    Realiza selección de features usando múltiples métodos.
    Retorna el DataFrame filtrado y un reporte.
    """
    print("\n🔍 Selección de features...")
    
    feature_names = X.columns.tolist()
    
    # --- 1. Eliminar features con varianza cero ---
    zero_var = X.columns[X.std() == 0].tolist()
    if zero_var:
        print(f"   ❌ Eliminadas {len(zero_var)} features con varianza cero: {zero_var}")
        X = X.drop(columns=zero_var)
        feature_names = [f for f in feature_names if f not in zero_var]
    
    # --- 2. Matriz de correlación ---
    corr_matrix = X.corr().abs()
    upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
    high_corr_pairs = []
    to_drop = set()
    
    for col in upper.columns:
        for idx in upper.index:
            if upper.loc[idx, col] > 0.85:
                high_corr_pairs.append((idx, col, upper.loc[idx, col]))
                # Eliminar la feature con menor información mutua
                to_drop.add(col)
    
    if high_corr_pairs:
        print(f"   🔗 Features altamente correlacionadas (>{0.85}):")
        for f1, f2, corr in high_corr_pairs[:5]:
            print(f"      {f1} ↔ {f2}: {corr:.3f}")
    
    # --- 3. Información mutua ---
    X_filled = X.fillna(0)
    mi_scores = mutual_info_classif(X_filled, y, random_state=RANDOM_STATE)
    mi_ranking = pd.Series(mi_scores, index=X.columns).sort_values(ascending=False)
    
    print(f"\n   📊 Top 10 features por Información Mutua:")
    for feat, score in mi_ranking.head(10).items():
        print(f"      {feat}: {score:.4f}")
    
    # --- 4. Feature importance con Random Forest ---
    rf_temp = RandomForestClassifier(n_estimators=100, random_state=RANDOM_STATE, n_jobs=-1)
    rf_temp.fit(X_filled, y)
    rf_importance = pd.Series(rf_temp.feature_importances_, index=X.columns).sort_values(ascending=False)
    
    print(f"\n   🌲 Top 10 features por Random Forest Importance:")
    for feat, score in rf_importance.head(10).items():
        print(f"      {feat}: {score:.4f}")
    
    # --- 5. Eliminar features de baja importancia ---
    # Mantener features que estén en el top por MI o RF
    mi_top = set(mi_ranking.head(15).index)
    rf_top = set(rf_importance.head(15).index)
    keep_features = mi_top | rf_top
    
    # Eliminar features muy correlacionadas (excepto las top)
    final_drop = to_drop - keep_features
    if final_drop:
        print(f"\n   ✂️  Eliminando {len(final_drop)} features redundantes: {final_drop}")
        X = X.drop(columns=list(final_drop), errors='ignore')
    
    print(f"\n   ✅ Features finales: {X.shape[1]}")
    
    return X, mi_ranking, rf_importance, corr_matrix


# =============================================================================
# SECCIÓN 6: MODELOS ML
# =============================================================================

def train_and_compare_models(X, y):
    """
    Entrena múltiples modelos con cross-validation y los compara.
    Retorna el mejor modelo y las métricas.
    """
    print("\n" + "=" * 70)
    print("🤖 ENTRENAMIENTO Y COMPARACIÓN DE MODELOS")
    print("=" * 70)
    
    # Escalar features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X.fillna(0))
    
    # Definir modelos
    models = {
        'Logistic Regression': LogisticRegression(
            max_iter=2000, C=1.0,
            random_state=RANDOM_STATE
        ),
        'Random Forest': RandomForestClassifier(
            n_estimators=300, max_depth=12, min_samples_split=10,
            min_samples_leaf=5, random_state=RANDOM_STATE, n_jobs=-1
        ),
        'SVM (RBF)': SVC(
            kernel='rbf', C=10, gamma='scale', probability=True,
            random_state=RANDOM_STATE
        ),
        'Neural Network (MLP)': MLPClassifier(
            hidden_layer_sizes=(128, 64, 32), max_iter=1000,
            early_stopping=True, validation_fraction=0.15,
            random_state=RANDOM_STATE, learning_rate='adaptive'
        ),
    }
    
    if HAS_XGBOOST:
        models['XGBoost'] = XGBClassifier(
            n_estimators=300, max_depth=6, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8,
            random_state=RANDOM_STATE, eval_metric='mlogloss',
            verbosity=0
        )
    else:
        models['Gradient Boosting'] = GradientBoostingClassifier(
            n_estimators=300, max_depth=6, learning_rate=0.05,
            subsample=0.8, random_state=RANDOM_STATE
        )
    
    # Cross-validation
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    
    results = {}
    best_score = -1
    best_model_name = None
    best_model = None
    
    for name, model in models.items():
        print(f"\n   🔄 Entrenando {name}...")
        
        try:
            # Accuracy
            acc_scores = cross_val_score(model, X_scaled, y, cv=cv,
                                         scoring='accuracy', n_jobs=-1)
            
            # F1 macro
            f1_scores = cross_val_score(model, X_scaled, y, cv=cv,
                                         scoring='f1_macro', n_jobs=-1)
            
            # Log loss (negativa en sklearn)
            ll_scores = cross_val_score(model, X_scaled, y, cv=cv,
                                         scoring='neg_log_loss', n_jobs=-1)
            
            results[name] = {
                'accuracy_mean': acc_scores.mean(),
                'accuracy_std': acc_scores.std(),
                'f1_mean': f1_scores.mean(),
                'f1_std': f1_scores.std(),
                'log_loss_mean': -ll_scores.mean(),
                'log_loss_std': ll_scores.std(),
            }
            
            print(f"      Accuracy:  {acc_scores.mean():.4f} ± {acc_scores.std():.4f}")
            print(f"      F1 Macro:  {f1_scores.mean():.4f} ± {f1_scores.std():.4f}")
            print(f"      Log Loss:  {-ll_scores.mean():.4f} ± {ll_scores.std():.4f}")
            
            # Seleccionar mejor modelo por F1 macro
            if f1_scores.mean() > best_score:
                best_score = f1_scores.mean()
                best_model_name = name
                best_model = model
        
        except Exception as e:
            print(f"      ❌ Error: {e}")
            results[name] = {'accuracy_mean': 0, 'f1_mean': 0, 'log_loss_mean': 999}
    
    # Entrenar todos los modelos con todos los datos
    print(f"\n   🏆 MEJOR MODELO (F1 Macro): {best_model_name} (F1 Macro: {best_score:.4f})")
    fitted_models = {}
    for name, model in models.items():
        try:
            model.fit(X_scaled, y)
            fitted_models[name] = model
        except Exception as e:
            print(f"      ❌ Error al entrenar final de {name}: {e}")
    
    return fitted_models, best_model_name, scaler, results


# =============================================================================
# SECCIÓN 7: SIMULACIÓN DEL MUNDIAL
# =============================================================================

def predict_match(model, scaler, df, elo_system, team_a, team_b, team_features_cache):
    """
    Predice el resultado de un partido usando el mejor modelo.
    Retorna probabilidades [draw, win_a, win_b].
    """
    features = build_match_features(df, elo_system, team_a, team_b, team_features_cache)
    X_match = pd.DataFrame([features])
    
    # Asegurar que las columnas coinciden
    X_scaled = scaler.transform(X_match.fillna(0))
    
    probs = model.predict_proba(X_scaled)[0]
    # probs: [P(draw), P(win_a), P(win_b)]
    
    return probs


def precompute_all_probabilities(model, scaler, df, elo_system, team_features_cache):
    """
    Pre-computa las probabilidades de TODOS los enfrentamientos posibles
    entre equipos del Mundial. Esto evita recalcular features en cada
    iteración de Monte Carlo.
    """
    print("\n⚡ Pre-computando probabilidades de todos los enfrentamientos...")
    
    all_teams = [normalize_name(t) for t in ALL_WC_TEAMS]
    prob_cache = {}
    total = len(all_teams) * (len(all_teams) - 1) // 2
    computed = 0
    
    for i in range(len(all_teams)):
        for j in range(i + 1, len(all_teams)):
            ta = all_teams[i]
            tb = all_teams[j]
            
            features = build_match_features(df, elo_system, ta, tb, team_features_cache)
            X_match = pd.DataFrame([features])
            X_scaled = scaler.transform(X_match.fillna(0))
            probs = model.predict_proba(X_scaled)[0]
            
            prob_cache[(ta, tb)] = probs  # [P(draw), P(win_a), P(win_b)]
            # Para el orden inverso, invertir win_a y win_b
            prob_cache[(tb, ta)] = np.array([probs[0], probs[2], probs[1]])
            
            computed += 1
    
    print(f"   ✅ {computed} enfrentamientos pre-computados")
    return prob_cache


def simulate_group_stage(prob_cache, n_simulations=2000):
    """Simula la fase de grupos completa múltiples veces (optimizado)."""
    print("\n" + "=" * 70)
    print("⚽ SIMULACIÓN DE LA FASE DE GRUPOS")
    print("=" * 70)
    
    # Determinar qué partidos ya se jugaron y cuáles faltan
    played_matches = set()
    for r in WC2026_RESULTS:
        key = (normalize_name(r['home']), normalize_name(r['away']))
        played_matches.add(key)
        played_matches.add((key[1], key[0]))
    
    # Calcular resultados reales por grupo (una sola vez)
    real_standings = {}
    for group in WC2026_GROUPS:
        real_standings[group] = {}
        for team in WC2026_GROUPS[group]:
            tn = normalize_name(team)
            real_standings[group][tn] = {'pts': 0, 'gd': 0, 'gf': 0}
    
    for r in WC2026_RESULTS:
        group = r['group']
        home = normalize_name(r['home'])
        away = normalize_name(r['away'])
        hs, as_ = r['home_score'], r['away_score']
        
        gd_home = hs - as_
        pts_home = 3 if hs > as_ else (1 if hs == as_ else 0)
        pts_away = 3 if as_ > hs else (1 if hs == as_ else 0)
        
        real_standings[group][home]['pts'] += pts_home
        real_standings[group][home]['gd'] += gd_home
        real_standings[group][home]['gf'] += hs
        
        real_standings[group][away]['pts'] += pts_away
        real_standings[group][away]['gd'] -= gd_home
        real_standings[group][away]['gf'] += as_
    
    # Identificar partidos pendientes y pre-cargar sus probabilidades
    pending_matches = []
    for group, teams in WC2026_GROUPS.items():
        for i in range(len(teams)):
            for j in range(i + 1, len(teams)):
                ta = normalize_name(teams[i])
                tb = normalize_name(teams[j])
                if (ta, tb) not in played_matches:
                    probs = prob_cache.get((ta, tb), np.array([0.33, 0.34, 0.33]))
                    pending_matches.append((group, ta, tb, probs))
    
    print(f"   📊 Partidos jugados: {len(WC2026_RESULTS)}")
    print(f"   📊 Partidos pendientes en fase de grupos: {len(pending_matches)}")
    
    # Simular múltiples veces
    advancement_count = defaultdict(int)
    group_winner_count = defaultdict(int)
    
    for sim in range(n_simulations):
        sim_standings = {}
        
        # Copiar resultados reales
        for group in WC2026_GROUPS:
            sim_standings[group] = {}
            for tn, stats in real_standings[group].items():
                sim_standings[group][tn] = {
                    'pts': stats['pts'],
                    'gd': stats['gd'],
                    'gf': stats['gf'],
                }
        
        # Simular partidos pendientes (usando probabilidades pre-computadas)
        for group, ta, tb, probs in pending_matches:
            rng = random.random()
            if rng < probs[0]:  # Draw
                sim_standings[group][ta]['pts'] += 1
                sim_standings[group][tb]['pts'] += 1
                goals = random.choice([0, 1, 1, 2])
                sim_standings[group][ta]['gf'] += goals
                sim_standings[group][tb]['gf'] += goals
            elif rng < probs[0] + probs[1]:  # Win A
                sim_standings[group][ta]['pts'] += 3
                gd = random.choice([1, 1, 2, 2, 3])
                gc = random.randint(0, 2)
                sim_standings[group][ta]['gd'] += gd
                sim_standings[group][ta]['gf'] += gc + gd
                sim_standings[group][tb]['gd'] -= gd
                sim_standings[group][tb]['gf'] += gc
            else:  # Win B
                sim_standings[group][tb]['pts'] += 3
                gd = random.choice([1, 1, 2, 2, 3])
                gc = random.randint(0, 2)
                sim_standings[group][tb]['gd'] += gd
                sim_standings[group][tb]['gf'] += gc + gd
                sim_standings[group][ta]['gd'] -= gd
                sim_standings[group][ta]['gf'] += gc
        
        # Determinar clasificados de cada grupo
        for group in WC2026_GROUPS:
            standings = sorted(
                sim_standings[group].items(),
                key=lambda x: (x[1]['pts'], x[1]['gd'], x[1]['gf']),
                reverse=True
            )
            
            if len(standings) >= 1:
                group_winner_count[standings[0][0]] += 1
                advancement_count[standings[0][0]] += 1
            if len(standings) >= 2:
                advancement_count[standings[1][0]] += 1
            if len(standings) >= 3:
                advancement_count[standings[2][0]] += 0.3
    
    return advancement_count, group_winner_count, n_simulations


def simulate_knockout(prob_cache, qualified_teams, n_simulations=2000):
    """Simula la fase eliminatoria completa (optimizado)."""
    print("\n" + "=" * 70)
    print("🏆 SIMULACIÓN DE LA FASE ELIMINATORIA")
    print("=" * 70)
    
    stage_counts = {
        'round_of_32': defaultdict(int),
        'round_of_16': defaultdict(int),
        'quarter_finals': defaultdict(int),
        'semi_finals': defaultdict(int),
        'final': defaultdict(int),
        'winner': defaultdict(int),
    }
    
    for sim in range(n_simulations):
        remaining = list(qualified_teams)
        random.shuffle(remaining)
        
        current_round = remaining[:32]
        round_names = ['round_of_32', 'round_of_16', 'quarter_finals',
                       'semi_finals', 'final', 'winner']
        round_idx = 0
        
        for team in current_round:
            stage_counts[round_names[round_idx]][team] += 1
        
        while len(current_round) > 1:
            round_idx += 1
            next_round = []
            
            for i in range(0, len(current_round), 2):
                if i + 1 >= len(current_round):
                    next_round.append(current_round[i])
                    continue
                
                ta = current_round[i]
                tb = current_round[i + 1]
                
                probs = prob_cache.get((ta, tb), np.array([0.33, 0.34, 0.33]))
                
                # En eliminatorias no hay empate
                p_a = probs[1] + probs[0] * 0.5
                
                if random.random() < p_a:
                    next_round.append(ta)
                else:
                    next_round.append(tb)
            
            current_round = next_round
            
            if round_idx < len(round_names):
                for team in current_round:
                    stage_counts[round_names[round_idx]][team] += 1
    
    return stage_counts, n_simulations


# =============================================================================
# SECCIÓN 8: VISUALIZACIONES
# =============================================================================

def plot_feature_importance(mi_ranking, rf_importance):
    """Genera gráficos de importancia de features."""
    fig, axes = plt.subplots(1, 2, figsize=(18, 8))
    fig.suptitle('📊 Importancia de Features', fontsize=16, fontweight='bold')
    
    # Mutual Information
    top_mi = mi_ranking.head(15)
    colors_mi = plt.cm.viridis(np.linspace(0.3, 0.9, len(top_mi)))
    axes[0].barh(range(len(top_mi)), top_mi.values[::-1], color=colors_mi)
    axes[0].set_yticks(range(len(top_mi)))
    axes[0].set_yticklabels(top_mi.index[::-1], fontsize=10)
    axes[0].set_xlabel('Mutual Information Score')
    axes[0].set_title('Información Mutua', fontsize=13, fontweight='bold')
    
    # Random Forest
    top_rf = rf_importance.head(15)
    colors_rf = plt.cm.magma(np.linspace(0.3, 0.9, len(top_rf)))
    axes[1].barh(range(len(top_rf)), top_rf.values[::-1], color=colors_rf)
    axes[1].set_yticks(range(len(top_rf)))
    axes[1].set_yticklabels(top_rf.index[::-1], fontsize=10)
    axes[1].set_xlabel('Feature Importance')
    axes[1].set_title('Random Forest Importance', fontsize=13, fontweight='bold')
    
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'feature_importance.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"   📊 Gráfico guardado: {path}")


def plot_correlation_matrix(corr_matrix):
    """Genera heatmap de correlación."""
    fig, ax = plt.subplots(figsize=(14, 12))
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
    sns.heatmap(corr_matrix, mask=mask, cmap='RdBu_r', center=0,
                annot=True, fmt='.2f', linewidths=0.5, ax=ax,
                cbar_kws={'label': 'Correlación'}, annot_kws={'size': 7})
    ax.set_title('🔗 Matriz de Correlación de Features', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'correlation_matrix.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"   📊 Gráfico guardado: {path}")


def plot_model_comparison(results):
    """Genera gráfico comparativo de modelos."""
    fig, axes = plt.subplots(1, 3, figsize=(20, 7))
    fig.suptitle('🤖 Comparación de Modelos ML', fontsize=16, fontweight='bold')
    
    model_names = list(results.keys())
    colors = plt.cm.Set2(np.linspace(0, 1, len(model_names)))
    
    # Accuracy
    accs = [results[m]['accuracy_mean'] for m in model_names]
    acc_stds = [results[m]['accuracy_std'] for m in model_names]
    bars = axes[0].bar(range(len(model_names)), accs, yerr=acc_stds,
                       color=colors, edgecolor='black', linewidth=0.5, capsize=5)
    axes[0].set_xticks(range(len(model_names)))
    axes[0].set_xticklabels(model_names, rotation=30, ha='right', fontsize=9)
    axes[0].set_ylabel('Accuracy')
    axes[0].set_title('Accuracy (↑ mejor)', fontweight='bold')
    axes[0].set_ylim(0, max(accs) * 1.15 if accs else 1)
    for bar, val in zip(bars, accs):
        axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                     f'{val:.3f}', ha='center', fontsize=9, fontweight='bold')
    
    # F1 Score
    f1s = [results[m]['f1_mean'] for m in model_names]
    f1_stds = [results[m]['f1_std'] for m in model_names]
    bars = axes[1].bar(range(len(model_names)), f1s, yerr=f1_stds,
                       color=colors, edgecolor='black', linewidth=0.5, capsize=5)
    axes[1].set_xticks(range(len(model_names)))
    axes[1].set_xticklabels(model_names, rotation=30, ha='right', fontsize=9)
    axes[1].set_ylabel('F1 Score (Macro)')
    axes[1].set_title('F1 Score Macro (↑ mejor)', fontweight='bold')
    axes[1].set_ylim(0, max(f1s) * 1.15 if f1s else 1)
    for bar, val in zip(bars, f1s):
        axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                     f'{val:.3f}', ha='center', fontsize=9, fontweight='bold')
    
    # Log Loss
    lls = [results[m]['log_loss_mean'] for m in model_names]
    ll_stds = [results[m]['log_loss_std'] for m in model_names]
    bars = axes[2].bar(range(len(model_names)), lls, yerr=ll_stds,
                       color=colors, edgecolor='black', linewidth=0.5, capsize=5)
    axes[2].set_xticks(range(len(model_names)))
    axes[2].set_xticklabels(model_names, rotation=30, ha='right', fontsize=9)
    axes[2].set_ylabel('Log Loss')
    axes[2].set_title('Log Loss (↓ mejor)', fontweight='bold')
    for bar, val in zip(bars, lls):
        axes[2].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                     f'{val:.3f}', ha='center', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'model_comparison.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"   📊 Gráfico guardado: {path}")


def plot_tournament_predictions(stage_counts, n_simulations):
    """Genera gráfico con las probabilidades de ganar el Mundial."""
    # Probabilidades de ganar
    winner_probs = {team: count / n_simulations
                    for team, count in stage_counts['winner'].items()}
    winner_probs = dict(sorted(winner_probs.items(), key=lambda x: x[1], reverse=True))
    
    # Top 20
    top_teams = list(winner_probs.keys())[:20]
    top_probs = [winner_probs[t] * 100 for t in top_teams]
    
    fig, ax = plt.subplots(figsize=(14, 10))
    
    colors = plt.cm.YlOrRd(np.linspace(0.3, 0.95, len(top_teams)))[::-1]
    bars = ax.barh(range(len(top_teams)), top_probs[::-1], color=colors,
                   edgecolor='black', linewidth=0.5)
    
    ax.set_yticks(range(len(top_teams)))
    ax.set_yticklabels(top_teams[::-1], fontsize=11, fontweight='bold')
    ax.set_xlabel('Probabilidad de ganar el Mundial (%)', fontsize=12)
    ax.set_title('🏆 PREDICCIÓN: ¿Quién ganará el Mundial 2026?',
                 fontsize=16, fontweight='bold', pad=20)
    
    for bar, val in zip(bars, top_probs[::-1]):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
                f'{val:.1f}%', va='center', fontsize=10, fontweight='bold')
    
    ax.grid(axis='x', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'winner_predictions.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"   📊 Gráfico guardado: {path}")
    
    return winner_probs


def plot_stage_progression(stage_counts, n_simulations):
    """Genera gráfico de progresión por rondas para los top equipos."""
    stages = ['round_of_16', 'quarter_finals', 'semi_finals', 'final', 'winner']
    stage_labels = ['Octavos', 'Cuartos', 'Semifinal', 'Final', 'Campeón']
    
    # Top 10 equipos por probabilidad de ganar
    winner_probs = {team: count / n_simulations
                    for team, count in stage_counts['winner'].items()}
    top_teams = sorted(winner_probs.keys(), key=lambda t: winner_probs[t], reverse=True)[:10]
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    colors = plt.cm.tab10(range(len(top_teams)))
    
    for i, team in enumerate(top_teams):
        probs = []
        for stage in stages:
            count = stage_counts[stage].get(team, 0)
            probs.append(count / n_simulations * 100)
        
        ax.plot(stage_labels, probs, '-o', color=colors[i], label=team,
                linewidth=2.5, markersize=8)
    
    ax.set_ylabel('Probabilidad (%)', fontsize=12)
    ax.set_title('📈 Progresión de probabilidades por ronda (Top 10)',
                 fontsize=14, fontweight='bold')
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
    ax.grid(alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'stage_progression.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"   📊 Gráfico guardado: {path}")


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║           🏆  PREDICTOR COPA DEL MUNDO FIFA 2026  🏆               ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")
    print(f"📅 Fecha de referencia: {REFERENCE_DATE.strftime('%d/%m/%Y')}")
    print(f"⚽ Equipos participantes: {len(ALL_WC_TEAMS)}")
    print(f"📊 Partidos ya jugados en WC2026: {len(WC2026_RESULTS)}")
    
    # =========================================================================
    # PASO 1: Descargar datos históricos
    # =========================================================================
    df_raw = download_historical_data()
    
    # Normalizar nombres
    df_raw['home_team'] = df_raw['home_team'].apply(normalize_name)
    df_raw['away_team'] = df_raw['away_team'].apply(normalize_name)
    df_raw['home_team_n'] = df_raw['home_team']
    df_raw['away_team_n'] = df_raw['away_team']
    
    # Limpiar
    df_raw['date'] = pd.to_datetime(df_raw['date']).dt.strftime('%Y-%m-%d')
    df_raw = df_raw.dropna(subset=['home_score', 'away_score'])
    df_raw['home_score'] = df_raw['home_score'].astype(int)
    df_raw['away_score'] = df_raw['away_score'].astype(int)
    
    print(f"\n📊 Dataset limpio: {len(df_raw):,} partidos")
    
    # =========================================================================
    # PASO 2: Calcular Elo ratings
    # =========================================================================
    print("\n📈 Calculando ratings Elo...")
    elo = EloSystem(k_base=30, home_advantage=100)
    elo.process_matches(df_raw)
    
    # Procesar también los resultados del WC2026
    for r in WC2026_RESULTS:
        elo.update(
            home_team=normalize_name(r['home']),
            away_team=normalize_name(r['away']),
            home_score=r['home_score'],
            away_score=r['away_score'],
            tournament='FIFA World Cup',
            date=r['date'],
            neutral=True
        )
    
    print("   ✅ Elo ratings calculados. Top 15 equipos del Mundial:")
    wc_elos = {normalize_name(t): elo.get_rating(normalize_name(t)) for t in ALL_WC_TEAMS}
    wc_elos_sorted = sorted(wc_elos.items(), key=lambda x: x[1], reverse=True)
    for i, (team, rating) in enumerate(wc_elos_sorted[:15]):
        print(f"      {i+1:2d}. {team:25s} → Elo: {rating:.0f}")
    
    # =========================================================================
    # PASO 3: Construir dataset de entrenamiento
    # =========================================================================
    X, y, team_features_cache = build_training_dataset(df_raw, elo)
    
    # =========================================================================
    # PASO 4: Selección de features
    # =========================================================================
    X_selected, mi_ranking, rf_importance, corr_matrix = feature_selection(X, y)
    
    # =========================================================================
    # PASO 5: Entrenar y comparar modelos
    # =========================================================================
    fitted_models, best_model_name, scaler, model_results = train_and_compare_models(
        X_selected, y
    )
    best_model = fitted_models[best_model_name]
    
    # =========================================================================
    # PASO 6: Generar visualizaciones
    # =========================================================================
    print("\n📊 Generando visualizaciones...")
    plot_feature_importance(mi_ranking, rf_importance)
    plot_correlation_matrix(corr_matrix)
    plot_model_comparison(model_results)
    
    # =========================================================================
    # PASO 7: Simulación del torneo
    # =========================================================================
    N_SIMS = 5000
    
    # Pre-computar todas las probabilidades (una sola vez)
    prob_cache = precompute_all_probabilities(
        best_model, scaler, df_raw, elo, team_features_cache
    )
    
    # Fase de grupos
    adv_counts, group_winner_counts, _ = simulate_group_stage(
        prob_cache, n_simulations=N_SIMS
    )
    
    # Determinar equipos clasificados (top por probabilidad de avanzar)
    adv_probs = {team: count / N_SIMS for team, count in adv_counts.items()}
    qualified = sorted(adv_probs.keys(), key=lambda t: adv_probs[t], reverse=True)[:32]
    
    print(f"\n   📋 32 equipos con mayor probabilidad de clasificar:")
    for i, team in enumerate(qualified):
        print(f"      {i+1:2d}. {team:25s} → {adv_probs[team]*100:.1f}%")
    
    # Fase eliminatoria
    stage_counts, n_ko_sims = simulate_knockout(
        prob_cache, qualified, n_simulations=N_SIMS
    )
    
    # =========================================================================
    # PASO 8: Resultados finales
    # =========================================================================
    print("\n" + "=" * 70)
    print("🏆 RESULTADOS FINALES — PREDICCIÓN MUNDIAL 2026")
    print("=" * 70)
    
    winner_probs = plot_tournament_predictions(stage_counts, N_SIMS)
    plot_stage_progression(stage_counts, N_SIMS)
    
    # Tabla final
    print(f"\n{'Pos':>4} {'Selección':25s} {'Prob. Campeón':>15} {'Prob. Final':>15} {'Prob. Semifinal':>15}")
    print("-" * 78)
    
    for i, (team, prob) in enumerate(winner_probs.items()):
        if i >= 20:
            break
        
        final_prob = stage_counts['final'].get(team, 0) / N_SIMS
        semi_prob = stage_counts['semi_finals'].get(team, 0) / N_SIMS
        
        medal = "🥇" if i == 0 else ("🥈" if i == 1 else ("🥉" if i == 2 else "  "))
        print(f"{medal}{i+1:2d}. {team:25s} {prob*100:>12.1f}% {final_prob*100:>12.1f}% {semi_prob*100:>12.1f}%")
    
    # Resumen del modelo
    print(f"\n📊 RESUMEN DEL MODELO")
    print(f"   • Modelo seleccionado: {best_model_name}")
    print(f"   • Features utilizadas: {X_selected.shape[1]}")
    print(f"   • Partidos de entrenamiento: {X_selected.shape[0]:,}")
    print(f"   • Simulaciones realizadas: {N_SIMS:,}")
    print(f"   • Accuracy (CV): {model_results[best_model_name]['accuracy_mean']:.4f}")
    print(f"   • F1 Macro (CV): {model_results[best_model_name]['f1_mean']:.4f}")
    
    print(f"\n📁 Gráficos guardados en: {OUTPUT_DIR}")
    print("\n✅ ¡Predicción completada!")
    
    return best_model, best_model_name, winner_probs


if __name__ == '__main__':
    best_model, best_model_name, predictions = main()
