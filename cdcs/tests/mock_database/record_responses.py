import responses
from . import v2_convert

def record_responses(host, version=3):
    
    if version == 2:
        record_responses_v2(host)
    else:
        record_responses_v3(host)

def record_responses_v2(host):
    
    from .data import records
    records = v2_convert(records)
    
    # Get all records (last ignored to use with upload_record)
    params = {}
    responses.add(responses.GET, f'{host}/rest/data/',
                  match=[responses.matchers.query_param_matcher(params)],
                  json=records, status=200)

    # Get records for one template
    params = {'template':'1'}
    responses.add(responses.GET, f'{host}/rest/data/',
                  match=[responses.matchers.query_param_matcher(params)],
                  json=records[:8], status=200)

    # Get the fourth record using title
    params = {'title':'first-record-4'}
    responses.add(responses.GET, f'{host}/rest/data/',
                  match=[responses.matchers.query_param_matcher(params)],
                  json=records[3:4], status=200)
    params = {'template':'1', 'title':'first-record-4'}
    responses.add(responses.GET, f'{host}/rest/data/',
                  match=[responses.matchers.query_param_matcher(params)],
                  json=records[3:4], status=200)

    # Get no matching records using title
    params = {'title':'does-not-exist'}
    responses.add(responses.GET, f'{host}/rest/data/',
                  match=[responses.matchers.query_param_matcher(params)],
                  json=[], status=200)

    # False response saying last record does not exist for upload_record
    params = {'title':'second-record-4', 'template':'3'}
    responses.add(responses.GET, f'{host}/rest/data/',
                  match=[responses.matchers.query_param_matcher(params)],
                  json=[], status=200)

    # Assign records to the global workspace
    responses.add(responses.PATCH, f'{host}/rest/data/1/assign/1',
                  json={}, status=200)
    responses.add(responses.PATCH, f'{host}/rest/data/2/assign/1',
                  json={}, status=200)
    responses.add(responses.PATCH, f'{host}/rest/data/3/assign/1',
                  json={}, status=200)
    responses.add(responses.PATCH, f'{host}/rest/data/4/assign/1',
                  json={}, status=200)  
    responses.add(responses.PATCH, f'{host}/rest/data/5/assign/1',
                  json={}, status=200)
    responses.add(responses.PATCH, f'{host}/rest/data/6/assign/1',
                  json={}, status=200)
    responses.add(responses.PATCH, f'{host}/rest/data/7/assign/1',
                  json={}, status=200)
    responses.add(responses.PATCH, f'{host}/rest/data/8/assign/1',
                  json={}, status=200)
    responses.add(responses.PATCH, f'{host}/rest/data/9/assign/1',
                  json={}, status=200)
    responses.add(responses.PATCH, f'{host}/rest/data/10/assign/1',
                  json={}, status=200)
    responses.add(responses.PATCH, f'{host}/rest/data/11/assign/1',
                  json={}, status=200)
    responses.add(responses.PATCH, f'{host}/rest/data/12/assign/1',
                  json={}, status=200)

    # Upload using the last record
    json = records[-1]
    data = {'title': json['title'],
            'template': json['template'],
            'xml_content': json['xml_content']}
    responses.add(responses.POST, f'{host}/rest/data/',
                  match=[responses.matchers.urlencoded_params_matcher(data)],
                  json=json, status=201)

    # Upload using the fourth record
    json = records[3]
    data = {'title': json['title'],
            'template': json['template'],
            'xml_content': json['xml_content']}
    responses.add(responses.POST, f'{host}/rest/data/',
                  match=[responses.matchers.urlencoded_params_matcher(data)],
                  json=json, status=201)

    # Update using the fourth record
    json = records[3]
    data = {'xml_content': json['xml_content']}
    responses.add(responses.PATCH, f'{host}/rest/data/4/',
                  match=[responses.matchers.urlencoded_params_matcher(data)],
                  json=json, status=200)

    # Delete the fourth record
    responses.add(responses.DELETE, f'{host}/rest/data/4/',
                  body=b'', status=204)


def record_responses_v3(host):
    
    from .data import records

    # Get all records (last ignored to use with upload_record)
    params = {}
    json = {'count':12, 'next':f'{host}/rest/data/?page=2', 'previous':None,
            'results':records[:10]}
    responses.add(responses.GET, f'{host}/rest/data/',
                  match=[responses.matchers.query_param_matcher(params)],
                  json=json, status=200)
    params = {'page':1}
    json = {'count':12, 'next':f'{host}/rest/data/?page=2', 'previous':None,
            'results':records[:10]}
    responses.add(responses.GET, f'{host}/rest/data/',
                  match=[responses.matchers.query_param_matcher(params)],
                  json=json, status=200)
    params = {'page':2}
    json = {'count':12, 'next':None, 'previous':f'{host}/rest/data/',
            'results':records[10:]}
    responses.add(responses.GET, f'{host}/rest/data/',
                  match=[responses.matchers.query_param_matcher(params)],
                  json=json, status=200)

    # Get records for one template
    params = {'template':1}
    json = {'count':8, 'next':None, 'previous':None,
            'results':records[:8]}
    responses.add(responses.GET, f'{host}/rest/data/',
                  match=[responses.matchers.query_param_matcher(params)],
                  json=json, status=200)

    # Get the fourth record using title
    params = {'title':'first-record-4'}
    json = {'count':1, 'next':None, 'previous':None,
            'results':records[3:4]}
    responses.add(responses.GET, f'{host}/rest/data/',
                  match=[responses.matchers.query_param_matcher(params)],
                  json=json, status=200)
    params = {'template':1, 'title':'first-record-4'}
    responses.add(responses.GET, f'{host}/rest/data/',
                  match=[responses.matchers.query_param_matcher(params)],
                  json=json, status=200)

    # Get no matching records using title
    json = {'count':0, 'next':None, 'previous':None,
            'results':[]}
    params = {'title':'does-not-exist'}
    responses.add(responses.GET, f'{host}/rest/data/',
                  match=[responses.matchers.query_param_matcher(params)],
                  json=json, status=200)

    # False response saying last record does not exist for upload_record
    json = {'count':0, 'next':None, 'previous':None,
            'results':[]}
    params = {'title':'second-record-4', 'template':3}
    responses.add(responses.GET, f'{host}/rest/data/',
                  match=[responses.matchers.query_param_matcher(params)],
                  json=json, status=200)

    # Assign records to the global workspace
    responses.add(responses.PATCH, f'{host}/rest/data/1/assign/1',
                  json={}, status=200)
    responses.add(responses.PATCH, f'{host}/rest/data/2/assign/1',
                  json={}, status=200)
    responses.add(responses.PATCH, f'{host}/rest/data/3/assign/1',
                  json={}, status=200)
    responses.add(responses.PATCH, f'{host}/rest/data/4/assign/1',
                  json={}, status=200)  
    responses.add(responses.PATCH, f'{host}/rest/data/5/assign/1',
                  json={}, status=200)
    responses.add(responses.PATCH, f'{host}/rest/data/6/assign/1',
                  json={}, status=200)
    responses.add(responses.PATCH, f'{host}/rest/data/7/assign/1',
                  json={}, status=200)
    responses.add(responses.PATCH, f'{host}/rest/data/8/assign/1',
                  json={}, status=200)
    responses.add(responses.PATCH, f'{host}/rest/data/9/assign/1',
                  json={}, status=200)
    responses.add(responses.PATCH, f'{host}/rest/data/10/assign/1',
                  json={}, status=200)
    responses.add(responses.PATCH, f'{host}/rest/data/11/assign/1',
                  json={}, status=200)
    responses.add(responses.PATCH, f'{host}/rest/data/12/assign/1',
                  json={}, status=200)

    # Upload using the last record
    json = records[-1]
    data = {'title': json['title'],
            'template': str(json['template']),
            'xml_content': json['xml_content']}
    responses.add(responses.POST, f'{host}/rest/data/',
                  match=[responses.matchers.urlencoded_params_matcher(data)],
                  json=json, status=201)

    # Upload using the fourth record
    json = records[3]
    data = {'title': json['title'],
            'template': str(json['template']),
            'xml_content': json['xml_content']}
    responses.add(responses.POST, f'{host}/rest/data/',
                  match=[responses.matchers.urlencoded_params_matcher(data)],
                  json=json, status=201)

    # Update using the fourth record
    json = records[3]
    data = {'xml_content': json['xml_content']}
    responses.add(responses.PATCH, f'{host}/rest/data/4/',
                  match=[responses.matchers.urlencoded_params_matcher(data)],
                  json=json, status=200)

    # Delete the fourth record
    responses.add(responses.DELETE, f'{host}/rest/data/4/',
                  body=b'', status=204)