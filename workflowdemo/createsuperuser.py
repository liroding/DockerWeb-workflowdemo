import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "workflowdemo.settings")
import django
django.setup()
from django.contrib.auth.models import User

username = 'admin'
password = 'dingyinglai'
email = 'admin@admin.com'

if User.objects.filter(username=username).count() == 0:
    User.objects.create_superuser(username, email, password)
    try:
        User.objects.get(username='AnonymousUser').delete()
    except Exception:
        pass
    print('Superuser created.')
else:
    print('Superuser creation skipped.')
