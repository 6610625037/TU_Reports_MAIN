from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from authentication.models import User
from tickets.models import Category, Ticket, TechnicianPresence
import random


class Command(BaseCommand):
    help = 'Create demo data for testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating demo data...')

        # Create Admin
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'role': 'admin',
                'displayname_th': 'ผู้ดูแลระบบ',
                'is_staff': True,
                'is_superuser': True
            }
        )
        admin.set_password('admin123')
        admin.save()
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Created admin user'))

        # Create Technicians
        techs = []
        for i in range(1, 6):
            tech, created = User.objects.get_or_create(
                username=f'tech00{i}',
                defaults={
                    'role': 'technician',
                    'displayname_th': f'ช่าง {i}',
                }
            )
            tech.set_password('tech123')
            tech.save()

            # Create presence
            TechnicianPresence.objects.get_or_create(
                technician=tech,
                defaults={
                    'location': Point(
                        100.605 + (i * 0.001),
                        14.070 + (i * 0.001),
                        srid=4326
                    ),
                    'is_available': True
                }
            )

            techs.append(tech)
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created technician: tech00{i}'))

        # Create Users
        users = []
        for i in range(1, 4):
            user, created = User.objects.get_or_create(
                username=f'user00{i}',
                defaults={
                    'role': 'user',
                    'displayname_th': f'ผู้ใช้ {i}',
                }
            )
            user.set_password('user123')
            user.save()
            users.append(user)
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created user: user00{i}'))

        # Create some sample tickets
        categories = Category.objects.all()
        if categories.exists():
            urgency_levels = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
            locations = [
                Point(100.605, 14.070, srid=4326),
                Point(100.606, 14.071, srid=4326),
                Point(100.607, 14.072, srid=4326),
            ]

            for i in range(5):
                ticket = Ticket.objects.create(
                    title=f'ตัวอย่างปัญหา #{i+1}',
                    description=f'รายละเอียดปัญหาตัวอย่างที่ {i+1}',
                    category=random.choice(categories),
                    created_by=random.choice(users),
                    urgency_level=random.choice(urgency_levels),
                    location=random.choice(locations),
                    address_description=f'อาคาร {i+1} ชั้น {random.randint(1,5)} ห้อง {random.randint(100,500)}'
                )
                self.stdout.write(self.style.SUCCESS(f'✓ Created sample ticket: {ticket.title}'))

        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('Demo data created successfully!'))
        self.stdout.write('='*50)
        self.stdout.write('\nTest Accounts:')
        self.stdout.write('  Admin:      admin / admin123')
        self.stdout.write('  Technician: tech001-tech005 / tech123')
        self.stdout.write('  User:       user001-user003 / user123')
        self.stdout.write('\nTU API Mock Accounts:')
        self.stdout.write('  Student:    student001 / student123')
        self.stdout.write('  Personnel:  personnel001 / personnel123')
        self.stdout.write('='*50 + '\n')
