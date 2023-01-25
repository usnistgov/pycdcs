import responses
from . import v2_convert

def blob_responses(host, version=3):
    """Mock responses for blob methods"""
    
    from .data import blobs, blob_content

    if version == 2:
        blobs = v2_convert(blobs)

    # Fill in host info
    for blob in blobs:
        blob['handle'] = blob['handle'].format(host=host)

    # Post a blob named "test_blob.txt"
    files = {'blob': blob_content}
    data = {'filename': 'test_blob.txt'}
    responses.add(responses.POST, f'{host}/rest/blob/',
                  #match=[responses.matchers.multipart_matcher(files, data=data)],
                  json=blobs[0], status=201)
    
    # Get all blobs
    params = {}
    responses.add(responses.GET, f'{host}/rest/blob/',
                  match=[responses.matchers.query_param_matcher(params)],
                  json=blobs, status=200)
    
    # Get blob according to filename
    params = {'filename':'test_blob.txt'}
    responses.add(responses.GET, f'{host}/rest/blob/',
                  match=[responses.matchers.query_param_matcher(params)],
                  json=blobs[:1], status=200)
    
    # Get blob - no matching filename
    params = {'filename':'fake.txt'}
    responses.add(responses.GET, f'{host}/rest/blob/',
                  match=[responses.matchers.query_param_matcher(params)],
                  json=[], status=200)

    # Get blob from id
    responses.add(responses.GET, f'{host}/rest/blob/1',
                  json=blobs[0], status=200)

    # Assign first blob to global workspace
    responses.add(responses.PATCH, f'{host}/rest/blob/1/assign/1',
                  json={}, status=200)

    # Assign second blob to global workspace
    responses.add(responses.PATCH, f'{host}/rest/blob/2/assign/1',
                  json={}, status=200)

    # Get blob contents
    responses.add(responses.GET, f'{host}/rest/blob/download/1',
                  body=blob_content, status=200)

    # Delete blob contents
    responses.add(responses.DELETE, f'{host}/rest/blob/1',
                  body=b'', status=204)