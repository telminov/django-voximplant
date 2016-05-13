# coding: utf-8
from django.core.management.base import BaseCommand
from ... import tools


class Command(BaseCommand):
    help = 'Grab data from VoxImplant'

    def handle(self, *args, **options):
        print('Load applications...')
        tools.download_apps()

        print('Load rules...')
        tools.download_rules()

        print('Load scenarios...')
        tools.download_scenarios()

