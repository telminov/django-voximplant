# coding: utf-8
import requests
from django.conf import settings
from . import models

API_URL = 'https://api.voximplant.com/platform_api'


class VoxApiException(Exception):
    def __init__(self, *args, **kwargs):
        self.response = kwargs.pop('response')


def get_apps() -> dict:
    url = API_URL + '/GetApplications'
    params = _get_auth_params()
    response = requests.get(url, params)

    if response.status_code != 200:
        raise VoxApiException('Got status code: %s.' % response.status_code, response=response)

    return response.json()['result']


def get_rules(app_vox_id: int) -> dict:
    url = API_URL + '/GetRules'
    params = _get_auth_params()
    params['application_id'] = app_vox_id
    params['with_scenarios'] = True
    response = requests.get(url, params)

    if response.status_code != 200:
        raise VoxApiException('Got status code: %s.' % response.status_code, response=response)

    return response.json()['result']


def get_scenarios() -> dict:
    url = API_URL + '/GetScenarios'
    params = _get_auth_params()
    response = requests.get(url, params)

    if response.status_code != 200:
        raise VoxApiException('Got status code: %s.' % response.status_code, response=response)

    return response.json()['result']


def get_scenario_rules(scenario_vox_id: int):
    rule_vox_ids = set()
    for app in models.Application.objects.filter(vox_id__isnull=False):
        for rule_data in get_rules(app.vox_id):
            for scenario_data in rule_data['scenarios']:
                if scenario_data['scenario_id'] == scenario_vox_id:
                    rule_vox_ids.add(rule_data['rule_id'])
    return rule_vox_ids


def update_or_create_scenario(scenario_vox_id: int):
    scenario = models.Scenario.objects.get(vox_id=scenario_vox_id)

    data = _get_auth_params()
    if scenario.vox_id:
        url = API_URL + '/SetScenarioInfo'
        data['scenario_id'] = scenario.vox_id
    else:
        url = API_URL + '/AddScenario'

    data['scenario_name'] = scenario.name
    data['scenario_script'] = scenario.get_script()
    response = requests.post(url, data)

    if response.status_code != 200:
        raise VoxApiException('Got status code: %s.' % response.status_code, response=response)
    elif 'error' in response.json():
        raise VoxApiException('Upload error: %s.' % response.json()['error']['msg'], response=response)

    return response.json()


def bind_scenario_rule(scenario_vox_id: int, rule_vox_id: int, bind: bool):
    rule = models.Rule.objects.get(vox_id=rule_vox_id)

    url = API_URL + '/BindScenario'
    data = _get_auth_params()
    data['scenario_id'] = scenario_vox_id
    data['rule_id'] = rule_vox_id
    data['application_id'] = rule.application.vox_id
    data['bind'] = int(bind)
    response = requests.post(url, data)

    if response.status_code != 200:
        raise VoxApiException('Got status code: %s.' % response.status_code, response=response)
    elif 'error' in response.json():
        raise VoxApiException('Upload error: %s.' % response.json()['error']['msg'], response=response)

    return response.json()


def _get_auth_params() -> dict:
    return {
        'account_id': settings.VOX_USER_ID,
        'api_key': settings.VOX_API_KEY,
    }
