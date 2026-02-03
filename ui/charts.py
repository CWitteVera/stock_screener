"""
Chart generation using Plotly
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Optional

def create_price_chart(df: pd.DataFrame, symbol: str, 
                       entry_price: Optional[float] = None,
                       target_price: Optional[float] = None,
                       stop_price: Optional[float] = None) -> go.Figure:
    """
    Create interactive price chart with indicators
    """
    
    # Create figure with secondary y-axis for volume
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.6, 0.2, 0.2],
        subplot_titles=(f'{symbol} Price & Moving Averages', 'Volume', 'RSI')
    )
    
    # Candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='Price'
        ),
        row=1, col=1
    )
    
    # Moving averages
    if 'SMA_20' in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['SMA_20'],
                name='20-day MA',
                line=dict(color='orange', width=1)
            ),
            row=1, col=1
        )
    
    if 'SMA_50' in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['SMA_50'],
                name='50-day MA',
                line=dict(color='blue', width=1)
            ),
            row=1, col=1
        )
    
    # Add trade levels if provided
    if entry_price:
        fig.add_hline(
            y=entry_price,
            line_dash="dash",
            line_color="yellow",
            annotation_text="Entry",
            row=1, col=1
        )
    
    if target_price:
        fig.add_hline(
            y=target_price,
            line_dash="dash",
            line_color="green",
            annotation_text="Target",
            row=1, col=1
        )
    
    if stop_price:
        fig.add_hline(
            y=stop_price,
            line_dash="dash",
            line_color="red",
            annotation_text="Stop",
            row=1, col=1
        )
    
    # Volume
    colors = ['red' if df['Close'].iloc[i] < df['Open'].iloc[i] else 'green' 
              for i in range(len(df))]
    
    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df['Volume'],
            name='Volume',
            marker_color=colors,
            showlegend=False
        ),
        row=2, col=1
    )
    
    # RSI
    if 'RSI' in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['RSI'],
                name='RSI',
                line=dict(color='purple', width=1),
                showlegend=False
            ),
            row=3, col=1
        )
        
        # RSI reference lines
        fig.add_hline(y=70, line_dash="dash", line_color="red", 
                     annotation_text="Overbought", row=3, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green",
                     annotation_text="Oversold", row=3, col=1)
    
    # Update layout
    fig.update_layout(
        title=f'{symbol} Technical Analysis',
        xaxis_rangeslider_visible=False,
        height=800,
        showlegend=True,
        hovermode='x unified'
    )
    
    # Update y-axes labels
    fig.update_yaxes(title_text="Price ($)", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)
    fig.update_yaxes(title_text="RSI", row=3, col=1)
    
    return fig

def create_macd_chart(df: pd.DataFrame, symbol: str) -> go.Figure:
    """
    Create MACD indicator chart
    """
    fig = go.Figure()
    
    if 'MACD' not in df.columns:
        return fig
    
    # MACD line
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['MACD'],
            name='MACD',
            line=dict(color='blue', width=2)
        )
    )
    
    # Signal line
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['MACD_signal'],
            name='Signal',
            line=dict(color='red', width=2)
        )
    )
    
    # Histogram
    colors = ['green' if val >= 0 else 'red' for val in df['MACD_hist']]
    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df['MACD_hist'],
            name='Histogram',
            marker_color=colors
        )
    )
    
    fig.update_layout(
        title=f'{symbol} MACD Indicator',
        xaxis_title='Date',
        yaxis_title='MACD',
        height=400,
        hovermode='x unified'
    )
    
    return fig

def create_score_radar_chart(trade) -> go.Figure:
    """
    Create radar chart showing trade scores
    """
    categories = ['MACD', 'RSI', 'Volume', 'Breakout', 'Momentum']
    values = [
        trade.macd_score,
        trade.rsi_score,
        trade.volume_score,
        trade.breakout_score,
        trade.momentum_score
    ]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name=trade.symbol
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=False,
        title=f'{trade.symbol} Technical Scores',
        height=400
    )
    
    return fig
