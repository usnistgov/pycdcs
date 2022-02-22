import responses

from .data import templates

def template_responses(host):
    """Mock responses for get_templates()"""
    
    # Individual queries for each template entry
    responses.add(responses.GET, f'{host}/rest/template/firsthash1/',
                    status=200, json=templates[0])
    responses.add(responses.GET, f'{host}/rest/template/secondhash1/',
                    status=200, json=templates[1])
    responses.add(responses.GET, f'{host}/rest/template/secondhash2/',
                    status=200, json=templates[2])
    responses.add(responses.GET, f'{host}/rest/template/thirdhash1/',
                    status=200, json=templates[3])