import os
import sys

# Добавьте ваш путь к проекту в Python path
# Вам нужно, чтобы этот путь вел к папке, где находится manage.py
path = '/home/studip/bookshelf/bookshelf'
if path not in sys.path:
    sys.path.append(path)

from django.core.wsgi import get_wsgi_application

# Укажите Django, где найти файл настроек
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookshelf.bookshelf.settings')

application = get_wsgi_application()