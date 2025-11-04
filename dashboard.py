#!/usr/bin/env python3
"""
Interactive Dashboard for Aircraft Data Analysis
Allows visualization of aircraft data from Excel file with multiple sheets
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import Dash, dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc

# Load data
EXCEL_FILE = 'data/Stand_2025_10_DE.xlsx'

# Initialize the Dash app with Bootstrap theme
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Load Excel file and get sheet names
xl = pd.ExcelFile(EXCEL_FILE)
sheet_names = xl.sheet_names

# Function to get descriptive label for sheets
def get_sheet_label(sheet_name):
    """Extract descriptive text from first row for sheets 1.a through 6"""
    sheets_with_descriptions = ['1.a', '1.b', '2.', '3.', '4.', '5.', '6.']

    if sheet_name in sheets_with_descriptions:
        try:
            df = pd.read_excel(xl, sheet_name=sheet_name, header=None, nrows=1)
            first_cell = str(df.iloc[0, 0])

            # Split by ' - ' and get the third segment (aircraft category)
            if ' - ' in first_cell:
                parts = first_cell.split(' - ')
                if len(parts) >= 3:
                    description = parts[2]  # Third segment contains the category
                    return f"{sheet_name} - {description}"
        except Exception as e:
            print(f"Could not extract description for {sheet_name}: {e}")

    return sheet_name  # Return original name if no description

# Create sheet options for dropdown
sheet_options = [{'label': get_sheet_label(sheet), 'value': sheet} for sheet in sheet_names]

# Function to load data from a specific sheet
def load_sheet_data(sheet_name):
    """Load data from a specific sheet with proper header handling"""
    try:
        df = pd.read_excel(xl, sheet_name=sheet_name, header=1)
        # Clean the data
        df = df.dropna(how='all')  # Remove completely empty rows

        # Ensure mass column is numeric
        if 'höchstzulässige Abflugmasse (kg)' in df.columns:
            df['höchstzulässige Abflugmasse (kg)'] = pd.to_numeric(
                df['höchstzulässige Abflugmasse (kg)'], errors='coerce'
            )

        return df
    except Exception as e:
        print(f"Error loading sheet {sheet_name}: {e}")
        return pd.DataFrame()

# App layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("🛩️ Aircraft Data Dashboard", className="text-center mb-4 mt-4"),
            html.P("Interactive analysis of Austrian aircraft registry data",
                   className="text-center text-muted mb-4")
        ])
    ]),

    dbc.Row([
        dbc.Col([
            html.Label("Select Sheet:", className="fw-bold"),
            dcc.Dropdown(
                id='sheet-selector',
                options=sheet_options,
                value=sheet_names[0],
                clearable=False,
                className="mb-3"
            )
        ], md=4),

        dbc.Col([
            html.Label("Group By:", className="fw-bold"),
            dcc.Dropdown(
                id='group-by-selector',
                options=[
                    {'label': 'Hersteller (Manufacturer)', 'value': 'Hersteller'},
                    {'label': 'Herstellerbezeichnung (Model)', 'value': 'Herstellerbezeichnung'},
                    {'label': 'Both', 'value': 'both'}
                ],
                value='Hersteller',
                clearable=False,
                className="mb-3"
            )
        ], md=4),

        dbc.Col([
            html.Label("Top N Results:", className="fw-bold"),
            dcc.Slider(
                id='top-n-slider',
                min=5,
                max=30,
                step=5,
                value=10,
                marks={i: str(i) for i in range(5, 35, 5)},
                className="mb-3"
            )
        ], md=4),
    ]),

    dbc.Row([
        dbc.Col([
            html.Label("Filter by Manufacturer (Hersteller):", className="fw-bold"),
            html.Div([
                dcc.Dropdown(
                    id='manufacturer-filter',
                    options=[],
                    value=None,
                    multi=True,
                    placeholder="Select one or more manufacturers (or leave empty for all)",
                    className="mb-3"
                )
            ])
        ], md=12),
    ]),

    html.Hr(),

    dbc.Row([
        dbc.Col([
            html.H4("📊 Aircraft Count by Group", className="mb-3"),
            dcc.Graph(id='bar-chart', style={'height': '500px'})
        ], md=12, lg=6),

        dbc.Col([
            html.H4("📈 Mass Distribution Density", className="mb-3"),
            dcc.Graph(id='density-plot', style={'height': '500px'})
        ], md=12, lg=6),
    ]),

    html.Hr(),

    dbc.Row([
        dbc.Col([
            html.H4("📋 Data Summary", className="mb-3"),
            html.Div(id='data-summary', className="mb-4")
        ])
    ]),

    dbc.Row([
        dbc.Col([
            html.H4("📑 Sample Data", className="mb-3"),
            html.Div(id='data-table', style={'overflowX': 'auto'})
        ])
    ])

], fluid=True, style={'backgroundColor': '#f8f9fa', 'minHeight': '100vh', 'paddingBottom': '50px'})


@callback(
    Output('manufacturer-filter', 'options'),
    Input('sheet-selector', 'value')
)
def update_manufacturer_options(selected_sheet):
    """Update manufacturer dropdown options based on selected sheet"""
    df = load_sheet_data(selected_sheet)

    if df.empty or 'Hersteller' not in df.columns:
        return []

    # Get unique manufacturers and sort them
    manufacturers = sorted(df['Hersteller'].dropna().unique())

    # Create options with manufacturer name and count
    options = []
    for manufacturer in manufacturers:
        count = len(df[df['Hersteller'] == manufacturer])
        options.append({
            'label': f'{manufacturer} ({count} aircraft)',
            'value': manufacturer
        })

    return options


@callback(
    Output('bar-chart', 'figure'),
    Output('density-plot', 'figure'),
    Output('data-summary', 'children'),
    Output('data-table', 'children'),
    Input('sheet-selector', 'value'),
    Input('group-by-selector', 'value'),
    Input('top-n-slider', 'value'),
    Input('manufacturer-filter', 'value')
)
def update_dashboard(selected_sheet, group_by, top_n, selected_manufacturers):
    """Update all dashboard components based on selections"""

    # Load data
    df = load_sheet_data(selected_sheet)

    if df.empty:
        empty_fig = go.Figure()
        empty_fig.add_annotation(text="No data available", showarrow=False)
        return empty_fig, empty_fig, "No data available", ""

    # Apply manufacturer filter if selected
    if selected_manufacturers and len(selected_manufacturers) > 0 and 'Hersteller' in df.columns:
        df = df[df['Hersteller'].isin(selected_manufacturers)]

        if df.empty:
            empty_fig = go.Figure()
            empty_fig.add_annotation(text="No data available for selected manufacturer(s)", showarrow=False)
            return empty_fig, empty_fig, "No data available for selected manufacturer(s)", ""

    # Prepare grouping
    if group_by == 'both':
        # Group by both columns
        if 'Hersteller' in df.columns and 'Herstellerbezeichnung' in df.columns:
            df['Group'] = df['Hersteller'].astype(str) + ' - ' + df['Herstellerbezeichnung'].astype(str)
            group_col = 'Group'
        else:
            group_col = 'Hersteller' if 'Hersteller' in df.columns else df.columns[0]
    else:
        group_col = group_by if group_by in df.columns else df.columns[0]

    # Create bar chart
    group_counts = df[group_col].value_counts().head(top_n)
    bar_fig = px.bar(
        x=group_counts.values,
        y=group_counts.index,
        orientation='h',
        labels={'x': 'Count', 'y': group_col},
        title=f'Top {top_n} {group_col} by Aircraft Count'
    )
    bar_fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        height=500,
        showlegend=False,
        hovermode='closest'
    )
    bar_fig.update_traces(marker_color='rgb(55, 83, 109)')

    # Create density plot
    mass_col = 'höchstzulässige Abflugmasse (kg)'
    if mass_col in df.columns:
        mass_data = df[mass_col].dropna()

        if len(mass_data) > 0:
            density_fig = go.Figure()

            # Add histogram
            density_fig.add_trace(go.Histogram(
                x=mass_data,
                name='Distribution',
                nbinsx=50,
                marker_color='rgba(55, 83, 109, 0.7)',
                yaxis='y',
                histnorm='probability density'
            ))

            # Add KDE (kernel density estimation) using Plotly
            from scipy import stats
            import numpy as np

            kde = stats.gaussian_kde(mass_data)
            x_range = np.linspace(mass_data.min(), mass_data.max(), 200)
            density = kde(x_range)

            density_fig.add_trace(go.Scatter(
                x=x_range,
                y=density,
                mode='lines',
                name='Density',
                line=dict(color='rgb(219, 64, 82)', width=2),
                yaxis='y2'
            ))

            density_fig.update_layout(
                title=f'Distribution of {mass_col}',
                xaxis_title=mass_col,
                yaxis_title='Probability Density',
                yaxis2=dict(
                    title='Density (KDE)',
                    overlaying='y',
                    side='right'
                ),
                height=500,
                showlegend=True,
                hovermode='x unified'
            )
        else:
            density_fig = go.Figure()
            density_fig.add_annotation(text="No mass data available", showarrow=False)
    else:
        density_fig = go.Figure()
        density_fig.add_annotation(text="Mass column not found", showarrow=False)

    # Create summary statistics
    summary_cards = dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Total Aircraft", className="card-title"),
                    html.H3(f"{len(df):,}", className="text-primary")
                ])
            ])
        ], md=3),

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Unique Manufacturers", className="card-title"),
                    html.H3(f"{df['Hersteller'].nunique() if 'Hersteller' in df.columns else 'N/A'}",
                           className="text-success")
                ])
            ])
        ], md=3),

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Average Mass (kg)", className="card-title"),
                    html.H3(f"{df[mass_col].mean():,.0f}" if mass_col in df.columns and not df[mass_col].isna().all() else "N/A",
                           className="text-info")
                ])
            ])
        ], md=3),

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Max Mass (kg)", className="card-title"),
                    html.H3(f"{df[mass_col].max():,.0f}" if mass_col in df.columns and not df[mass_col].isna().all() else "N/A",
                           className="text-warning")
                ])
            ])
        ], md=3),
    ])

    # Create data table preview
    table_data = df.head(10).to_html(classes='table table-striped table-hover', index=False)

    return bar_fig, density_fig, summary_cards, html.Div([html.Div(className="table-responsive",
                                                                     children=html.Iframe(srcDoc=table_data,
                                                                                         style={'width': '100%',
                                                                                                'height': '400px',
                                                                                                'border': 'none'}))])


if __name__ == '__main__':
    print("Starting Aircraft Data Dashboard...")
    print(f"Loading data from: {EXCEL_FILE}")
    print(f"Found {len(sheet_names)} sheets")
    print("\nNavigate to: http://127.0.0.1:8050")
    print("Press Ctrl+C to stop the server\n")

    app.run(debug=True, host='127.0.0.1', port=8050)
