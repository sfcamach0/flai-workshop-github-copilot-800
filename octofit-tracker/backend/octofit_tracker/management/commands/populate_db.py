from django.core.management.base import BaseCommand
from pymongo import MongoClient
from datetime import datetime, timedelta
import random


class Command(BaseCommand):
    help = 'Populate the octofit_db database with test data'

    def handle(self, *args, **options):
        # Connect to MongoDB
        client = MongoClient('localhost', 27017)
        db = client['octofit_db']

        self.stdout.write(self.style.SUCCESS('Connected to MongoDB'))

        # Clear existing data
        self.stdout.write('Clearing existing data...')
        db.users.delete_many({})
        db.teams.delete_many({})
        db.activities.delete_many({})
        db.leaderboard.delete_many({})
        db.workouts.delete_many({})

        # Create unique index on email field for users
        db.users.create_index([('email', 1)], unique=True)
        self.stdout.write(self.style.SUCCESS('Created unique index on users.email'))

        # Sample data - Superhero theme
        marvel_heroes = [
            {'name': 'Tony Stark', 'email': 'ironman@marvel.com', 'alias': 'Iron Man', 'team': 'Team Marvel'},
            {'name': 'Steve Rogers', 'email': 'captainamerica@marvel.com', 'alias': 'Captain America', 'team': 'Team Marvel'},
            {'name': 'Thor Odinson', 'email': 'thor@marvel.com', 'alias': 'Thor', 'team': 'Team Marvel'},
            {'name': 'Natasha Romanoff', 'email': 'blackwidow@marvel.com', 'alias': 'Black Widow', 'team': 'Team Marvel'},
            {'name': 'Bruce Banner', 'email': 'hulk@marvel.com', 'alias': 'Hulk', 'team': 'Team Marvel'},
            {'name': 'Peter Parker', 'email': 'spiderman@marvel.com', 'alias': 'Spider-Man', 'team': 'Team Marvel'},
        ]

        dc_heroes = [
            {'name': 'Clark Kent', 'email': 'superman@dc.com', 'alias': 'Superman', 'team': 'Team DC'},
            {'name': 'Bruce Wayne', 'email': 'batman@dc.com', 'alias': 'Batman', 'team': 'Team DC'},
            {'name': 'Diana Prince', 'email': 'wonderwoman@dc.com', 'alias': 'Wonder Woman', 'team': 'Team DC'},
            {'name': 'Barry Allen', 'email': 'flash@dc.com', 'alias': 'The Flash', 'team': 'Team DC'},
            {'name': 'Arthur Curry', 'email': 'aquaman@dc.com', 'alias': 'Aquaman', 'team': 'Team DC'},
            {'name': 'Hal Jordan', 'email': 'greenlantern@dc.com', 'alias': 'Green Lantern', 'team': 'Team DC'},
        ]

        # Insert users
        all_heroes = marvel_heroes + dc_heroes
        for hero in all_heroes:
            user_doc = {
                'name': hero['name'],
                'email': hero['email'],
                'alias': hero['alias'],
                'team': hero['team'],
                'created_at': datetime.now(),
                'total_points': 0
            }
            db.users.insert_one(user_doc)

        self.stdout.write(self.style.SUCCESS(f'Inserted {len(all_heroes)} users'))

        # Insert teams
        teams = [
            {
                'name': 'Team Marvel',
                'description': 'Earth\'s Mightiest Heroes',
                'members': [hero['email'] for hero in marvel_heroes],
                'total_points': 0,
                'created_at': datetime.now()
            },
            {
                'name': 'Team DC',
                'description': 'Justice League United',
                'members': [hero['email'] for hero in dc_heroes],
                'total_points': 0,
                'created_at': datetime.now()
            }
        ]
        db.teams.insert_many(teams)
        self.stdout.write(self.style.SUCCESS('Inserted 2 teams'))

        # Insert activities
        activity_types = ['Running', 'Swimming', 'Cycling', 'Weight Training', 'Yoga', 'Boxing']
        activities = []
        
        for hero in all_heroes:
            # Create 5-10 activities per hero
            num_activities = random.randint(5, 10)
            for i in range(num_activities):
                activity = {
                    'user_email': hero['email'],
                    'user_name': hero['name'],
                    'user_alias': hero['alias'],
                    'activity_type': random.choice(activity_types),
                    'duration_minutes': random.randint(15, 120),
                    'distance_km': round(random.uniform(1, 20), 2),
                    'calories_burned': random.randint(100, 800),
                    'points': random.randint(10, 100),
                    'date': datetime.now() - timedelta(days=random.randint(0, 30)),
                    'notes': f'{hero["alias"]} training session'
                }
                activities.append(activity)
        
        db.activities.insert_many(activities)
        self.stdout.write(self.style.SUCCESS(f'Inserted {len(activities)} activities'))

        # Calculate and update user points
        for hero in all_heroes:
            user_activities = db.activities.find({'user_email': hero['email']})
            total_points = sum([act.get('points', 0) for act in user_activities])
            db.users.update_one(
                {'email': hero['email']},
                {'$set': {'total_points': total_points}}
            )

        # Calculate and update team points
        for team in ['Team Marvel', 'Team DC']:
            team_members = db.users.find({'team': team})
            total_points = sum([user.get('total_points', 0) for user in team_members])
            db.teams.update_one(
                {'name': team},
                {'$set': {'total_points': total_points}}
            )

        # Create leaderboard
        leaderboard_entries = []
        for hero in all_heroes:
            user = db.users.find_one({'email': hero['email']})
            leaderboard_entries.append({
                'user_email': hero['email'],
                'user_name': hero['name'],
                'user_alias': hero['alias'],
                'team': hero['team'],
                'total_points': user.get('total_points', 0),
                'rank': 0,  # Will be calculated
                'updated_at': datetime.now()
            })
        
        # Sort by points and assign ranks
        leaderboard_entries.sort(key=lambda x: x['total_points'], reverse=True)
        for idx, entry in enumerate(leaderboard_entries, start=1):
            entry['rank'] = idx
        
        db.leaderboard.insert_many(leaderboard_entries)
        self.stdout.write(self.style.SUCCESS(f'Inserted {len(leaderboard_entries)} leaderboard entries'))

        # Insert workout suggestions
        workouts = [
            {
                'name': 'Super Soldier Training',
                'description': 'High-intensity training program inspired by Captain America',
                'category': 'Strength',
                'duration_minutes': 60,
                'difficulty': 'Advanced',
                'exercises': ['Push-ups', 'Pull-ups', 'Squats', 'Shield throws'],
                'recommended_for': ['Team Marvel']
            },
            {
                'name': 'Speedster Circuit',
                'description': 'Lightning-fast cardio workout for speed demons',
                'category': 'Cardio',
                'duration_minutes': 45,
                'difficulty': 'Intermediate',
                'exercises': ['Sprints', 'Burpees', 'Jump rope', 'High knees'],
                'recommended_for': ['Team DC']
            },
            {
                'name': 'Amazonian Warrior Workout',
                'description': 'Warrior training from Themyscira',
                'category': 'Strength',
                'duration_minutes': 75,
                'difficulty': 'Advanced',
                'exercises': ['Sword training', 'Shield defense', 'Combat drills'],
                'recommended_for': ['Team DC']
            },
            {
                'name': 'Web-Slinger Agility',
                'description': 'Enhance your agility and flexibility',
                'category': 'Flexibility',
                'duration_minutes': 30,
                'difficulty': 'Beginner',
                'exercises': ['Stretching', 'Yoga', 'Balance exercises'],
                'recommended_for': ['Team Marvel']
            },
            {
                'name': 'Arc Reactor Endurance',
                'description': 'Build stamina like Iron Man',
                'category': 'Endurance',
                'duration_minutes': 90,
                'difficulty': 'Advanced',
                'exercises': ['Distance running', 'Cycling', 'Swimming'],
                'recommended_for': ['Team Marvel', 'Team DC']
            },
            {
                'name': 'Kryptonian Strength',
                'description': 'Build strength of steel',
                'category': 'Strength',
                'duration_minutes': 60,
                'difficulty': 'Advanced',
                'exercises': ['Deadlifts', 'Bench press', 'Overhead press'],
                'recommended_for': ['Team DC']
            }
        ]
        
        db.workouts.insert_many(workouts)
        self.stdout.write(self.style.SUCCESS(f'Inserted {len(workouts)} workout suggestions'))

        # Display summary
        self.stdout.write(self.style.SUCCESS('\n=== Database Population Summary ==='))
        self.stdout.write(f'Users: {db.users.count_documents({})}')
        self.stdout.write(f'Teams: {db.teams.count_documents({})}')
        self.stdout.write(f'Activities: {db.activities.count_documents({})}')
        self.stdout.write(f'Leaderboard entries: {db.leaderboard.count_documents({})}')
        self.stdout.write(f'Workouts: {db.workouts.count_documents({})}')
        self.stdout.write(self.style.SUCCESS('\nDatabase populated successfully!'))

        client.close()
