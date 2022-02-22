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

    def test_init_testcall(self):
        """This function tests CDCS init and the associated testcall"""
        
        # Test #1: anonymous cdcs does no testcall
        assert self.cdcs.host == self.host
        assert self.cdcs.username is None
        assert self.cdcs.cert is None
        assert self.cdcs.verify is True
        
        # Test #2: Mock response for valid username + password
        with responses.RequestsMock() as rsps:
            rsps.add(responses.GET, f'{self.host}/rest/data/', status=200, json=[])
            cdcs = CDCS(host=self.host, username='Me', password='correct_password')
            assert cdcs.username == 'Me'

        # Test #3: Mock response for invalid username + password
        with responses.RequestsMock() as rsps:
            rsps.add(responses.GET, f'{self.host}/rest/data/', status=401,
                     json={'detail': 'Invalid username/password.'})
            with raises(requests.HTTPError):
                cdcs = CDCS(host=self.host, username='Me', password='wrong_password')
        
        # Test #4: Call testcall with bad url
        with raises(requests.ConnectionError):
            self.cdcs.testcall()
            
        # Test #5: Mock testcall with good url but no permissions
        with responses.RequestsMock() as rsps:
            rsps.add(responses.GET, f'{self.host}/rest/data/', status=401,
                     json={'detail': 'Authentication credentials were not provided.'})           
            with raises(requests.HTTPError):
                cdcs.testcall()
