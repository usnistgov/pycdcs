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
    def cdcs_v3(self):
        try:
            return self.__cdcs_v3
        except:
            with responses.RequestsMock() as rsps:
                rsps.add(responses.GET, f'{self.host}/rest/core-settings/', status=200,
                     json={'core_version':'2.0.1'})
                cdcs = CDCS(host=self.host, username='')
            self.__cdcs_v3 = cdcs
            return self.__cdcs_v3

    @responses.activate
    def test_query_v3(self):
        """Tests query"""

        # Add Mock responses
        template_manager_responses(self.host, 3)
        template_responses(self.host, 3)
        query_responses(self.host, 3)

        records = self.cdcs_v3.query()
        assert len(records) == 12

        records = self.cdcs_v3.query(template='first')
        assert len(records) == 8

        records = self.cdcs_v3.query(template='second')
        assert len(records) == 4

        records = self.cdcs_v3.query(title='second-record-2')
        assert len(records) == 1
        assert records.title[0] == 'second-record-2'
        assert records.template_title[0] == 'second'

        records = self.cdcs_v3.query(mongoquery={"first.name": "first-record-7"})
        assert len(records) == 1
        assert records.title[0] == 'first-record-7'
        assert records.template_title[0] == 'first'

        records = self.cdcs_v3.query(keyword='first-record-3')
        assert len(records) == 1
        assert records.title[0] == 'first-record-3'
        assert records.template_title[0] == 'first'

        with raises(ValueError):
            records = self.cdcs_v3.query(mongoquery={"first.name": "first-record-7"},
                                      keyword='first-record-3')
