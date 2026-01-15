"""
Dashboard de Análise Fundamentalista
Interface moderna para visualização de indicadores financeiros de empresas brasileiras.
"""

from pathlib import Path

import pandas as pd
import plotly.graph_objs as go
from shiny import App, reactive, ui
from shinywidgets import output_widget, render_widget

# Configuração de caminhos
DATA_DIR = Path(__file__).parent.parent.parent / "data" / "processed"

# Cores do tema
COLORS = {
    'primary': '#1e3a5f',
    'secondary': '#3d5a80',
    'accent': '#ee6c4d',
    'success': '#2a9d8f',
    'warning': '#e9c46a',
    'danger': '#e76f51',
    'light': '#f8f9fa',
    'dark': '#293241',
    'chart_blue': '#4361ee',
    'chart_green': '#2ec4b6',
    'chart_orange': '#ff9f1c',
    'chart_red': '#e71d36',
}

# Carrega os dados
names_companies = pd.read_csv(DATA_DIR / 'names_companies.csv', sep=';')['DENOM_SOCIAL'].tolist()
bp = pd.read_csv(DATA_DIR / 'bp.csv', sep=';', encoding='latin1')
dre = pd.read_csv(DATA_DIR / 'dre.csv', sep=';', encoding='latin1')
indic_liq = pd.read_csv(DATA_DIR / 'indic_liq.csv', sep=';', encoding='latin1')
indic_end = pd.read_csv(DATA_DIR / 'indic_end.csv', sep=';', encoding='latin1')
indic_enf = pd.read_csv(DATA_DIR / 'indic_enf.csv', sep=';', encoding='latin1')
indic_rent = pd.read_csv(DATA_DIR / 'indic_rent.csv', sep=';', encoding='latin1')

# Layout do gráfico padrão
CHART_LAYOUT = dict(
    template='plotly_white',
    hovermode='x unified',
    margin=dict(l=40, r=40, t=60, b=40),
    font=dict(family='Inter, sans-serif', size=12),
    title_font=dict(size=16, color=COLORS['dark']),
    legend=dict(
        orientation='h',
        yanchor='bottom',
        y=1.02,
        xanchor='right',
        x=1
    ),
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
)

# CSS customizado
custom_css = """
<style>
    body {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
    }
    .bslib-sidebar-layout {
        --bs-sidebar-bg: linear-gradient(180deg, #1e3a5f 0%, #293241 100%);
    }
    .sidebar {
        background: linear-gradient(180deg, #1e3a5f 0%, #293241 100%) !important;
        color: white !important;
    }
    .sidebar label {
        color: #e4e8ec !important;
        font-weight: 500;
    }
    .card {
        border: none;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    }
    .nav-link {
        border-radius: 8px !important;
        margin: 2px;
        font-weight: 500;
    }
    .nav-link.active {
        background: linear-gradient(135deg, #4361ee 0%, #3d5a80 100%) !important;
        color: white !important;
    }
    h1, h2, h3 {
        color: #293241;
        font-weight: 600;
    }
    .title-section {
        background: linear-gradient(135deg, #1e3a5f 0%, #3d5a80 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
    }
</style>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
"""

# Interface do usuário
app_ui = ui.page_fluid(
    ui.HTML(custom_css),
    ui.div(
        ui.h1("📊 Dashboard de Análise Fundamentalista", style="margin:0; font-size: 1.8rem;"),
        ui.p("Indicadores financeiros de empresas brasileiras listadas na B3", 
             style="margin:0; opacity: 0.9; font-size: 0.95rem;"),
        class_="title-section"
    ),
    ui.layout_sidebar(
        ui.sidebar(
            ui.div(
                ui.p("🏢 Selecione a Empresa", style="font-size: 1.1rem; font-weight: 600; margin-bottom: 1rem;"),
                ui.input_selectize(
                    id="companies",
                    label="",
                    choices=names_companies,
                    selected="VALE S.A.",
                    width="100%"
                ),
                style="padding: 0.5rem;"
            ),
            ui.hr(style="border-color: rgba(255,255,255,0.2);"),
            ui.div(
                ui.p("📈 Sobre o Dashboard", style="font-weight: 600; margin-bottom: 0.5rem;"),
                ui.p("Visualize indicadores de:", style="font-size: 0.85rem; opacity: 0.8;"),
                ui.tags.ul(
                    ui.tags.li("Liquidez", style="font-size: 0.8rem;"),
                    ui.tags.li("Endividamento", style="font-size: 0.8rem;"),
                    ui.tags.li("Eficiência", style="font-size: 0.8rem;"),
                    ui.tags.li("Rentabilidade", style="font-size: 0.8rem;"),
                    style="opacity: 0.8; padding-left: 1.2rem;"
                ),
                style="padding: 0.5rem;"
            ),
            width=280,
            bg="#1e3a5f"
        ),
        ui.navset_card_tab(
            # Demonstrativos
            ui.nav_panel(
                "📋 Demonstrativos",
                ui.row(
                    ui.column(12, ui.card(output_widget("bp_chart"), style="padding: 1rem;")),
                ),
                ui.row(
                    ui.column(12, ui.card(output_widget("dre_chart"), style="padding: 1rem; margin-top: 1rem;")),
                ),
            ),
            # Liquidez
            ui.nav_panel(
                "💧 Liquidez",
                ui.row(
                    ui.column(6, ui.card(output_widget("liq_corrente"), style="padding: 1rem;")),
                    ui.column(6, ui.card(output_widget("liq_imediata"), style="padding: 1rem;")),
                ),
                ui.row(
                    ui.column(6, ui.card(output_widget("liq_seca"), style="padding: 1rem; margin-top: 1rem;")),
                    ui.column(6, ui.card(output_widget("liq_geral"), style="padding: 1rem; margin-top: 1rem;")),
                ),
            ),
            # Endividamento
            ui.nav_panel(
                "🏦 Endividamento",
                ui.row(
                    ui.column(6, ui.card(output_widget("end_divida_pl"), style="padding: 1rem;")),
                    ui.column(6, ui.card(output_widget("end_divida_ativos"), style="padding: 1rem;")),
                ),
                ui.row(
                    ui.column(6, ui.card(output_widget("end_divida_ebit"), style="padding: 1rem; margin-top: 1rem;")),
                    ui.column(6, ui.card(output_widget("end_pl_ativos"), style="padding: 1rem; margin-top: 1rem;")),
                ),
            ),
            # Eficiência
            ui.nav_panel(
                "⚡ Eficiência",
                ui.row(
                    ui.column(4, ui.card(output_widget("margem_bruta"), style="padding: 1rem;")),
                    ui.column(4, ui.card(output_widget("margem_liquida"), style="padding: 1rem;")),
                    ui.column(4, ui.card(output_widget("margem_ebit"), style="padding: 1rem;")),
                ),
            ),
            # Rentabilidade
            ui.nav_panel(
                "💰 Rentabilidade",
                ui.row(
                    ui.column(4, ui.card(output_widget("rent_roe"), style="padding: 1rem;")),
                    ui.column(4, ui.card(output_widget("rent_roa"), style="padding: 1rem;")),
                    ui.column(4, ui.card(output_widget("rent_roic"), style="padding: 1rem;")),
                ),
            ),
            id="main_tabs"
        )
    ),
    theme=ui.Theme("bootstrap"),
)


def create_line_chart(df, x_col, y_col, title, color=COLORS['chart_blue'], fill=False):
    """Cria um gráfico de linhas padronizado."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df[x_col],
        y=df[y_col],
        mode='lines+markers',
        name=title,
        line=dict(color=color, width=3),
        marker=dict(size=8),
        fill='tozeroy' if fill else None,
        fillcolor=f'rgba{tuple(list(int(color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4)) + [0.1])}' if fill else None
    ))
    fig.update_layout(**CHART_LAYOUT, title=title)
    fig.update_xaxes(title='', gridcolor='rgba(0,0,0,0.05)')
    fig.update_yaxes(title='', gridcolor='rgba(0,0,0,0.05)')
    return go.FigureWidget(fig)


def create_bar_chart(df, x_col, y_cols, names, colors, title):
    """Cria um gráfico de barras empilhadas."""
    fig = go.Figure()
    for y_col, name, color in zip(y_cols, names, colors):
        fig.add_bar(x=df[x_col], y=df[y_col], name=name, marker_color=color)
    fig.update_layout(**CHART_LAYOUT, title=title, barmode='group')
    fig.update_xaxes(title='', gridcolor='rgba(0,0,0,0.05)')
    fig.update_yaxes(title='R$ (milhões)', gridcolor='rgba(0,0,0,0.05)')
    return go.FigureWidget(fig)


def server(input, output, session):
    """Lógica do servidor."""
    
    @reactive.Calc
    def filtered_bp():
        return bp[bp['DENOM_CIA'] == input.companies()]
    
    @reactive.Calc
    def filtered_dre():
        return dre[dre['DENOM_CIA'] == input.companies()]
    
    @reactive.Calc
    def filtered_liq():
        return indic_liq[indic_liq['DENOM_CIA'] == input.companies()]
    
    @reactive.Calc
    def filtered_end():
        return indic_end[indic_end['DENOM_CIA'] == input.companies()]
    
    @reactive.Calc
    def filtered_enf():
        return indic_enf[indic_enf['DENOM_CIA'] == input.companies()]
    
    @reactive.Calc
    def filtered_rent():
        return indic_rent[indic_rent['DENOM_CIA'] == input.companies()]

    # Demonstrativos
    @output
    @render_widget
    def bp_chart():
        df = filtered_bp()
        fig = go.Figure()
        fig.add_bar(x=df['DT_REFER'], y=df['Ativo Circulante'], name='Ativo Circulante', marker_color=COLORS['chart_blue'])
        fig.add_bar(x=df['DT_REFER'], y=df['Ativo Não Circulante'], name='Ativo Não Circulante', marker_color=COLORS['chart_green'])
        fig.add_scatter(x=df['DT_REFER'], y=df['Ativo Total'], mode='lines+markers', name='Ativo Total', 
                       line=dict(color=COLORS['dark'], width=3))
        fig.update_layout(**CHART_LAYOUT, title='📊 Balanço Patrimonial - Ativos', barmode='stack')
        return go.FigureWidget(fig)

    @output
    @render_widget
    def dre_chart():
        df = filtered_dre()
        fig = go.Figure()
        fig.add_bar(x=df['DT_REFER'], y=df['Receita de Venda de Bens e/ou Serviços'], 
                   name='Receita', marker_color=COLORS['chart_blue'])
        fig.add_bar(x=df['DT_REFER'], y=df['Custo dos Bens e/ou Serviços Vendidos'], 
                   name='Custo', marker_color=COLORS['chart_red'])
        fig.add_scatter(x=df['DT_REFER'], y=df['Lucro/Prejuízo Consolidado do Período'], 
                       mode='lines+markers', name='Lucro/Prejuízo', 
                       line=dict(color=COLORS['chart_orange'], width=4))
        fig.update_layout(**CHART_LAYOUT, title='📈 Demonstração do Resultado (DRE)', barmode='group')
        return go.FigureWidget(fig)

    # Liquidez
    @output
    @render_widget
    def liq_corrente():
        return create_line_chart(filtered_liq(), 'DT_REFER', 'liquidez_corrente', 
                                '💧 Liquidez Corrente', COLORS['chart_blue'], True)
    
    @output
    @render_widget
    def liq_imediata():
        return create_line_chart(filtered_liq(), 'DT_REFER', 'liquidez_imediata',
                                '⚡ Liquidez Imediata', COLORS['chart_green'], True)
    
    @output
    @render_widget
    def liq_seca():
        return create_line_chart(filtered_liq(), 'DT_REFER', 'liquidez_seca',
                                '🔥 Liquidez Seca', COLORS['chart_orange'], True)
    
    @output
    @render_widget
    def liq_geral():
        return create_line_chart(filtered_liq(), 'DT_REFER', 'liquidez_geral',
                                '📊 Liquidez Geral', COLORS['secondary'], True)

    # Endividamento
    @output
    @render_widget
    def end_divida_pl():
        return create_line_chart(filtered_end(), 'DT_REFER', 'divida_pl',
                                '📉 Dívida / PL', COLORS['chart_red'], True)
    
    @output
    @render_widget
    def end_divida_ativos():
        return create_line_chart(filtered_end(), 'DT_REFER', 'divida_ativos',
                                '🏢 Dívida / Ativos', COLORS['chart_orange'], True)
    
    @output
    @render_widget
    def end_divida_ebit():
        return create_line_chart(filtered_end(), 'DT_REFER', 'divida_ebit',
                                '💳 Dívida / EBIT', COLORS['warning'], True)
    
    @output
    @render_widget
    def end_pl_ativos():
        return create_line_chart(filtered_end(), 'DT_REFER', 'pl_ativos',
                                '💼 PL / Ativos', COLORS['chart_green'], True)

    # Eficiência
    @output
    @render_widget
    def margem_bruta():
        return create_line_chart(filtered_enf(), 'DT_REFER', 'margem_bruta',
                                '📈 Margem Bruta (%)', COLORS['chart_blue'], True)
    
    @output
    @render_widget
    def margem_liquida():
        return create_line_chart(filtered_enf(), 'DT_REFER', 'margem_liquida',
                                '💰 Margem Líquida (%)', COLORS['chart_green'], True)
    
    @output
    @render_widget
    def margem_ebit():
        return create_line_chart(filtered_enf(), 'DT_REFER', 'margem_ebit',
                                '⚡ Margem EBIT (%)', COLORS['chart_orange'], True)

    # Rentabilidade
    @output
    @render_widget
    def rent_roe():
        return create_line_chart(filtered_rent(), 'DT_REFER', 'roe',
                                '🎯 ROE (%)', COLORS['chart_blue'], True)
    
    @output
    @render_widget
    def rent_roa():
        return create_line_chart(filtered_rent(), 'DT_REFER', 'roa',
                                '🏢 ROA (%)', COLORS['chart_green'], True)
    
    @output
    @render_widget
    def rent_roic():
        return create_line_chart(filtered_rent(), 'DT_REFER', 'roic',
                                '💎 ROIC (%)', COLORS['chart_orange'], True)


# Aplicação
app = App(app_ui, server)