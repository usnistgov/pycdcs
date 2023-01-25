import responses

from . import v2_convert

def workspace_responses(host, version=3):
    """Mock responses for workspace methods"""
    
    from .data import workspaces

    if version == 2:
        workspaces = v2_convert(workspaces)

    # Get all workspaces
    responses.add(responses.GET, f'{host}/rest/workspace/', status=200,
                  json=workspaces)