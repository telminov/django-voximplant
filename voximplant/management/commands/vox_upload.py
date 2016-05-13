# coding: utf-8
from django.core.management.base import BaseCommand
from ... import tools


class Command(BaseCommand):
    help = 'Grab data from VoxImplant'

    def handle(self, *args, **options):
        print('Upload scenarios...')
        tools.upload_scenarios()

