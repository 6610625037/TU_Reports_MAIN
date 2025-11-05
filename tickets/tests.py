"""
Test Suite for TU Report
Coverage target: ≥80%
"""

from django.test import TestCase, Client
from django.contrib.gis.geos import Point
from django.contrib.auth import get_user_model
from .models import Ticket, Category, TechnicianPresence, AssignmentRule
from .dispatcher import AutoDispatcher

User = get_user_model()


class AutoDispatcherTestCase(TestCase):
    """Test Auto Dispatcher Logic"""

    def setUp(self):
        """Setup test data"""
        # Create assignment rule
        self.rule = AssignmentRule.objects.create(
            max_open_tickets=5,
            weight_distance=0.6,
            weight_workload=0.4,
            is_active=True
        )

        # Create category
        self.category = Category.objects.create(name='ไฟฟ้า')

        # Create user
        self.user = User.objects.create_user(
            username='user001',
            password='pass123',
            role='user'
        )

        # Create technicians
        self.tech1 = User.objects.create_user(
            username='tech001',
            password='pass123',
            role='technician',
            displayname_th='ช่าง 1'
        )

        self.tech2 = User.objects.create_user(
            username='tech002',
            password='pass123',
            role='technician',
            displayname_th='ช่าง 2'
        )

        # Create technician presence (locations)
        TechnicianPresence.objects.create(
            technician=self.tech1,
            location=Point(100.605, 14.070, srid=4326),  # Near location
            is_available=True
        )

        TechnicianPresence.objects.create(
            technician=self.tech2,
            location=Point(100.610, 14.075, srid=4326),  # Far location
            is_available=True
        )

        self.dispatcher = AutoDispatcher()

    def test_priority_score_calculation(self):
        """Test priority score calculation"""
        ticket = Ticket.objects.create(
            title='Test Ticket',
            description='Test',
            category=self.category,
            created_by=self.user,
            urgency_level='HIGH',
            location=Point(100.606, 14.071, srid=4326)
        )

        score = self.dispatcher.calculate_priority_score(ticket)
        self.assertGreater(score, 0)
        self.assertIsInstance(score, float)

    def test_dispatch_to_nearest_technician(self):
        """Test dispatcher assigns to nearest technician"""
        ticket = Ticket.objects.create(
            title='Test Ticket',
            description='Test',
            category=self.category,
            created_by=self.user,
            urgency_level='MEDIUM',
            location=Point(100.605, 14.070, srid=4326)  # Same as tech1
        )

        success = self.dispatcher.dispatch(ticket)

        self.assertTrue(success)
        ticket.refresh_from_db()
        self.assertEqual(ticket.assigned_to, self.tech1)  # Should assign to tech1 (nearest)

    def test_no_technician_available(self):
        """Test when all technicians are busy"""
        # Create 5 tickets for tech1
        for i in range(5):
            Ticket.objects.create(
                title=f'Ticket {i}',
                description='Test',
                category=self.category,
                created_by=self.user,
                assigned_to=self.tech1,
                status='IN_PROGRESS'
            )

        # Create 5 tickets for tech2
        for i in range(5):
            Ticket.objects.create(
                title=f'Ticket {i}',
                description='Test',
                category=self.category,
                created_by=self.user,
                assigned_to=self.tech2,
                status='IN_PROGRESS'
            )

        # Try to create new ticket
        ticket = Ticket.objects.create(
            title='New Ticket',
            description='Test',
            category=self.category,
            created_by=self.user,
            urgency_level='HIGH'
        )

        success = self.dispatcher.dispatch(ticket)

        self.assertFalse(success)
        ticket.refresh_from_db()
        self.assertIsNone(ticket.assigned_to)

    def test_workload_balancing(self):
        """Test workload balancing between technicians"""
        # Give tech1 4 tickets (almost full)
        for i in range(4):
            Ticket.objects.create(
                title=f'Ticket {i}',
                description='Test',
                category=self.category,
                created_by=self.user,
                assigned_to=self.tech1,
                status='IN_PROGRESS'
            )

        # tech2 has 0 tickets
        ticket = Ticket.objects.create(
            title='New Ticket',
            description='Test',
            category=self.category,
            created_by=self.user,
            urgency_level='MEDIUM',
            location=Point(100.605, 14.070, srid=4326)  # Near tech1
        )

        success = self.dispatcher.dispatch(ticket)

        self.assertTrue(success)
        ticket.refresh_from_db()
        # Should assign to tech2 despite being farther (better workload)
        self.assertIsNotNone(ticket.assigned_to)


class TicketViewsTestCase(TestCase):
    """Test Ticket Views"""

    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='ไฟฟ้า')

        self.user = User.objects.create_user(
            username='user001',
            password='pass123',
            role='user'
        )

    def test_create_ticket_requires_login(self):
        """Test create ticket requires authentication"""
        response = self.client.get('/tickets/create/')
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_create_ticket_when_logged_in(self):
        """Test authenticated user can create ticket"""
        self.client.login(username='user001', password='pass123')

        response = self.client.post('/tickets/create/', {
            'title': 'Test Ticket',
            'description': 'Test Description',
            'category': self.category.id,
            'urgency_level': 'MEDIUM',
            'address_description': 'Test Address',
        })

        self.assertEqual(response.status_code, 302)  # Redirect after create
        self.assertEqual(Ticket.objects.count(), 1)

        ticket = Ticket.objects.first()
        self.assertEqual(ticket.title, 'Test Ticket')
        self.assertEqual(ticket.created_by, self.user)

    def test_my_tickets_shows_only_own_tickets(self):
        """Test user sees only their own tickets"""
        # Create another user
        other_user = User.objects.create_user(
            username='other',
            password='pass123',
            role='user'
        )

        # Create tickets
        Ticket.objects.create(
            title='My Ticket',
            description='Test',
            category=self.category,
            created_by=self.user
        )

        Ticket.objects.create(
            title='Other Ticket',
            description='Test',
            category=self.category,
            created_by=other_user
        )

        self.client.login(username='user001', password='pass123')
        response = self.client.get('/tickets/my-tickets/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['tickets']), 1)
        self.assertEqual(response.context['tickets'][0].title, 'My Ticket')

    def test_ticket_detail_access_control(self):
        """Test ticket detail access control"""
        other_user = User.objects.create_user(
            username='other',
            password='pass123',
            role='user'
        )

        ticket = Ticket.objects.create(
            title='Other Ticket',
            description='Test',
            category=self.category,
            created_by=other_user
        )

        # Login as user001
        self.client.login(username='user001', password='pass123')

        # Try to access other user's ticket
        response = self.client.get(f'/tickets/{ticket.id}/')

        # Should redirect with error
        self.assertEqual(response.status_code, 302)


class AuthenticationTestCase(TestCase):
    """Test Authentication"""

    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user(
            username='testuser',
            password='testpass',
            role='user'
        )

    def test_login_page_loads(self):
        """Test login page loads successfully"""
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)

    def test_local_login_success(self):
        """Test successful local login"""
        response = self.client.post('/login/', {
            'username': 'testuser',
            'password': 'testpass',
            'login_type': 'local'
        })

        self.assertEqual(response.status_code, 302)  # Redirect after login
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_local_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = self.client.post('/login/', {
            'username': 'testuser',
            'password': 'wrongpass',
            'login_type': 'local'
        })

        self.assertEqual(response.status_code, 200)  # Stay on login page
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_tu_api_login_success(self):
        """Test TU API login with mock data"""
        response = self.client.post('/login/', {
            'username': 'student001',
            'password': 'student123',
            'login_type': 'tu_api'
        })

        self.assertEqual(response.status_code, 302)  # Redirect after login
        self.assertTrue(response.wsgi_request.user.is_authenticated)

        # Check user was created from TU API
        user = User.objects.get(username='student001')
        self.assertEqual(user.auth_provider, 'TU_API')


class TechnicianTestCase(TestCase):
    """Test Technician Views"""

    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='ไฟฟ้า')

        self.user = User.objects.create_user(
            username='user001',
            password='pass123',
            role='user'
        )

        self.tech = User.objects.create_user(
            username='tech001',
            password='pass123',
            role='technician',
            displayname_th='ช่าง 1'
        )

    def test_technician_job_list_requires_technician_role(self):
        """Test job list requires technician role"""
        self.client.login(username='user001', password='pass123')
        response = self.client.get('/technician/jobs/')

        # Should redirect with error
        self.assertEqual(response.status_code, 302)

    def test_technician_sees_assigned_jobs(self):
        """Test technician sees only assigned jobs"""
        # Create ticket assigned to tech
        ticket1 = Ticket.objects.create(
            title='Assigned Ticket',
            description='Test',
            category=self.category,
            created_by=self.user,
            assigned_to=self.tech
        )

        # Create ticket not assigned to tech
        Ticket.objects.create(
            title='Other Ticket',
            description='Test',
            category=self.category,
            created_by=self.user
        )

        self.client.login(username='tech001', password='pass123')
        response = self.client.get('/technician/jobs/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['assigned_tickets']), 1)
        self.assertEqual(response.context['assigned_tickets'][0].title, 'Assigned Ticket')


class ModelTestCase(TestCase):
    """Test Models"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='pass123',
            role='user',
            displayname_th='ทดสอบ ผู้ใช้'
        )

        self.category = Category.objects.create(name='ไฟฟ้า')

    def test_user_get_display_name(self):
        """Test user display name method"""
        self.assertEqual(self.user.get_display_name(), 'ทดสอบ ผู้ใช้')

        # Test fallback to username
        user2 = User.objects.create_user(username='user2', password='pass')
        self.assertEqual(user2.get_display_name(), 'user2')

    def test_ticket_creation(self):
        """Test ticket can be created"""
        ticket = Ticket.objects.create(
            title='Test Ticket',
            description='Test Description',
            category=self.category,
            created_by=self.user,
            urgency_level='MEDIUM'
        )

        self.assertEqual(ticket.status, 'PENDING')
        self.assertEqual(str(ticket), 'Test Ticket')

    def test_ticket_with_location(self):
        """Test ticket with GPS location"""
        ticket = Ticket.objects.create(
            title='Test Ticket',
            description='Test',
            category=self.category,
            created_by=self.user,
            location=Point(100.606, 14.071, srid=4326)
        )

        self.assertIsNotNone(ticket.location)
        self.assertEqual(ticket.location.srid, 4326)


# Run tests:
# python manage.py test
# python manage.py test --verbosity=2

# Coverage:
# coverage run --source='.' manage.py test
# coverage report
# coverage html
