import responses
from . import v2_convert

def pid_responses(host, version=3):
    """Mock responses for pid methods"""
    
    from .data import pid_paths, pid_xpaths

    if version == 2:
        pid_paths = v2_convert(pid_paths)

    # Get all pid_paths
    responses.add(responses.GET, f'{host}/pid/rest/settings/path/',
                  json=pid_paths, status=200)

    # Upload a new pid_path
    data = {}
    data['template'] = '1'
    data['path'] = 'roooty.key'
    responses.add(responses.POST, f'{host}/rest/xslt/',
                  match=[responses.matchers.urlencoded_params_matcher(data)],
                  json={'id':3, 'path':'roooty.key', 'template':1}, status=201)
    data = {}
    data['template'] = '3'
    data['path'] = 'rooty.key'
    responses.add(responses.POST, f'{host}/rest/xslt/',
                  match=[responses.matchers.urlencoded_params_matcher(data)],
                  json=pid_paths[1], status=201)
    
    # Modify the xslt
    data = {}
    data['path'] = 'rooty.key'
    responses.add(responses.PATCH, f'{host}/pid/rest/settings/path/2/',
                  match=[responses.matchers.urlencoded_params_matcher(data)],
                  json=pid_paths[1], status=201)

    # Delete xslt
    responses.add(responses.DELETE, f'{host}/pid/rest/settings/path/2/',
                  body=b'', status=204)
    
    
    # Get pid settings
    responses.add(responses.GET, f'{host}/pid/rest/settings/',
                  json={'auto_set_pid': True, 'path': '', 'format': '[a-zA-Z0-9_\\-]+',
                        'system_name': 'local', 'system_type': 'core_linked_records_app.utils.providers.local.LocalIdProvider',
                        'prefixes': ['test']}, status=200)

    # Change pid settings
    data = {}
    data['auto_set_pid'] = 'True'
    responses.add(responses.PATCH, f'{host}/pid/rest/settings/',
                  match=[responses.matchers.urlencoded_params_matcher(data)],
                  json={'auto_set_pid': True, 'path': '', 'format': '[a-zA-Z0-9_\\-]+',
                        'system_name': 'local', 'system_type': 'core_linked_records_app.utils.providers.local.LocalIdProvider',
                        'prefixes': ['test']}, status=200)
    
    data = {}
    data['auto_set_pid'] = 'False'
    responses.add(responses.PATCH, f'{host}/pid/rest/settings/',
                  match=[responses.matchers.urlencoded_params_matcher(data)],
                  json={'auto_set_pid': False, 'path': '', 'format': '[a-zA-Z0-9_\\-]+',
                        'system_name': 'local', 'system_type': 'core_linked_records_app.utils.providers.local.LocalIdProvider',
                        'prefixes': ['test']}, status=200)

    

#################### OLD XPATH ROUTES #######################
    
    # Get all pid_paths
    responses.add(responses.GET, f'{host}/pid/rest/settings/xpath/',
                  json=pid_xpaths, status=200)

    # Upload a new pid_path
    data = {}
    data['template'] = '1'
    data['xpath'] = 'roooty.key'
    responses.add(responses.POST, f'{host}/rest/xslt/',
                  match=[responses.matchers.urlencoded_params_matcher(data)],
                  json={'id':3, 'xpath':'roooty.key', 'template':1}, status=201)
    data = {}
    data['template'] = '3'
    data['xpath'] = 'rooty.key'
    responses.add(responses.POST, f'{host}/rest/xslt/',
                  match=[responses.matchers.urlencoded_params_matcher(data)],
                  json=pid_xpaths[1], status=201)
    
    # Modify the xslt
    data = {}
    data['xpath'] = 'rooty.key'
    responses.add(responses.PATCH, f'{host}/pid/rest/settings/xpath/2/',
                  match=[responses.matchers.urlencoded_params_matcher(data)],
                  json=pid_xpaths[1], status=201)

    # Delete xslt
    responses.add(responses.DELETE, f'{host}/pid/rest/settings/xpath/2/',
                  body=b'', status=204)
    
    
    # Get pid settings
    responses.add(responses.GET, f'{host}/pid/rest/settings/',
                  json={'auto_set_pid': True, 'xpath': '', 'format': '[a-zA-Z0-9_\\-]+',
                        'system_name': 'local', 'system_type': 'core_linked_records_app.utils.providers.local.LocalIdProvider',
                        'prefixes': ['test']}, status=200)

    # Change pid settings
    data = {}
    data['auto_set_pid'] = 'True'
    responses.add(responses.PATCH, f'{host}/pid/rest/settings/',
                  match=[responses.matchers.urlencoded_params_matcher(data)],
                  json={'auto_set_pid': True, 'xpath': '', 'format': '[a-zA-Z0-9_\\-]+',
                        'system_name': 'local', 'system_type': 'core_linked_records_app.utils.providers.local.LocalIdProvider',
                        'prefixes': ['test']}, status=200)
    
    data = {}
    data['auto_set_pid'] = 'False'
    responses.add(responses.PATCH, f'{host}/pid/rest/settings/',
                  match=[responses.matchers.urlencoded_params_matcher(data)],
                  json={'auto_set_pid': False, 'xpath': '', 'format': '[a-zA-Z0-9_\\-]+',
                        'system_name': 'local', 'system_type': 'core_linked_records_app.utils.providers.local.LocalIdProvider',
                        'prefixes': ['test']}, status=200)