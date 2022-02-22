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
    def test_query(self):
        """Tests query"""

        # Add Mock responses
        template_manager_responses(self.host)
        template_responses(self.host)
        query_responses(self.host)

        records = self.cdcs.query()
        assert len(records) == 12

        records = self.cdcs.query(template='first')
        assert len(records) == 8

        records = self.cdcs.query(template='second')
        assert len(records) == 4

        records = self.cdcs.query(title='second-record-2')
        assert len(records) == 1
        assert records.title[0] == 'second-record-2'
        assert records.template_title[0] == 'second'

        records = self.cdcs.query(mongoquery={"first.name": "first-record-7"})
        assert len(records) == 1
        assert records.title[0] == 'first-record-7'
        assert records.template_title[0] == 'first'

        records = self.cdcs.query(keyword='first-record-3')
        assert len(records) == 1
        assert records.title[0] == 'first-record-3'
        assert records.template_title[0] == 'first'

        with raises(ValueError):
            records = self.cdcs.query(mongoquery={"first.name": "first-record-7"},
                                      keyword='first-record-3')

        
