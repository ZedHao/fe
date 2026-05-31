#!/usr/bin/env python
import os
import sys

base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, base_dir)


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'new_server.settings')
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
