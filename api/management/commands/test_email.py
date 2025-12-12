from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from api.models import Order, Payment, CustomUser
from api.email_service import EmailService

class Command(BaseCommand):
    help = 'Test email functionality'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email address to send test email to',
            default='test@example.com'
        )
        parser.add_argument(
            '--type',
            type=str,
            choices=['simple', 'order', 'payment'],
            help='Type of email to test',
            default='simple'
        )

    def handle(self, *args, **options):
        email = options['email']
        email_type = options['type']
        
        try:
            if email_type == 'simple':
                # Test simple email
                result = send_mail(
                    subject='Test Email from CultureUp',
                    message='This is a test email to verify email configuration is working properly.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False
                )
                
                if result:
                    self.stdout.write(
                        self.style.SUCCESS(f'Simple test email sent successfully to {email}')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR('Failed to send simple test email')
                    )
            
            elif email_type == 'order':
                # Test order confirmation email with mock data
                try:
                    # Get or create a test user
                    user, created = CustomUser.objects.get_or_create(
                        username='testbuyer',
                        defaults={
                            'email': email,
                            'first_name': 'Test',
                            'last_name': 'Buyer',
                            'user_type': 'buyer'
                        }
                    )
                    
                    # Get the latest order or create a mock context
                    latest_order = Order.objects.filter(buyer=user).first()
                    
                    if latest_order:
                        result = EmailService.send_purchase_confirmation(latest_order)
                        if result:
                            self.stdout.write(
                                self.style.SUCCESS(f'Order confirmation email sent to {email}')
                            )
                        else:
                            self.stdout.write(
                                self.style.ERROR('Failed to send order confirmation email')
                            )
                    else:
                        self.stdout.write(
                            self.style.WARNING('No orders found. Create an order first to test order emails.')
                        )
                        
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error testing order email: {str(e)}')
                    )
            
            elif email_type == 'payment':
                # Test payment confirmation email
                try:
                    latest_payment = Payment.objects.filter(status='completed').first()
                    
                    if latest_payment:
                        result = EmailService.send_payment_confirmation(latest_payment)
                        if result:
                            self.stdout.write(
                                self.style.SUCCESS(f'Payment confirmation email sent to {email}')
                            )
                        else:
                            self.stdout.write(
                                self.style.ERROR('Failed to send payment confirmation email')
                            )
                    else:
                        self.stdout.write(
                            self.style.WARNING('No completed payments found. Create a payment first to test payment emails.')
                        )
                        
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error testing payment email: {str(e)}')
                    )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Email test failed: {str(e)}')
            )
            
        # Display current email settings
        self.stdout.write('\n' + '='*50)
        self.stdout.write('Current Email Settings:')
        self.stdout.write(f'EMAIL_BACKEND: {settings.EMAIL_BACKEND}')
        self.stdout.write(f'EMAIL_HOST: {getattr(settings, "EMAIL_HOST", "Not set")}')
        self.stdout.write(f'EMAIL_PORT: {getattr(settings, "EMAIL_PORT", "Not set")}')
        self.stdout.write(f'EMAIL_USE_TLS: {getattr(settings, "EMAIL_USE_TLS", "Not set")}')
        self.stdout.write(f'EMAIL_HOST_USER: {getattr(settings, "EMAIL_HOST_USER", "Not set")}')
        self.stdout.write(f'DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}')
        self.stdout.write('='*50)