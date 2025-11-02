import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# --- SAFE PLOTLY LAYOUT HELPER ---
def safe_update_layout(fig, title_text, xaxis_title, yaxis_title, theme, **kwargs):
    """
    Safely update Plotly figure layout with proper nested structure.
    This prevents titlefont errors by using correct Plotly syntax.
    """
    try:
        layout_dict = {
            'title': {
                'text': str(title_text),
                'font': {'size': 18, 'color': str(theme.get('primary', '#000000')), 'family': 'Orbitron'}
            },
            'xaxis': {
                'title': {'text': str(xaxis_title), 'font': {'color': str(theme.get('secondary', '#000000'))}},
                'tickfont': {'color': str(theme.get('text', '#000000'))},
                'gridcolor': str(theme.get('gridline_color', '#E0E0E0'))
            },
            'yaxis': {
                'title': {'text': str(yaxis_title), 'font': {'color': str(theme.get('secondary', '#000000'))}},
                'tickfont': {'color': str(theme.get('text', '#000000'))},
                'gridcolor': str(theme.get('gridline_color', '#E0E0E0'))
            },
            'plot_bgcolor': str(theme.get('chart_bg', 'rgba(255, 255, 255, 0.6)')),
            'paper_bgcolor': str(theme.get('paper_bg', 'rgba(255, 255, 255, 0.3)')),
            'font': {'color': str(theme.get('text', '#000000'))}
        }
        
        # Add any extra kwargs
        layout_dict.update(kwargs)
        
        fig.update_layout(**layout_dict)
    except Exception as e:
        st.warning(f"⚠️ Could not apply custom theme: {str(e)}")
    
    return fig

# --- UTILITY: HEX TO RGBA CONVERTER ---
def hex_to_rgba(hex_color, opacity=0.1):
    """Converts a 6-character hex color to an rgba string with specified opacity."""
    h = hex_color.lstrip('#')
    if len(h) == 6:
        r, g, b = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    else:
        r, g, b = (0, 0, 0)
    return f'rgba({r}, {g}, {b}, {opacity})'

# --- UTILITY: RGBA STRING TO MATPLOTLIB TUPLE ---
def rgba_string_to_mpl_tuple(rgba_string):
    """Converts a standard CSS rgba() string to a Matplotlib normalized (0-1) RGBA tuple."""
    if not isinstance(rgba_string, str) or not rgba_string.startswith('rgba('):
        return rgba_string 
    
    match = re.search(r'rgba\((\d+),\s*(\d+),\s*(\d+),\s*([0-9.]+)\)', rgba_string)
    if match:
        r = int(match.group(1)) / 255.0
        g = int(match.group(2)) / 255.0
        b = int(match.group(3)) / 255.0
        a = float(match.group(4))
        return (r, g, b, a)
    return (0.0, 0.0, 0.0, 0.0)

# --- POPULAR OTT SHOWS FOR HOMEPAGE (WITH REAL IMAGES) ---
FEATURED_SHOWS = [
    {"title": "Stranger Things", "url": "https://images.unsplash.com/photo-1594908900066-3f47337549d8?w=400&h=600&fit=crop"},
    {"title": "The Crown", "url": "https://images.unsplash.com/photo-1485846234645-a62644f84728?w=400&h=600&fit=crop"},
    {"title": "Squid Game", "url": "https://images.unsplash.com/photo-1611162617213-7d7a39e9b1d7?w=400&h=600&fit=crop"},
    {"title": "Wednesday", "url": "https://images.unsplash.com/photo-1518676590629-3dcbd9c5a5c9?w=400&h=600&fit=crop"},
    {"title": "Money Heist", "url": "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=400&h=600&fit=crop"},
    {"title": "Bridgerton", "url": "https://images.unsplash.com/photo-1519750783826-e2420f4d687f?w=400&h=600&fit=crop"},
]

# --- PLATFORM LOGOS FOR SIDEBAR/FOOTER ---
PLATFORM_LOGOS = {
    "NETFLIX": {"bg": "E50914", "text": "FFFFFF"},
    "PRIME VIDEO": {"bg": "00A8E1", "text": "FFFFFF"},
    "DISNEY+": {"bg": "01133F", "text": "FFFFFF"},
    "hbo": {"bg": "000000", "text": "FFFFFF"},
    "CRUNCHYROLL": {"bg": "F47521", "text": "FFFFFF"},
}

# --- COLOR THEME DEFINITIONS ---
COLOR_THEMES = {
    "🌿 Mint Dream (Light)": {
        "primary": "#4CAF50", "secondary": "#81C784", "accent": "#A5D6A7",
        "bg_gradient": "linear-gradient(135deg, rgba(241,248,233,0.8) 0%, rgba(232,245,233,0.8) 50%, rgba(241,248,233,0.8) 100%)",
        "chart_bg": "rgba(255, 255, 255, 0.6)", "paper_bg": "rgba(255, 255, 255, 0.3)",
        "text": "#212121", "gridline_color": "#E0E0E0"
    },
    "💜 Lavender Haze (Light)": {
        "primary": "#7986CB", "secondary": "#9FA8DA", "accent": "#C5CAE9",
        "bg_gradient": "linear-gradient(135deg, rgba(237,231,246,0.8) 0%, rgba(230,224,248,0.8) 50%, rgba(237,231,246,0.8) 100%)",
        "chart_bg": "rgba(255, 255, 255, 0.6)", "paper_bg": "rgba(255, 255, 255, 0.3)",
        "text": "#212121", "gridline_color": "#E0E0E0"
    },
    "🧡 Apricot Blush (Light)": {
        "primary": "#FFB74D", "secondary": "#FFCC80", "accent": "#FFE0B2",
        "bg_gradient": "linear-gradient(135deg, rgba(255,243,224,0.8) 0%, rgba(255,248,225,0.8) 50%, rgba(255,243,224,0.8) 100%)",
        "chart_bg": "rgba(255, 255, 255, 0.6)", "paper_bg": "rgba(255, 255, 255, 0.3)",
        "text": "#212121", "gridline_color": "#E0E0E0"
    },
    "💙 Sky Serenity (Light)": {
        "primary": "#4FC3F7", "secondary": "#81D4FA", "accent": "#B3E5FC",
        "bg_gradient": "linear-gradient(135deg, rgba(225,245,254,0.8) 0%, rgba(224,247,250,0.8) 50%, rgba(225,245,254,0.8) 100%)",
        "chart_bg": "rgba(255, 255, 255, 0.6)", "paper_bg": "rgba(255, 255, 255, 0.3)",
        "text": "#212121", "gridline_color": "#E0E0E0"
    },
    "N» Netflix (Light)": {
        "primary": "#E50914", "secondary": "#221f1f", "accent": "#B81D24",
        "bg_gradient": "linear-gradient(135deg, rgba(250,250,250,0.8) 0%, rgba(240,240,240,0.8) 50%, rgba(250,250,250,0.8) 100%)",
        "chart_bg": "rgba(255, 255, 255, 0.6)", "paper_bg": "rgba(255, 255, 255, 0.3)",
        "text": "#212121", "gridline_color": "#E0E0E0"
    },
    "G» Google Looker (Light)": {
        "primary": "#4285F4", "secondary": "#34A853", "accent": "#FBBC05",
        "bg_gradient": "linear-gradient(135deg, rgba(255,255,255,0.8) 0%, rgba(248,249,250,0.8) 50%, rgba(255,255,255,0.8) 100%)",
        "chart_bg": "rgba(255, 255, 255, 0.6)", "paper_bg": "rgba(255, 255, 255, 0.3)",
        "text": "#212121", "gridline_color": "#E0E0E0"
    },
    "T» Tableau (Light)": {
        "primary": "#1F77B4", "secondary": "#FF7F0E", "accent": "#2CA02C",
        "bg_gradient": "linear-gradient(135deg, rgba(255,255,255,0.8) 0%, rgba(245,245,245,0.8) 50%, rgba(255,255,255,0.8) 100%)",
        "chart_bg": "rgba(255, 255, 255, 0.6)", "paper_bg": "rgba(255, 255, 255, 0.3)",
        "text": "#212121", "gridline_color": "#DCDCDC"
    },
    "🔵 Cyberpunk Blue (Dark)": {
        "primary": "#00f5ff", "secondary": "#00a8ff", "accent": "#0077ff",
        "bg_gradient": "linear-gradient(135deg, rgba(10,14,39,0.85) 0%, rgba(26,29,58,0.85) 50%, rgba(15,17,35,0.85) 100%)",
        "chart_bg": "rgba(10, 14, 39, 0.6)", "paper_bg": "rgba(10, 14, 39, 0.3)",
        "text": "#a0d8f1", "gridline_color": "rgba(0, 245, 255, 0.1)"
    },
    "🟣 Neon Purple (Dark)": {
        "primary": "#bf00ff", "secondary": "#8800ff", "accent": "#ff00ff",
        "bg_gradient": "linear-gradient(135deg, rgba(26,0,51,0.85) 0%, rgba(45,0,77,0.85) 50%, rgba(26,0,51,0.85) 100%)",
        "chart_bg": "rgba(42, 0, 77, 0.6)", "paper_bg": "rgba(26, 0, 51, 0.3)",
        "text": "#e0b3ff", "gridline_color": "rgba(191, 0, 255, 0.1)"
    },
    "🧬 Cyberpunk Mix (Dark)": {
        "primary": "#FF00FF", "secondary": "#00FFFF", "accent": "#FFFF00",
        "bg_gradient": "linear-gradient(135deg, rgba(20,0,30,0.85) 0%, rgba(40,0,50,0.85) 50%, rgba(20,0,30,0.85) 100%)",
        "chart_bg": "rgba(30, 0, 40, 0.6)", "paper_bg": "rgba(50, 0, 60, 0.3)",
        "text": "#F0F0F0", "gridline_color": "rgba(255, 0, 255, 0.1)"
    },
    "🟢 Matrix Green (Dark)": {
        "primary": "#00ff41", "secondary": "#00cc33", "accent": "#39ff14",
        "bg_gradient": "linear-gradient(135deg, rgba(0,26,13,0.85) 0%, rgba(0,51,25,0.85) 50%, rgba(0,26,13,0.85) 100%)",
        "chart_bg": "rgba(0, 51, 25, 0.6)", "paper_bg": "rgba(0, 26, 13, 0.3)",
        "text": "#b3ffcc", "gridline_color": "rgba(0, 255, 65, 0.1)"
    },
    "🔴 Netflix Red (Dark)": {
        "primary": "#E50914", "secondary": "#B20710", "accent": "#831010",
        "bg_gradient": "linear-gradient(135deg, rgba(15,1,1,0.85) 0%, rgba(26,2,2,0.85) 50%, rgba(15,1,1,0.85) 100%)",
        "chart_bg": "rgba(51, 5, 5, 0.6)", "paper_bg": "rgba(26, 2, 2, 0.3)",
        "text": "#ffb3b3", "gridline_color": "rgba(229, 9, 20, 0.1)"
    },
    "🟠 Sunset Orange (Dark)": {
        "primary": "#ff6b35", "secondary": "#ff8c42", "accent": "#ffa600",
        "bg_gradient": "linear-gradient(135deg, rgba(26,15,0,0.85) 0%, rgba(51,31,0,0.85) 50%, rgba(26,15,0,0.85) 100%)",
        "chart_bg": "rgba(51, 31, 0, 0.6)", "paper_bg": "rgba(26, 15, 0, 0.3)",
        "text": "#ffd6b3", "gridline_color": "rgba(255, 107, 53, 0.1)"
    },
    "🩵 Ice Blue (Dark)": {
        "primary": "#5dfdcb", "secondary": "#7cc6fe", "accent": "#96efff",
        "bg_gradient": "linear-gradient(135deg, rgba(0,26,31,0.85) 0%, rgba(0,51,68,0.85) 50%, rgba(0,26,31,0.85) 100%)",
        "chart_bg": "rgba(0, 51, 68, 0.6)", "paper_bg": "rgba(0, 26, 31, 0.3)",
        "text": "#c8f4f9", "gridline_color": "rgba(93, 253, 203, 0.1)"
    },
    "💛 Golden Hour (Dark)": {
        "primary": "#FFD700", "secondary": "#FFA500", "accent": "#FF8C00",
        "bg_gradient": "linear-gradient(135deg, rgba(26,20,0,0.85) 0%, rgba(51,40,0,0.85) 50%, rgba(26,20,0,0.85) 100%)",
        "chart_bg": "rgba(51, 40, 0, 0.6)", "paper_bg": "rgba(26, 20, 0, 0.3)",
        "text": "#ffe6b3", "gridline_color": "rgba(255, 215, 0, 0.1)"
    },
    "💗 Rose Pink (Dark)": {
        "primary": "#ff1493", "secondary": "#ff69b4", "accent": "#ff85c1",
        "bg_gradient": "linear-gradient(135deg, rgba(26,0,16,0.85) 0%, rgba(51,0,32,0.85) 50%, rgba(26,0,16,0.85) 100%)",
        "chart_bg": "rgba(51, 0, 32, 0.6)", "paper_bg": "rgba(26, 0, 16, 0.3)",
        "text": "#ffb3de", "gridline_color": "rgba(255, 20, 147, 0.1)"
    }
}

# --- DYNAMIC CSS GENERATOR ---
def generate_theme_css(theme):
    text_on_primary = "#212121" if theme["text"] == "#212121" else "#FFFFFF"

    if theme["text"] == "#212121":
        header_style = f"""
        h1, h2, h3 {{
            font-family: 'Orbitron', sans-serif !important;
            color: {theme["text"]};
            text-shadow: 0 0 5px {hex_to_rgba(theme["primary"], 0.3)};
            letter-spacing: 2px;
        }}
        """
    else:
        header_style = f"""
        h1, h2, h3 {{
            font-family: 'Orbitron', sans-serif !important;
            background: linear-gradient(90deg, {theme["primary"]}, {theme["secondary"]}, {theme["accent"]});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 30px {hex_to_rgba(theme["primary"], 0.5)};
            letter-spacing: 2px;
            color: {theme["text"]};
        }}
        """

    return f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;500;600;700&display=swap');
        
        .stApp {{
            background-image: {theme["bg_gradient"]}, url("https://images.unsplash.com/photo-1574267432644-f65b5fe8fb11?w=1920&h=1080&fit=crop");
            background-size: cover;
            background-attachment: fixed;
            background-position: center center;
            font-family: 'Rajdhani', sans-serif;
            color: {theme["text"]};
        }}
        
        {header_style}
        
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
            background: {theme["paper_bg"]};
            padding: 10px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            border: 1px solid {hex_to_rgba(theme["primary"], 0.2)};
        }}
        
        .stTabs [data-baseweb="tab"] {{
            background: linear-gradient(135deg, {hex_to_rgba(theme["accent"], 0.1)}, {hex_to_rgba(theme["secondary"], 0.1)});
            border-radius: 10px;
            color: {theme["primary"]};
            font-family: 'Orbitron', sans-serif;
            font-weight: 600;
            border: 1px solid {hex_to_rgba(theme["primary"], 0.3)};
            padding: 12px 24px;
            transition: all 0.3s ease;
        }}
        
        .stTabs [data-baseweb="tab"]:hover {{
            background: linear-gradient(135deg, {hex_to_rgba(theme["accent"], 0.3)}, {hex_to_rgba(theme["secondary"], 0.3)});
            border-color: {theme["primary"]};
            box-shadow: 0 0 20px {hex_to_rgba(theme["primary"], 0.6)};
            transform: translateY(-2px);
        }}
        
        .stTabs [aria-selected="true"] {{
            background: linear-gradient(135deg, {theme["accent"]}, {theme["secondary"]}) !important;
            box-shadow: 0 0 30px {hex_to_rgba(theme["primary"], 0.8)}, inset 0 0 20px rgba(255, 255, 255, 0.1);
            border-color: {theme["primary"]} !important;
            color: {text_on_primary} !important;
        }}
        
        .stTabs [aria-selected="true"] p {{
            color: {text_on_primary} !important; 
        }}
        
        .stSlider > div > div > div {{
            background: linear-gradient(90deg, {theme["accent"]}, {theme["primary"]});
        }}
        
        .stSlider > div > div > div > div {{
            background-color: {theme["primary"]};
            box-shadow: 0 0 15px {hex_to_rgba(theme["primary"], 0.8)};
        }}
        
        .stSelectbox > div > div {{
            background: {theme["paper_bg"]};
            border: 2px solid {hex_to_rgba(theme["primary"], 0.4)};
            border-radius: 10px;
            color: {theme["primary"]};
            font-family: 'Rajdhani', sans-serif;
            font-weight: 500;
        }}
        
        [data-testid="stMetricValue"] {{
            font-family: 'Orbitron', sans-serif;
            font-size: 2.5rem;
            background: linear-gradient(90deg, {theme["primary"]}, {theme["secondary"]});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 20px {hex_to_rgba(theme["primary"], 0.5)};
        }}
        
        [data-testid="stMetricLabel"] {{
            font-family: 'Rajdhani', sans-serif;
            color: {theme["text"]};
            font-size: 1.1rem;
            font-weight: 600;
            letter-spacing: 1px;
        }}
        
        .stAlert {{
            background: {hex_to_rgba(theme["accent"], 0.1)};
            border-left: 4px solid {theme["primary"]};
            border-radius: 10px;
            backdrop-filter: blur(10px);
        }}
        
        .streamlit-expanderHeader {{
            background: linear-gradient(135deg, {hex_to_rgba(theme["accent"], 0.2)}, {hex_to_rgba(theme["secondary"], 0.2)});
            border: 1px solid {hex_to_rgba(theme["primary"], 0.3)};
            border-radius: 10px;
            color: {theme["primary"]};
            font-family: 'Orbitron', sans-serif;
        }}
        
        .stRadio > label {{
            color: {theme["text"]};
            font-family: 'Rajdhani', sans-serif;
            font-weight: 600;
        }}
        
        [data-testid="stSidebar"] {{
            background-image: {theme["bg_gradient"]}, url("https://images.unsplash.com/photo-1574267432644-f65b5fe8fb11?w=1920&h=1080&fit=crop");
            background-size: cover;
            background-position: center center;
            border-right: 2px solid {hex_to_rgba(theme["primary"], 0.3)};
        }}
        
        .stMarkdown {{
            color: {theme["text"]};
            font-size: 1.05rem;
        }}
        
        [data-testid="stDataFrame"] {{
            border: 1px solid {hex_to_rgba(theme["primary"], 0.3)};
            border-radius: 10px;
        }}
        
        .stButton > button {{
            background: linear-gradient(135deg, {theme["accent"]}, {theme["secondary"]});
            color: {text_on_primary};
            border: 2px solid {theme["primary"]};
            border-radius: 10px;
            font-family: 'Orbitron', sans-serif;
            font-weight: 700;
            padding: 12px 30px;
            box-shadow: 0 0 20px {hex_to_rgba(theme["primary"], 0.5)};
            transition: all 0.3s ease;
        }}
        
        .stButton > button:hover {{
            box-shadow: 0 0 30px {hex_to_rgba(theme["primary"], 0.9)};
            transform: translateY(-3px);
            border-color: {theme["primary"]};
        }}
        
        .stMultiSelect > div > div {{
            background: {theme["paper_bg"]};
            border: 2px solid {hex_to_rgba(theme["primary"], 0.4)};
            border-radius: 10px;
        }}
        
        .stCheckbox > label {{
            color: {theme["text"]};
        }}
        
        .show-card {{
            border-radius: 10px;
            overflow: hidden;
            transition: all 0.3s ease-out;
            border: 2px solid {hex_to_rgba(theme["primary"], 0.3)};
            box-shadow: 0 5px 15px {hex_to_rgba(theme["primary"], 0.2)};
            background: {theme["chart_bg"]};
        }}
        
        .show-card:hover {{
            transform: scale(1.05) translateY(-5px);
            box-shadow: 0 10px 30px {hex_to_rgba(theme["primary"], 0.5)};
            border-color: {theme["primary"]};
        }}
        
        @keyframes glow {{
            from {{ text-shadow: 0 0 20px {hex_to_rgba(theme["primary"], 0.5)}; }}
            to {{ text-shadow: 0 0 40px {hex_to_rgba(theme["primary"], 0.8)}; }}
        }}
    </style>
    """

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Strategic OTT Content Analysis Dashboard",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- SESSION STATE ---
if 'page' not in st.session_state:
    st.session_state.page = 'home'

# --- DATA LOADING ---
@st.cache_data
def load_netflix_data():
    try:
        df = pd.read_csv('netflix_titles (1).csv')
        df['country'] = df['country'].fillna('Unknown')
        df['is_us'] = df['country'].apply(lambda x: 'United States' in x)
        
        def get_primary_country(country_str):
            if pd.isna(country_str): return 'Unknown'
            return str(country_str).split(',')[0].strip()

        df['origin_country'] = df['country'].apply(get_primary_country)
        df['release_year'] = pd.to_numeric(df['release_year'], errors='coerce')
        df = df.dropna(subset=['release_year'])
        df['release_year'] = df['release_year'].astype(int)
        df['period'] = df['release_year'].apply(lambda x: 'After 2015' if x > 2015 else 'Before/On 2015')
        df['runtime_min'] = df[df['type'] == 'Movie']['duration'].str.replace(' min', '', regex=False).astype(float)
        df['num_seasons'] = df[df['type'] == 'TV Show']['duration'].str.replace(' Seasons', '', regex=False).str.replace(' Season', '', regex=False).astype(float)
        
        return df
    except FileNotFoundError:
        st.error("Error: 'netflix_titles (1).csv' not found.")
        return pd.DataFrame()

@st.cache_data
def load_platform_comparison_data():
    platform_dfs = []
    
    def load_standard_platform(filename, platform_name, country_col='country'):
        try:
            df = pd.read_csv(filename)
            df['platform'] = platform_name
            if country_col != 'country':
                df = df.rename(columns={country_col: 'country'})
            if 'type' not in df.columns:
                 df['type'] = 'Unknown' 
            if country_col == 'production_countries':
                 df['country'] = df['country'].apply(lambda x: re.sub(r"[\[\]']", "", str(x)).split(',')[0])
            if platform_name == 'Disney+' and 'year' in df.columns:
                df = df.rename(columns={'year': 'release_year'})
            
            required_cols = ['title', 'release_year', 'country', 'platform', 'type']
            if not all(col in df.columns for col in required_cols): return pd.DataFrame()
            return df[required_cols]
        except FileNotFoundError:
            st.warning(f"Could not find '{filename}'.")
            return pd.DataFrame()

    platform_dfs.append(load_standard_platform('netflix_titles (1).csv', 'Netflix'))
    platform_dfs.append(load_standard_platform('amazon_prime_titles.csv', 'Amazon Prime'))
    platform_dfs.append(load_standard_platform('disney_plus_shows.csv', 'Disney+', country_col='country'))
    platform_dfs.append(load_standard_platform('apple_tv_titles.csv', 'Apple TV', country_col='production_countries'))
    platform_dfs.append(load_standard_platform('crunchyroll_titles.csv', 'Crunchyroll', country_col='production_countries'))
    platform_dfs.append(load_standard_platform('hbo_titles.csv', 'HBO', country_col='production_countries'))

    platform_dfs = [df for df in platform_dfs if not df.empty]
    if not platform_dfs: return pd.DataFrame()
    
    all_platforms = pd.concat(platform_dfs, ignore_index=True)
    all_platforms['country'] = all_platforms['country'].fillna('Unknown')
    us_aliases = ['US', 'United States']
    all_platforms['is_local'] = ~all_platforms['country'].apply(lambda x: any(alias in str(x) for alias in us_aliases))
    
    all_platforms['release_year'] = pd.to_numeric(all_platforms['release_year'], errors='coerce')
    all_platforms = all_platforms.dropna(subset=['release_year'])
    all_platforms['release_year'] = all_platforms['release_year'].astype(int)
    
    return all_platforms

# --- HOMEPAGE ---
def render_homepage(theme):
    st.markdown(f"""
        <div style='text-align: center; padding: 50px 20px; background: {theme["chart_bg"]}; border-radius: 20px; border: 3px solid {theme["primary"]}; margin-bottom: 40px; box-shadow: 0 0 50px {hex_to_rgba(theme["primary"], 0.3)};'>
            <h1 style='font-family: Orbitron; font-size: 4.5rem; background: linear-gradient(90deg, {theme["primary"]}, {theme["secondary"]}, {theme["accent"]}); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0; animation: glow 2s ease-in-out infinite alternate;'>
                🎬 OTT PLATFORM ANALYTICS HUB 🎬
            </h1>
            <p style='color: {theme["text"]}; font-size: 1.8rem; font-family: Rajdhani; letter-spacing: 4px; margin-top: 20px; font-weight: 600;'>
                STRATEGIC OTT CONTENT INTELLIGENCE PLATFORM
            </p>
            <p style='color: {theme["text"]}; font-size: 1.2rem; font-family: Rajdhani; margin-top: 15px; opacity: 0.8;'>
                Unlock data-driven insights across global streaming platforms
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"<h2 style='text-align: center; font-family: Orbitron; margin-top: 40px; margin-bottom: 30px;'>🌟 Featured Content 🌟</h2>", unsafe_allow_html=True)
    
    cols = st.columns(3)
    for idx, show in enumerate(FEATURED_SHOWS[:6]):
        with cols[idx % 3]:
            st.markdown(f"""
                <div class='show-card'>
                    <img src='{show["url"]}' style='width: 100%; height: 400px; object-fit: cover;' />
                    <div style='padding: 15px; background: {theme["paper_bg"]}; text-align: center;'>
                        <h4 style='color: {theme["text"]}; font-family: Orbitron; margin: 0;'>{show["title"]}</h4>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown(f"<h2 style='text-align: center; font-family: Orbitron; margin-top: 40px; margin-bottom: 30px;'>📊 Platform Features</h2>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    features = [
        {"icon": "🌐", "title": "Multi-Platform", "desc": "Analyze data across Netflix, Prime, Disney+ & more"},
        {"icon": "📈", "title": "Real-Time Stats", "desc": "Dynamic visualizations with live filtering"},
        {"icon": "🎨", "title": "Custom Themes", "desc": "10+ stunning color themes to choose from"},
        {"icon": "🌍", "title": "Global Insights", "desc": "International content trends & analytics"}
    ]
    
    for col, feature in zip([col1, col2, col3, col4], features):
        with col:
            st.markdown(f"""
                <div style='text-align: center; padding: 30px; background: {theme["chart_bg"]}; border-radius: 15px; border: 2px solid {theme["primary"]}; height: 250px;'>
                    <div style='font-size: 3rem; margin-bottom: 15px;'>{feature["icon"]}</div>
                    <h3 style='font-family: Orbitron; font-size: 1.2rem;'>{feature["title"]}</h3>
                    <p style='color: {theme["text"]}; font-size: 0.95rem;'>{feature["desc"]}</p>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 LAUNCH DASHBOARD", use_container_width=True, type="primary"):
            st.session_state.page = 'dashboard'
            st.rerun()

# --- HYPOTHESIS 1: LOCAL LANGUAGE ---
def render_H1_local_language(df, theme):
    st.header("🌍 Hypothesis 1: Local-Language Representation")
    
    # Safe theme value retrieval with defaults - ensure hex colors for compatibility
    def ensure_valid_color(color_value, default):
        """Ensure color is valid for Plotly (hex or rgba format)"""
        if not color_value:
            return default
        color_str = str(color_value)
        # If it's rgba format, keep it
        if color_str.startswith('rgba(') or color_str.startswith('rgb('):
            return color_str
        # If it's hex, ensure it has #
        if not color_str.startswith('#'):
            return f"#{color_str}"
        return color_str
    
    grid_color = ensure_valid_color(theme.get("gridline_color"), "#E0E0E0")
    primary_color = ensure_valid_color(theme.get("primary"), "#4CAF50")
    secondary_color = ensure_valid_color(theme.get("secondary"), "#81C784")
    text_color = ensure_valid_color(theme.get("text"), "#212121")
    chart_bg = ensure_valid_color(theme.get("chart_bg"), "rgba(255, 255, 255, 0.6)")
    paper_bg = ensure_valid_color(theme.get("paper_bg"), "rgba(255, 255, 255, 0.3)")

    with st.sidebar:
        st.markdown("### 🎛️ CONTROL PANEL (H1)")
        st.markdown("---")
        
        min_year = int(df['release_year'].min())
        max_year = int(df['release_year'].max())
        
        year_range = st.slider(
            "📅 Release Year Range",
            min_value=min_year,
            max_value=max_year,
            value=(2010, max_year),
            step=1,
            key='h1_year_range',
            help="Filter content by release year to analyze temporal trends"
        )
        
        all_platforms = sorted(df['platform'].unique())
        selected_platforms = st.multiselect(
            "🎬 Select Platforms",
            options=all_platforms,
            default=all_platforms,
            key='h1_platforms',
            help="Choose which platforms to include in the analysis"
        )
        
        view_mode = st.radio(
            "📊 Visualization Mode",
            ["Absolute Values", "Percentage View"],
            key='h1_view_mode',
            help="Toggle between raw counts and percentage distribution"
        )
        
        trend_type = st.selectbox(
            "📈 Trend Chart Type",
            ["Line Chart", "Area Chart", "Scatter Plot"],
            key='h1_trend_type',
            help="Select visualization style for temporal trends"
        )
    
    df_filtered = df[
        (df['release_year'].between(year_range[0], year_range[1])) &
        (df['platform'].isin(selected_platforms))
    ]
    
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    
    with col_m1:
        total_titles = len(df_filtered)
        st.metric("🎞️ Total Titles Analyzed", f"{total_titles:,}", 
                     help="Total number of titles in selected range")
    
    with col_m2:
        local_ratio = (df_filtered['is_local'].sum() / len(df_filtered) * 100) if len(df_filtered) > 0 else 0
        st.metric("🌍 Global Content Ratio", f"{local_ratio:.1f}%",
                     help="Percentage of non-U.S. content across all platforms")
    
    with col_m3:
        platform_count = df_filtered['platform'].nunique()
        st.metric("📺 Active Platforms", platform_count,
                     help="Number of platforms in current selection")
    
    with col_m4:
        year_span = year_range[1] - year_range[0] + 1
        st.metric("⏱️ Year Span", f"{year_span} years",
                     help="Time range of analysis")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        ratio_df = df_filtered.groupby('platform')['is_local'].agg(['mean', 'sum', 'count']).reset_index()
        ratio_df['local_ratio'] = ratio_df['mean'] * 100
        ratio_df = ratio_df.sort_values('local_ratio', ascending=False)
        
        fig_ratio = go.Figure()
        
        # Use a safe color for line - avoid rgba for marker borders
        safe_line_color = primary_color if primary_color.startswith('#') else '#4CAF50'
        
        fig_ratio.add_trace(go.Bar(
            x=ratio_df['platform'],
            y=ratio_df['local_ratio'],
            text=ratio_df['local_ratio'].round(1),
            texttemplate='%{text}%',
            textposition='outside',
            marker={
                'color': ratio_df['local_ratio'].tolist(),
                'colorscale': 'Turbo',
                'line': {'color': safe_line_color, 'width': 2},
                'colorbar': {
                    'title': "Local %",
                    'thickness': 15,
                    'len': 0.7,
                    'tickfont': {'color': safe_line_color}
                }
            },
            hovertemplate='<b>%{x}</b><br>Local Content: %{y:.1f}%<br>Total: %{customdata} titles<extra></extra>',
            customdata=ratio_df['count'].tolist()
        ))
        
        safe_update_layout(
            fig_ratio,
            title_text="🌍 Local Content Distribution by Platform",
            xaxis_title="Platform",
            yaxis_title="Local Content Ratio (%)",
            theme=theme,
            hovermode='x unified',
            showlegend=False
        )
        
        st.plotly_chart(fig_ratio, use_container_width=True)

    with col2:
        trend_agg = df_filtered.groupby(['platform', 'release_year'])['is_local'].mean().reset_index()
        trend_agg['local_ratio'] = trend_agg['is_local'] * 100
        
        try:
            if trend_type == "Line Chart":
                fig_trend = go.Figure()
                for platform in selected_platforms:
                    platform_data = trend_agg[trend_agg['platform'] == platform]
                    fig_trend.add_trace(go.Scatter(
                        x=platform_data['release_year'],
                        y=platform_data['local_ratio'],
                        name=platform,
                        mode='lines+markers',
                        line=dict(width=3),
                        marker=dict(size=8, line=dict(width=2, color='white')),
                        hovertemplate='<b>%{fullData.name}</b><br>Year: %{x}<br>Local: %{y:.1f}%<extra></extra>'
                    ))
                
                # Apply layout using safe helper
                safe_update_layout(
                    fig_trend,
                    title_text=f"📈 Localization Evolution ({year_range[0]}-{year_range[1]})",
                    xaxis_title="Release Year",
                    yaxis_title="Local Content Ratio (%)",
                    theme=theme,
                    hovermode='x unified',
                    legend={
                        'title': {'text': "Platform", 'font': {'color': str(theme.get('primary', '#000000'))}},
                        'font': {'color': str(theme.get('text', '#000000'))},
                        'bgcolor': str(theme.get('chart_bg', 'rgba(255, 255, 255, 0.6)')),
                        'bordercolor': str(theme.get('primary', '#000000')),
                        'borderwidth': 1
                    }
                )
                
            elif trend_type == "Area Chart":
                fig_trend = px.area(
                    trend_agg,
                    x="release_year",
                    y="local_ratio",
                    color="platform",
                    title=f"📈 Localization Trend ({year_range[0]}-{year_range[1]})"
                )
                
                # Apply simplified layout for Area Chart
                fig_trend.update_layout(
                    plot_bgcolor=chart_bg,
                    paper_bgcolor=paper_bg,
                    font={'color': text_color},
                    xaxis={'gridcolor': grid_color},
                    yaxis={'gridcolor': grid_color}
                )
                
            else:  # Scatter Plot
                fig_trend = px.scatter(
                    trend_agg,
                    x="release_year",
                    y="local_ratio",
                    color="platform",
                    size="local_ratio",
                    title=f"📈 Localization Trend ({year_range[0]}-{year_range[1]})"
                )
                
                # Apply simplified layout for Scatter Plot
                fig_trend.update_layout(
                    plot_bgcolor=chart_bg,
                    paper_bgcolor=paper_bg,
                    font={'color': text_color},
                    xaxis={'gridcolor': grid_color},
                    yaxis={'gridcolor': grid_color}
                )
            
            st.plotly_chart(fig_trend, use_container_width=True)
            
        except Exception as e:
            st.error(f"⚠️ Error creating trend visualization: {str(e)}")
            st.info("Please try selecting a different chart type from the sidebar.")
    
    with st.expander("🔍 Advanced Analytics & Insights (H1)"):
        col_a1, col_a2 = st.columns(2)
        
        with col_a1:
            st.markdown("#### 📊 Platform Comparison Matrix")
            comparison_df = df_filtered.groupby('platform').agg({
                'is_local': ['mean', 'sum', 'count']
            }).round(3)
            comparison_df.columns = ['Local Ratio', 'Local Count', 'Total Count']
            comparison_df['Local Ratio'] = (comparison_df['Local Ratio'] * 100).round(1)
            st.dataframe(comparison_df, use_container_width=True)
        
        with col_a2:
            st.markdown("#### 📈 Year-over-Year Growth Rate (Local Content Ratio)")
            if len(trend_agg) > 0:
                pivot_df = trend_agg.pivot(index='release_year', columns='platform', values='local_ratio')
                growth_rate = pivot_df.pct_change() * 100
                st.dataframe(growth_rate.tail(5).round(2), use_container_width=True)

# --- HYPOTHESIS 2: RECENCY ---
def render_H2_recency(df, theme):
    st.header("⏰ Hypothesis 2: Content Recency Analysis")
    
    grid_color = theme.get("gridline_color", "#E0E0E0")

    with st.sidebar:
        st.markdown("### ⚙️ RECENCY CONTROLS (H2)")
        st.markdown("---")
        
        year_cutoff = st.select_slider(
            "📆 Recency Cutoff Year",
            options=list(range(2005, 2023)),
            value=2015,
            key='h2_year_cutoff',
            help="Define the threshold between 'recent' and 'older' content"
        )
        
        content_type_filter = st.radio(
            "🎭 Content Type",
            ["All Content", "Movies Only", "TV Shows Only"],
            key='h2_content_type',
            help="Filter by content type"
        )
        
        show_statistics = st.checkbox("📊 Show Statistical Summary", value=True, key='h2_show_stats')
    
    df_filtered = df.copy()
    if content_type_filter == "Movies Only":
        df_filtered = df_filtered[df_filtered['type'] == 'Movie']
    elif content_type_filter == "TV Shows Only":
        df_filtered = df_filtered[df_filtered['type'] == 'TV Show']
    
    df_filtered['interactive_period'] = df_filtered['release_year'].apply(
        lambda x: f'After {year_cutoff}' if x > year_cutoff else f'Before/On {year_cutoff}'
    )
    
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    
    recent_count = len(df_filtered[df_filtered['release_year'] > year_cutoff])
    older_count = len(df_filtered[df_filtered['release_year'] <= year_cutoff])
    recent_pct = (recent_count / len(df_filtered) * 100) if len(df_filtered) > 0 else 0
    
    with col_m1:
        st.metric("🆕 Recent Content", f"{recent_count:,}", 
                     f"{recent_pct:.1f}% of catalog")
    
    with col_m2:
        st.metric("📼 Older Content", f"{older_count:,}",
                     f"{100-recent_pct:.1f}% of catalog")
    
    with col_m3:
        median_year = int(df_filtered['release_year'].median()) if not df_filtered.empty else 'N/A'
        st.metric("📅 Median Release Year", median_year)
    
    with col_m4:
        avg_year = int(df_filtered['release_year'].mean()) if not df_filtered.empty else 'N/A'
        st.metric("🗓️ Average Release Year", avg_year)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)

    with col1:
        df_hist = df_filtered[df_filtered['release_year'] > 1920]
        
        fig_hist = go.Figure()
        
        hist_data = df_hist.groupby('release_year').size().reset_index(name='count')
        
        colors = [theme["accent"] if year > year_cutoff else theme["text"]
                  for year in hist_data['release_year']]
        
        fig_hist.add_trace(go.Bar(
            x=hist_data['release_year'],
            y=hist_data['count'],
            marker=dict(
                color=colors,
                line=dict(color=theme["primary"], width=1)
            ),
            hovertemplate='<b>Year: %{x}</b><br>Titles: %{y}<extra></extra>'
        ))
        
        fig_hist.add_vline(
            x=year_cutoff,
            line_dash="dash",
            line_color=theme["primary"],
            line_width=3,
            annotation_text=f"Cutoff: {year_cutoff}",
            annotation_position="top",
            annotation_font_color=theme["primary"]
        )
        
        safe_update_layout(
            fig_hist,
            title_text="📊 Netflix Content Volume Timeline",
            xaxis_title="Release Year",
            yaxis_title="Number of Titles",
            theme=theme,
            bargap=0.05,
            showlegend=False
        )
        
        st.plotly_chart(fig_hist, use_container_width=True)

    with col2:
        st.subheader("Content Type Production Over Time (Swimlane)")
        
        df_swim = df_filtered[df_filtered['release_year'] > 2000]
        
        df_stacked = df_swim.groupby(['release_year', 'type']).size().reset_index(name='count')

        fig_area = px.area(
            df_stacked,
            x="release_year",
            y="count",
            color="type",
            title=f"Content Production Swimlane (Post-2000)",
            labels={"release_year": "Release Year", "count": "Number of Titles Added", "type": "Content Type"},
            color_discrete_map={
                "Movie": theme["primary"],
                "TV Show": theme["secondary"]
            }
        )
        
        safe_update_layout(
            fig_area,
            title_text=f"📈 Content Production Swimlane (Post-2000)",
            xaxis_title="Release Year",
            yaxis_title="Number of Titles Added",
            theme=theme,
            hovermode='x unified',
            legend={
                'font': {'color': str(theme.get('text', '#000000')), 'size': 12},
                'bgcolor': str(theme.get('chart_bg', 'rgba(255, 255, 255, 0.6)')),
                'bordercolor': str(theme.get('primary', '#000000')),
                'borderwidth': 1
            }
        )
        
        st.plotly_chart(fig_area, use_container_width=True)
    
    if show_statistics:
        with st.expander("📈 Statistical Analysis (H2)"):
            col_s1, col_s2, col_s3 = st.columns(3)
            
            if not df_filtered.empty:
                with col_s1:
                    st.markdown("#### 📊 Distribution Stats")
                    st.write(f"**Std Deviation:** {df_filtered['release_year'].std():.2f} years")
                    st.write(f"**Range:** {df_filtered['release_year'].max() - df_filtered['release_year'].min()} years")
                    st.write(f"**Mode:** {df_filtered['release_year'].mode()[0]}")
                
                with col_s2:
                    st.markdown("#### 📉 Quartile Analysis")
                    q1 = df_filtered['release_year'].quantile(0.25)
                    q2 = df_filtered['release_year'].quantile(0.50)
                    q3 = df_filtered['release_year'].quantile(0.75)
                    st.write(f"**Q1 (25%):** {int(q1)}")
                    st.write(f"**Q2 (50%):** {int(q2)}")
                    st.write(f"**Q3 (75%):** {int(q3)}")
                
                with col_s3:
                    st.markdown("#### ⭐ Recency Score")
                    recency_score = (recent_count / len(df_filtered) * 100) if len(df_filtered) > 0 else 0
                    st.write(f"**Score:** {recency_score:.1f}%")

# --- HYPOTHESIS 3: INTERNATIONAL GROWTH ---
def render_H3_international_growth(df, theme):
    st.header("🌎 Hypothesis 3: International Content Sourcing")
    
    with st.sidebar:
        st.markdown("### 🗺️ GEOGRAPHY CONTROLS (H3)")
        st.markdown("---")
        
        min_content_count = st.slider(
            "🎯 Minimum Map Title Count",
            min_value=1,
            max_value=100,
            value=15,
            step=5,
            key='h3_min_count',
            help="Only countries meeting this title count will be shaded on the map."
        )
        
        treemap_level = st.selectbox(
            "🎬 Treemap Focus",
            ["Top 10 Countries", "Top 50 Countries"],
            key='h3_treemap_level',
            help="Limit the treemap to the most prolific non-US countries."
        )
        
        content_type = st.radio(
            "📺 Content Type Filter",
            ["All", "Movie", "TV Show"],
            key='h3_type_filter'
        )
        
    df_non_us = df[df['is_us'] == False].copy()
    if content_type != "All":
        df_non_us = df_non_us[df_non_us['type'] == content_type]

    if df_non_us.empty:
        st.warning("⚠️ No non-U.S. content found for the selected type.")
        return

    col_m1, col_m2, col_m3 = st.columns(3)

    total_non_us = len(df_non_us)
    total_countries = df_non_us['origin_country'].nunique()

    with col_m1:
        st.metric("🎥 Total Non-U.S. Titles", f"{total_non_us:,}", help=f"Total {content_type} titles sourced from outside the US.")
    
    with col_m2:
        st.metric("🌍 Origin Countries", total_countries, help="Total number of unique countries providing non-US content.")

    with col_m3:
        top_country = df_non_us['origin_country'].mode()[0] if not df_non_us.empty else 'N/A'
        st.metric("🏆 Most Prolific Country", top_country, help="Primary non-US country source.")

    st.markdown("---")
    
    st.subheader(f"🗺️ Global Sourcing Map (Titles ≥ {min_content_count})")
    
    country_counts = df_non_us['origin_country'].value_counts().reset_index()
    country_counts.columns = ['Country', 'Count']
    
    country_counts = country_counts[country_counts['Country'] != 'Unknown']
    country_counts = country_counts[country_counts['Count'] >= min_content_count]
    
    fig_map = px.choropleth(
        country_counts, 
        locations='Country',
        locationmode='country names',
        color='Count',
        hover_name='Country',
        color_continuous_scale=px.colors.sequential.Sunsetdark,
        title='🌍 Volume of Content by Primary Non-U.S. Origin Country',
        template='plotly_dark'
    )
    fig_map.update_geos(
        showland=True, 
        landcolor=theme["chart_bg"], 
        showocean=True, 
        oceancolor=theme["paper_bg"],
        showcountries=True,
        countrycolor=theme["primary"]
    )
    fig_map.update_layout(
        title_font=dict(color=theme["primary"], family='Orbitron', size=18),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor=theme["paper_bg"],
        font=dict(color=theme["text"]),
        coloraxis_colorbar=dict(
            title=dict(text="Title Count", font=dict(color=theme["primary"])), 
            tickfont=dict(color=theme["text"])
        )
    )
    st.plotly_chart(fig_map, use_container_width=True)

    st.subheader(f"🎭 Treemap: {treemap_level} by Genre")
    
    df_non_us_genres = df_non_us.copy()
    if 'listed_in' not in df_non_us_genres.columns:
        st.warning("⚠️ The 'listed_in' column is missing for genre analysis in H3.")
        return

    df_non_us_genres['genre'] = df_non_us_genres['listed_in'].str.split(', ')
    df_exploded = df_non_us_genres.explode('genre')
    treemap_df = df_exploded.groupby(['origin_country', 'genre']).size().reset_index(name='Count')
    
    top_n = 10 if treemap_level == "Top 10 Countries" else 50
    top_countries = treemap_df.groupby('origin_country')['Count'].sum().nlargest(top_n).index
    treemap_df_filtered = treemap_df[treemap_df['origin_country'].isin(top_countries)]
    
    if treemap_df_filtered.empty:
        st.warning(f"⚠️ No data to display for {treemap_level} with current filters.")
        return

    fig_tree = px.treemap(
        treemap_df_filtered, 
        path=[px.Constant("🌍 Non-US Content"), 'origin_country', 'genre'], 
        values='Count',
        color='Count',
        color_continuous_scale='Plasma',
        title=f'📊 Hierarchy of Content Volume in Top {top_n} Non-U.S. Countries by Genre'
    )
    fig_tree.update_layout(
        margin = dict(t=50, l=25, r=25, b=25),
        title_font=dict(color=theme["primary"], family='Orbitron', size=18),
        paper_bgcolor=theme["paper_bg"],
        font=dict(color=theme["text"])
    )
    st.plotly_chart(fig_tree, use_container_width=True)

# --- HYPOTHESIS 4: SEABORN STATISTICAL ANALYSIS ---
def render_H4_seaborn_analysis(df, theme):
    st.header("📊 Bonus: Seaborn Statistical Analysis")
    st.markdown(f"""
    <p style='color: {theme["text"]};'>
    This section uses the <b>Seaborn</b> library (which is built on Matplotlib) to create statistical plots. 
    Note: As Seaborn generates static images, its styling is dynamically adjusted to complement the selected theme.
    </p>
    """, unsafe_allow_html=True)

    mpl_fig_bg = rgba_string_to_mpl_tuple(theme["chart_bg"])
    mpl_axes_bg = rgba_string_to_mpl_tuple(theme["paper_bg"])
    mpl_grid_color = theme.get("gridline_color", hex_to_rgba(theme["primary"], 0.2))
    
    if "rgba" in str(mpl_grid_color):
        mpl_grid_color = rgba_string_to_mpl_tuple(mpl_grid_color)
        
    sns.set_theme(style="darkgrid", rc={
        "figure.facecolor": mpl_fig_bg,
        "axes.facecolor": mpl_axes_bg,
        "text.color": theme["text"],
        "axes.labelcolor": theme["text"],
        "xtick.color": theme["text"],
        "ytick.color": theme["text"],
        "grid.color": mpl_grid_color
    })

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Movie Runtime Distribution (KDE)")
        df_movies = df[df['runtime_min'].notna()]
        
        if df_movies.empty:
            st.warning("No movie data available for runtime analysis.")
        else:
            fig, ax = plt.subplots()
            sns.kdeplot(df_movies['runtime_min'], fill=True, color=theme["primary"], ax=ax)
            ax.set_title("Density of Movie Runtimes")
            ax.set_xlabel("Runtime (Minutes)")
            ax.set_ylabel("Density")
            st.pyplot(fig)

    with col2:
        st.subheader("TV Show Season Count")
        df_tv = df[df['num_seasons'].notna()]
        
        if df_tv.empty:
            st.warning("No TV show data available for season analysis.")
        else:
            fig, ax = plt.subplots()
            sns.histplot(df_tv['num_seasons'], discrete=True, color=theme["secondary"], ax=ax, shrink=0.8)
            ax.set_title("Frequency of Season Counts")
            ax.set_xlabel("Number of Seasons")
            ax.set_ylabel("Count")
            if not df_tv.empty:
                try:
                    max_seasons = int(df_tv['num_seasons'].max())
                    if max_seasons > 0:
                        ax.set_xticks(range(1, max_seasons + 1))
                except ValueError:
                    pass
            st.pyplot(fig)
        
    st.markdown("---")
    
    st.subheader("Violin Plot: Runtime Distribution by Rating")
    df_movies = df[df['runtime_min'].notna()].copy()
    top_ratings = df_movies['rating'].value_counts().nlargest(8).index
    df_violin = df_movies[df_movies['rating'].isin(top_ratings)]
    
    if df_violin.empty:
        st.warning("No data for violin plot.")
    else:
        fig, ax = plt.subplots(figsize=(12, 7))
        sns.violinplot(
            data=df_violin, 
            x='rating', 
            y='runtime_min', 
            ax=ax, 
            color=theme["secondary"],
            inner='quartile',
            linewidth=1.5
        )
        ax.set_title("Movie Runtime Distribution by Age Rating (Top 8)")
        ax.set_xlabel("Rating")
        ax.set_ylabel("Runtime (Minutes)")
        st.pyplot(fig)
        
    st.markdown("---")
    st.subheader("Genre vs. Decade Release Heatmap")
    
    df_heat = df.copy()
    if 'release_year' not in df_heat.columns:
        st.warning("Column 'release_year' not found for heatmap.")
        return
        
    df_heat['decade'] = (df_heat['release_year'] // 10) * 10
    df_heat = df_heat[df_heat['decade'] >= 1980]
    
    if 'listed_in' not in df_heat.columns:
        st.warning("Column 'listed_in' not found for heatmap genre analysis.")
        return
        
    df_heat['genre'] = df_heat['listed_in'].str.split(', ')
    df_heat_exploded = df_heat.explode('genre')
    
    top_genres = df_heat_exploded['genre'].value_counts().nlargest(10).index
    df_heat_filtered = df_heat_exploded[df_heat_exploded['genre'].isin(top_genres)]
    
    pivot_table = df_heat_filtered.pivot_table(index='genre', columns='decade', values='title', aggfunc='count', fill_value=0)
    
    if pivot_table.empty:
        st.warning("No data to display in heatmap with current filters.")
    else:
        fig, ax = plt.subplots(figsize=(12, 8))
        sns.heatmap(
            pivot_table, 
            annot=True, 
            fmt="g", 
            cmap="viridis", 
            ax=ax,
            linewidths=.5,
            linecolor=theme.get("gridline_color", "#333")
        )
        ax.set_title("Heatmap of Top 10 Genres Released by Decade")
        ax.set_xlabel("Decade")
        ax.set_ylabel("Genre")
        st.pyplot(fig)

# --- DASHBOARD PAGE RENDER FUNCTION ---
def render_dashboard_page(theme, selected_theme_name):
    """Renders the main analysis dashboard content."""
    
    df_netflix = load_netflix_data()
    df_comparison = load_platform_comparison_data()

    st.markdown(f"""
        <div style='text-align: center; padding: 30px; background: {theme["chart_bg"]}; border-radius: 15px; border: 2px solid {theme["primary"]}; margin-bottom: 30px; box-shadow: 0 0 30px {hex_to_rgba(theme["primary"], 0.25)};'>
            <h1 style='font-family: Orbitron; font-size: 3.5rem; background: linear-gradient(90deg, {theme["primary"]}, {theme["secondary"]}, {theme["accent"]}); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-shadow: 0 0 30px {hex_to_rgba(theme["primary"], 0.5)}; margin: 0;'>
                🎬 STRATEGIC INTELLIGENCE 🎬
            </h1>
            <p style='color: {theme["text"]}; font-size: 1.3rem; font-family: Rajdhani; letter-spacing: 3px; margin-top: 15px; margin-bottom: 0;'>
                📊 NEXT-GENERATION OTT CONTENT ANALYTICS PLATFORM 📊
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown(f"""
    <div style='background: {theme["chart_bg"]}; border-left: 4px solid {theme["primary"]}; padding: 15px; border-radius: 10px; margin-bottom: 20px;'>
    <p style='color: {theme["text"]}; font-size: 1.1rem; margin: 0;'>
    📺 <b>Dashboard Structure:</b> All strategic hypotheses are analyzed on this unified page. Use the <b style='color: {theme["primary"]};'>🎛️ CONTROL PANELS</b> in the sidebar to dynamically filter visualizations for each section.
    </p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    
    if df_netflix.empty and df_comparison.empty:
        st.error("⚠️ Cannot proceed. Please ensure all data files (especially netflix_titles (1).csv) are correctly placed and named.")
        return

    if not df_comparison.empty:
        render_H1_local_language(df_comparison, theme)
    else:
        st.error("❌ Cannot run Hypothesis 1 (Local Language). Check all 6 platform files are available and correctly named.")
        
    st.markdown("---")
    st.markdown("---")
    st.markdown("---")

    if not df_netflix.empty:
        render_H2_recency(df_netflix, theme)
    else:
        st.error("❌ Cannot run Hypothesis 2 (Content Recency). Check 'netflix_titles (1).csv'.")
        
    st.markdown("---")
    st.markdown("---")
    st.markdown("---")

    if not df_netflix.empty:
        render_H3_international_growth(df_netflix, theme)
    else:
        st.error("❌ Cannot run Hypothesis 3 (Global Growth). Check 'netflix_titles (1).csv'.")

    st.markdown("---")
    st.markdown("---")
    st.markdown("---")

    if not df_netflix.empty:
        render_H4_seaborn_analysis(df_netflix, theme)
    else:
        st.error("❌ Cannot run Hypothesis 4 (Seaborn Analysis). Check 'netflix_titles (1).csv'.")
    
    st.markdown("---")
    st.markdown(f"""
        <div style='text-align: center; padding: 25px; background: {theme["chart_bg"]}; border-radius: 10px; border: 1px solid {hex_to_rgba(theme["primary"], 0.25)}; margin-top: 30px;'>
            
            <img src="https://images.unsplash.com/photo-1574267432644-f65b5fe8fb11?w=600&h=100&fit=crop" style="border-radius: 5px; margin-bottom: 20px; max-width: 100%; opacity: 0.7;" />

            <p style='font-size: 1.1rem; color: {theme["secondary"]}; font-family: Orbitron; margin: 0;'>
                ⚡ Powered by Advanced Analytics Engine | Real-time Strategic Intelligence ⚡
            </p>
            <p style='font-size: 0.9rem; color: {theme["text"]}; margin-top: 10px; margin-bottom: 10px;'>
                🎯 Data processed through quantum algorithms for maximum insight extraction 🎯
            </p>
            <p style='font-size: 0.85rem; color: {theme["text"]}; margin: 0;'>
                Current Theme: <span style='color: {theme["primary"]}; font-weight: bold; font-family: Orbitron;'>{selected_theme_name}</span>
            </p>
            <p style='font-size: 0.75rem; color: {theme["text"]}; margin-top: 8px; opacity: 0.7;'>
                🎬 Netflix | 📺 Streaming | 🌍 Global Entertainment Platform 🌍
            </p>
        </div>
    """, unsafe_allow_html=True)


# --- MAIN DASHBOARD FUNCTION ---
def main_dashboard():
    
    with st.sidebar:
        st.markdown("# 🎨 THEME SELECTOR")
        selected_theme_name = st.selectbox(
            "Choose Your Visual Theme",
            options=list(COLOR_THEMES.keys()),
            index=0,
            help="Select a color palette for the entire dashboard",
            key="global_theme_selector"
        )
        
        theme = COLOR_THEMES[selected_theme_name]
        
        st.markdown("---")
        
        st.markdown("### 🧭 NAVIGATION")
        
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.page = 'home'
            st.rerun()
        
        if st.button("📊 Dashboard", use_container_width=True):
            st.session_state.page = 'dashboard'
            st.rerun()
        
        st.markdown("---")
        
        theme_index = list(COLOR_THEMES.keys()).index(selected_theme_name)
        platform_name = list(PLATFORM_LOGOS.keys())[theme_index % len(PLATFORM_LOGOS)]
        logo_colors = PLATFORM_LOGOS[platform_name]
        
        st.image(
            f"https://placehold.co/400x200/{logo_colors['bg']}/{logo_colors['text']}?text={platform_name}&font=orbitron",
            use_column_width=True,
            caption=f"Strategic Intelligence: {platform_name}"
        )

    
    st.markdown(generate_theme_css(theme), unsafe_allow_html=True)
    
    if st.session_state.page == 'home':
        render_homepage(theme)
    else:
        render_dashboard_page(theme, selected_theme_name)


# --- EXECUTE ---
if __name__ == "__main__":
    main_dashboard()
