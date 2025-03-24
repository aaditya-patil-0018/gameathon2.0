import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path
import numpy as np
from datetime import datetime

# Add the project root directory to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.players.players import Players
from typing import Dict, List
import numpy as np

# Set page config
st.set_page_config(
    page_title="Cricket Team Analysis Dashboard",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border: none;
    }
    .stMetric:hover {
        transform: translateY(-2px);
        transition: transform 0.2s ease-in-out;
    }
    .css-1d391kg {
        padding-top: 2rem;
    }
    .stPlotlyChart {
        background-color: transparent !important;
        padding: 0 !important;
        border-radius: 0 !important;
        box-shadow: none !important;
    }
    .js-plotly-plot {
        background-color: transparent !important;
    }
    .plotly-graph-div {
        background-color: transparent !important;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize the Players class
@st.cache_resource
def get_players():
    return Players()

def plot_role_distribution(team_data: pd.DataFrame, team_name: str):
    """Plot role distribution for a team"""
    role_counts = team_data['Player Type'].value_counts()
    fig = px.pie(
        values=role_counts.values, 
        names=role_counts.index,
        title=f"Role Distribution - {team_name}",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig.update_traces(textinfo='percent+label')
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        title=dict(
            font=dict(size=16, color='#2c3e50'),
            x=0.5,
            y=0.95
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    return fig

def plot_credit_distribution(team_data: pd.DataFrame, team_name: str):
    """Plot credit distribution for a team"""
    fig = px.histogram(
        team_data,
        x='Credits',
        title=f"Credit Distribution - {team_name}",
        nbins=20,
        color_discrete_sequence=['#3498db']
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        title=dict(
            font=dict(size=16, color='#2c3e50'),
            x=0.5,
            y=0.95
        ),
        xaxis_title="Credits",
        yaxis_title="Number of Players",
        showlegend=False,
        bargap=0.1
    )
    return fig

def plot_team_comparison(team1_data: pd.DataFrame, team2_data: pd.DataFrame, team1_name: str, team2_name: str):
    """Plot comparison between two teams"""
    # Role comparison
    role_comparison = pd.DataFrame({
        team1_name: team1_data['Player Type'].value_counts(),
        team2_name: team2_data['Player Type'].value_counts()
    }).fillna(0)
    
    fig = go.Figure()
    colors = ['#3498db', '#e74c3c']
    for idx, team in enumerate([team1_name, team2_name]):
        fig.add_trace(go.Bar(
            name=team,
            x=role_comparison.index,
            y=role_comparison[team],
            text=role_comparison[team],
            textposition='auto',
            marker_color=colors[idx]
        ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        title=dict(
            text="Role Distribution Comparison",
            font=dict(size=16, color='#2c3e50'),
            x=0.5,
            y=0.95
        ),
        barmode='group',
        bargap=0.15,
        bargroupgap=0.1,
        xaxis_title="Player Role",
        yaxis_title="Number of Players",
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    return fig

def plot_team_strength_radar(team_data: pd.DataFrame, team_name: str):
    """Plot team strength radar chart"""
    # Calculate team strengths
    batting_strength = len(team_data[team_data['Player Type'].isin(['BAT', 'ALL'])])
    bowling_strength = len(team_data[team_data['Player Type'].isin(['BOWL', 'ALL'])])
    keeping_strength = len(team_data[team_data['Player Type'] == 'WK'])
    all_rounder_strength = len(team_data[team_data['Player Type'] == 'ALL'])
    credit_strength = team_data['Credits'].mean()
    
    # Normalize values
    max_values = {
        'Batting': 20,
        'Bowling': 20,
        'Keeping': 5,
        'All-Rounders': 10,
        'Credit Value': 10
    }
    
    categories = ['Batting', 'Bowling', 'Keeping', 'All-Rounders', 'Credit Value']
    values = [
        batting_strength / max_values['Batting'],
        bowling_strength / max_values['Bowling'],
        keeping_strength / max_values['Keeping'],
        all_rounder_strength / max_values['All-Rounders'],
        credit_strength / max_values['Credit Value']
    ]
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name=team_name,
        line=dict(color='#3498db'),
        fillcolor='rgba(52, 152, 219, 0.2)'
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                tickfont=dict(size=10)
            ),
            angularaxis=dict(
                tickfont=dict(size=10)
            )
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        title=dict(
            text=f"Team Strength Analysis - {team_name}",
            font=dict(size=16, color='#2c3e50'),
            x=0.5,
            y=0.95
        )
    )
    return fig

def get_fantasy_suggestions(players: Players, team: str = None):
    """Get fantasy team suggestions based on value and role balance"""
    df = players.df
    if team:
        df = df[df['Team'] == team]
    
    # Calculate value score (lower credits = higher value)
    df['value_score'] = df['Credits'] * -1
    
    # Get top players by role
    suggestions = {
        'Wicket Keepers': df[df['Player Type'] == 'WK'].nlargest(2, 'value_score'),
        'Batsmen': df[df['Player Type'] == 'BAT'].nlargest(4, 'value_score'),
        'Bowlers': df[df['Player Type'] == 'BOWL'].nlargest(4, 'value_score'),
        'All-Rounders': df[df['Player Type'] == 'ALL'].nlargest(2, 'value_score')
    }
    
    return suggestions

def main():
    st.title("Cricket Team Analysis Dashboard")
    
    # Initialize Players class
    players = get_players()
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Select Analysis",
        ["Team Overview", "Team Comparison", "Player Search", "Value Analysis", "Fantasy Suggestions"]
    )
    
    # Add date and time
    st.sidebar.markdown(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if page == "Team Overview":
        st.header("Team Overview")
        
        # Team selection with search
        teams = players.get_total_teams()
        selected_team = st.selectbox("Select Team", teams)
        
        # Get team data
        team_data = players.get_team_players(selected_team)
        
        # Display team logo and basic stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Players", len(team_data))
        with col2:
            st.metric("Average Credits", f"{team_data['Credits'].mean():.2f}")
        with col3:
            st.metric("Max Credits", f"{team_data['Credits'].max():.2f}")
        with col4:
            st.metric("Total Credits", f"{team_data['Credits'].sum():.2f}")
        
        # Display role distribution and credit distribution side by side
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(plot_role_distribution(team_data, selected_team), use_container_width=True)
        with col2:
            st.plotly_chart(plot_credit_distribution(team_data, selected_team), use_container_width=True)
        
        # Display team strength radar chart
        st.plotly_chart(plot_team_strength_radar(team_data, selected_team), use_container_width=True)
        
        # Display detailed player list with filters
        st.subheader("Team Players")
        role_filter = st.multiselect("Filter by Role", team_data['Player Type'].unique())
        credit_range = st.slider("Credit Range", float(team_data['Credits'].min()), float(team_data['Credits'].max()), (float(team_data['Credits'].min()), float(team_data['Credits'].max())))
        
        filtered_data = team_data[
            (team_data['Credits'] >= credit_range[0]) & 
            (team_data['Credits'] <= credit_range[1])
        ]
        if role_filter:
            filtered_data = filtered_data[filtered_data['Player Type'].isin(role_filter)]
        
        st.dataframe(filtered_data)
        
    elif page == "Team Comparison":
        st.header("Team Comparison")
        
        # Team selection with search
        col1, col2 = st.columns(2)
        with col1:
            team1 = st.selectbox("Select First Team", players.get_total_teams())
        with col2:
            team2 = st.selectbox("Select Second Team", players.get_total_teams())
        
        # Get comparison data
        comparison = players.compare_teams(team1, team2)
        
        # Display comparison plots
        team1_data = players.get_team_players(team1)
        team2_data = players.get_team_players(team2)
        
        st.plotly_chart(plot_team_comparison(team1_data, team2_data, team1, team2), use_container_width=True)
        
        # Display detailed comparison with metrics
        st.subheader("Detailed Comparison")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**{team1} Analysis**")
            st.metric("Total Credits", f"{comparison['team1']['total_credits']:.2f}")
            st.metric("Average Credits", f"{comparison['team1']['avg_credits']:.2f}")
            st.write("Role Distribution:")
            for role, count in comparison['team1']['role_distribution'].items():
                st.write(f"- {role}: {count}")
            st.write("Top Players:")
            for player in comparison['team1']['top_5_players']:
                st.write(f"- {player['Player Name']} ({player['Player Type']}) - {player['Credits']} credits")
        
        with col2:
            st.write(f"**{team2} Analysis**")
            st.metric("Total Credits", f"{comparison['team2']['total_credits']:.2f}")
            st.metric("Average Credits", f"{comparison['team2']['avg_credits']:.2f}")
            st.write("Role Distribution:")
            for role, count in comparison['team2']['role_distribution'].items():
                st.write(f"- {role}: {count}")
            st.write("Top Players:")
            for player in comparison['team2']['top_5_players']:
                st.write(f"- {player['Player Name']} ({player['Player Type']}) - {player['Credits']} credits")
        
        # Display comparison metrics
        st.subheader("Comparison Metrics")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Credit Difference", f"{comparison['comparison']['credit_difference']:.2f}")
        with col2:
            st.metric("Average Credit Difference", f"{comparison['comparison']['avg_credit_difference']:.2f}")
        with col3:
            st.metric("Role Balance Score", f"{sum(abs(comp['difference']) for comp in comparison['comparison']['role_balance'].values()):.2f}")
        
    elif page == "Player Search":
        st.header("Player Search")
        
        # Advanced search interface
        col1, col2 = st.columns(2)
        with col1:
            search_query = st.text_input("Search Players", "")
        with col2:
            team_filter = st.selectbox("Filter by Team", ["All"] + players.get_total_teams())
        
        col1, col2 = st.columns(2)
        with col1:
            role_filter = st.multiselect("Filter by Role", ["BAT", "BOWL", "ALL", "WK"])
        with col2:
            credit_range = st.slider("Credit Range", 0.0, 20.0, (0.0, 20.0), 0.5)
        
        if search_query or role_filter or credit_range != (0.0, 20.0):
            team = None if team_filter == "All" else team_filter
            results = players.search_players(search_query, team)
            
            if role_filter:
                results = results[results['Player Type'].isin(role_filter)]
            
            results = results[
                (results['Credits'] >= credit_range[0]) & 
                (results['Credits'] <= credit_range[1])
            ]
            
            if not results.empty:
                st.write(f"Found {len(results)} players")
                
                # Display results in a nice format
                for _, player in results.iterrows():
                    with st.expander(f"{player['Player Name']} ({player['Team']})"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.write(f"**Role:** {player['Player Type']}")
                        with col2:
                            st.write(f"**Credits:** {player['Credits']}")
                        with col3:
                            st.write(f"**Team:** {player['Team']}")
            else:
                st.warning("No players found matching your search criteria")
        
    elif page == "Value Analysis":
        st.header("Value Analysis")
        
        # Team selection
        team = st.selectbox("Select Team for Value Analysis", ["All"] + players.get_total_teams())
        
        # Advanced filters
        col1, col2 = st.columns(2)
        with col1:
            min_credits = st.slider("Minimum Credits Threshold", 0.0, 20.0, 0.0, 0.5)
        with col2:
            role_filter = st.multiselect("Filter by Role", ["BAT", "BOWL", "ALL", "WK"])
        
        # Get value players
        team_filter = None if team == "All" else team
        value_players = players.get_value_players(team_filter, min_credits)
        
        if role_filter:
            value_players = value_players[value_players['Player Type'].isin(role_filter)]
        
        if not value_players.empty:
            st.write("Top Value Players (Low Credits, High Potential)")
            
            # Display value players in a nice format
            for _, player in value_players.iterrows():
                with st.expander(f"{player['Player Name']} ({player['Team']})"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**Role:** {player['Player Type']}")
                    with col2:
                        st.write(f"**Credits:** {player['Credits']}")
                    with col3:
                        st.write(f"**Value Score:** {player['value_score']:.2f}")
            
            # Plot value distribution
            fig = px.scatter(
                value_players,
                x='Credits',
                y='value_score',
                hover_data=['Player Name', 'Player Type', 'Team'],
                title="Value vs Credits Distribution",
                color='Player Type',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12),
                title=dict(
                    font=dict(size=16, color='#2c3e50'),
                    x=0.5,
                    y=0.95
                ),
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No players found matching your criteria")
            
    elif page == "Fantasy Suggestions":
        st.header("Fantasy Team Suggestions")
        
        # Team selection
        team = st.selectbox("Select Team for Fantasy Suggestions", ["All"] + players.get_total_teams())
        
        # Get fantasy suggestions
        suggestions = get_fantasy_suggestions(players, team if team != "All" else None)
        
        # Display suggestions in a nice format
        st.subheader("Recommended Fantasy Team")
        
        for role, players_df in suggestions.items():
            with st.expander(f"{role} ({len(players_df)} players)"):
                for _, player in players_df.iterrows():
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**{player['Player Name']}**")
                    with col2:
                        st.write(f"**Team:** {player['Team']}")
                    with col3:
                        st.write(f"**Credits:** {player['Credits']}")
        
        # Calculate total credits
        total_credits = sum(df['Credits'].sum() for df in suggestions.values())
        st.metric("Total Team Credits", f"{total_credits:.2f}")

if __name__ == "__main__":
    main()
