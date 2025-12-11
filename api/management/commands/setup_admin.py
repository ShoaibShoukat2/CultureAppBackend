# setup_admin.py - Management command to setup admin users and sample data
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from api.models import *
from decimal import Decimal
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Setup admin users and sample data for ArtConnect platform'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-superuser',
            action='store_true',
            help='Create a superuser account',
        )
        parser.add_argument(
            '--create-sample-data',
            action='store_true',
            help='Create sample data for testing',
        )
        parser.add_argument(
            '--admin-username',
            type=str,
            default='admin',
            help='Admin username (default: admin)',
        )
        parser.add_argument(
            '--admin-email',
            type=str,
            default='admin@artconnect.com',
            help='Admin email (default: admin@artconnect.com)',
        )
        parser.add_argument(
            '--admin-password',
            type=str,
            default='admin123',
            help='Admin password (default: admin123)',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🎨 Setting up ArtConnect Admin Backend...')
        )

        if options['create_superuser']:
            self.create_admin_user(options)

        if options['create_sample_data']:
            self.create_sample_data()

        self.stdout.write(
            self.style.SUCCESS('✅ Admin setup completed successfully!')
        )

    def create_admin_user(self, options):
        """Create admin/superuser accounts"""
        username = options['admin_username']
        email = options['admin_email']
        password = options['admin_password']

        # Create superuser
        if not User.objects.filter(username=username).exists():
            superuser = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                user_type='admin',
                is_verified=True,
                first_name='Admin',
                last_name='User'
            )
            self.stdout.write(
                self.style.SUCCESS(f'✅ Superuser created: {username}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'⚠️  Superuser {username} already exists')
            )

        # Create additional admin users
        admin_users = [
            {
                'username': 'admin_manager',
                'email': 'manager@artconnect.com',
                'password': 'manager123',
                'first_name': 'Admin',
                'last_name': 'Manager'
            },
            {
                'username': 'content_moderator',
                'email': 'moderator@artconnect.com',
                'password': 'moderator123',
                'first_name': 'Content',
                'last_name': 'Moderator'
            }
        ]

        for admin_data in admin_users:
            if not User.objects.filter(username=admin_data['username']).exists():
                admin_user = User.objects.create_user(
                    username=admin_data['username'],
                    email=admin_data['email'],
                    password=admin_data['password'],
                    user_type='admin',
                    is_staff=True,
                    is_verified=True,
                    first_name=admin_data['first_name'],
                    last_name=admin_data['last_name']
                )
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Admin user created: {admin_data["username"]}')
                )

    def create_sample_data(self):
        """Create sample data for testing"""
        self.stdout.write('📊 Creating sample data...')

        # Create categories
        categories = [
            {'name': 'Digital Art', 'description': 'Digital artwork and illustrations'},
            {'name': 'Traditional Painting', 'description': 'Oil, acrylic, and watercolor paintings'},
            {'name': 'Photography', 'description': 'Professional photography services'},
            {'name': 'Graphic Design', 'description': 'Logo design, branding, and graphics'},
            {'name': 'Sculpture', 'description': '3D art and sculptures'},
            {'name': 'Animation', 'description': '2D and 3D animation services'},
        ]

        for cat_data in categories:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            if created:
                self.stdout.write(f'  ✅ Category created: {category.name}')

        # Create sample artists
        artists_data = [
            {
                'username': 'artist_john',
                'email': 'john@example.com',
                'first_name': 'John',
                'last_name': 'Artist',
                'skills': 'Digital Art, Illustration, Character Design',
                'hourly_rate': 50.00,
                'experience_level': 'expert'
            },
            {
                'username': 'artist_sarah',
                'email': 'sarah@example.com',
                'first_name': 'Sarah',
                'last_name': 'Painter',
                'skills': 'Traditional Painting, Portraits, Landscapes',
                'hourly_rate': 40.00,
                'experience_level': 'intermediate'
            },
            {
                'username': 'artist_mike',
                'email': 'mike@example.com',
                'first_name': 'Mike',
                'last_name': 'Designer',
                'skills': 'Graphic Design, Logo Design, Branding',
                'hourly_rate': 35.00,
                'experience_level': 'intermediate'
            }
        ]

        for artist_data in artists_data:
            if not User.objects.filter(username=artist_data['username']).exists():
                artist = User.objects.create_user(
                    username=artist_data['username'],
                    email=artist_data['email'],
                    password='password123',
                    user_type='artist',
                    is_verified=True,
                    first_name=artist_data['first_name'],
                    last_name=artist_data['last_name']
                )
                
                # Create artist profile
                ArtistProfile.objects.create(
                    user=artist,
                    skills=artist_data['skills'],
                    hourly_rate=artist_data['hourly_rate'],
                    experience_level=artist_data['experience_level'],
                    bio=f"Professional {artist_data['first_name']} with expertise in {artist_data['skills']}",
                    rating=random.uniform(4.0, 5.0)
                )
                
                self.stdout.write(f'  ✅ Artist created: {artist.username}')

        # Create sample buyers
        buyers_data = [
            {
                'username': 'buyer_alice',
                'email': 'alice@company.com',
                'first_name': 'Alice',
                'last_name': 'Johnson',
                'company_name': 'Creative Corp'
            },
            {
                'username': 'buyer_bob',
                'email': 'bob@startup.com',
                'first_name': 'Bob',
                'last_name': 'Smith',
                'company_name': 'Tech Startup Inc'
            }
        ]

        for buyer_data in buyers_data:
            if not User.objects.filter(username=buyer_data['username']).exists():
                buyer = User.objects.create_user(
                    username=buyer_data['username'],
                    email=buyer_data['email'],
                    password='password123',
                    user_type='buyer',
                    is_verified=True,
                    first_name=buyer_data['first_name'],
                    last_name=buyer_data['last_name']
                )
                
                # Create buyer profile
                BuyerProfile.objects.create(
                    user=buyer,
                    company_name=buyer_data['company_name'],
                    address=f"123 Business St, City, State 12345"
                )
                
                self.stdout.write(f'  ✅ Buyer created: {buyer.username}')

        # Create sample equipment
        equipment_data = [
            {
                'name': 'Professional Canvas 16x20',
                'description': 'High-quality canvas for painting',
                'equipment_type': 'canvas',
                'price': 25.99,
                'stock_quantity': 50
            },
            {
                'name': 'Acrylic Paint Set',
                'description': 'Complete set of acrylic paints',
                'equipment_type': 'paint',
                'price': 45.99,
                'stock_quantity': 30
            },
            {
                'name': 'Professional Brush Set',
                'description': 'Set of professional painting brushes',
                'equipment_type': 'brush',
                'price': 35.99,
                'stock_quantity': 25
            }
        ]

        for eq_data in equipment_data:
            equipment, created = Equipment.objects.get_or_create(
                name=eq_data['name'],
                defaults=eq_data
            )
            if created:
                self.stdout.write(f'  ✅ Equipment created: {equipment.name}')

        # Create sample jobs
        if Category.objects.exists() and User.objects.filter(user_type='buyer').exists():
            buyers = User.objects.filter(user_type='buyer')
            categories = Category.objects.all()
            
            jobs_data = [
                {
                    'title': 'Logo Design for Tech Startup',
                    'description': 'Need a modern, professional logo for our new tech startup. Should be scalable and work in both color and black/white.',
                    'budget_min': 200,
                    'budget_max': 500,
                    'duration_days': 7,
                    'required_skills': 'Logo Design, Graphic Design, Branding',
                    'experience_level': 'intermediate'
                },
                {
                    'title': 'Digital Portrait Commission',
                    'description': 'Looking for an artist to create a digital portrait based on photos. Style should be realistic with some artistic flair.',
                    'budget_min': 150,
                    'budget_max': 300,
                    'duration_days': 10,
                    'required_skills': 'Digital Art, Portrait, Illustration',
                    'experience_level': 'expert'
                }
            ]
            
            for job_data in jobs_data:
                if not Job.objects.filter(title=job_data['title']).exists():
                    job = Job.objects.create(
                        buyer=random.choice(buyers),
                        category=random.choice(categories),
                        deadline=timezone.now() + timezone.timedelta(days=job_data['duration_days']),
                        **job_data
                    )
                    self.stdout.write(f'  ✅ Job created: {job.title}')

        # Create analytics record
        analytics, created = PlatformAnalytics.objects.get_or_create(
            date=timezone.now().date()
        )
        if created:
            analytics.calculate_daily_stats()
            self.stdout.write('  ✅ Analytics record created')

        self.stdout.write(
            self.style.SUCCESS('📊 Sample data creation completed!')
        )