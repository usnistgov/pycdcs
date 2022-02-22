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
    def test_get_records(self):
        """Tests get_records()"""

        # Add Mock responses
        record_responses(self.host)
        template_responses(self.host)
        template_manager_responses(self.host)

        # Test no parameters
        records = self.cdcs.get_records()
        assert len(records) == 11

        # Test template
        records = self.cdcs.get_records(template='first')
        assert len(records) == 8

        # Test title
        records = self.cdcs.get_records(title='first-record-4')
        assert len(records) == 1
        assert records.title[0] == 'first-record-4' 

        # Test title and template
        records = self.cdcs.get_records(template='first', title='first-record-4')
        assert len(records) == 1
        assert records.title[0] == 'first-record-4' 

    @responses.activate
    def test_get_record(self):
        """Tests get_record()"""

        # Add Mock responses
        record_responses(self.host)
        template_responses(self.host)
        template_manager_responses(self.host) 

        # Test title
        record = self.cdcs.get_record(title='first-record-4')
        assert record.title == 'first-record-4'

        # Test title and template
        record = self.cdcs.get_record(template='first', title='first-record-4')
        assert record.title == 'first-record-4'

        # Test no and multiple results
        with raises(ValueError):
            record = self.cdcs.get_record(template='first')
        with raises(ValueError):
            record = self.cdcs.get_record(title='does-not-exist')

    @responses.activate
    def test_assign_records(self):
        """Tests assign_records()"""

        # Add Mock responses
        record_responses(self.host)
        template_responses(self.host)
        template_manager_responses(self.host) 
        workspace_responses(self.host)

        # Get records for testing
        records = self.cdcs.get_records(template='first')
        record = self.cdcs.get_record(title='first-record-4')

        workspace = 'Global Public Workspace'

        # Test assign by record
        self.cdcs.assign_records(workspace, records=records)
        self.cdcs.assign_records(workspace, records=record)
        self.cdcs.assign_records(self.cdcs.global_workspace, records=record)

        # Test assign by id
        self.cdcs.assign_records(workspace, ids=records.id.tolist())
        self.cdcs.assign_records(workspace, ids=record.id)

        # Test assign by template
        self.cdcs.assign_records(workspace, template='first')
        
        # Test assign by title
        self.cdcs.assign_records(workspace, title='first-record-4')

        # Test assign by template and title
        self.cdcs.assign_records(workspace, template='first', title='first-record-4')

        # Test invalid entries
        with raises(ValueError):
            self.cdcs.assign_records(workspace, template='first', records=record)
        with raises(ValueError):
            self.cdcs.assign_records(workspace, title='first', records=record)
        with raises(ValueError):
            self.cdcs.assign_records(workspace, template='first', ids=record.id)
        with raises(ValueError):
            self.cdcs.assign_records(workspace, title='first', ids=record.id)
        with raises(ValueError):
            self.cdcs.assign_records(workspace, records=record, ids=record.id)
        with raises(TypeError):
            self.cdcs.assign_records(workspace, records='badjunk')
        with raises(ValueError):
            self.cdcs.assign_records(workspace)
        
    @responses.activate
    def test_upload_record(self, tmpdir):
        """Tests upload_record()"""

        # Add Mock responses
        record_responses(self.host)
        query_responses(self.host)
        template_responses(self.host)
        template_manager_responses(self.host)
        workspace_responses(self.host)

        # Specify content and save to a file
        template = 'second'
        title = 'second-record-4'
        content = '<?xml version="1.0" encoding="utf-8"?><second><name>second-record-4</name></second>'
        filename = Path(tmpdir, f'{title}.xml')
        with open(filename, 'w') as f:
            f.write(content)

        # Basic upload
        self.cdcs.upload_record(template, title=title, content=content)

        # Upload plus workspace
        self.cdcs.upload_record(template, title=title, content=content,
                                workspace='Global Public Workspace')

        # Upload by filename
        self.cdcs.upload_record(template, filename=filename)

        # Upload duplicate
        content2 = '<?xml version="1.0" encoding="utf-8"?><first><name>first-record-4</name></first>'
        self.cdcs.upload_record('first', title='first-record-4',
                                content=content2, duplicatecheck=False)
        with raises(ValueError):
            self.cdcs.upload_record('first', title='first-record-4',
                                    content=content2)

        # Check invalid inputs
        with raises(ValueError):
            self.cdcs.upload_record(template, filename=filename, content=content)
        with raises(ValueError):
            self.cdcs.upload_record(template, content=content)
        with raises(ValueError):
            self.cdcs.upload_record(template)
        with raises(TypeError):
            self.cdcs.upload_record(template, title=title, content=23746)

    @responses.activate
    def test_update_record(self, tmpdir):
        """Tests update_record()"""

        # Add Mock responses
        record_responses(self.host)
        template_responses(self.host)
        template_manager_responses(self.host) 
        workspace_responses(self.host)

        # Specify content and save to a file
        template = 'first'
        title = 'first-record-4'
        content = '<?xml version="1.0" encoding="utf-8"?><first><name>first-record-4</name></first>'
        filename = Path(tmpdir, f'{title}.xml')
        with open(filename, 'w') as f:
            f.write(content)

        record = self.cdcs.get_record(template=template, title=title)

        # Basic update
        self.cdcs.update_record(template=template, title=title, content=content)
        self.cdcs.update_record(record=record, content=content)

        # Update plus workspace
        self.cdcs.update_record(template=template, title=title, content=content,
                                workspace='Global Public Workspace')

        # Update by filename
        self.cdcs.update_record(template=template, filename=filename)
        self.cdcs.update_record(record=record, filename=filename)

        # Try update for record that doesn't exist
        content2 = '<?xml version="1.0" encoding="utf-8"?><second><name>second-record-4</name></second>'
        with raises(ValueError):
            self.cdcs.update_record(template='second', title='second-record-4',
                                    content=content2)

        # Check invalid inputs
        with raises(ValueError):
            self.cdcs.update_record(template=template, filename=filename,
                                    content=content)
        with raises(ValueError):
            self.cdcs.update_record(template=template, content=content)
        with raises(ValueError):
            self.cdcs.update_record(template=template)
        with raises(TypeError):
            self.cdcs.update_record(template=template, title=title,
                                    content=23746)

    @responses.activate
    def test_delete_record(self, tmpdir):
        """Tests delete_record()"""

        # Add Mock responses
        record_responses(self.host)
        template_responses(self.host)
        template_manager_responses(self.host) 

        self.cdcs.delete_record(template='first', title='first-record-4')

        record = self.cdcs.get_record(title='first-record-4')
        self.cdcs.delete_record(record=record)