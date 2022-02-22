import responses

from .data import template_managers

def template_manager_responses(host):
    """Mock responses for get_template_managers()"""

    # Default query - return entries for 'is_disabled' is False
    params={}
    responses.add(responses.GET,
                    f'{host}/rest/template-version-manager/global/',
                    status=200, json=template_managers[0:2],
                    match=[responses.matchers.query_param_matcher(params)])
    
    # Query for title == 'first'
    params={'title':'first'}
    responses.add(responses.GET,
                    f'{host}/rest/template-version-manager/global/',
                    status=200, json=template_managers[0:1],
                    match=[responses.matchers.query_param_matcher(params)])
    
    # Query for title == 'second'
    params={'title':'second'}
    responses.add(responses.GET,
                    f'{host}/rest/template-version-manager/global/',
                    status=200, json=template_managers[1:2],
                    match=[responses.matchers.query_param_matcher(params)])

    # Query for title -- 'zeroth' (return no matches) 
    params={'title':'zeroth'}
    responses.add(responses.GET,
                    f'{host}/rest/template-version-manager/global/',
                    status=200, json=[],
                    match=[responses.matchers.query_param_matcher(params)])
    
    # Query for 'is_disabled' is True
    params={'is_disabled':'True'}
    responses.add(responses.GET,
                    f'{host}/rest/template-version-manager/global/',
                    status=200, json=template_managers[2:],
                    match=[responses.matchers.query_param_matcher(params)])
    
    # Alternate url for useronly = True option
    responses.add(responses.GET,
                    f'{host}/rest/template-version-manager/user/',
                    status=200, json=[])