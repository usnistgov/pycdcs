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
    def test_get_template_managers(self):
        """Tests get_template_managers"""

        # Add Mock responses
        template_manager_responses(self.host)

        # Test get_template_managers
        managers = self.cdcs.get_template_managers()
        assert managers.title.tolist() == ['first', 'second']

        # Test get_template_managers with useronly=True
        managers = self.cdcs.get_template_managers(useronly=True)
        assert len(managers) == 0

        # Test get_template_managers with title
        managers = self.cdcs.get_template_managers(title='first')
        assert managers.title[0] == 'first'

        # Test get_template_managers with is_disabled=True
        managers = self.cdcs.get_template_managers(is_disabled=True)
        assert managers.title.tolist() == ['third']

    @responses.activate
    def test_get_templates(self):
        """Tests get_templates"""

        # Add Mock responses
        template_manager_responses(self.host)
        template_responses(self.host)

        # Test templates 
        templates = self.cdcs.get_templates()
        assert templates.title.tolist() == ['first', 'second']
        assert templates.id.tolist() == ['firsthash1', 'secondhash2']

        # Test templates with current=False
        templates = self.cdcs.get_templates(current=False)
        assert templates.title.tolist() == ['first', 'second', 'second']
        assert templates.id.tolist() == ['firsthash1', 'secondhash1', 'secondhash2']

        # Test templates with is_disabled=True
        templates = self.cdcs.get_templates(is_disabled=True)
        assert templates.title.tolist() == ['third']
        assert templates.id.tolist() == ['thirdhash1']

    @responses.activate
    def test_get_template(self):
        """Tests get_template"""

        # Add Mock responses
        template_manager_responses(self.host)
        template_responses(self.host)

        # Test template
        template = self.cdcs.get_template('second', current=True)
        assert template.id == 'secondhash2'

        # Test template errors for multiple, no matches
        with raises(ValueError):
            template = self.cdcs.get_template()
        with raises(ValueError):
            template = self.cdcs.get_template('zeroth')

    @responses.activate
    def test_template_titles(self):
        """Tests template_titles"""

        # Add Mock responses
        template_manager_responses(self.host)
        template_responses(self.host)

        # Test template_titles
        assert self.cdcs.template_titles == ['first', 'second']