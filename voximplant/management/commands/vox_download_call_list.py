# coding: utf-8
from django.core.management.base import BaseCommand
from ... import tools


class Command(BaseCommand):
    help = 'Get call list detail'

    def add_arguments(self, parser):
        parser.add_argument('--id', dest='call_list_id', type=int)

    def handle(self, *args, **options):
        call_list_id = options['call_list_id']
        tools.download_call_list(call_list_id)

