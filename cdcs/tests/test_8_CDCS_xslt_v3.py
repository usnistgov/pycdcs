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
    def test_get_xslts_v3(self):
        """Tests get_xslts()"""

        # Add Mock responses
        xslt_responses(self.host, 3)

        # Test get_blobs() with no arguments
        xslts = self.cdcs_v3.get_xslts()
        assert xslts.id.tolist() == [1, 2, 3, 4]
        assert xslts.name.tolist() == ['template1-xsl1', 'template1-xsl2',
                                       'template2-xsl1', 'template3-xsl1']

    @responses.activate
    def test_get_xslt_v3(self):
        """Tests get_xslt()"""

        # Add Mock responses
        xslt_responses(self.host, 3)

        # Test get_xslt() with filename
        xslt = self.cdcs_v3.get_xslt(name='template1-xsl1')
        assert xslt.id == 1
        assert xslt.filename == 'template1-xsl1.xsl'

        # Test get_xslt() with id
        xslt = self.cdcs_v3.get_xslt(filename='template2-xsl1.xsl')
        assert xslt.id == 3
        assert xslt['name'] == 'template2-xsl1'

        # Test get_xslt() errors for multiple, no matches
        with raises(ValueError):
            xslt = self.cdcs_v3.get_xslt()
        with raises(ValueError):
            xslt = self.cdcs_v3.get_xslt(filename='fake.txt')

    @responses.activate
    def test_upload_xslt_v3(self, tmpdir):
        """Tests upload_xslt()"""

        # Add Mock responses
        xslt_responses(self.host, 3)

        # Create xslt name, content and file
        filename = Path(tmpdir, 'template3-xsl1.xsl')
        name = 'template3-xsl1'
        content = '<?xml version="1.0" encoding="UTF-8"?><xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns="http://www.w3.org/TR/xhtml1/strict"> <xsl:output method="html" encoding="utf-8" indent="yes" /></xsl:stylesheet>'
        with open(filename, 'w') as f:
            f.write(content)

        # Test upload_xslt() with only a filename
        self.cdcs_v3.upload_xslt(filename=filename)

        # Test upload_xslt() from name and content
        self.cdcs_v3.upload_xslt(name=name, content=content)

        # Test upload_xslt() from name, filename, and content
        self.cdcs_v3.upload_xslt(name=name, filename=filename, content=content)

    @responses.activate
    def test_update_xslt_v3(self, tmpdir):
        """Tests update_xslt()"""

        # Add Mock responses
        xslt_responses(self.host, 3)

        # Create xslt name, content and file
        filename = Path(tmpdir, 'template3-xsl1.xsl')
        name = 'template3-xsl1'
        content = '<?xml version="1.0" encoding="UTF-8"?><xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns="http://www.w3.org/TR/xhtml1/strict"> <xsl:output method="html" encoding="utf-8" indent="yes" /></xsl:stylesheet>'
        with open(filename, 'w') as f:
            f.write(content)

        xslt = self.cdcs_v3.get_xslt(name='template3-xsl1')

        # Test update_xslt()
        self.cdcs_v3.update_xslt(xslt=xslt, filename=filename, name=name)

        # Test update_xslt()
        self.cdcs_v3.update_xslt(xslt_id=4, filename=filename, name=name)
        
    @responses.activate
    def test_delete_xslt_v3(self):
        """Tests delete_xslt()"""

        # Add Mock responses
        xslt_responses(self.host, 3)

        xslt = self.cdcs_v3.get_xslt(name='template3-xsl1')

        # Test delete_xslt()
        self.cdcs_v3.delete_xslt(xslt=xslt)
        self.cdcs_v3.delete_xslt(xslt_id=4)
        self.cdcs_v3.delete_xslt(filename='template3-xsl1.xsl')

        # Test delete_xslt() with invalid inputs
        with raises(ValueError):
            self.cdcs_v3.delete_xslt(xslt=xslt, xslt_id=4)
        with raises(ValueError):
            self.cdcs_v3.delete_xslt(xslt=xslt, filename='template3-xsl1.xsl')
        with raises(ValueError):
            self.cdcs_v3.delete_xslt(xslt_id=4, filename='template3-xsl1.xsl')



