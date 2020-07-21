# coding: utf-8

# Local imports
from .. import RestClient

class CDCS(RestClient):
    """
    Class for accessing instances the Configurable Database Curation System
    (CDCS).  Designed for versions 2.5+.
    """
    
    # Import defined methods
    from ._template import (get_template_managers, get_templates, get_template,
                            template_titles)
    from ._query import query
    from ._record import (get_records, get_record, upload_record,
                          update_record, delete_record)
    from ._blob import (get_blobs, get_blob, upload_blob, delete_blob,
                        get_blob_contents, download_blob)
    from ._workspace import (get_workspaces, get_workspace,
                             assign_record_workspace, assign_blob_workspace,
                             global_workspace)
    
    def testcall(self):
        """
        Simple rest call to check if authentication parameters are valid.
        Calls /rest/data with 
        """
        rest_url = '/rest/data/'
        params = {'title':'ARBITRARYNONEXISTANTTITLE'}
        self.get(rest_url, params=params)
