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
    def test_auto_set_pid(self):
        """Tests auto_set_pid attribute"""
        
        # Add Mock responses
        pid_responses(self.host, 2)

        # Test auto_set_pid getter
        assert self.cdcs_v2.auto_set_pid is True

        # Test auto_set_pid setter
        self.cdcs_v2.auto_set_pid = False
        self.cdcs_v2.auto_set_pid = True

        # Test context manager
        with self.cdcs_v2.auto_set_pid_off():
            pass

    @responses.activate
    def test_get_pid_paths_v2(self):
        """Tests get_pid_paths()"""

        # Add Mock responses
        pid_responses(self.host, 2)

        # Test get_pid_paths() with no arguments
        pid_paths = self.cdcs_v2.get_pid_paths()
        assert pid_paths.id.tolist() == ['1', '2']
        assert pid_paths.xpath.tolist() == ['root.key', 'rooty.key']

    @responses.activate
    def test_get_pid_path_v2(self):
        """Tests get_pid_path()"""

        # Add Mock responses
        pid_responses(self.host, 2)
        template_responses(self.host, 2)
        template_manager_responses(self.host, 2)

        # Test get_pid_path() with filename
        pid_path = self.cdcs_v2.get_pid_path(template='second')
        assert pid_path.id == '2'
        assert pid_path.xpath == 'rooty.key'

    @responses.activate
    def test_upload_pid_path_v2(self, tmpdir):
        """Tests upload_pid_path()"""

        # Add Mock responses
        pid_responses(self.host, 2)
        template_responses(self.host, 2)
        template_manager_responses(self.host, 2)

        # Test upload_xslt() with only a filename
        with raises(ValueError):
            self.cdcs_v2.upload_pid_path('second', 'rooty.key')

    @responses.activate
    def test_update_pid_path_v2(self, tmpdir):
        """Tests update_pid_path()"""

        # Add Mock responses
        pid_responses(self.host, 2)
        template_responses(self.host, 2)
        template_manager_responses(self.host, 2)

        self.cdcs_v2.update_pid_path('second', 'rooty.key')
        
    @responses.activate
    def test_delete_pid_path_v2(self):
        """Tests delete_pid_path()"""

        # Add Mock responses
        pid_responses(self.host, 2)
        template_responses(self.host, 2)
        template_manager_responses(self.host, 2)

        self.cdcs_v2.delete_pid_path('second')


    
