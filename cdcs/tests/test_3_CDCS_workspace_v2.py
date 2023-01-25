from multiprocessing.sharedctypes import Value
from pathlib import Path
import requests
import responses
from cdcs import CDCS
from pytest import raises

from mock_database import *

class TestCDCS():
    
    @property
    def host(self):
        """str: A fake host url for testing"""
        return 'https://fakeurl.fake'
    
    @property
    def cdcs_v2(self):
        try:
            return self.__cdcs_v2
        except:
            with responses.RequestsMock() as rsps:
                rsps.add(responses.GET, f'{self.host}/rest/core-settings/', status=404)
                cdcs = CDCS(host=self.host, username='')
            self.__cdcs_v2 = cdcs
            return self.__cdcs_v2

    @responses.activate
    def test_get_workspaces_v2(self):
        """Tests get_workspaces()"""

        # Add Mock responses
        workspace_responses(self.host, 2)

        # Test get_workspaces()
        workspaces = self.cdcs_v2.get_workspaces()
        assert len(workspaces) == 2
        assert workspaces['id'].tolist() == ['1', '2']
        assert workspaces['title'].tolist() == ['Global Public Workspace', "Bob's stuff"]
        assert workspaces['owner'].tolist() == [None, 'Bob']
        assert workspaces['is_public'].tolist() == [True, False]

    @responses.activate
    def test_get_workspace_v2(self):
        """Tests get_workspace()"""

        # Add Mock responses
        workspace_responses(self.host, 2)

        # Test get_workspace() with valid title
        workspace = self.cdcs_v2.get_workspace("Bob's stuff")
        assert workspace.id == '2'

        # Test get_workspace() for multiple or no matches
        with raises(ValueError):
            workspace = self.cdcs_v2.get_workspace()
        with raises(ValueError):
            workspace = self.cdcs_v2.get_workspace('Bad title')

    @responses.activate
    def test_global_workspace_v2(self):
        """Tests global_workspace"""

        # Add Mock responses
        workspace_responses(self.host, 2)
    
        # Test global_workspace
        workspace = self.cdcs_v2.global_workspace
        assert workspace.id == '1'
