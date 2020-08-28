# coding: utf-8

# Local imports
from .. import RestClient

class CDCS(RestClient):
    """
    Class for accessing instances the Configurable Database Curation System
    (CDCS).  Designed for versions 2.5+.
    """
    def __init__(self, host, cdcsversion='2.10.0', username=None, password=None,
                 certification=None):
        """
        Class initializer. Tests and stores access information.
        
        Args:
            host: (str) URL for the database's server.
            cdcsversion: (str, optional) The version of the CDCS database
                given as "#.#.#".  Class methods may not work properly if the
                wrong database version is set.  Default value is "2.10.0".
            username: (str, optional) Username of desired account on the
                server.  A prompt will ask for the username if not given.
            password: (str, optional) Password of desired account on the
                server.  A prompt will ask for the password if not given.
            certification: (str, optional) Path to an authentication
                certificate, if needed, to access the database's server.
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
        super().__init__(host, username=username, password=password,
                 certification=certification)

    # Import defined methods
    from ._workspace import (get_workspaces, get_workspace,
                             global_workspace)
    
    from ._template import (get_template_managers, get_templates, get_template,
                            template_titles)

    from ._query import query
    
    from ._record import (get_records, get_record, upload_record, assign_records,
                          update_record, delete_record)

    from ._blob import (get_blobs, get_blob, upload_blob, delete_blob, assign_blobs,
                        get_blob_contents, download_blob)
    
    @property
    def cdcsversion(self):
        return self.__cdcsversion

    def testcall(self):
        """
        Simple rest call to check if authentication parameters are valid.
        Calls /rest/data with 
        """
        rest_url = '/rest/data/'
        params = {'title':'ARBITRARYNONEXISTANTTITLE'}
        self.get(rest_url, params=params)
