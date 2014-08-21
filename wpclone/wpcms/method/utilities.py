from django.core.mail.message import EmailMessage
from django.template.loader import get_template
from django.template import Context

__author__ = 'om'
from wpcms.models import WPUser

from django.contrib.auth.hashers import make_password,check_password



def wp_user_authenticate(username,password):
    try:
        user = WPUser.objects.get(user_login = username)
    except WPUser.DoesNotExist:
        return False
    if user:
        if check_password(password,user.user_pass):
            return user
        else:
            return False
    else:
        return False


def send_password_reset(first_name, user_email, token, current_site):
    """
    Send reset password link in email
    Params:
    first_name = First name of user
    user_email = Email of user
    token = Activation Token for user
    """
    print "send_password reset is executed"
    # Get html content of template with variables
    email_body = get_template("admin/reset_password_email_send.html").render(Context({
        'username': first_name,
        'token': token,
        'current_site': current_site,
        'error': True,}))
    send_email(
        email_subject = "Welcome",
        email_body = email_body,
        to_list = user_email
    )


def send_email(email_subject, email_body, to_list):
    """
    Core function to send an email
    Params:
    email_subject : Email subject string
    email_body : Email body string
    to_list : List of destination email ids
    """
    print "send_email executed"
    try:
        email = EmailMessage(subject=email_subject, body=email_body, to=to_list)
        # print "Body:" + str(email.body)
        # print "To:" + str(email.to)
        email.content_subtype = 'html'
        email.send()
    except Exception as e:
        print "Error in sending email:" + str(e)
