
# Standard library imports
from pathlib import Path

# https://pandas.pydata.org/
import pandas as pd

def upload_blob(self, filename, blobbytes=None, verbose=False):
    """
    Adds a blob file to the repository.
    
    Args:
        filename: (str or Path) the path to the file to upload.
        verbose: (bool, optional) Setting this to True will print extra
            status messages.  Default value is False.
    Returns:
        (str) The URL handle where the blob can be downloaded from.
    """
    # Read file content
    if blobbytes is None:
        blobbytes = open(filename, 'rb')
    
    # Read file content
    files = {}
    files['blob'] = blobbytes
    
    # Set file name
    data  = {}
    data = {'filename': filename}
    
    # Send request
    rest_url = '/rest/blob/'
    response = self.post(rest_url, files=files, data=data)
    
    if verbose and response.status_code == 201:
        blob = pd.Series(response.json())
        print(f'File "{filename}" uploaded as blob "{blob.filename}" ({blob.id})')
    
    return blob.handle
    
def get_blobs(self, filename=None):
    """
    Retrieves the metadata for blobs
    
    Args:
        filename: (str, optional) The name of the file to limit the search by.
    
    Returns:
        (pandas.DataFrame) The metadata for all matching blobs.
    """
    
    # Set params
    params = {}
    if filename is not None:
        params['filename'] = filename
    
    # Send response
    rest_url = '/rest/blob/'
    response = self.get(rest_url, params=params)
    
    return pd.DataFrame(response.json())

def get_blob(self, id=None, filename=None):
    """
    Retrieves the metadata for a single blob.  The blob can be uniquely
    identified using its id or filename.
    
    Args:
        id: (str, optional) The unique ID associated with the blob.
        filename: (str, optional) The name of the file to limit the search by.
    
    Raises:
        (ValueError) If both id and filename are given, or if exactly one
        matching blob not found.
    
    Returns:
        (pandas.Series) The metadata for the matching blob.
    """
    if id is None:
        blobs = self.get_blobs(filename=filename)
        
        if len(blobs) == 1:
            return blobs.iloc[0]
        elif len(blobs) == 0:
            raise ValueError('No matching blobs found')
        else:
            raise ValueError('Multiple matching blobs found')
    else:
        if filename is not None:
            raise ValueError('id and filename cannot both be given')
        rest_url = f'/rest/blob/{id}'
        response = self.get(rest_url)
        return pd.Series(response.json())

def get_blob_contents(self, blob=None, id=None, filename=None):
    """
    Retrieves the contents for a single blob.  The blob can be uniquely
    identified by passing the blob metadata, or by using its id or filename.
    
    Args:
        blob: (pandas.Series, optional) The blob metadata for a blob.
        id: (str, optional) The unique ID associated with the blob.
        filename: (str, optional) The name of the file to limit the search by.
    
    Raises:
        (ValueError) If more than one argument given, or if filename does not
            uniquely identify a blob.
    
    Returns:
        (bytes) The blob file contents.
    """
    if blob is None:
        blob = self.get_blob(id=id, filename=filename)
    elif id is not None:
        raise ValueError('blob and id cannot both be given')
    elif filename is not None:
        raise ValueError('blob and filename cannot both be given')
    
    rest_url = f'/rest/blob/download/{blob.id}'
    response = self.get(rest_url)
    return response.content
        
def download_blob(self, blob=None, id=None, filename=None, savedir='.'):
    """
    Retrieves the contents for a single blob and saves it using the stored file
    name.  The blob can be uniquely identified by passing the blob metadata, or
    by using its id or filename.
    
    Args:
        blob: (pandas.Series, optional) The blob metadata for a blob.
        id: (str, optional) The unique ID associated with the blob.
        filename: (str, optional) The name of the file to limit the search by.
        savedir: (str or Path, optional) The directory to save the file to.
        Default value uses the current working directory.
    
    Raises:
        (ValueError) If more than one argument given, or if filename does not
            uniquely identify a blob.
    
    Returns:
        (bytes) The blob file contents.
    """
    if blob is None:
        blob = self.get_blob(id=id, filename=filename)
    elif id is not None:
        raise ValueError('blob and id cannot both be given')
    elif filename is not None:
        raise ValueError('blob and filename cannot both be given')
        
    savepath = Path(savedir, blob.filename)
    with open(savepath, 'wb') as f:
        f.write(self.get_blob_contents(blob=blob))

def delete_blob(self, blob=None, id=None, filename=None, verbose=False):
    """
    Deletes a single blob from the curator.  The blob can be uniquely
    identified by passing the blob metadata, or by using its id or filename.
    
    Args:
        blob: (pandas.Series, optional) The blob metadata for a blob.
        id: (str, optional) The unique ID associated with the blob.
        filename: (str, optional) The name of the file to limit the search by.
        verbose: (bool, optional) Setting this to True will print extra
            status messages.  Default value is False.
    
    Raises:
        (ValueError) If more than one argument given, or if filename does not
            uniquely identify a blob.
    """
    if blob is None:
        blob = self.get_blob(id=id, filename=filename)
    elif id is not None:
        raise ValueError('blob and id cannot both be given')
    elif filename is not None:
        raise ValueError('blob and filename cannot both be given')
        
    rest_url = f'/rest/blob/{blob.id}'
    response = self.delete(rest_url)
    
    if verbose and response.status_code == 204:
        print(f'Successfully deleted blob "{blob.filename}" ({blob.id})')
