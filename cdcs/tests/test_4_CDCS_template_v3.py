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
    def test_get_template_managers_v3(self):
        """Tests get_template_managers"""

        # Add Mock responses
        template_manager_responses(self.host, 3)

        # Test get_template_managers
        managers = self.cdcs_v3.get_template_managers()
        assert managers.title.tolist() == ['first', 'second']

        # Test get_template_managers with useronly=True
        managers = self.cdcs_v3.get_template_managers(useronly=True)
        assert len(managers) == 0

        # Test get_template_managers with title
        managers = self.cdcs_v3.get_template_managers(title='first')
        assert managers.title[0] == 'first'

        # Test get_template_managers with is_disabled=True
        managers = self.cdcs_v3.get_template_managers(is_disabled=True)
        assert managers.title.tolist() == ['third']

    @responses.activate
    def test_get_templates_v3(self):
        """Tests get_templates"""

        # Add Mock responses
        template_manager_responses(self.host, 3)
        template_responses(self.host, 3)

        # Test templates 
        templates = self.cdcs_v3.get_templates()
        assert templates.title.tolist() == ['first', 'second']
        assert templates.id.tolist() == [1, 3]

        # Test templates with current=False
        templates = self.cdcs_v3.get_templates(current=False)
        assert templates.title.tolist() == ['first', 'second', 'second']
        assert templates.id.tolist() == [1, 2, 3]

        # Test templates with is_disabled=True
        templates = self.cdcs_v3.get_templates(is_disabled=True)
        assert templates.title.tolist() == ['third']
        assert templates.id.tolist() == [4]

    @responses.activate
    def test_get_template_v3(self):
        """Tests get_template"""

        # Add Mock responses
        template_manager_responses(self.host, 3)
        template_responses(self.host, 3)

        # Test template
        template = self.cdcs_v3.get_template('second', current=True)
        assert template.id == 3

        # Test template errors for multiple, no matches
        with raises(ValueError):
            template = self.cdcs_v3.get_template()
        with raises(ValueError):
            template = self.cdcs_v3.get_template('zeroth')

    @responses.activate
    def test_template_titles_v3(self):
        """Tests template_titles"""

        # Add Mock responses
        template_manager_responses(self.host, 3)
        template_responses(self.host, 3)

        # Test template_titles
        assert self.cdcs_v3.template_titles == ['first', 'second']

    @responses.activate
    def test_empty_template_titles_v3(self):
        """Unique test for initial database"""
        responses.add(responses.GET,
                    f'{self.host}/rest/template-version-manager/global/',
                    status=200, json=[],
                    match=[responses.matchers.query_param_matcher({})])
        assert self.cdcs_v3.template_titles == []

    @responses.activate
    def test_upload_template_v3(self):
        """Tests upload_template()"""

        # Add Mock responses
        template_manager_responses(self.host, 3)
        template_responses(self.host, 3)

        # Generic schema content
        content = '<?xml version="1.0" encoding="UTF-8" standalone="no"?><xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema" attributeFormDefault="unqualified" elementFormDefault="unqualified"><xsd:element name="test" type="xsd:anyType"/></xsd:schema>'

        title = 'test'
        self.cdcs_v3.upload_template(title=title, content=content)

        with raises(ValueError):
            title = 'first'
            self.cdcs_v3.upload_template(title=title, content=content)

    @responses.activate
    def test_update_template_v3(self):
        """Tests update_template()"""
        # Add Mock responses
        template_manager_responses(self.host, 3)
        template_responses(self.host, 3)

        # Generic schema content
        content = '<?xml version="1.0" encoding="UTF-8" standalone="no"?><xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema" attributeFormDefault="unqualified" elementFormDefault="unqualified"><xsd:element name="test" type="xsd:anyType"/></xsd:schema>'

        title = 'first'
        self.cdcs_v3.update_template(title=title, content=content)

        with raises(ValueError):
            title = 'zeroth'
            self.cdcs_v3.update_template(title=title, content=content)

    @responses.activate
    def test_set_current_template_v3(self):
        """Tests set_current_template()"""
        # Add Mock responses
        template_manager_responses(self.host, 3)
        template_responses(self.host, 3)
        
        self.cdcs_v3.set_current_template('second', version=1)
        
        with raises(ValueError):
            self.cdcs_v3.set_current_template('second', version=2)
        
        with raises(IndexError):
            self.cdcs_v3.set_current_template('first', version=2)