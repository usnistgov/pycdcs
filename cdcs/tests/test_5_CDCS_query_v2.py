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
    def test_query_v2(self):
        """Tests query"""

        # Add Mock responses
        template_manager_responses(self.host, 2)
        template_responses(self.host, 2)
        query_responses(self.host, 2)

        records = self.cdcs_v2.query()
        assert len(records) == 12

        records = self.cdcs_v2.query(template='first')
        assert len(records) == 8

        records = self.cdcs_v2.query(template='second')
        assert len(records) == 4

        records = self.cdcs_v2.query(title='second-record-2')
        assert len(records) == 1
        assert records.title[0] == 'second-record-2'
        assert records.template_title[0] == 'second'

        records = self.cdcs_v2.query(mongoquery={"first.name": "first-record-7"})
        assert len(records) == 1
        assert records.title[0] == 'first-record-7'
        assert records.template_title[0] == 'first'

        records = self.cdcs_v2.query(keyword='first-record-3')
        assert len(records) == 1
        assert records.title[0] == 'first-record-3'
        assert records.template_title[0] == 'first'

        with raises(ValueError):
            records = self.cdcs_v2.query(mongoquery={"first.name": "first-record-7"},
                                      keyword='first-record-3')
