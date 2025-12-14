from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils import timezone


def send_notification_email(subject, message, recipient_email, html_message=None):
    """
    Send notification email with optional HTML content
    
    Args:
        subject: Email subject
        message: Plain text message
        recipient_email: Recipient's email address
        html_message: Optional HTML version of the message
    """
    try:
        email = EmailMultiAlternatives(
            subject=subject,
            body=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient_email]
        )
        
        # Add HTML alternative if provided
        if html_message:
            email.attach_alternative(html_message, "text/html")
            
        email.send()
        print(f"Email sent successfully to {recipient_email}")
    except Exception as e:
        print(f"Email sending failed to {recipient_email}: {str(e)}")


def send_contract_notification_email(contract, event_type, recipient_type):
    """
    Send contract-specific notification emails with better formatting
    
    Args:
        contract: Contract instance
        event_type: 'created', 'signed_by_artist', 'signed_by_buyer', 'activated'
        recipient_type: 'artist' or 'buyer'
    """
    
    if recipient_type == 'artist':
        recipient_email = contract.artist.email
        recipient_name = contract.artist.username
        other_party = contract.buyer.username
    else:
        recipient_email = contract.buyer.email
        recipient_name = contract.buyer.username
        other_party = contract.artist.username
    
    # Email content based on event type
    if event_type == 'created':
        subject = f"New Contract Created - {contract.job.title}"
        message = f"""
Hello {recipient_name},

A new contract has been created for the project "{contract.job.title}".

Contract Details:
- Project: {contract.job.title}
- Amount: PKR{contract.amount}
- Deadline: {contract.deadline.strftime('%B %d, %Y')}
- Status: {contract.get_status_display()}

Please review the contract terms and sign to proceed with the project.

Best regards,
CultureUp Team
        """
        
    elif event_type == 'signed_by_artist':
        subject = f"Contract Signed by Artist - {contract.job.title}"
        message = f"""
Hello {recipient_name},

Great news! {other_party} has signed the contract for "{contract.job.title}".

The contract is now waiting for your signature to become active.

Please review and sign the contract to start the project.

Best regards,
CultureUp Team
        """
        
    elif event_type == 'signed_by_buyer':
        subject = f"Contract Signed by Buyer - {contract.job.title}"
        message = f"""
Hello {recipient_name},

Excellent! {other_party} has signed the contract for "{contract.job.title}".

The contract is now waiting for your signature to become active.

Please review and sign the contract to start working on the project.

Best regards,
CultureUp Team
        """
        
    elif event_type == 'activated':
        subject = f"Contract Activated - {contract.job.title}"
        message = f"""
Hello {recipient_name},

Congratulations! The contract for "{contract.job.title}" is now ACTIVE.

Both parties have signed the contract and work can now begin!

Contract Details:
- Project: {contract.job.title}
- Amount: PKR{contract.amount}
- Deadline: {contract.deadline.strftime('%B %d, %Y')}

{"As the artist, you can now start working on the project." if recipient_type == 'artist' else "The artist will now begin working on your project."}

Best regards,
CultureUp Team
        """
        
    elif event_type == 'completed':
        subject = f"Contract Completed - {contract.job.title}"
        message = f"""
Hello {recipient_name},

Great news! The contract for "{contract.job.title}" has been successfully completed.

Contract Summary:
- Project: {contract.job.title}
- Amount: PKR{contract.amount}
- Completion Date: {timezone.now().strftime('%B %d, %Y')}

{"Your work has been delivered and payment has been released." if recipient_type == 'artist' else "The project has been completed successfully. Thank you for working with our platform!"}

We hope you had a great experience. Please consider leaving a review for your {"client" if recipient_type == 'artist' else "artist"}.

Best regards,
CultureUp Team
        """
        
    elif event_type == 'terminated':
        subject = f"Contract Terminated - {contract.job.title}"
        message = f"""
Hello {recipient_name},

We regret to inform you that the contract for "{contract.job.title}" has been terminated.

Contract Details:
- Project: {contract.job.title}
- Amount: PKR{contract.amount}
- Termination Date: {timezone.now().strftime('%B %d, %Y')}

If you have any questions about this termination, please contact our support team.

Best regards,
CultureUp Team
        """
    
    try:
        send_notification_email(subject, message, recipient_email)
    except Exception as e:
        print(f"Failed to send contract notification: {str(e)}")
