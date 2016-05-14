# coding: utf-8
import tempfile

import os
import json
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


def create_call_list(call_list: models.CallList):
    url = API_URL + '/CreateCallList'
    params = _get_auth_params()
    params['rule_id'] = call_list.rule.vox_id
    params['priority'] = call_list.priority
    params['max_simultaneous'] = call_list.max_simultaneous
    params['num_attempts'] = call_list.num_attempts
    params['name'] = call_list.name
    params['interval_seconds'] = call_list.interval_seconds

    phones_data = {}
    custom_data_keys = set([])
    for phone in call_list.phones.all():
        phone_data = json.loads(phone.custom_data_json)
        custom_data_keys.update(phone_data.keys())
        phones_data[phone.phone_number] = phone_data

    body_header = ['phone_number'] + list(custom_data_keys)
    body_data = []
    for phone_number, custom_data in phones_data.items():
        row = [phone_number]
        for key in custom_data_keys:
            value = custom_data.get(key, '')
            row.append(value)
        body_data.append(row)

    body_content = ';'.join(body_header)
    for row in body_data:
        body_content += '\n' + ';'.join(row)

    _, file_path = tempfile.mkstemp(prefix='call_list_', suffix='.csv')
    with open(file_path, mode='w') as f:
        f.write(body_content)

    with open(file_path, mode='r') as f:
        response = requests.post(url, params=params, files={'file_content': f})

    os.unlink(file_path)

    if response.status_code != 200:
        raise VoxApiException('Got status code: %s.' % response.status_code, response=response)
    elif 'error' in response.json():
        raise VoxApiException('Create call list error: %s.' % response.json()['error']['msg'], response=response)

    result = response.json()
    return result


def _get_auth_params() -> dict:
    return {
        'account_id': settings.VOX_USER_ID,
        'api_key': settings.VOX_API_KEY,
    }
