# coding: utf-8
from django.core.management.base import BaseCommand
from ... import tools


class Command(BaseCommand):
    help = 'Start Call List'

    def add_arguments(self, parser):
        parser.add_argument('--id', dest='call_list_id', type=int)
        parser.add_argument('-f', '--force', dest='force', action='store_true')

    def handle(self, *args, **options):
        call_list_id = options['call_list_id']
        force = bool(options.get('force'))
        tools.call_list_send(call_list_id, force)

