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
        
    def test_init_v2(self):
        
        # Test #1: anonymous 2.x.x
        with responses.RequestsMock() as rsps:
            rsps.add(responses.GET, f'{self.host}/rest/core-settings/', status=404)
            cdcs = CDCS(host=self.host, username='')

        assert cdcs.host == self.host
        assert cdcs.username is None
        assert cdcs.cert is None
        assert cdcs.verify is True
        assert cdcs.cdcsversion == (2, 15, 0)

        # Test #2: anonymous plus a cdcs version
        cdcs = CDCS(host=self.host, username='', cdcsversion='2.9.1')

        assert cdcs.host == self.host
        assert cdcs.username is None
        assert cdcs.cert is None
        assert cdcs.verify is True
        assert cdcs.cdcsversion == (2, 9, 1)

        # Test #3: Mock response for valid username + password
        with responses.RequestsMock() as rsps:
            rsps.add(responses.GET, f'{self.host}/rest/data/', status=200, json=[])
            rsps.add(responses.GET, f'{self.host}/rest/core-settings/', status=404)
            cdcs = CDCS(host=self.host, username='Me', password='correct_password')
            assert cdcs.username == 'Me'
            assert cdcs.cdcsversion == (2, 15, 0)

        # Test #4: Mock response for invalid username + password
        with responses.RequestsMock() as rsps:
            rsps.add(responses.GET, f'{self.host}/rest/data/', status=401,
                     json={'detail': 'Invalid username/password.'})
            with raises(requests.HTTPError):
                cdcs = CDCS(host=self.host, username='Me', password='wrong_password')
        
        # Test #5: Call testcall with bad url
        with raises(requests.ConnectionError):
            cdcs.testcall()
            
        # Test #6: Mock testcall with good url but no permissions
        with responses.RequestsMock() as rsps:
            rsps.add(responses.GET, f'{self.host}/rest/data/', status=401,
                     json={'detail': 'Authentication credentials were not provided.'})           
            with raises(requests.HTTPError):
                cdcs.testcall()

    def test_init_testcall_v3(self):
        """This function tests CDCS init and the associated testcall"""
        
        # Test #1: anonymous bad authentication
        with responses.RequestsMock() as rsps:
            rsps.add(responses.GET, f'{self.host}/rest/core-settings/', status=401,
                     json={'detail': 'Authentication credentials were not provided.'})  
            cdcs = CDCS(host=self.host, username='')

        assert cdcs.host == self.host
        assert cdcs.username is None
        assert cdcs.cert is None
        assert cdcs.verify is True
        assert cdcs.cdcsversion == (3, 2, 0)

        # Test #1: anonymous good authentication
        with responses.RequestsMock() as rsps:
            rsps.add(responses.GET, f'{self.host}/rest/core-settings/', status=200,
                     json={'core_version':'2.0.1'})
            cdcs = CDCS(host=self.host, username='')

        assert cdcs.host == self.host
        assert cdcs.username is None
        assert cdcs.cert is None
        assert cdcs.verify is True
        assert cdcs.cdcsversion == (3, 0, 1)

        # Test #2: anonymous plus a cdcs version
        cdcs = CDCS(host=self.host, username='', cdcsversion='3.1.0')

        assert cdcs.host == self.host
        assert cdcs.username is None
        assert cdcs.cert is None
        assert cdcs.verify is True
        assert cdcs.cdcsversion == (3, 1, 0)

        # Test #3: Mock response for valid username + password
        with responses.RequestsMock() as rsps:
            rsps.add(responses.GET, f'{self.host}/rest/data/', status=200, json=[])
            rsps.add(responses.GET, f'{self.host}/rest/core-settings/', status=200,
                     json={'core_version':'2.0.1'})
            cdcs = CDCS(host=self.host, username='Me', password='correct_password')
            assert cdcs.username == 'Me'
            assert cdcs.cdcsversion == (3, 0, 1)

        # Test #4: Mock response for invalid username + password
        with responses.RequestsMock() as rsps:
            rsps.add(responses.GET, f'{self.host}/rest/data/', status=401,
                     json={'detail': 'Invalid username/password.'})
            with raises(requests.HTTPError):
                cdcs = CDCS(host=self.host, username='Me', password='wrong_password')
        
        # Test #5: Call testcall with bad url
        with raises(requests.ConnectionError):
            cdcs.testcall()
            
        # Test #6: Mock testcall with good url but no permissions
        with responses.RequestsMock() as rsps:
            rsps.add(responses.GET, f'{self.host}/rest/data/', status=401,
                     json={'detail': 'Authentication credentials were not provided.'})           
            with raises(requests.HTTPError):
                cdcs.testcall()

        