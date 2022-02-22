import responses

from .data import records

def record_responses(host):
    
    # Get all records (last ignored to use with upload_record)
    params = {}
    responses.add(responses.GET, f'{host}/rest/data/',
                  match=[responses.matchers.query_param_matcher(params)],
                  json=records[:-1], status=200)

    # Get records for one template
    params = {'template':'firsthash1'}
    responses.add(responses.GET, f'{host}/rest/data/',
                  match=[responses.matchers.query_param_matcher(params)],
                  json=records[:8], status=200)

    # Get the fourth record using title
    params = {'title':'first-record-4'}
    responses.add(responses.GET, f'{host}/rest/data/',
                  match=[responses.matchers.query_param_matcher(params)],
                  json=records[3:4], status=200)
    params = {'template':'firsthash1', 'title':'first-record-4'}
    responses.add(responses.GET, f'{host}/rest/data/',
                  match=[responses.matchers.query_param_matcher(params)],
                  json=records[3:4], status=200)

    # Get no matching records using title
    params = {'title':'does-not-exist'}
    responses.add(responses.GET, f'{host}/rest/data/',
                  match=[responses.matchers.query_param_matcher(params)],
                  json=[], status=200)

    # False response saying last record does not exist for upload_record
    params = {'title':'second-record-4', 'template':'secondhash2'}
    responses.add(responses.GET, f'{host}/rest/data/',
                  match=[responses.matchers.query_param_matcher(params)],
                  json=[], status=200)

    # Assign records to the global workspace
    responses.add(responses.PATCH, f'{host}/rest/data/r1/assign/somehashkey',
                  json={}, status=200)
    responses.add(responses.PATCH, f'{host}/rest/data/r2/assign/somehashkey',
                  json={}, status=200)
    responses.add(responses.PATCH, f'{host}/rest/data/r3/assign/somehashkey',
                  json={}, status=200)
    responses.add(responses.PATCH, f'{host}/rest/data/r4/assign/somehashkey',
                  json={}, status=200)  
    responses.add(responses.PATCH, f'{host}/rest/data/r5/assign/somehashkey',
                  json={}, status=200)
    responses.add(responses.PATCH, f'{host}/rest/data/r6/assign/somehashkey',
                  json={}, status=200)
    responses.add(responses.PATCH, f'{host}/rest/data/r7/assign/somehashkey',
                  json={}, status=200)
    responses.add(responses.PATCH, f'{host}/rest/data/r8/assign/somehashkey',
                  json={}, status=200)
    responses.add(responses.PATCH, f'{host}/rest/data/r9/assign/somehashkey',
                  json={}, status=200)
    responses.add(responses.PATCH, f'{host}/rest/data/r10/assign/somehashkey',
                  json={}, status=200)
    responses.add(responses.PATCH, f'{host}/rest/data/r11/assign/somehashkey',
                  json={}, status=200)
    responses.add(responses.PATCH, f'{host}/rest/data/r12/assign/somehashkey',
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
    responses.add(responses.PATCH, f'{host}/rest/data/r4/',
                  match=[responses.matchers.urlencoded_params_matcher(data)],
                  json=json, status=200)

    # Delete the fourth record
    responses.add(responses.DELETE, f'{host}/rest/data/r4/',
                  body=b'', status=204)
