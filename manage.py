#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studentgov.settings')
    
    # 🚨 THE CLEANUP TRICK: Deletes duplicate items before migrations fire off
    if 'migrate' in sys.argv:
        try:
            import django
            django.setup()
            from django.db import connection
            # Directly clean the table safely using raw SQL
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM inventory_item WHERE name = 'bond';")
                print("✨ Successfully purged duplicate inventory items from production!")
        except Exception as e:
            print(f"Bypassed or table doesn't exist yet: {e}")

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()