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
                 username: Optional[str] = None,
                 password: Optional[str] = None,
                 auth: Optional[Tuple[str]] = None,
                 cert: Union[str, Tuple[str], None] = None, 
                 certification: Union[str, Tuple[str], None] = None,
                 verify: Optional[bool] = True,
                 cdcsversion: Optional[str] = None):
        """
        Class initializer. Tests and stores access information.
        
        Parameters
        ----------
        host : str
            URL for the database's server.
        username : str, optional
            Username of desired account on the server. A prompt will ask for
            the username if not given.
        password : str, optional
            Password of desired account on the server.  A prompt will ask for
            the password if not given.
        auth : tuple, optional
            Auth tuple to enable Basic/Digest/Custom HTTP Auth.  Alternative to
            giving username and password separately.
        cert : str, optional
            if String, path to ssl client cert file (.pem). If Tuple,
            ('cert', 'key') pair.
        certification : str, optional
            Alias for cert. Retained for compatibility.
        verify : bool or str, optional
            Either a boolean, in which case it controls whether we verify the
            server's TLS certificate, or a string, in which case it must be a
            path to a CA bundle to use. Defaults to True.
        cdcsversion : str, optional
            For CDCS versions 2.X.X, this allows for specifying the full CDCS
            version to ensure the class methods perform the correct REST
            calls.  This can be specified as "#.#.#", or if None is given will
            default to "2.15.0".  For CDCS versions 3.X.X, this is ignored as
            version info is obtained directly from the database.
        """

        # Call RestClient's init
        super().__init__(host, username=username, password=password, auth=auth,
                         cert=cert, certification=certification, verify=verify)

        # Handle CDCS version 
        self.set_cdcsversion(cdcsversion=cdcsversion)

    # Import defined methods
    from ._workspace import (get_workspaces, get_workspace,
                             global_workspace)
    
    from ._template import (get_template_managers, disable_template_manager,
                            restore_template_manager, get_templates, get_template,
                            template_titles, upload_template, update_template,
                            disable_template, restore_template, set_current_template)

    from ._query import query, query_count
    
    from ._record import (get_records, get_records_v2, get_record, upload_record,
                          assign_records, update_record, delete_record, transform_record)

    from ._blob import (get_blobs, get_blob, upload_blob, delete_blob, assign_blobs,
                        get_blob_contents, download_blob)

    from ._pid_xpath import (get_pid_xpaths, get_pid_xpath, upload_pid_xpath,
                             update_pid_xpath, delete_pid_xpath)
    
    from ._xslt import (get_xslts, get_xslt, upload_xslt, update_xslt, delete_xslt)
    
    @property
    def cdcsversion(self) -> Tuple:
        """Set CDCS version for 2.X.X, or core version bumped by 1 major version for 3.X.X"""
        return self.__cdcsversion

    def testcall(self):
        """Simple rest call to check if authentication parameters are valid."""
        
        # Call /rest/data/ and parse by a non-existent title
        rest_url = '/rest/data/'
        params = {'title':'ARBITRARYNONEXISTANTTITLE'}
        self.get(rest_url, params=params)

    def set_cdcsversion(self, 
                        cdcsversion: Optional[str] = None):

        # Make a call to fetch cdcs core version
        r = self.get('/rest/core-settings/', checkstatus=False)

        # If CDCS is 3, then the URL exists
        if r.status_code == 200:

            # Read, split and transform core version into ints
            cdcsversion = r.json()['core_version'].split('.')
            for i in range(3):
                cdcsversion[i] = int(cdcsversion[i])
            
            # Bump the primary version up by 1
            # NOTE This is core version +1 NOT CDCS version!!!
            cdcsversion[0] += 1

        # If CDCS is 2, then the rest URL is invalid
        elif r.status_code == 404:

            # Set default version
            if cdcsversion is None:
                cdcsversion = '2.15.0'

            # Split and transform into ints
            cdcsversion = cdcsversion.split('.')
            try:
                assert len(cdcsversion) == 3
                for i in range(3):
                    cdcsversion[i] = int(cdcsversion[i])
            except:
                raise ValueError('cdcs version must be given in format #.#.#')
            if cdcsversion[0] < 2:
                raise ValueError('CDCS class only works for versions 2+')

        self.__cdcsversion = tuple(cdcsversion)