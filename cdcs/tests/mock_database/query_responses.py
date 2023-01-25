import responses
from . import v2_convert

def query_responses(host, version=3):
    
    from .data import records
    if version == 2:
        records = v2_convert(records)

    # Query with no parameters, page 1
    params = {}
    data = {'query': '{}'}
    json = {'count':12, 'next':f'{host}/rest/data/query/?page=2', 'previous':None, 'results':records[:10]}
    responses.add(responses.POST, f'{host}/rest/data/query/',
                  match=[
                      responses.matchers.urlencoded_params_matcher(data),
                      responses.matchers.query_param_matcher(params)],
                  json=json, status=200)
    params = {'page':1}
    responses.add(responses.POST, f'{host}/rest/data/query/',
                  match=[
                      responses.matchers.urlencoded_params_matcher(data),
                      responses.matchers.query_param_matcher(params)],
                  json=json, status=200)

    # Query with no parameters, page 2
    params = {'page':"2"}
    data = {'query': '{}'}
    json = {'count':12, 'next':None, 'previous':f'{host}/rest/data/query/', 'results':records[10:]}
    responses.add(responses.POST, f'{host}/rest/data/query/',
                  match=[
                      responses.matchers.urlencoded_params_matcher(data),
                      responses.matchers.query_param_matcher(params)],
                  json=json, status=200)

    # Query with first template
    params = {}
    data = {}
    data['query'] = '{}'
    if version == 2:
        data['templates'] = '[{"id": "1"}]'
    else:
        data['templates'] = '[{"id": 1}]'
    json = {'count':8, 'next':None, 'previous':None, 'results':records[:8]}
    responses.add(responses.POST, f'{host}/rest/data/query/',
                  match=[
                      responses.matchers.urlencoded_params_matcher(data),
                      responses.matchers.query_param_matcher(params)],
                  json=json, status=200)

    # Query with second template
    params = {}
    data = {}
    data['query'] = '{}'
    if version == 2:
        data['templates'] = '[{"id": "3"}]'
    else:
        data['templates'] = '[{"id": 3}]'
    json = {'count':4, 'next':None, 'previous':None, 'results':records[8:]}
    responses.add(responses.POST, f'{host}/rest/data/query/',
                  match=[
                      responses.matchers.urlencoded_params_matcher(data),
                      responses.matchers.query_param_matcher(params)],
                  json=json, status=200)

    # Query with title
    params = {}
    data = {}
    data['query'] = '{}'
    data['title'] = 'second-record-2'
    json = {'count':1, 'next':None, 'previous':None, 'results':records[9:10]}
    responses.add(responses.POST, f'{host}/rest/data/query/',
                  match=[
                      responses.matchers.urlencoded_params_matcher(data),
                      responses.matchers.query_param_matcher(params)],
                  json=json, status=200)

    # Query with title
    params = {}
    data = {}
    data['query'] = '{}'
    data['title'] = 'first-record-4'
    json = {'count':1, 'next':None, 'previous':None, 'results':records[3:4]}
    responses.add(responses.POST, f'{host}/rest/data/query/',
                  match=[
                      responses.matchers.urlencoded_params_matcher(data),
                      responses.matchers.query_param_matcher(params)],
                  json=json, status=200)

     # Query with title
    params = {}
    data = {}
    data['query'] = '{}'
    data['title'] = 'second-record-4'
    if version == 2:
        data['templates'] = '[{"id": "3"}]'
    else:
        data['templates'] = '[{"id": 3}]'
    json = {'count':0, 'next':None, 'previous':None, 'results':[]}
    responses.add(responses.POST, f'{host}/rest/data/query/',
                  match=[
                      responses.matchers.urlencoded_params_matcher(data),
                      responses.matchers.query_param_matcher(params)],
                  json=json, status=200)
    
    params = {}
    data = {}
    data['query'] = '{}'
    data['title'] = 'first-record-4'
    if version == 2:
        data['templates'] = '[{"id": "1"}]'
    else:
        data['templates'] = '[{"id": 1}]'
    json = {'count':1, 'next':None, 'previous':None, 'results':records[3:4]}
    responses.add(responses.POST, f'{host}/rest/data/query/',
                  match=[
                      responses.matchers.urlencoded_params_matcher(data),
                      responses.matchers.query_param_matcher(params)],
                  json=json, status=200)

    # Query with query
    params = {}
    data = {'query': '{"first.name": "first-record-7"}'}
    json = {'count':1, 'next':None, 'previous':None, 'results':records[6:7]}
    responses.add(responses.POST, f'{host}/rest/data/query/',
                  match=[
                      responses.matchers.urlencoded_params_matcher(data),
                      responses.matchers.query_param_matcher(params)],
                  json=json, status=200)

    # Query with keyword
    params = {}
    data = {'query': 'first-record-3'}
    json = {'count':1, 'next':None, 'previous':None, 'results':records[2:3]}
    responses.add(responses.POST, f'{host}/rest/data/query/keyword/',
                  match=[
                      responses.matchers.urlencoded_params_matcher(data),
                      responses.matchers.query_param_matcher(params)],
                  json=json, status=200)