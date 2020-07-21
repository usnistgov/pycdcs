# coding: utf-8

# https://pandas.pydata.org/
import pandas as pd

def get_workspaces(self, title=None):
    """
    Retrieves information for the existing workspaces.

    Args:
        title: (str, optional) The workspace title to limit the search
            by.
    
    Returns:
        pandas.DataFrame: The matching workspaces.
    """
    rest_url = '/rest/workspace/'
    response = self.get(rest_url)
    workspaces = pd.DataFrame(response.json())

    if title is not None:
        workspaces = workspaces[workspaces.title == title]

    return workspaces

def get_workspace(self, title=None):
    """
    Retrieves a single workspace.  Given parameters must uniquely
    identify a workspace.

    Args:
        title: (str, optional) The workspace title to limit the search
            by.
    
    Returns:
        pandas.Series: The matching workspace.

    Raises:
        ValueError: If no or multiple matching workspaces found.
    """

    workspaces = self.get_workspaces(title=title)
    
    # Check that number of workspaces is exactly one.
    if len(workspaces) == 1:
        return workspaces.iloc[0]
    elif len(workspaces) == 0:
        raise ValueError('No matching workspaces found')
    else:
        raise ValueError('Multiple matching workspaces found')

def assign_record_workspace(self, records, workspace, verbose=False):
        """
        Assigns one or more records to the specified workspace.

        Args:
            records: (pandas.Series or pandas.DataFrame) The user record(s) to
                assign to the workspace.
            workspace: (pandas.Series) The workspace to assign the record(s)
                to.
            verbose: (bool, optional) Setting this to True will print extra
                status messages.  Default value is False.
        """
        if isinstance(workspace, pd.Series):
            workspace_id = workspace.id
            workspace_title = workspace.title
        else:
            raise ValueError('invalid workspace: must be pandas.Series')
        
        if isinstance(records, pd.Series):
            record_ids = [records.id]
            record_titles = [records.title]
        elif isinstance(records, pd.DataFrame):
            record_ids = records.id.tolist()
            record_titles = records.title.tolist()
        else:
            raise ValueError('invalid records: must be pandas.Series or pandas.DataFrame')
            
        for record_id, record_title in zip(record_ids, record_titles):
            rest_url = f'/rest/data/{record_id}/assign/{workspace_id}'
            response = self.patch(rest_url)

            if verbose and response.status_code == 200:
                print(f'record {record_title} ({record_id}) assigned to workspace {workspace_title} ({workspace_id})')

def assign_blob_workspace(self, blobs, workspace, verbose=False):
    """
    Assigns one or more blobs to the specified workspace.

    Args:
        blobs: (pandas.Series or pandas.DataFrame) The user blob(s) to
            assign to the workspace.
        workspace: (pandas.Series) The workspace to assign the blob(s)
            to.
        verbose: (bool, optional) Setting this to True will print extra
            status messages.  Default value is False.
    """
    if isinstance(workspace, pd.Series):
        workspace_id = workspace.id
        workspace_title = workspace.title
    else:
        raise ValueError('invalid workspace: must be pandas.Series')
    
    if isinstance(blobs, pd.Series):
        blob_ids = [blobs.id]
        blob_filenames = [blobs.filename]
    elif isinstance(blobs, pd.DataFrame):
        blob_ids = blobs.id.tolist()
        blob_filenames = blobs.filename.tolist()
    else:
        raise ValueError('invalid blobs: must be pandas.Series or pandas.DataFrame')
        
    for blob_id, blob_filename in zip(blob_ids, blob_filenames):
        rest_url = f'/rest/blob/{blob_id}/assign/{workspace_id}'
        response = self.patch(rest_url)

        if verbose and response.status_code == 200:
            print(f'blob {blob_filename} ({blob_id}) assigned to workspace {workspace_title} ({workspace_id})')

@property
def global_workspace(self):
    """pandas.Series: The global public workspace"""
    return self.get_workspace(title='Global Public Workspace')

