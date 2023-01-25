import responses
from . import v2_convert

def template_responses(host, version=3):
    """Mock responses for get_templates()"""
    
    from .data import templates

    if version == 2:
        templates = v2_convert(templates)

    # Individual get_template calls for each template
    responses.add(responses.GET, f'{host}/rest/template/1/',
                    status=200, json=templates[0])
    responses.add(responses.GET, f'{host}/rest/template/2/',
                    status=200, json=templates[1])
    responses.add(responses.GET, f'{host}/rest/template/3/',
                    status=200, json=templates[2])
    responses.add(responses.GET, f'{host}/rest/template/4/',
                    status=200, json=templates[3])


    # Upload template
    content = '<?xml version="1.0" encoding="UTF-8" standalone="no"?><xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema" attributeFormDefault="unqualified" elementFormDefault="unqualified"><xsd:element name="test" type="xsd:anyType"/></xsd:schema>'
    data = {}
    data['title'] = 'test'
    data['filename'] = 'test.xsd'
    data['content'] = content
    json = {}
    json['id'] = 5
    json['user'] = None
    json['filename'] = data['filename']
    json['checksum'] = None
    json['content'] =  content
    json['hash'] = 'somehash'
    json['dependencies'] = []
    responses.add(responses.POST, f'{host}/rest/template/global/',
                  match=[responses.matchers.urlencoded_params_matcher(data)],
                  status=201, json=json)
    responses.add(responses.POST, f'{host}/rest/template/user/',
                  match=[responses.matchers.urlencoded_params_matcher(data)],
                  status=201, json=json)

    # Upload template, with existing title
    # Note, should not actually get called!!
    data = {}
    data['title'] = 'first'
    data['filename'] = 'first.xsd'
    data['content'] = content
    json = {"message":{"title":["This field must be unique."]}}
    responses.add(responses.POST, f'{host}/rest/template/global/',
                  match=[responses.matchers.urlencoded_params_matcher(data)],
                  status=400, json=json)

    # Update template
    data = {}
    data['filename'] = 'first.xsd'
    data['content'] = content
    json = {}
    json['id'] = 5
    json['user'] = None
    json['filename'] = data['filename']
    json['checksum'] = None
    json['content'] =  content
    json['hash'] = 'somehash'
    json['dependencies'] = []
    responses.add(responses.POST, f'{host}/rest/template-version-manager/1/version/',
                  status=201, json=json)

    # Set current template
    responses.add(responses.PATCH, f'{host}/rest/template/version/1/current/',
                  status=200, body=b'')
    responses.add(responses.PATCH, f'{host}/rest/template/version/2/current/',
                  status=200, body=b'')
    responses.add(responses.PATCH, f'{host}/rest/template/version/3/current/',
                  status=200, body=b'')
    responses.add(responses.PATCH, f'{host}/rest/template/version/4/current/',
                  status=200, body=b'')
    responses.add(responses.PATCH, f'{host}/rest/template/version/5/current/',
                  status=200, body=b'')
    responses.add(responses.PATCH, f'{host}/rest/template/version/6/current/',
                  status=404, body=b'{"message":"Template not found."}')