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
    def test_get_records_v3(self):
        """Tests get_records()"""

        # Add Mock responses
        record_responses(self.host, 3)
        template_responses(self.host, 3)
        template_manager_responses(self.host, 3)

        # Test no parameters
        records = self.cdcs_v3.get_records()
        assert len(records) == 12

        # Test template
        records = self.cdcs_v3.get_records(template='first')
        assert len(records) == 8

        # Test title
        records = self.cdcs_v3.get_records(title='first-record-4')
        assert len(records) == 1
        assert records.title[0] == 'first-record-4' 

        # Test title and template
        records = self.cdcs_v3.get_records(template='first', title='first-record-4')
        assert len(records) == 1
        assert records.title[0] == 'first-record-4' 

    @responses.activate
    def test_get_record_v3(self):
        """Tests get_record()"""

        # Add Mock responses
        record_responses(self.host, 3)
        template_responses(self.host, 3)
        template_manager_responses(self.host, 3) 

        # Test title
        record = self.cdcs_v3.get_record(title='first-record-4')
        assert record.title == 'first-record-4'

        # Test title and template
        record = self.cdcs_v3.get_record(template='first', title='first-record-4')
        assert record.title == 'first-record-4'

        # Test no and multiple results
        with raises(ValueError):
            record = self.cdcs_v3.get_record(template='first')
        with raises(ValueError):
            record = self.cdcs_v3.get_record(title='does-not-exist')

    @responses.activate
    def test_assign_records_v3(self):
        """Tests assign_records()"""

        # Add Mock responses
        record_responses(self.host, 3)
        template_responses(self.host, 3)
        template_manager_responses(self.host, 3) 
        workspace_responses(self.host, 3)

        # Get records for testing
        records = self.cdcs_v3.get_records(template='first')
        record = self.cdcs_v3.get_record(title='first-record-4')

        workspace = 'Global Public Workspace'

        # Test assign by record
        self.cdcs_v3.assign_records(workspace, records=records)
        self.cdcs_v3.assign_records(workspace, records=record)
        self.cdcs_v3.assign_records(self.cdcs_v3.global_workspace, records=record)

        # Test assign by id
        self.cdcs_v3.assign_records(workspace, ids=records.id.tolist())
        self.cdcs_v3.assign_records(workspace, ids=record.id)

        # Test assign by template
        self.cdcs_v3.assign_records(workspace, template='first')
        
        # Test assign by title
        self.cdcs_v3.assign_records(workspace, title='first-record-4')

        # Test assign by template and title
        self.cdcs_v3.assign_records(workspace, template='first', title='first-record-4')

        # Test invalid entries
        with raises(ValueError):
            self.cdcs_v3.assign_records(workspace, template='first', records=record)
        with raises(ValueError):
            self.cdcs_v3.assign_records(workspace, title='first', records=record)
        with raises(ValueError):
            self.cdcs_v3.assign_records(workspace, template='first', ids=record.id)
        with raises(ValueError):
            self.cdcs_v3.assign_records(workspace, title='first', ids=record.id)
        with raises(ValueError):
            self.cdcs_v3.assign_records(workspace, records=record, ids=record.id)
        with raises(TypeError):
            self.cdcs_v3.assign_records(workspace, records='badjunk')
        with raises(ValueError):
            self.cdcs_v3.assign_records(workspace)
        
    @responses.activate
    def test_upload_record_v3(self, tmpdir):
        """Tests upload_record()"""

        # Add Mock responses
        record_responses(self.host, 3)
        query_responses(self.host, 3)
        template_responses(self.host, 3)
        template_manager_responses(self.host, 3)
        workspace_responses(self.host, 3)

        # Specify content and save to a file
        template = 'second'
        title = 'second-record-4'
        content = '<?xml version="1.0" encoding="utf-8"?><second><name>second-record-4</name></second>'
        filename = Path(tmpdir, f'{title}.xml')
        with open(filename, 'w') as f:
            f.write(content)

        # Basic upload
        self.cdcs_v3.upload_record(template, title=title, content=content)

        # Upload plus workspace
        self.cdcs_v3.upload_record(template, title=title, content=content,
                                workspace='Global Public Workspace')

        # Upload by filename
        self.cdcs_v3.upload_record(template, filename=filename)

        # Upload duplicate
        content2 = '<?xml version="1.0" encoding="utf-8"?><first><name>first-record-4</name></first>'
        self.cdcs_v3.upload_record('first', title='first-record-4',
                                content=content2, duplicatecheck=False)
        with raises(ValueError):
            self.cdcs_v3.upload_record('first', title='first-record-4',
                                    content=content2)

        # Check invalid inputs
        with raises(ValueError):
            self.cdcs_v3.upload_record(template, filename=filename, content=content)
        with raises(ValueError):
            self.cdcs_v3.upload_record(template, content=content)
        with raises(ValueError):
            self.cdcs_v3.upload_record(template)
        with raises(TypeError):
            self.cdcs_v3.upload_record(template, title=title, content=23746)

    @responses.activate
    def test_update_record_v3(self, tmpdir):
        """Tests update_record()"""

        # Add Mock responses
        record_responses(self.host, 3)
        template_responses(self.host, 3)
        template_manager_responses(self.host, 3) 
        workspace_responses(self.host, 3)

        # Specify content and save to a file
        template = 'first'
        title = 'first-record-4'
        content = '<?xml version="1.0" encoding="utf-8"?><first><name>first-record-4</name></first>'
        filename = Path(tmpdir, f'{title}.xml')
        with open(filename, 'w') as f:
            f.write(content)

        record = self.cdcs_v3.get_record(template=template, title=title)

        # Basic update
        self.cdcs_v3.update_record(template=template, title=title, content=content)
        self.cdcs_v3.update_record(record=record, content=content)

        # Update plus workspace
        self.cdcs_v3.update_record(template=template, title=title, content=content,
                                workspace='Global Public Workspace')

        # Update by filename
        self.cdcs_v3.update_record(template=template, filename=filename)
        self.cdcs_v3.update_record(record=record, filename=filename)

        # Try update for record that doesn't exist
        content2 = '<?xml version="1.0" encoding="utf-8"?><second><name>second-record-4</name></second>'
        with raises(ValueError):
            self.cdcs_v3.update_record(template='second', title='second-record-4',
                                    content=content2)

        # Check invalid inputs
        with raises(ValueError):
            self.cdcs_v3.update_record(template=template, filename=filename,
                                    content=content)
        with raises(ValueError):
            self.cdcs_v3.update_record(template=template, content=content)
        with raises(ValueError):
            self.cdcs_v3.update_record(template=template)
        with raises(TypeError):
            self.cdcs_v3.update_record(template=template, title=title,
                                    content=23746)

    @responses.activate
    def test_delete_record_v3(self):
        """Tests delete_record()"""

        # Add Mock responses
        record_responses(self.host, 3)
        template_responses(self.host, 3)
        template_manager_responses(self.host, 3) 

        self.cdcs_v3.delete_record(template='first', title='first-record-4')

        record = self.cdcs_v3.get_record(title='first-record-4')
        self.cdcs_v3.delete_record(record=record)