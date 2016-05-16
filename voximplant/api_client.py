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


def apps_get() -> dict:
    url = API_URL + '/GetApplications'
    params = _get_auth_params()
    response = requests.get(url, params)

    if response.status_code != 200:
        raise VoxApiException('Got status code: %s.' % response.status_code, response=response)

    return response.json()['result']


def app_update_or_create(app: models.Application):
    data = _get_auth_params()
    if app.vox_id:
        url = API_URL + '/SetApplicationInfo'
        data['application_id'] = app.vox_id
    else:
        url = API_URL + '/AddApplication'

    data['application_name'] = app.name
    response = requests.post(url, data)

    if response.status_code != 200:
        raise VoxApiException('Got status code: %s.' % response.status_code, response=response)
    elif 'error' in response.json():
        raise VoxApiException('Upload error: %s.' % response.json()['error']['msg'], response=response)

    return response.json()


def rules_get(app_vox_id: int) -> dict:
    url = API_URL + '/GetRules'
    params = _get_auth_params()
    params['application_id'] = app_vox_id
    params['with_scenarios'] = True
    response = requests.get(url, params)

    if response.status_code != 200:
        raise VoxApiException('Got status code: %s.' % response.status_code, response=response)

    return response.json()['result']


def rule_update_or_create(rule: models.Rule):
    assert rule.application.vox_id

    data = _get_auth_params()
    if rule.vox_id:
        url = API_URL + '/SetRuleInfo'
        data['rule_id'] = rule.vox_id
    else:
        url = API_URL + '/AddRule'
        data['application_id'] = rule.application.vox_id

    data['rule_name'] = rule.name
    data['rule_pattern'] = rule.pattern
    response = requests.post(url, data)

    if response.status_code != 200:
        raise VoxApiException('Got status code: %s.' % response.status_code, response=response)
    elif 'error' in response.json():
        raise VoxApiException('Upload error: %s.' % response.json()['error']['msg'], response=response)

    return response.json()


def scenarios_get() -> dict:
    url = API_URL + '/GetScenarios'
    params = _get_auth_params()
    response = requests.get(url, params)

    if response.status_code != 200:
        raise VoxApiException('Got status code: %s.' % response.status_code, response=response)

    return response.json()['result']


def scenario_get_rules(scenario_vox_id: int):
    rule_vox_ids = set()
    for app in models.Application.objects.filter(vox_id__isnull=False):
        for rule_data in rules_get(app.vox_id):
            for scenario_data in rule_data['scenarios']:
                if scenario_data['scenario_id'] == scenario_vox_id:
                    rule_vox_ids.add(rule_data['rule_id'])
    return rule_vox_ids


def scenario_update_or_create(scenario: models.Scenario):
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


def scenario_bind_rule(scenario_vox_id: int, rule_vox_id: int, bind: bool):
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


def call_list_create(call_list: models.CallList):
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


def call_list_get_detail(call_list: models.CallList):
    url = API_URL + '/GetCallListDetails'
    params = _get_auth_params()
    params['list_id'] = call_list.vox_id
    params['output'] = 'json'

    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise VoxApiException('Got status code: %s.' % response.status_code, response=response)

    result = response.json()['result']
    for item in result:
        item['custom_data'] = json.loads(item['custom_data'])
        item['phone_number'] = item['custom_data']['phone_number']
    return result


def call_list_stop(call_list: models.CallList):
    url = API_URL + '/StopCallListProcessing'
    data = _get_auth_params()
    data['list_id'] = call_list.vox_id

    response = requests.post(url, data=data)

    if response.status_code != 200:
        raise VoxApiException('Got status code: %s.' % response.status_code, response=response)
    elif 'error' in response.json():
        raise VoxApiException('Stop call list error: %s.' % response.json()['error']['msg'], response=response)

    result = response.json()
    return result


def call_list_recover(call_list: models.CallList):
    url = API_URL + '/RecoverCallList'
    data = _get_auth_params()
    data['list_id'] = call_list.vox_id

    response = requests.post(url, data=data)

    if response.status_code != 200:
        raise VoxApiException('Got status code: %s.' % response.status_code, response=response)
    elif 'error' in response.json():
        raise VoxApiException('Recover call list error: %s.' % response.json()['error']['msg'], response=response)

    result = response.json()
    return result


def _get_auth_params() -> dict:
    return {
        'account_id': settings.VOX_USER_ID,
        'api_key': settings.VOX_API_KEY,
    }
