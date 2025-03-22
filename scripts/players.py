import pandas as pd
from tabulate import tabulate
from typing import Dict, List, Tuple

class Players:

    def __init__(self):
        """Initialize the Players class with the squad data"""
        self.df = pd.read_csv("../data/squad_player_names.csv")
        self.columns = self.df.columns
        print(f"\n\033[33mColumns in database => {list(self.df.columns)}\033[0m") # to understand the columns present in the dataframe

    def get_total_teams(self):
        """Get list of all teams in the tournament"""
        teams = self.df["Team"].unique()
        print("\nTeams:")
        for n, team_name in enumerate(teams):
            print(f"{n+1}: {team_name}")
        print("\n")
        return teams

    def get_team_players(self, teamname: str) -> pd.DataFrame:
        """Get all players from a specific team"""
        player_details = self.df.query(f"Team=='{teamname}'")
        print(tabulate(player_details, headers=self.columns, tablefmt="grid", showindex=False))
        return player_details

    def get_players_by_role(self, teamname: str) -> Dict[str, pd.DataFrame]:
        """Categorize players by their roles for a specific team"""
        team_players = self.df.query(f"Team=='{teamname}'")
        roles = {
            'Wicket Keeper': team_players[team_players['Player Type'] == 'WK'],
            'Batsman': team_players[team_players['Player Type'] == 'BAT'],
            'Bowler': team_players[team_players['Player Type'] == 'BOWL'],
            'All-rounder': team_players[team_players['Player Type'] == 'ALL']
        }
        return roles

    def today_match_data(self, team1: str, team2: str) -> Dict:
        """Analyze and compare two teams for today's match"""
        # Get players from both teams
        team1_players = self.df.query(f"Team=='{team1}'")
        team2_players = self.df.query(f"Team=='{team2}'")

        # Calculate team statistics
        team1_stats = self._calculate_team_stats(team1_players)
        team2_stats = self._calculate_team_stats(team2_players)

        # Get player roles for both teams
        team1_roles = self.get_players_by_role(team1)
        team2_roles = self.get_players_by_role(team2)

        return {
            'team1': {
                'name': team1,
                'stats': team1_stats,
                'roles': team1_roles
            },
            'team2': {
                'name': team2,
                'stats': team2_stats,
                'roles': team2_roles
            }
        }

    def _calculate_team_stats(self, team_df: pd.DataFrame) -> Dict:
        """Calculate various statistics for a team"""
        stats = {
            'total_players': len(team_df),
            'average_credits': team_df['Credits'].mean(),
            'max_credits': team_df['Credits'].max(),
            'role_distribution': team_df['Player Type'].value_counts().to_dict(),
            'top_players': team_df.nlargest(5, 'Credits')[['Player Name', 'Player Type', 'Credits']].to_dict('records')
        }
        return stats

    def display_match_analysis(self, team1: str, team2: str):
        """Display a detailed analysis of the match between two teams"""
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
            
            print("\n" + "-"*50)

# run the code for testing purpose
# whenever this file is runned
if __name__ == "__main__":
    # create object of the players
    player = Players()

    print("Commands to use:")
    print("[1] Get total teams")
    print("[2] Get team players data")
    print("[3] Today's Match Analysis")
    print("[4] Get players by role")
    print("[5] Exit")

    run = True
    while run:
        command = int(input("\ncommand > "))
        if command == 1:
            player.get_total_teams()
        elif command == 2:
            team_name = input("Team name: ")
            player.get_team_players(teamname=team_name)
        elif command == 3:
            team1 = input("Team 1: ")
            team2 = input("Team 2: ")
            player.display_match_analysis(team1, team2)
        elif command == 4:
            team_name = input("Team name: ")
            roles = player.get_players_by_role(team_name)
            for role, players in roles.items():
                print(f"\n{role}:")
                print(tabulate(players, headers=player.columns, tablefmt="grid", showindex=False))
        elif command == 5:
            run = False
        else:
            print("Invalid command. Please try again.")
