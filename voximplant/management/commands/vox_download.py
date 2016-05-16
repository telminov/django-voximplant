# coding: utf-8
from django.core.management.base import BaseCommand
from ... import tools


class Command(BaseCommand):
    help = 'Grab data from VoxImplant'

    def handle(self, *args, **options):
        print('Load scenarios...')
        tools.scenarios_download()

        print('Load applications...')
        tools.apps_download()

        print('Load rules...')
        tools.rules_download()

