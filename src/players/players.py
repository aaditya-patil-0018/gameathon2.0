import pandas as pd
from tabulate import tabulate
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import numpy as np

class Players:
    def __init__(self, data_path: str = None):
        """Initialize the Players class with the squad data
        
        Args:
            data_path (str, optional): Path to the squad data CSV file. 
                                      If None, uses default path relative to package.
        """
        if data_path is None:
            # Get the package directory and construct path to data
            package_dir = Path(__file__).parent.parent.parent
            self.data_dir = package_dir / "data"
            self.df = pd.read_csv(self.data_dir / "squad_player_names.csv")
        else:
            self.df = pd.read_csv(data_path)
        
        self.columns = self.df.columns
        
        # Add derived columns for better analysis
        self.df['value_score'] = self.df['Credits'] * -1  # Lower credits = higher value
        self.df['role_value'] = self.df.apply(self._calculate_role_value, axis=1)
        self.df['team_value'] = self.df.groupby('Team')['value_score'].transform('mean')

    def _calculate_role_value(self, row: pd.Series) -> float:
        """Calculate value score based on player role and credits"""
        role_multipliers = {
            'ALL': 1.5,  # All-rounders are more valuable
            'BAT': 1.2,  # Batsmen slightly more valuable
            'BOWL': 1.0,  # Bowlers base value
            'WK': 1.3    # Wicket keepers slightly more valuable
        }
        return row['value_score'] * role_multipliers.get(row['Player Type'], 1.0)

    def get_total_teams(self) -> List[str]:
        """Get list of all teams in the tournament
        
        Returns:
            List[str]: List of team names
        """
        return self.df["Team"].unique().tolist()

    def get_team_players(self, teamname: str) -> pd.DataFrame:
        """Get all players from a specific team
        
        Args:
            teamname (str): Name of the team
            
        Returns:
            pd.DataFrame: DataFrame containing player details for the specified team
        """
        return self.df.query(f"Team=='{teamname}'")

    def get_players_by_role(self, teamname: str) -> Dict[str, pd.DataFrame]:
        """Categorize players by their roles for a specific team
        
        Args:
            teamname (str): Name of the team
            
        Returns:
            Dict[str, pd.DataFrame]: Dictionary mapping roles to DataFrames of players
        """
        team_players = self.df.query(f"Team=='{teamname}'")
        roles = {
            'Wicket Keeper': team_players[team_players['Player Type'] == 'WK'],
            'Batsman': team_players[team_players['Player Type'] == 'BAT'],
            'Bowler': team_players[team_players['Player Type'] == 'BOWL'],
            'All-rounder': team_players[team_players['Player Type'] == 'ALL']
        }
        return roles

    def today_match_data(self, team1: str, team2: str) -> Dict:
        """Analyze and compare two teams for today's match
        
        Args:
            team1 (str): Name of the first team
            team2 (str): Name of the second team
            
        Returns:
            Dict: Dictionary containing analysis data for both teams
        """
        # Get players from both teams
        team1_players = self.df.query(f"Team=='{team1}'")
        team2_players = self.df.query(f"Team=='{team2}'")

        # Calculate team statistics
        team1_stats = self._calculate_team_stats(team1_players)
        team2_stats = self._calculate_team_stats(team2_players)

        # Get player roles for both teams
        team1_roles = self.get_players_by_role(team1)
        team2_roles = self.get_players_by_role(team2)

        # Calculate team strengths
        team1_strengths = self.get_team_strengths(team1)
        team2_strengths = self.get_team_strengths(team2)

        return {
            'team1': {
                'name': team1,
                'stats': team1_stats,
                'roles': team1_roles,
                'strengths': team1_strengths
            },
            'team2': {
                'name': team2,
                'stats': team2_stats,
                'roles': team2_roles,
                'strengths': team2_strengths
            }
        }

    def _calculate_team_stats(self, team_df: pd.DataFrame) -> Dict:
        """Calculate various statistics for a team
        
        Args:
            team_df (pd.DataFrame): DataFrame containing team players
            
        Returns:
            Dict: Dictionary containing team statistics
        """
        stats = {
            'total_players': len(team_df),
            'average_credits': team_df['Credits'].mean(),
            'max_credits': team_df['Credits'].max(),
            'role_distribution': team_df['Player Type'].value_counts().to_dict(),
            'top_players': team_df.nlargest(5, 'Credits')[['Player Name', 'Player Type', 'Credits']].to_dict('records'),
            'value_players': team_df.nlargest(5, 'value_score')[['Player Name', 'Player Type', 'Credits', 'value_score']].to_dict('records'),
            'credit_distribution': {
                '0-5': len(team_df[team_df['Credits'] <= 5]),
                '5-10': len(team_df[(team_df['Credits'] > 5) & (team_df['Credits'] <= 10)]),
                '10-15': len(team_df[(team_df['Credits'] > 10) & (team_df['Credits'] <= 15)]),
                '15+': len(team_df[team_df['Credits'] > 15])
            }
        }
        return stats

    def display_match_analysis(self, team1: str, team2: str) -> None:
        """Display a detailed analysis of the match between two teams
        
        Args:
            team1 (str): Name of the first team
            team2 (str): Name of the second team
        """
        match_data = self.today_match_data(team1, team2)
        
        print(f"\n\033[1mMatch Analysis: {team1} vs {team2}\033[0m")
        print("\n" + "="*50)
        
        for team in ['team1', 'team2']:
            team_info = match_data[team]
            print(f"\n\033[1m{team_info['name']} Analysis:\033[0m")
            print(f"Total Players: {team_info['stats']['total_players']}")
            print(f"Average Credits: {team_info['stats']['average_credits']:.2f}")
            print(f"Maximum Credits: {team_info['stats']['max_credits']}")
            
            print("\nRole Distribution:")
            for role, count in team_info['stats']['role_distribution'].items():
                print(f"- {role}: {count}")
            
            print("\nTop Players:")
            for player in team_info['stats']['top_players']:
                print(f"- {player['Player Name']} ({player['Player Type']}) - {player['Credits']} credits")
            
            print("\nValue Players:")
            for player in team_info['stats']['value_players']:
                print(f"- {player['Player Name']} ({player['Player Type']}) - {player['Credits']} credits (Value Score: {player['value_score']:.2f})")
            
            print("\nCredit Distribution:")
            for range_name, count in team_info['stats']['credit_distribution'].items():
                print(f"- {range_name}: {count} players")
            
            print("\n" + "-"*50)

    def search_players(self, query: str, team: Optional[str] = None) -> pd.DataFrame:
        """Search for players by name or partial name
        
        Args:
            query (str): Search query (case-insensitive)
            team (str, optional): Filter by team name
            
        Returns:
            pd.DataFrame: DataFrame containing matching players
        """
        mask = self.df['Player Name'].str.contains(query, case=False, na=False)
        if team:
            mask &= self.df['Team'] == team
        return self.df[mask]

    def get_players_by_credit_range(self, min_credits: float, max_credits: float) -> pd.DataFrame:
        """Get players within a specific credit range
        
        Args:
            min_credits (float): Minimum credits
            max_credits (float): Maximum credits
            
        Returns:
            pd.DataFrame: DataFrame containing players within the credit range
        """
        return self.df[
            (self.df['Credits'] >= min_credits) & 
            (self.df['Credits'] <= max_credits)
        ]

    def compare_teams(self, team1: str, team2: str) -> Dict:
        """Compare two teams based on various metrics
        
        Args:
            team1 (str): Name of the first team
            team2 (str): Name of the second team
            
        Returns:
            Dict: Dictionary containing comparison metrics
        """
        team1_data = self.df[self.df['Team'] == team1]
        team2_data = self.df[self.df['Team'] == team2]
        
        comparison = {
            'team1': {
                'name': team1,
                'total_credits': team1_data['Credits'].sum(),
                'avg_credits': team1_data['Credits'].mean(),
                'role_distribution': team1_data['Player Type'].value_counts().to_dict(),
                'top_5_players': team1_data.nlargest(5, 'Credits')[['Player Name', 'Player Type', 'Credits']].to_dict('records'),
                'value_players': team1_data.nlargest(5, 'value_score')[['Player Name', 'Player Type', 'Credits', 'value_score']].to_dict('records')
            },
            'team2': {
                'name': team2,
                'total_credits': team2_data['Credits'].sum(),
                'avg_credits': team2_data['Credits'].mean(),
                'role_distribution': team2_data['Player Type'].value_counts().to_dict(),
                'top_5_players': team2_data.nlargest(5, 'Credits')[['Player Name', 'Player Type', 'Credits']].to_dict('records'),
                'value_players': team2_data.nlargest(5, 'value_score')[['Player Name', 'Player Type', 'Credits', 'value_score']].to_dict('records')
            },
            'comparison': {
                'credit_difference': team1_data['Credits'].sum() - team2_data['Credits'].sum(),
                'avg_credit_difference': team1_data['Credits'].mean() - team2_data['Credits'].mean(),
                'role_balance': self._compare_role_distribution(team1_data, team2_data),
                'value_comparison': {
                    'team1_value': team1_data['value_score'].mean(),
                    'team2_value': team2_data['value_score'].mean(),
                    'value_difference': team1_data['value_score'].mean() - team2_data['value_score'].mean()
                }
            }
        }
        return comparison

    def _compare_role_distribution(self, team1_data: pd.DataFrame, team2_data: pd.DataFrame) -> Dict:
        """Compare role distribution between two teams
        
        Args:
            team1_data (pd.DataFrame): First team's data
            team2_data (pd.DataFrame): Second team's data
            
        Returns:
            Dict: Dictionary containing role comparison metrics
        """
        team1_roles = team1_data['Player Type'].value_counts()
        team2_roles = team2_data['Player Type'].value_counts()
        
        comparison = {}
        all_roles = set(team1_roles.index) | set(team2_roles.index)
        
        for role in all_roles:
            team1_count = team1_roles.get(role, 0)
            team2_count = team2_roles.get(role, 0)
            comparison[role] = {
                'team1_count': team1_count,
                'team2_count': team2_count,
                'difference': team1_count - team2_count
            }
        
        return comparison

    def get_value_players(self, team: Optional[str] = None, min_credits: float = 0) -> pd.DataFrame:
        """Get players with high value for money (low credits but high potential)
        
        Args:
            team (str, optional): Filter by team name
            min_credits (float): Minimum credits threshold
            
        Returns:
            pd.DataFrame: DataFrame containing value players
        """
        df = self.df[self.df['Credits'] >= min_credits]
        if team:
            df = df[df['Team'] == team]
            
        # Sort by role value score
        return df.nlargest(10, 'role_value')

    def analyze_squad_composition(self, team: str) -> Dict:
        """Analyze the composition of a team's squad
        
        Args:
            team (str): Name of the team
            
        Returns:
            Dict: Dictionary containing squad composition analysis
        """
        team_data = self.df[self.df['Team'] == team]
        
        analysis = {
            'total_players': len(team_data),
            'credit_distribution': {
                'min': team_data['Credits'].min(),
                'max': team_data['Credits'].max(),
                'mean': team_data['Credits'].mean(),
                'median': team_data['Credits'].median(),
                'std': team_data['Credits'].std()
            },
            'role_distribution': team_data['Player Type'].value_counts().to_dict(),
            'credit_ranges': {
                '0-5': len(team_data[team_data['Credits'] <= 5]),
                '5-10': len(team_data[(team_data['Credits'] > 5) & (team_data['Credits'] <= 10)]),
                '10-15': len(team_data[(team_data['Credits'] > 10) & (team_data['Credits'] <= 15)]),
                '15+': len(team_data[team_data['Credits'] > 15])
            },
            'value_analysis': {
                'avg_value_score': team_data['value_score'].mean(),
                'top_value_players': team_data.nlargest(5, 'value_score')[['Player Name', 'Player Type', 'Credits', 'value_score']].to_dict('records')
            }
        }
        return analysis

    def get_team_strengths(self, team: str) -> Dict:
        """Analyze team strengths based on player distribution
        
        Args:
            team (str): Name of the team
            
        Returns:
            Dict: Dictionary containing team strength analysis
        """
        team_data = self.df[self.df['Team'] == team]
        
        strengths = {
            'batting_strength': len(team_data[team_data['Player Type'].isin(['BAT', 'ALL'])]),
            'bowling_strength': len(team_data[team_data['Player Type'].isin(['BOWL', 'ALL'])]),
            'keeping_strength': len(team_data[team_data['Player Type'] == 'WK']),
            'all_rounder_strength': len(team_data[team_data['Player Type'] == 'ALL']),
            'total_credits': team_data['Credits'].sum(),
            'avg_player_credits': team_data['Credits'].mean(),
            'value_strength': team_data['value_score'].mean(),
            'role_value_strength': team_data['role_value'].mean()
        }
        
        # Calculate strength ratios
        total_players = len(team_data)
        strengths.update({
            'batting_ratio': strengths['batting_strength'] / total_players,
            'bowling_ratio': strengths['bowling_strength'] / total_players,
            'keeping_ratio': strengths['keeping_strength'] / total_players,
            'all_rounder_ratio': strengths['all_rounder_strength'] / total_players
        })
        
        return strengths

    def display_team_strengths(self, team: str) -> None:
        """Display a formatted analysis of team strengths
        
        Args:
            team (str): Name of the team
        """
        strengths = self.get_team_strengths(team)
        
        print(f"\n\033[1mTeam Strengths Analysis: {team}\033[0m")
        print("\n" + "="*50)
        
        print("\nPlayer Distribution:")
        print(f"Total Players: {strengths['batting_strength'] + strengths['bowling_strength']}")
        print(f"Batsmen: {strengths['batting_strength']} ({strengths['batting_ratio']*100:.1f}%)")
        print(f"Bowlers: {strengths['bowling_strength']} ({strengths['bowling_ratio']*100:.1f}%)")
        print(f"Wicket Keepers: {strengths['keeping_strength']} ({strengths['keeping_ratio']*100:.1f}%)")
        print(f"All-rounders: {strengths['all_rounder_strength']} ({strengths['all_rounder_ratio']*100:.1f}%)")
        
        print("\nCredit Analysis:")
        print(f"Total Credits: {strengths['total_credits']:.1f}")
        print(f"Average Player Credits: {strengths['avg_player_credits']:.1f}")
        
        print("\nValue Analysis:")
        print(f"Average Value Score: {strengths['value_strength']:.2f}")
        print(f"Average Role Value: {strengths['role_value_strength']:.2f}")
        
        print("\n" + "-"*50) 