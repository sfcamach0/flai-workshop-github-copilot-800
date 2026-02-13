from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import User, Team, Activity, Leaderboard, Workout


class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
    
    def test_user_creation(self):
        """Test user model creation"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertTrue(self.user.is_active)
    
    def test_user_str(self):
        """Test user string representation"""
        self.assertEqual(str(self.user), 'testuser')


class TeamModelTest(TestCase):
    def setUp(self):
        self.team = Team.objects.create(
            name='Test Team',
            description='A test team',
            created_by='testuser',
            members=['user1', 'user2']
        )
    
    def test_team_creation(self):
        """Test team model creation"""
        self.assertEqual(self.team.name, 'Test Team')
        self.assertEqual(len(self.team.members), 2)
    
    def test_team_str(self):
        """Test team string representation"""
        self.assertEqual(str(self.team), 'Test Team')


class ActivityModelTest(TestCase):
    def setUp(self):
        self.activity = Activity.objects.create(
            user_id='testuser',
            activity_type='running',
            duration=30,
            distance=5.0,
            calories=300
        )
    
    def test_activity_creation(self):
        """Test activity model creation"""
        self.assertEqual(self.activity.activity_type, 'running')
        self.assertEqual(self.activity.duration, 30)
        self.assertEqual(self.activity.distance, 5.0)


class UserAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'username': 'apiuser',
            'email': 'api@example.com',
            'password': 'apipass123',
            'first_name': 'API',
            'last_name': 'User'
        }
    
    def test_create_user(self):
        """Test creating a user via API"""
        response = self.client.post('/api/users/', self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_list_users(self):
        """Test listing users via API"""
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TeamAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.team_data = {
            'name': 'API Team',
            'description': 'Team created via API',
            'created_by': 'apiuser',
            'members': []
        }
    
    def test_create_team(self):
        """Test creating a team via API"""
        response = self.client.post('/api/teams/', self.team_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_list_teams(self):
        """Test listing teams via API"""
        response = self.client.get('/api/teams/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ActivityAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.activity_data = {
            'user_id': 'testuser',
            'activity_type': 'running',
            'duration': 30,
            'distance': 5.0,
            'calories': 300,
            'notes': 'Morning run'
        }
    
    def test_create_activity(self):
        """Test creating an activity via API"""
        response = self.client.post('/api/activities/', self.activity_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_list_activities(self):
        """Test listing activities via API"""
        response = self.client.get('/api/activities/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class LeaderboardAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        Leaderboard.objects.create(
            user_id='user1',
            username='testuser1',
            total_points=100,
            total_activities=10,
            total_duration=300
        )
    
    def test_list_leaderboard(self):
        """Test listing leaderboard via API"""
        response = self.client.get('/api/leaderboard/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class WorkoutAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.workout_data = {
            'name': 'Beginner Cardio',
            'description': 'A beginner cardio workout',
            'difficulty_level': 'beginner',
            'duration': 30,
            'activity_type': 'cardio',
            'exercises': ['jumping jacks', 'running in place']
        }
    
    def test_create_workout(self):
        """Test creating a workout via API"""
        response = self.client.post('/api/workouts/', self.workout_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_list_workouts(self):
        """Test listing workouts via API"""
        response = self.client.get('/api/workouts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
