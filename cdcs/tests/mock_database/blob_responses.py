import responses

from .data import blobs, blob_content

def blob_responses(host):
    """Mock responses for blob methods"""
    
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
    responses.add(responses.GET, f'{host}/rest/blob/randomblobhash',
                  json=blobs[0], status=200)

    # Assign first blob to global workspace
    responses.add(responses.PATCH, f'{host}/rest/blob/randomblobhash/assign/somehashkey',
                  json={}, status=200)

    # Assign second blob to global workspace
    responses.add(responses.PATCH, f'{host}/rest/blob/otherblobhash/assign/somehashkey',
                  json={}, status=200)

    # Get blob contents
    responses.add(responses.GET, f'{host}/rest/blob/download/randomblobhash',
                  body=blob_content, status=200)

    # Delete blob contents
    responses.add(responses.DELETE, f'{host}/rest/blob/randomblobhash',
                  body=b'', status=204)