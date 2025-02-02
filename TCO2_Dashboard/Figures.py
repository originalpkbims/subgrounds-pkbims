import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pycountry
from collections import defaultdict
from helpers import add_px_figure
from plotly.subplots import make_subplots
from colors import colors, fonts


def sub_plots_volume(sd_pool, last_sd_pool, title_indicator, title_graph):
    fig = make_subplots(
        rows=2,
        cols=1,
        specs=[[{"type": "domain"}], [{"type": "xy"}]],
        subplot_titles=("", title_graph),
        vertical_spacing=0.1,
    )

    fig.update_layout(font_color='white')

    fig.add_trace(go.Indicator(
        mode="number+delta",
        value=sum(sd_pool['Quantity']),
        title=dict(text=title_indicator, font=dict(size=20)),
        number=dict(suffix=" tCO2", font=dict(size=52)),
        delta={'position': "bottom", 'reference': sum(
            last_sd_pool['Quantity']), 'relative': True, 'valueformat': '.1%'},
        domain={'x': [0.25, .75], 'y': [0.6, 1]}))

    add_px_figure(
        px.bar(
            sd_pool.groupby("Date")['Quantity'].sum().reset_index(),
            x="Date",
            y="Quantity",
            title=title_graph,
        ),
        fig,
        row=2, col=1)

    fig.update_layout(height=600, paper_bgcolor=colors['bg_color'], plot_bgcolor=colors['bg_color'], xaxis=dict(showgrid=False),
                      yaxis=dict(showgrid=False), font_size=20)
    return fig


def sub_plots_vintage(sd_pool, last_sd_pool, title_indicator, title_graph):
    fig = make_subplots(
        rows=2,
        cols=1,
        specs=[[{"type": "domain"}], [{"type": "xy"}]],
        subplot_titles=("", title_graph),
        vertical_spacing=0.1,
    )
    fig.update_layout(font_color='white')

    fig.add_trace(go.Indicator(
        mode="number+delta",
        value=np.average(sd_pool['Vintage'], weights=sd_pool['Quantity']),
        number=dict(valueformat=".1f", font=dict(size=52)),
        delta={"reference": np.average(
            last_sd_pool['Vintage'], weights=last_sd_pool['Quantity']), "valueformat": ".1f"},
        title=dict(text=title_indicator, font=dict(size=20)),
        domain={'x': [0.25, .75], 'y': [0.6, 1]}))

    add_px_figure(
        px.bar(
            sd_pool.groupby('Vintage')[
                'Quantity'].sum().to_frame().reset_index(),
            x='Vintage',
            y='Quantity',
            title=title_graph
        ),
        fig,
        row=2, col=1
    )
    fig.update_layout(height=600, paper_bgcolor=colors['bg_color'], plot_bgcolor=colors['bg_color'], xaxis=dict(showgrid=False),
                      yaxis=dict(showgrid=False), font_size=20)

    return fig


def map(df, title):

    country_index = defaultdict(str, {country: pycountry.countries.search_fuzzy(country)[
                                0].alpha_3 for country in df.Region.astype(str).unique() if country != 'nan'})
    country_volumes = df.groupby('Region')['Quantity'].sum(
    ).sort_values(ascending=False).to_frame().reset_index()
    country_volumes['Country Code'] = [country_index[country]
                                       for country in country_volumes['Region']]
    fig = px.choropleth(country_volumes, locations="Country Code",
                        color="Quantity",
                        hover_name='Region',
                        color_continuous_scale=px.colors.sequential.Plasma,
                        height=600)

    fig.update_layout(geo=dict(bgcolor='rgba(0,0,0,0)', lakecolor='#4E5D6C',
                               landcolor='darkgrey',
                               subunitcolor='grey'), title=dict(
        text=title,
        x=0.5, font=dict(
            color=colors['kg_color_sub2'],
            size=fonts['figure'])),
        font_color='white', dragmode=False, paper_bgcolor=colors['bg_color'], font_size=20)
    return fig


def total_volume(sd_pool):
    fig = make_subplots(
        rows=2,
        cols=1,
        specs=[[{"type": "domain"}], [{"type": "xy"}]],
        vertical_spacing=0.1,
        subplot_titles=("", "")
    )
    fig.update_layout(font_color='white')

    fig.add_trace(go.Indicator(
        mode="number",
        value=sum(sd_pool['Quantity']),
        title=dict(text="Credits tokenized (total)", font=dict(size=20)),
        number=dict(suffix=" tCO2", font=dict(size=52)),
        domain={'x': [0.25, .75], 'y': [0.6, 1]}))

    add_px_figure(
        px.bar(
            sd_pool.groupby("Date")['Quantity'].sum().reset_index(),
            x="Date",
            y="Quantity",
            title=""
        ),
        fig,
        row=2, col=1)

    fig.update_layout(height=600, paper_bgcolor=colors['bg_color'], plot_bgcolor=colors['bg_color'], xaxis=dict(showgrid=False),
                      yaxis=dict(showgrid=False), font_size=20)
    return fig


def total_vintage(sd_pool):
    fig = make_subplots(
        rows=2,
        cols=1,
        specs=[[{"type": "domain"}], [{"type": "xy"}]],
        vertical_spacing=0.1,
        subplot_titles=("", "")
    )
    fig.update_layout(font_color='white')

    fig.add_trace(go.Indicator(
        mode="number",
        value=np.average(sd_pool['Vintage'], weights=sd_pool['Quantity']),
        number=dict(valueformat=".1f", font=dict(size=52)),
        title=dict(text="Average Credit Vintage (total)", font=dict(size=20)),
        domain={'x': [0.25, .75], 'y': [0.6, 1]}))
    add_px_figure(
        px.bar(
            sd_pool.groupby('Vintage')[
                'Quantity'].sum().to_frame().reset_index(),
            x='Vintage',
            y='Quantity',
            title=''
        ),
        fig,
        row=2, col=1
    )

    fig.update_layout(height=600, paper_bgcolor=colors['bg_color'], plot_bgcolor=colors['bg_color'], xaxis=dict(showgrid=False),
                      yaxis=dict(showgrid=False), font_size=20)
    return fig


def methodology_volume_vs_region(df):
    fig = px.bar(
        df.groupby('Methodology')['Quantity'].sum().to_frame().reset_index(),
        x='Methodology',
        y='Quantity',
        title=''
    )
    fig.update_layout(height=600, paper_bgcolor=colors['bg_color'], plot_bgcolor=colors['bg_color'], xaxis=dict(showgrid=False),
                      yaxis=dict(showgrid=False), font_color='white', font_size=20)
    return fig

def pool_pie_chart(df):
    labels = ['BCT', 'NCT', 'TCO2']
    BCT = df['BCT Quantity'].sum()
    NCT = df['NCT Quantity'].sum()
    TCO2 = df['Total Quantity'].sum()-BCT-NCT
    values = [BCT, NCT, TCO2]
    fig = go.Figure()
    fig.add_trace(go.Pie(labels=labels, values=values,  textinfo='percent', textfont=dict(
        color='white', size=20), hoverlabel=dict(font_color='white', font_size=20), hole=.3))
    fig.update_layout(
        # title=dict(
        #     # text='BCT Composition based on Eligible TCO2',
        #     x=0.5,
        #     font=dict(
        #         color=colors['kg_color_sub2'],size=20
        #     )),
        paper_bgcolor=colors['bg_color'], font_color='white', font_size=20)

    return fig


def eligible_pool_pie_chart(df, pool_key):
    if pool_key == "BCT":
        df = df[df["Vintage"] >= 2008].reset_index()
    elif pool_key == "NCT":
        df = df[df["Vintage"] >= 2012].reset_index()
    labels = [pool_key, f'NON_{pool_key}']
    BCT = df[f'{pool_key} Quantity'].sum()
    Non_BCT = df['Total Quantity'].sum()-BCT
    values = [BCT, Non_BCT]
    fig_eligible = go.Figure()
    fig_eligible.add_trace(go.Pie(labels=labels, values=values,  textinfo='percent', textfont=dict(
        color='white', size=20), hoverlabel=dict(font_color='white', font_size=20), hole=.3))
    fig_eligible.update_traces(marker=dict(colors=['red', 'green']))

    fig_eligible.update_layout(
        # title=dict(
        # text=f'How much of Eligible TCO2 is exchanged for {pool_key}?',
        # x=0.5,
        # font=dict(
        #     color=colors['kg_color_sub2'],size=20
        # )),
        paper_bgcolor=colors['bg_color'], font_color='white', font_size=20)
    return fig_eligible
