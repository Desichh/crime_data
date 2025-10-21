import warnings
warnings.filterwarnings("ignore")  # Hilangkan warning dari pandas & plotly

import pandas as pd
from dash import Dash, dcc, html, Input, Output, dash_table
import plotly.express as px
import dash_bootstrap_components as dbc

# === URL FILE GOOGLE DRIVE ===
# Link baru: https://drive.google.com/file/d/1Vn-xqU6wkNXKl579ToyZqNm9Sr4ffFNI/view?usp=sharing
file_id = "1Vn-xqU6wkNXKl579ToyZqNm9Sr4ffFNI"
url = f"https://drive.google.com/uc?id={file_id}"

# === BACA DATA ===
try:
    df = pd.read_csv(url)
    print("✅ Data berhasil dimuat dari Google Drive:", df.shape)
except Exception as e:
    print("❌ Gagal memuat data:", e)
    df = pd.DataFrame(columns=[
        'Date Rptd', 'DATE OCC', 'TIME OCC', 'AREA NAME', 'Crm Cd Desc',
        'Premis Desc', 'Weapon Desc', 'Vict Age', 'LAT', 'LON'
    ])

# --- Persiapan Data ---
if not df.empty:
    # Pastikan kolom waktu & tanggal rapi
    if 'TIME OCC' in df.columns:
        df['TIME OCC'] = df['TIME OCC'].astype(str).str.zfill(4).str[:2]
        df['TIME OCC'] = pd.to_numeric(df['TIME OCC'], errors='coerce').fillna(0).astype(int)

    if 'AREA NAME' in df.columns:
        df['AREA NAME'] = df['AREA NAME'].astype(str).str.title()

    # Parsing tanggal
    if 'DATE OCC' in df.columns:
        df['DATE OCC'] = pd.to_datetime(df['DATE OCC'], errors='coerce')

# === INISIALISASI DASH ===
app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
app.title = "Crime Monitoring Dashboard"

# === LAYOUT ===
app.layout = html.Div(style={'backgroundColor': 'white', 'padding': '20px', 'color': '#111'}, children=[
    html.H1("🚨 Crime Monitoring Dashboard",
            style={'textAlign': 'center', 'color': '#3a3a3a', 'marginBottom': '10px'}),

    html.P("Analisis Kejahatan Berdasarkan Wilayah, Waktu, dan Pola Korban",
           style={'textAlign': 'center', 'fontSize': '18px', 'color': '#555'}),

    # === Dropdown Wilayah ===
    html.Div([
        html.Label("🏙️ Pilih Wilayah:", style={'fontWeight': 'bold', 'fontSize': '18px'}),
        dcc.Dropdown(
            id='area-select',
            options=([{'label': a, 'value': a} for a in sorted(df['AREA NAME'].dropna().unique())]
                     if not df.empty and 'AREA NAME' in df.columns else []),
            value=(sorted(df['AREA NAME'].dropna().unique())[0]
                   if not df.empty and 'AREA NAME' in df.columns and len(df['AREA NAME'].dropna()) > 0 else None),
            placeholder="Pilih wilayah...",
            clearable=False,
            style={'width': '60%', 'margin': '0 auto', 'color': '#000'}
        )
    ], style={'textAlign': 'center', 'marginBottom': '30px'}),

    # === Statistik Ringkas ===
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader("Total Kasus di Wilayah Ini", style={'backgroundColor': '#007bff', 'color': 'white'}),
            dbc.CardBody(id='total-cases', style={'fontSize': '26px', 'fontWeight': 'bold', 'textAlign': 'center'})
        ], style={'borderRadius': '12px', 'border': '1px solid #e0e0e0', 'boxShadow': '0 2px 8px rgba(0,0,0,0.1)'})),

        dbc.Col(dbc.Card([
            dbc.CardHeader("Jenis Kejahatan Terbanyak", style={'backgroundColor': '#6f42c1', 'color': 'white'}),
            dbc.CardBody(id='top-crime', style={'fontSize': '22px', 'textAlign': 'center'})
        ], style={'borderRadius': '12px', 'border': '1px solid #e0e0e0', 'boxShadow': '0 2px 8px rgba(0,0,0,0.1)'})),

        dbc.Col(dbc.Card([
            dbc.CardHeader("Jam Paling Rawan", style={'backgroundColor': '#f39c12', 'color': 'white'}),
            dbc.CardBody(id='top-hour', style={'fontSize': '22px', 'textAlign': 'center'})
        ], style={'borderRadius': '12px', 'border': '1px solid #e0e0e0', 'boxShadow': '0 2px 8px rgba(0,0,0,0.1)'})),
    ], className="mb-4"),

    # === Peta dan Grafik Jam Rawan ===
    dbc.Row([
        dbc.Col(dcc.Graph(id='map-chart', style={'height': '600px'}), width=7),
        dbc.Col(dcc.Graph(id='time-chart', style={'height': '600px'}), width=5)
    ]),

    # === Grafik Tambahan ===
    dbc.Row([
        dbc.Col(dcc.Graph(id='crime-chart'), width=6),
        dbc.Col(dcc.Graph(id='weapon-chart'), width=6),
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id='premis-chart'), width=6),
        dbc.Col(dcc.Graph(id='age-chart'), width=6),
    ]),

    html.H3("📋 Data Detail", style={'textAlign': 'center', 'marginTop': '30px', 'color': '#3a3a3a'}),

    dash_table.DataTable(
        id='data-table',
        columns=[{"name": i, "id": i} for i in
                 ['Date Rptd', 'TIME OCC', 'AREA NAME', 'Crm Cd Desc', 'Premis Desc', 'LAT', 'LON']],
        page_size=8,
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left', 'padding': '6px', 'fontFamily': 'Arial', 'color': '#111'},
        style_header={'backgroundColor': '#6f42c1', 'color': 'white', 'fontWeight': 'bold'}
    )
])

# === CALLBACK ===
@app.callback(
    [Output('map-chart', 'figure'),
     Output('time-chart', 'figure'),
     Output('crime-chart', 'figure'),
     Output('weapon-chart', 'figure'),
     Output('premis-chart', 'figure'),
     Output('age-chart', 'figure'),
     Output('data-table', 'data'),
     Output('total-cases', 'children'),
     Output('top-crime', 'children'),
     Output('top-hour', 'children')],
    [Input('area-select', 'value')]
)
def update_dashboard(selected_area):
    if df.empty or selected_area is None:
        return [{}] * 6 + [[]] + ["-", "-", "-"]

    dff = df[df['AREA NAME'] == selected_area]

    total_kasus = len(dff)
    top_crime = dff['Crm Cd Desc'].value_counts().idxmax() if not dff.empty else "-"
    top_hour = dff['TIME OCC'].value_counts().idxmax() if not dff.empty else "-"

    # === Peta ===
    if 'LAT' in dff.columns and 'LON' in dff.columns:
        map_fig = px.density_mapbox(
            dff.dropna(subset=['LAT', 'LON']),
            lat='LAT', lon='LON', radius=12,
            center=dict(lat=dff['LAT'].mean(), lon=dff['LON'].mean()),
            zoom=10,
            title=f"📍 Peta Sebaran Kejahatan di {selected_area}",
            color_continuous_scale='OrRd'
        )
        map_fig.update_layout(mapbox_style="carto-positron", paper_bgcolor='white',
                              font_color='#111', margin=dict(l=20, r=20, t=50, b=20))
    else:
        map_fig = px.scatter(title="Tidak ada data koordinat")

    # === Grafik Jam Rawan ===
    time_counts = dff['TIME OCC'].value_counts().sort_index().reset_index()
    time_counts.columns = ['Jam', 'Jumlah Kasus']
    time_fig = px.area(time_counts, x='Jam', y='Jumlah Kasus',
                       title=f"🕒 Distribusi Jam Rawan Kejahatan di {selected_area}",
                       color_discrete_sequence=['#6C63FF'])
    time_fig.update_traces(fillcolor='rgba(108,99,255,0.3)')
    time_fig.update_layout(paper_bgcolor='white', font_color='#111')

    # === Jenis Kejahatan ===
    crime_counts = dff['Crm Cd Desc'].value_counts().nlargest(10).reset_index()
    crime_counts.columns = ['Jenis Kejahatan', 'Jumlah']
    crime_fig = px.bar(crime_counts, x='Jenis Kejahatan', y='Jumlah', color='Jumlah',
                       title=f"⚖️ 10 Jenis Kejahatan Terbanyak di {selected_area}",
                       color_continuous_scale='Purples')
    crime_fig.update_layout(paper_bgcolor='white', font_color='#111')

    # === Senjata ===
    if 'Weapon Desc' in dff.columns:
        weapon_counts = dff['Weapon Desc'].value_counts().nlargest(8).reset_index()
        weapon_counts.columns = ['Senjata', 'Jumlah']
        weapon_fig = px.bar(weapon_counts, x='Senjata', y='Jumlah', color='Jumlah',
                            title='🔫 Jenis Senjata yang Digunakan', color_continuous_scale='Oranges')
    else:
        weapon_fig = px.bar(title="🔫 Tidak ada data senjata")

    # === Lokasi Kejadian ===
    if 'Premis Desc' in dff.columns:
        premis_counts = dff['Premis Desc'].value_counts().nlargest(8).reset_index()
        premis_counts.columns = ['Lokasi', 'Jumlah']
        premis_fig = px.bar(premis_counts, x='Lokasi', y='Jumlah', color='Jumlah',
                            title='🏠 Jenis Lokasi Kejadian', color_continuous_scale='Blues')
    else:
        premis_fig = px.bar(title="🏠 Tidak ada data lokasi")

    # === Umur Korban ===
    if 'Vict Age' in dff.columns:
        age_fig = px.histogram(dff, x='Vict Age', nbins=20,
                               title="👥 Distribusi Umur Korban", color_discrete_sequence=['#6C63FF'])
    else:
        age_fig = px.bar(title="👥 Tidak ada data umur korban")

    # === Data Table ===
    try:
        data_table = dff.head(50).to_dict('records')
    except Exception:
        data_table = []

    return map_fig, time_fig, crime_fig, weapon_fig, premis_fig, age_fig, data_table, str(total_kasus), str(top_crime), f"{top_hour}:00"


# === RUN SERVER ===
if __name__ == '__main__':
    app.run(debug=True)