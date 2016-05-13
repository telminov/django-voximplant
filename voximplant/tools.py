# coding: utf-8
import requests
from django.conf import settings
from . import models

API_URL = 'https://api.voximplant.com/platform_api'


class VoxApiException(Exception):
    def __init__(self, *args, **kwargs):
        self.response = kwargs.pop('response')


def download_apps():
    url = API_URL + '/GetApplications'
    params = _get_auth_params()
    response = requests.get(url, params)

    if response.status_code != 200:
        raise VoxApiException('Got status code: %s.' % response.status_code, response=response)

    result = response.json()['result']

    incoming_ids = set([i['application_id'] for i in result])
    exists_ids = set(models.Application.objects.filter(vox_id__isnull=False).values_list('vox_id', flat=True))
    deleted_ids = exists_ids - incoming_ids
    models.Application.objects.filter(vox_id__in=deleted_ids).delete()

    for item_data in result:
        app, _ = models.Application.objects.get_or_create(vox_id=item_data['application_id'])
        app.name = item_data['application_name']
        app.modified = item_data['modified'] + 'Z'
        app.save()


def download_rules():
    url = API_URL + '/GetRules'
    params = _get_auth_params()

    for app in models.Application.objects.filter(vox_id__isnull=False):
        params['application_id'] = app.vox_id
        response = requests.get(url, params)

        if response.status_code != 200:
            raise VoxApiException('Got status code: %s.' % response.status_code, response=response)

        result = response.json()['result']

        incoming_ids = set([i['rule_id'] for i in result])
        exists_ids = set(models.Rule.objects.filter(vox_id__isnull=False).values_list('vox_id', flat=True))
        deleted_ids = exists_ids - incoming_ids
        models.Rule.objects.filter(vox_id__in=deleted_ids).delete()

        for item_data in result:
            rule, _ = models.Rule.objects.get_or_create(vox_id=item_data['rule_id'], defaults={'application': app})
            rule.name = item_data['rule_name']
            rule.pattern = item_data['rule_pattern']
            rule.modified = item_data['modified'] + 'Z'
            rule.save()


def download_scenarios():
    url = API_URL + '/GetScenarios'
    params = _get_auth_params()
    response = requests.get(url, params)

    if response.status_code != 200:
        raise VoxApiException('Got status code: %s.' % response.status_code, response=response)

    result = response.json()['result']

    incoming_ids = set([i['scenario_id'] for i in result])
    exists_ids = set(models.Scenario.objects.filter(vox_id__isnull=False).values_list('vox_id', flat=True))
    deleted_ids = exists_ids - incoming_ids
    models.Scenario.objects.filter(vox_id__in=deleted_ids).delete()

    for item_data in result:
        scenario, _ = models.Scenario.objects.get_or_create(vox_id=item_data['scenario_id'])
        scenario.name = item_data['scenario_name']
        scenario.modified = item_data['modified'] + 'Z'
        scenario.save()


def _get_auth_params() -> dict:
    return {
        'account_id': settings.VOX_USER_ID,
        'api_key': settings.VOX_API_KEY,
    }

