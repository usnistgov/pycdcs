# coding: utf-8

# Standard library imports
from pathlib import Path
from re import template
from typing import Optional, Union

# https://pandas.pydata.org/
import pandas as pd

xslt_keys = ['id', 'name', 'filename', 'content', '_cls']

def get_xslts(self,
              name: Optional[str] = None,
              filename: Optional[str] = None) -> pd.DataFrame:
    """
    Retrieves xslts.

    Parameters
    ----------
    name : str, optional
        The xslt name to limit the search by.
    filename : str, optional
        The xslt filename to limit the search by.
        
    Returns
    -------
    pandas.DataFrame
        All matching xslts.
    """
    rest_url = '/rest/xslt/'

    response = self.get(rest_url)
    xslts = pd.DataFrame(response.json())
    if len(xslts) == 0:
        xslts = pd.DataFrame(columns=xslt_keys)

    if name is not None:
        xslts = xslts[xslts.name == name]
    if filename is not None:
        xslts = xslts[xslts.filename == filename]
    xslts = xslts.reset_index(drop=True)

    return xslts

def get_xslt(self, 
             name: Optional[str] = None,
             filename: Optional[str] = None) -> pd.Series:
    """
    Retrieves a single xslt.  Given parameters must uniquely
    identify an xslt.

    Parameters
    ----------
    name : str, optional
        The xslt name to limit the search by.
    filename : str, optional
        The xslt filename to limit the search by.

    Returns
    -------
    pandas.Series
        The matching xslt.

    Raises
    ------
    ValueError
        If no or multiple matching xslts found.
    """

    xslts = self.get_xslts(name=name, filename=filename)
    
    # Check that number of xslts is exactly one.
    if len(xslts) == 1:
        return xslts.iloc[0]
    elif len(xslts) == 0:
        raise ValueError('No matching xslts found')
    else:
        raise ValueError('Multiple matching xslts found')

def upload_xslt(self,
                name: Optional[str] = None,
                filename: Optional[str] = None,
                content: Union[str, bytes, None] = None,
                verbose: bool = False):
    """
    """
    # Check if filename has been given
    if filename is not None:
        
        # Load content if needed
        if content is None:
            with open(filename, 'rb') as xmlfile:
                content = xmlfile.read()
        
        # Set name if needed
        if name is None:
            name = Path(filename).stem

        # Remove directory path from filename
        filename = Path(filename).name

    elif name is not None:
        filename = name + '.xsd'
        
    else:
        raise ValueError('filename or name must be given')
        
    if content is None:
        raise ValueError('filename or content must be given')

    # Encode str as bytes if needed
    if isinstance(content, str):
        try:
            e = content.index('?>')
        except:
            encoding = 'UTF-8'
        else:
            try:
                s = content[:e].index('encoding') + 8
            except:
                encoding = 'UTF-8'
            else:
                s = content[s:e].index('"')+s+1
                e = content[s:e].index('"') + s
                encoding = content[s:e]
        content = content.encode(encoding)

    elif not isinstance(content, bytes):
        raise TypeError('content must be str or bytes')
    
    # Set data dict
    data = {
        'name': name, 
        'filename': filename, 
        'content': content
    }

    # Send request
    rest_url = '/rest/xslt/'
    response = self.post(rest_url, data=data)

    if verbose and response.status_code == 201:
        xslt_id = response.json()['id']
        print(f'xslt {name} ({xslt_id}) successfully uploaded.')

def update_xslt(self,
                name: Optional[str] = None,
                filename: Optional[str] = None,
                content: Union[str, bytes, None] = None,
                newname: Optional[str] = None,
                newfilename: Optional[str] = None,
                xslt: Optional[pd.Series] = None,
                xslt_id: Optional[str] = None,
                verbose: bool = False):
    """
    Updates values associated with an XSLT transformation.  The XSLT entry to be
    updated can be uniquely identified using name and filename, xslt, or xslt_id.
    
    Parameters
    ----------
    name : str, optional
        An xslt name. Will be used to identify the existing xslt entry to update if
        neither xslt nor xslt_id parameters are given. If either xslt or xslt_id are
        given, this can be used to assign a new name to the entry.
    filename : str, optional
        An xslt filename. Will be used to identify the existing xslt entry to update if
        neither xslt nor xslt_id parameters are given. If either xslt or xslt_id are
        given, this can be used to assign a new filename to the entry.
    content : str, optional
        New xsl content to assign to the entry.
    newname : str, optional
        New name to assign to the entry.
    newfilename : str, optional
        New filename to assign to the entry.
    xslt : pd.Series, optional
        The xslt entry information for the entry that is being updated.  
    xslt_id : str, optional
        The database id that uniquely identifies the xslt entry. 
    verbose : bool, optional
        Setting this to True will print extra status messages.  Default value
        is False.
    """
    
    # Get xslt_id from xslt
    if xslt is not None:
        if xslt_id is not None:
            raise ValueError('xslt and xslt_id cannot both be given')
        xslt_id = xslt['id']
    
    # Get new values if xslt_id is known
    if xslt_id is not None:
        
        if name is not None:
            if newname is not None:
                raise ValueError('name and newname are aliases when xslt or xslt_id are given')
            newname = name
            
        if filename is not None:
            if newfilename is not None:
                raise ValueError('filename and newfilename are aliases when xslt or xslt_id are given')
            newfilename = filename
    
    # Get matching xslt from name, filename values
    else:
        xslt = self.get_xslt(name=name, filename=filename)
        xslt_id = xslt['id']
           
    if newfilename is not None:
        if content is None and Path(newfilename).is_file():
            with open(newfilename, 'rb') as xmlfile:
                content = xmlfile.read()
        newfilename = Path(newfilename).name
    
    if isinstance(content, str):
        try:
            e = content.index('?>')
        except:
            encoding = 'UTF-8'
        else:
            try:
                s = content[:e].index('encoding') + 8
            except:
                encoding = 'UTF-8'
            else:
                s = content[s:e].index('"')+s+1
                e = content[s:e].index('"') + s
                encoding = content[s:e]
        content = content.encode(encoding)
    
    # Set data dict
    data = {
        'name': newname, 
        'filename': newfilename, 
        'content': content
    }
    
    rest_url = f'/rest/xslt/{xslt_id}/'
    response = self.patch(rest_url, data=data)
    
    if verbose and response.status_code == 201:
        name = response.json()['name']
        print(f'xslt {name} ({xslt_id}) successfully updated.')

def delete_xslt(self,
                name: Optional[str] = None,
                filename: Optional[str] = None,
                xslt: Optional[pd.Series] = None,
                xslt_id: Optional[str] = None,
                verbose: bool = False):

    # Get xslt_id from xslt
    if xslt is not None:
        if xslt_id is not None:
            raise ValueError('xslt and xslt_id cannot both be given')
        xslt_id = xslt['id']
    
    # Get new values if xslt_id is known
    if xslt_id is not None:
        
        if name is not None:
            raise ValueError('name cannot be given with xslt or xslt_id')
                        
        if filename is not None:
            raise ValueError('filename cannot be given with xslt or xslt_id')
            
    # Get matching xslt from name, filename values
    else:
        xslt = self.get_xslt(name=name, filename=filename)
        xslt_id = xslt['id']

    rest_url = f'/rest/xslt/{xslt_id}/'
    response = self.delete(rest_url)

    if verbose and response.status_code == 204:
        print(f'xslt with id ({xslt_id}) has been deleted.')
