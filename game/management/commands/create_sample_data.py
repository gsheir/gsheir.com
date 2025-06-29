from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from game.models import League, LeagueParticipant, Round, Team, Player
import random


class Command(BaseCommand):
    help = 'Create sample data for development'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create sample users
        users = []
        for i in range(1, 6):
            username = f'user{i}'
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@example.com',
                    'first_name': f'User',
                    'last_name': str(i)
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                self.stdout.write(f'Created user: {username}')
            users.append(user)
        
        # Create sample teams
        team_names = [
            ('England', 'England'),
            ('Spain', 'Spain'),
            ('Germany', 'Germany'),
            ('France', 'France'),
            ('Netherlands', 'Netherlands'),
            ('Sweden', 'Sweden'),
            ('Italy', 'Italy'),
            ('Norway', 'Norway')
        ]
        
        teams = []
        for name, country in team_names:
            team, created = Team.objects.get_or_create(
                name=name,
                country=country
            )
            if created:
                self.stdout.write(f'Created team: {name}')
            teams.append(team)
        
        # Create sample players
        player_names = [
            'Lucy Bronze', 'Beth Mead', 'Ellen White', 'Keira Walsh',
            'Aitana Bonmatí', 'Alexia Putellas', 'Jenni Hermoso', 'Irene Paredes',
            'Alexandra Popp', 'Lena Oberdorf', 'Svenja Huth', 'Giulia Gwinn',
            'Marie-Antoinette Katoto', 'Wendie Renard', 'Kadidiatou Diani', 'Grace Geyoro',
            'Vivianne Miedema', 'Lieke Martens', 'Danielle van de Donk', 'Jackie Groenen',
            'Fridolina Rolfö', 'Stina Blackstenius', 'Kosovare Asllani', 'Magdalena Eriksson',
            'Valentina Giacinti', 'Barbara Bonansea', 'Cristiana Girelli', 'Sara Gama',
            'Ada Hegerberg', 'Caroline Graham Hansen', 'Guro Reiten', 'Maren Mjelde'
        ]
        
        positions = ['Forward', 'Midfielder', 'Defender', 'Goalkeeper']
        
        for i, name in enumerate(player_names):
            team = teams[i // 4]  # 4 players per team
            position = random.choice(positions)
            goals = random.randint(0, 8)
            
            player, created = Player.objects.get_or_create(
                name=name,
                team=team,
                defaults={
                    'position': position,
                    'goals_scored': goals
                }
            )
            if created:
                self.stdout.write(f'Created player: {name} ({team.name})')
        
        # Create sample rounds
        now = timezone.now()
        rounds_data = [
            ('Group Stage - Matchday 1', 1, now - timedelta(days=10), now + timedelta(days=5)),
            ('Group Stage - Matchday 2', 2, now + timedelta(days=5), now + timedelta(days=10)),
            ('Group Stage - Matchday 3', 3, now + timedelta(days=10), now + timedelta(days=15)),
            ('Round of 16', 4, now + timedelta(days=15), now + timedelta(days=20)),
        ]
        
        for name, number, start, end in rounds_data:
            round_obj, created = Round.objects.get_or_create(
                number=number,
                defaults={
                    'name': name,
                    'selection_opens': start - timedelta(hours=24),
                    'selection_closes': start - timedelta(hours=1),
                    'starts_at': start,
                    'ends_at': end,
                    'is_active': number == 2,  # Make round 2 active
                    'is_completed': number == 1  # Mark round 1 as completed
                }
            )
            if created:
                self.stdout.write(f'Created round: {name}')
        
        # Create sample league
        league, created = League.objects.get_or_create(
            name='Sample League',
            defaults={
                'code': 'SAMPLE',
                'created_by': users[0],
                'max_participants': 5
            }
        )
        if created:
            self.stdout.write('Created sample league')
        
        # Add users to league
        for user in users:
            participant, created = LeagueParticipant.objects.get_or_create(
                league=league,
                user=user
            )
            if created:
                self.stdout.write(f'Added {user.username} to league')
        
        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))
        self.stdout.write('You can now login with any of these accounts:')
        self.stdout.write('  Username: user1, user2, user3, user4, user5')
        self.stdout.write('  Password: password123')
        self.stdout.write(f'  League code: {league.code}')
