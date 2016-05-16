# django-voximplant
Django application for VoxImplant integration.

## settings
```
VOX_USER_ID = '1'
VOX_API_KEY = '123'
VOX_SCRIPTS_PATH = os.path.join(BASE_DIR, 'vox_scripts')
VOX_MAX_SIMULTANEOUS = 10
VOX_APPLICATION_NAME = 'test_app.accaount_name.voximplant.com'
```

## start settings
Download exists vox implant data
```
./manage.py vox_download
```

Create if not exists project application and role for them /admin/voximplant/application/add/

Upload changes
```
./manage.py vox_upload
```

