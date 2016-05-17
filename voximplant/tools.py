# coding: utf-8
import time
from django.db.models import Q, F
from django.utils.timezone import now
from . import models
from . import api_client


class SendCallListException(Exception):
    pass


class DownloadCallListException(Exception):
    pass


def scenarios_download():
    result = api_client.scenarios_get()

    incoming_ids = set([i['scenario_id'] for i in result])
    exists_ids = set(models.Scenario.objects.filter(vox_id__isnull=False).values_list('vox_id', flat=True))
    deleted_ids = exists_ids - incoming_ids
    models.Scenario.objects.filter(vox_id__in=deleted_ids).delete()

    for item_data in result:
        scenario, _ = models.Scenario.objects.get_or_create(vox_id=item_data['scenario_id'])
        scenario.name = item_data['scenario_name']
        scenario.modified = item_data['modified'] + 'Z'
        scenario.save()


def apps_download():
    result = api_client.apps_get()

    incoming_ids = set([i['application_id'] for i in result])
    exists_ids = set(models.Application.objects.filter(vox_id__isnull=False).values_list('vox_id', flat=True))
    deleted_ids = exists_ids - incoming_ids
    models.Application.objects.filter(vox_id__in=deleted_ids).delete()

    for item_data in result:
        app, _ = models.Application.objects.get_or_create(vox_id=item_data['application_id'])
        app.name = item_data['application_name']
        app.modified = item_data['modified'] + 'Z'
        app.save()


def apps_upload():
    apps = models.Application.objects.filter(Q(vox_id__isnull=True) | Q(modified__gte=F('uploaded')))
    for app in apps:
        update_params = {'uploaded': now()}
        result = api_client.app_update_or_create(app)
        if result.get('application_id'):
            update_params['vox_id'] = result['application_id']
        models.Application.objects.filter(id=app.id).update(**update_params)


def rules_upload():
    rules = models.Rule.objects.filter(application__vox_id__isnull=False)\
        .filter(Q(vox_id__isnull=True) | Q(modified__gte=F('uploaded')))

    for rule in rules:
        is_new = not rule.vox_id

        update_params = {'uploaded': now()}
        result = api_client.rule_update_or_create(rule)
        if result.get('rule_id'):
            update_params['vox_id'] = result['rule_id']
        models.Rule.objects.filter(id=rule.id).update(**update_params)

        if is_new:
            rule = models.Rule.objects.get(id=rule.id)
            for scenario in rule.scenarios.filter(vox_id__isnull=False):
                api_client.scenario_bind_rule(scenario.vox_id, rule.vox_id, True)


def rules_download():
    for app in models.Application.objects.filter(vox_id__isnull=False):
        result = api_client.rules_get(app.vox_id)

        incoming_ids = set([i['rule_id'] for i in result])
        exists_ids = set(models.Rule.objects.filter(vox_id__isnull=False).values_list('vox_id', flat=True))
        deleted_ids = exists_ids - incoming_ids
        models.Rule.objects.filter(application=app, vox_id__in=deleted_ids).delete()

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


def scenarios_upload():
    scenarios = models.Scenario.objects.all()
    for scenario in scenarios:
        if not scenario.file_path:
            continue

        if not scenario.uploaded or scenario.get_modified() > scenario.uploaded:
            update_params = {'uploaded': now()}
            result = api_client.scenario_update_or_create(scenario)
            if result.get('scenario_id'):
                update_params['vox_id'] = result['scenario_id']
            models.Scenario.objects.filter(id=scenario.id).update(**update_params)
            scenario = models.Scenario.objects.get(id=scenario.id)

        remote_rules = api_client.scenario_get_rules(scenario.vox_id)
        local_rules = set([r.vox_id for r in scenario.rules.all() if r.vox_id])
        all_rules = local_rules | remote_rules
        for rule_vox_id in all_rules:
            bind = rule_vox_id in local_rules
            api_client.scenario_bind_rule(scenario.vox_id, rule_vox_id, bind)


def call_list_send(call_list_id: int, force=False):
    call_list = models.CallList.objects.get(id=call_list_id)
    assert not call_list.vox_id

    if not force and call_list.started:
        raise SendCallListException(
            'Call list with id "%s" already started at "%s"' % (call_list.id, call_list.started))

    result = api_client.call_list_create(call_list)
    call_list.vox_id = result['list_id']
    call_list.started = now()
    call_list.save()


def call_list_stop(call_list_id: int):
    call_list = models.CallList.objects.get(id=call_list_id)
    assert call_list.vox_id

    api_client.call_list_stop(call_list)
    call_list.canceled = now()
    call_list.save()


def call_list_recover(call_list_id: int):
    call_list = models.CallList.objects.get(id=call_list_id)
    assert call_list.vox_id

    if not call_list.canceled:
        raise SendCallListException('Call list with id "%s" is not stopped' % call_list.id)

    api_client.call_list_recover(call_list)
    call_list.canceled = None
    call_list.save()


def call_list_download(call_list_id: int, verbosity: int = 1):
    call_list = models.CallList.objects.get(id=call_list_id)
    if not call_list.vox_id:
        raise DownloadCallListException('Call list with id "%s" have not vox_id' % call_list.id)

    result = api_client.call_list_get_detail(call_list)
    for item in result:
        phone = call_list.phones.get(phone_number=item['phone_number'])
        phone.status = item['status']
        phone.last_attempt = item['last_attempt'] + 'Z' if item['last_attempt'] else None
        phone.attempts_left = item['attmepts_left']
        phone.result_data_json = item.get('result_data', '')
        if not phone.completed and item['status'] == 'Processed':
            phone.completed = now()
        phone.save()

    call_list.downloaded = now()
    call_list.save()


def call_lists_check(infinitely: bool = False, sleep_sec: int = 10, verbosity: int = 1):
    while True:
        uncompleted_ids = set(
            models.CallListPhone.objects
                .exclude(status__in=(models.CallListPhone.STATUS_PROCESSED, models.CallListPhone.STATUS_ERROR))
                .filter(call_list__started__isnull=False, completed__isnull=True)
                .filter(Q(call_list__canceled__isnull=True) | Q(call_list__canceled__gte=F('call_list__downloaded')))  # make last check callist state after canceling
                .values_list('call_list__id', flat=True))
        if verbosity > 1:
            print('Started and uncompleted call lists: ', len(uncompleted_ids))

        for call_list_id in uncompleted_ids:
            if verbosity > 1:
                print('Downloading call list with id "%s"... ' % call_list_id)

            call_list_download(call_list_id, verbosity=verbosity)

            if verbosity > 1:
                print('complete.')

        if infinitely:
            if verbosity > 2:
                print('Sleep', sleep_sec)

            time.sleep(sleep_sec)
        else:
            return
