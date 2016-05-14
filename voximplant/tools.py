# coding: utf-8
# from django.db.models import Q, F
from django.utils.timezone import now
from . import models
from . import api_client


class SendCallListException(Exception):
    pass


class DownloadCallListException(Exception):
    pass


def download_scenarios():
    result = api_client.get_scenarios()

    incoming_ids = set([i['scenario_id'] for i in result])
    exists_ids = set(models.Scenario.objects.filter(vox_id__isnull=False).values_list('vox_id', flat=True))
    deleted_ids = exists_ids - incoming_ids
    models.Scenario.objects.filter(vox_id__in=deleted_ids).delete()

    for item_data in result:
        scenario, _ = models.Scenario.objects.get_or_create(vox_id=item_data['scenario_id'])
        scenario.name = item_data['scenario_name']
        scenario.modified = item_data['modified'] + 'Z'
        scenario.save()


def download_apps():
    result = api_client.get_apps()

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
    for app in models.Application.objects.filter(vox_id__isnull=False):
        result = api_client.get_rules(app.vox_id)

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

            incoming_scenario_ids = set([s['scenario_id'] for s in item_data['scenarios']])
            exists_scenario_ids = set(s.vox_id for s in rule.scenarios.all())

            deleted_scenario_ids = incoming_scenario_ids - exists_scenario_ids
            deleted_scenarios = models.Scenario.objects.filter(vox_id__in=deleted_scenario_ids)
            for deleted_scenario in deleted_scenarios:
                rule.scenarios.remove(deleted_scenario)

            added_scenario_ids = exists_scenario_ids - incoming_scenario_ids
            added_scenarios = models.Scenario.objects.filter(vox_id__in=added_scenario_ids)
            for added_scenario in added_scenarios:
                rule.scenarios.add(added_scenario)


def upload_scenarios():
    # scenarios = models.Scenario.objects.filter(Q(uploaded__isnull=True) | Q(uploaded__lte=F('modified')))
    scenarios = models.Scenario.objects.all()
    for scenario in scenarios:
        if scenario.get_modified() > scenario.uploaded:
            update_params = {'uploaded': now()}
            result = api_client.update_or_create_scenario(scenario.vox_id)
            if result.get('scenario_id'):
                update_params['vox_id'] = result['scenario_id']
            models.Scenario.objects.filter(id=scenario.id).update(**update_params)
            scenario = models.Scenario.objects.get(id=scenario.id)

        remote_rules = api_client.get_scenario_rules(scenario.vox_id)
        local_rules = set([r.vox_id for r in scenario.rules.all()])
        all_rules = local_rules | remote_rules
        for rule_vox_id in all_rules:
            bind = rule_vox_id in local_rules
            api_client.bind_scenario_rule(scenario.vox_id, rule_vox_id, bind)


def send_call_list(call_list_id: int, force=False):
    call_list = models.CallList.objects.get(id=call_list_id)
    if not force and call_list.started:
        raise SendCallListException('Call list with id "%s" already started at "%s"' % (call_list.id, call_list.started))

    result = api_client.create_call_list(call_list)
    call_list.vox_id = result['list_id']
    call_list.started = now()
    call_list.save()


def download_call_list(call_list_id: int):
    call_list = models.CallList.objects.get(id=call_list_id)
    if not call_list.vox_id:
        raise DownloadCallListException('Call list with id "%s" have not vox_id' % call_list.id)

    result = api_client.get_call_list_detail(call_list)
    for item in result:
        phone = call_list.phones.get(phone_number=item['phone_number'])
        phone.status = item['status']
        phone.last_attempt = item['last_attempt']
        phone.attempts_left = item['attmepts_left']
        phone.result_data_json = item['result_data']
        if not phone.completed and item['status'] == 'Processed':
            phone.completed = now()
        phone.save()
