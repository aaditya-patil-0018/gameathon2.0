#!/usr/bin/env python3
import sys
from pathlib import Path
import pandas as pd
from tabulate import tabulate
from typing import Dict, List, Optional
import argparse

# Add the project root directory to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.players.players import Players

def print_header(text: str) -> None:
    """Print a formatted header"""
    print("\n" + "="*50)
    print(f"\033[1m{text}\033[0m")
    print("="*50 + "\n")

def print_subheader(text: str) -> None:
    """Print a formatted subheader"""
    print(f"\n\033[1m{text}\033[0m")
    print("-"*30)

def display_menu() -> None:
    """Display the main menu options"""
    print_header("Cricket Team Analysis CLI")
    print("1. Display Team Statistics")
    print("2. Compare Two Teams")
    print("3. Search Players")
    print("4. Analyze Squad Composition")
    print("5. Display Team Strengths")
    print("6. Get Value Players")
    print("7. Get Players by Credit Range")
    print("8. Display Match Analysis")
    print("9. Exit")
    print("\n" + "="*50)

def get_team_selection(players: Players) -> str:
    """Get team selection from user"""
    teams = players.get_total_teams()
    print("\nAvailable teams:")
    for i, team in enumerate(teams, 1):
        print(f"{i}. {team}")
    
    while True:
        try:
            choice = int(input("\nSelect team number: "))
            if 1 <= choice <= len(teams):
                return teams[choice - 1]
            print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

def get_credit_range() -> tuple:
    """Get credit range from user"""
    while True:
        try:
            min_credits = float(input("Enter minimum credits: "))
            max_credits = float(input("Enter maximum credits: "))
            if min_credits <= max_credits:
                return min_credits, max_credits
            print("Minimum credits must be less than or equal to maximum credits.")
        except ValueError:
            print("Please enter valid numbers.")

def display_team_stats(players: Players) -> None:
    """Display statistics for a selected team"""
    team = get_team_selection(players)
    team_data = players.get_team_players(team)
    
    print_header(f"Team Statistics: {team}")
    
    # Display basic stats
    print_subheader("Basic Statistics")
    print(f"Total Players: {len(team_data)}")
    print(f"Average Credits: {team_data['Credits'].mean():.2f}")
    
    # Display role distribution
    print_subheader("Role Distribution")
    roles = players.get_players_by_role(team)
    for role, players_df in roles.items():
        print(f"{role}: {len(players_df)} players")
    
    # Display top players
    print_subheader("Top Players")
    top_players = team_data.nlargest(5, 'Credits')
    print(tabulate(top_players[['Player Name', 'Player Type', 'Credits']], 
                  headers='keys', tablefmt='grid'))

def compare_teams(players: Players) -> None:
    """Compare two teams"""
    print_header("Compare Teams")
    
    print("Select first team:")
    team1 = get_team_selection(players)
    print("\nSelect second team:")
    team2 = get_team_selection(players)
    
    comparison = players.compare_teams(team1, team2)
    
    print_header(f"Team Comparison: {team1} vs {team2}")
    
    # Display comparison metrics
    print_subheader("Comparison Metrics")
    print(f"Credit Difference: {comparison['comparison']['credit_difference']:.2f}")
    print(f"Average Credit Difference: {comparison['comparison']['avg_credit_difference']:.2f}")
    
    # Display role comparison
    print_subheader("Role Comparison")
    for role, metrics in comparison['comparison']['role_balance'].items():
        print(f"{role}:")
        print(f"  {team1}: {metrics['team1_count']}")
        print(f"  {team2}: {metrics['team2_count']}")
        print(f"  Difference: {metrics['difference']}")

def search_players(players: Players) -> None:
    """Search for players"""
    print_header("Search Players")
    query = input("Enter search query: ")
    
    results = players.search_players(query)
    if not results.empty:
        print("\nSearch Results:")
        print(tabulate(results[['Player Name', 'Team', 'Player Type', 'Credits']], 
                      headers='keys', tablefmt='grid'))
    else:
        print("No players found matching your search.")

def analyze_squad(players: Players) -> None:
    """Analyze squad composition"""
    team = get_team_selection(players)
    analysis = players.analyze_squad_composition(team)
    
    print_header(f"Squad Analysis: {team}")
    
    # Display basic stats
    print_subheader("Basic Statistics")
    print(f"Total Players: {analysis['total_players']}")
    
    # Display credit distribution
    print_subheader("Credit Distribution")
    for range_name, count in analysis['credit_ranges'].items():
        print(f"{range_name}: {count} players")
    
    # Display role distribution
    print_subheader("Role Distribution")
    for role, count in analysis['role_distribution'].items():
        print(f"{role}: {count} players")
    
    # Display value analysis
    print_subheader("Value Analysis")
    print(f"Average Value Score: {analysis['value_analysis']['avg_value_score']:.2f}")
    print("\nTop Value Players:")
    print(tabulate(analysis['value_analysis']['top_value_players'], 
                  headers='keys', tablefmt='grid'))

def display_team_strengths(players: Players) -> None:
    """Display team strengths"""
    team = get_team_selection(players)
    players.display_team_strengths(team)

def get_value_players(players: Players) -> None:
    """Get value players"""
    print_header("Value Players")
    
    team = input("Enter team name (or press Enter for all teams): ").strip()
    min_credits = float(input("Enter minimum credits (default: 0): ") or 0)
    
    results = players.get_value_players(team if team else None, min_credits)
    if not results.empty:
        print("\nValue Players:")
        print(tabulate(results[['Player Name', 'Team', 'Player Type', 'Credits', 'value_score']], 
                      headers='keys', tablefmt='grid'))
    else:
        print("No value players found matching your criteria.")

def get_players_by_credit_range(players: Players) -> None:
    """Get players within a credit range"""
    print_header("Players by Credit Range")
    min_credits, max_credits = get_credit_range()
    
    results = players.get_players_by_credit_range(min_credits, max_credits)
    if not results.empty:
        print("\nPlayers in Credit Range:")
        print(tabulate(results[['Player Name', 'Team', 'Player Type', 'Credits']], 
                      headers='keys', tablefmt='grid'))
    else:
        print("No players found in the specified credit range.")

def display_match_analysis(players: Players) -> None:
    """Display match analysis"""
    print_header("Match Analysis")
    
    print("Select first team:")
    team1 = get_team_selection(players)
    print("\nSelect second team:")
    team2 = get_team_selection(players)
    
    players.display_match_analysis(team1, team2)

def main():
    """Main CLI function"""
    try:
        players = Players()
    except Exception as e:
        print(f"Error initializing Players class: {str(e)}")
        sys.exit(1)
    
    while True:
        display_menu()
        try:
            choice = int(input("\nEnter your choice (1-9): "))
            
            if choice == 1:
                display_team_stats(players)
            elif choice == 2:
                compare_teams(players)
            elif choice == 3:
                search_players(players)
            elif choice == 4:
                analyze_squad(players)
            elif choice == 5:
                display_team_strengths(players)
            elif choice == 6:
                get_value_players(players)
            elif choice == 7:
                get_players_by_credit_range(players)
            elif choice == 8:
                display_match_analysis(players)
            elif choice == 9:
                print("\nThank you for using Cricket Team Analysis CLI!")
                sys.exit(0)
            else:
                print("Invalid choice. Please try again.")
            
            input("\nPress Enter to continue...")
            
        except ValueError:
            print("Please enter a valid number.")
        except KeyboardInterrupt:
            print("\n\nThank you for using Cricket Team Analysis CLI!")
            sys.exit(0)
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    main() 