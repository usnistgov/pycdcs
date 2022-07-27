# coding: utf-8

# Standard library imports
from typing import Optional, Union, Tuple

# Local imports
from .. import RestClient

class CDCS(RestClient):
    """
    Class for accessing instances the Configurable Database Curation System
    (CDCS).  Designed for versions 2.5+.
    """
    def __init__(self, host: str,
                 cdcsversion: str = '2.15.0',
                 username: Optional[str] = None,
                 password: Optional[str] = None,
                 auth: Optional[Tuple[str]] = None,
                 cert: Union[str, Tuple[str], None] = None, 
                 certification: Union[str, Tuple[str], None] = None,
                 verify: Optional[bool] = True):
        """
        Class initializer. Tests and stores access information.
        
        Parameters
        ----------
        host : str
            URL for the database's server.
        cdcsversion : str, optional
            The version of the CDCS database given as "#.#.#".  Specifying
            this allows for compatibility with older databases where
            different rest calls may be required for the same method.
            Default value is "2.15.0".
        username : str, optional
            Username of desired account on the server. A prompt will ask for
            the username if not given.
        password : str, optional
            Password of desired account on the server.  A prompt will ask for
            the password if not given.
        auth : tuple, optional
            Auth tuple to enable Basic/Digest/Custom HTTP Auth.  Alternative to
            giving username and password seperately.
        cert : str, optional
            if String, path to ssl client cert file (.pem). If Tuple,
            ('cert', 'key') pair.
        certification : str, optional
            Alias for cert. Retained for compatibility.
        verify : bool or str, optional
            Either a boolean, in which case it controls whether we verify the
            server's TLS certificate, or a string, in which case it must be a
            path to a CA bundle to use. Defaults to True.
        """
        # Handle CDCS version 
        cdcsversion = cdcsversion.split('.')
        try:
            assert len(cdcsversion) == 3
            for i in range(3):
                cdcsversion[i] = int(cdcsversion[i])
        except:
            raise ValueError('cdcs version must be given in format #.#.#')
        if cdcsversion[0] < 2:
            raise ValueError('CDCS class only works for versions 2+')
        self.__cdcsversion = cdcsversion

        # Call RestClient's init
        super().__init__(host, username=username, password=password, auth=auth,
                         cert=cert, certification=certification, verify=verify)

    # Import defined methods
    from ._workspace import (get_workspaces, get_workspace,
                             global_workspace)
    
    from ._template import (get_template_managers, get_templates, get_template,
                            template_titles)

    from ._query import query, query_count
    
    from ._record import (get_records, get_record, upload_record, assign_records,
                          update_record, delete_record)

    from ._blob import (get_blobs, get_blob, upload_blob, delete_blob, assign_blobs,
                        get_blob_contents, download_blob)
    from ._pid_xpath import (get_pid_xpaths, get_pid_xpath, upload_pid_xpath,
                             update_pid_xpath, delete_pid_xpath)
    
    @property
    def cdcsversion(self) -> str:
        """str: The cdcs version set"""
        return self.__cdcsversion

    def testcall(self):
        """Simple rest call to check if authentication parameters are valid."""
        
        # Call /rest/data/ and parse by a non-existent title
        rest_url = '/rest/data/'
        params = {'title':'ARBITRARYNONEXISTANTTITLE'}
        self.get(rest_url, params=params)
