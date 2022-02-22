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
    def cdcs(self):
        """A cdcs object with anonymous user. Create only once"""
        try:
            return self.__cdcs
        except:
            self.__cdcs = CDCS(host=self.host, username='')
            return self.__cdcs

    @responses.activate
    def test_get_workspaces(self):
        """Tests get_workspaces()"""

        # Add Mock responses
        workspace_responses(self.host)

        # Test get_workspaces()
        workspaces = self.cdcs.get_workspaces()
        assert len(workspaces) == 2
        assert workspaces['id'].tolist() == ['somehashkey', 'someotherhashkey']
        assert workspaces['title'].tolist() == ['Global Public Workspace', "Bob's stuff"]
        assert workspaces['owner'].tolist() == [None, 'Bob']
        assert workspaces['is_public'].tolist() == [True, False]

    @responses.activate
    def test_get_workspace(self):
        """Tests get_workspace()"""

        # Add Mock responses
        workspace_responses(self.host)

        # Test get_workspace() with valid title
        workspace = self.cdcs.get_workspace("Bob's stuff")
        assert workspace.id == 'someotherhashkey'

        # Test get_workspace() for multiple or no matches
        with raises(ValueError):
            workspace = self.cdcs.get_workspace()
        with raises(ValueError):
            workspace = self.cdcs.get_workspace('Bad title')

    @responses.activate
    def test_global_workspace(self):
        """Tests global_workspace"""

        # Add Mock responses
        workspace_responses(self.host)
    
        # Test global_workspace
        workspace = self.cdcs.global_workspace
        assert workspace.id == 'somehashkey'