import responses

from .data import workspaces

def workspace_responses(host):
    """Mock responses for workspace methods"""
    
    # Get all workspaces
    responses.add(responses.GET, f'{host}/rest/workspace/', status=200,
                  json=workspaces)