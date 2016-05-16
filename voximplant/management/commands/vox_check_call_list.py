# coding: utf-8
from django.core.management.base import BaseCommand
from ... import tools


class Command(BaseCommand):
    help = 'Start Call List'

    def add_arguments(self, parser):
        parser.add_argument('-i', '--infinitely', dest='infinitely', action='store_true')
        parser.add_argument('-s', '--sleep', dest='sleep_sec', type=int, default=10)

    def handle(self, *args, **options):
        infinitely = options.get('infinitely')
        sleep_sec = options.get('sleep_sec')
        verbosity = options.get('verbosity')
        tools.check_call_list(infinitely, sleep_sec=sleep_sec, verbosity=verbosity)

