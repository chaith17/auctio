import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auctio.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
if not User.objects.filter(username='testuser').exists():
    User.objects.create_user('testuser', 'test@example.com', 'testpassword')
    print("User 'testuser' created.")
else:
    print("User 'testuser' already exists.")
