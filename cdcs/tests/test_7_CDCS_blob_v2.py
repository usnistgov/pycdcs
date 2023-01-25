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
    def test_upload_blob_v2(self, tmpdir):
        """Tests upload_blob()"""

        # Add Mock responses
        blob_responses(self.host, 2)
        workspace_responses(self.host, 2)

        # Create file to upload
        filename = Path(tmpdir, 'test_blob.txt')
        with open(filename, 'w') as f:
            f.write('This is my blob for testing')

        # Test upload_blob() from a file object
        with open(filename, 'rb') as f:
            handle = self.cdcs_v2.upload_blob(filename=filename, blobbytes=f)
        assert handle == f'{self.host}/rest/blob/download/1/'

        # Test upload_blob() from only the filename
        handle = self.cdcs_v2.upload_blob(filename=filename)
        assert handle == f'{self.host}/rest/blob/download/1/'
    
        # Test upload_blob() with workspace
        handle = self.cdcs_v2.upload_blob(filename=filename,
                                       workspace='Global Public Workspace')
        assert handle == f'{self.host}/rest/blob/download/1/'

    @responses.activate
    def test_get_blobs_v2(self):
        """Tests get_blobs()"""

        # Add Mock responses
        blob_responses(self.host, 2)

        # Test get_blobs() with no arguments
        blobs = self.cdcs_v2.get_blobs()
        assert blobs.id.tolist() == ['1', '2']
        assert blobs.filename.tolist() == ['test_blob.txt', 'no_blob.txt']

    @responses.activate
    def test_get_blob_v2(self):
        """Tests get_blob()"""

        # Add Mock responses
        blob_responses(self.host, 2)

        # Test get_blob() with filename
        blob = self.cdcs_v2.get_blob(filename='test_blob.txt')
        assert blob.id == '1'
        assert blob.filename == 'test_blob.txt'

        # Test get_blob() with id
        blob = self.cdcs_v2.get_blob(id='1')
        assert blob.id == '1'
        assert blob.filename == 'test_blob.txt'

        # Test get_blob() errors for multiple, no matches
        with raises(ValueError):
            blob = self.cdcs_v2.get_blob()
        with raises(ValueError):
            blob = self.cdcs_v2.get_blob(filename='fake.txt')
        with raises(ValueError):
            blob = self.cdcs_v2.get_blob(filename='fake.txt', id='yo!')

    @responses.activate
    def test_assign_blobs_v2(self):
        """Tests assign_blobs()"""

        # Add Mock responses
        blob_responses(self.host, 2)
        workspace_responses(self.host, 2)

        # Get blob(s) for testing below
        blobs = self.cdcs_v2.get_blobs()
        blob = self.cdcs_v2.get_blob(filename='test_blob.txt')

        # Test assign_blobs() with valid inputs
        self.cdcs_v2.assign_blobs(workspace='Global Public Workspace',
                               filename='test_blob.txt')
        self.cdcs_v2.assign_blobs(workspace='Global Public Workspace',
                               ids='1')
        self.cdcs_v2.assign_blobs(workspace='Global Public Workspace',
                               ids=['1', '2'])
        self.cdcs_v2.assign_blobs(workspace='Global Public Workspace',
                               blobs=blobs)
        self.cdcs_v2.assign_blobs(workspace='Global Public Workspace',
                               blobs=blob)

        # Test assign_blobs() with invalid inputs
        with raises(ValueError):
            self.cdcs_v2.assign_blobs(workspace='Global Public Workspace',
                                   filename='test_blob.txt',
                                   ids='1')
        with raises(ValueError):
            self.cdcs_v2.assign_blobs(workspace='Global Public Workspace',
                                   filename='test_blob.txt',
                                   blobs=blobs)
        with raises(ValueError):
            self.cdcs_v2.assign_blobs(workspace='Global Public Workspace',
                                   ids='1',
                                   blobs=blobs)
        with raises(TypeError):
            self.cdcs_v2.assign_blobs(workspace='Global Public Workspace',
                                   blobs='not blobs')
        with raises(ValueError):
            self.cdcs_v2.assign_blobs(workspace='Global Public Workspace')

    @responses.activate
    def test_get_blob_contents_v2(self):
        """Tests get_blob_contents()"""

        # Add Mock responses
        blob_responses(self.host, 2)

        # Get blob for testing below
        blob = self.cdcs_v2.get_blob(filename='test_blob.txt')

        # Test get_blob_contents()
        content = self.cdcs_v2.get_blob_contents(blob=blob)
        assert content == b'This is my blob for testing'
        content = self.cdcs_v2.get_blob_contents(id='1')
        assert content == b'This is my blob for testing'       
        content = self.cdcs_v2.get_blob_contents(filename='test_blob.txt')
        assert content == b'This is my blob for testing'
        
        # Test get_blob_contents() with invalid inputs
        with raises(ValueError):
            content = self.cdcs_v2.get_blob_contents(blob=blob, id='1')
        with raises(ValueError):
            content = self.cdcs_v2.get_blob_contents(blob=blob, filename='test_blob.txt')
        with raises(ValueError):
            content = self.cdcs_v2.get_blob_contents(id='1', filename='test_blob.txt')

    @responses.activate
    def test_download_blob_v2(self, tmpdir):
        """Tests download_blob()"""

        # Add Mock responses
        blob_responses(self.host, 2)

        # Get blob for testing below
        blob = self.cdcs_v2.get_blob(filename='test_blob.txt')

        # Set filename
        filename = Path(tmpdir, 'test_blob.txt')

        # Test download_blob() from blob
        self.cdcs_v2.download_blob(blob=blob, savedir=tmpdir)
        with open(filename) as f:
            assert f.read() == 'This is my blob for testing'
        filename.unlink()

        # Test download_blob() from id
        self.cdcs_v2.download_blob(id='1', savedir=tmpdir)
        with open(filename) as f:
            assert f.read() == 'This is my blob for testing'
        filename.unlink()

        # Test download_blob() from filename
        self.cdcs_v2.download_blob(filename='test_blob.txt', savedir=tmpdir)
        with open(filename) as f:
            assert f.read() == 'This is my blob for testing'
        filename.unlink()

        # Test download_blob() with invalid inputs
        with raises(ValueError):
            self.cdcs_v2.download_blob(blob=blob, id='1')
        with raises(ValueError):
            self.cdcs_v2.download_blob(blob=blob, filename='test_blob.txt')
        with raises(ValueError):
            self.cdcs_v2.download_blob(id='1', filename='test_blob.txt')

    @responses.activate
    def test_delete_blob_v2(self):
        """Tests delete_blob()"""

        # Add Mock responses
        blob_responses(self.host, 2)

        # Get blob for testing below
        blob = self.cdcs_v2.get_blob(filename='test_blob.txt')

        # Test delete_blob()
        self.cdcs_v2.delete_blob(blob=blob)        
        self.cdcs_v2.delete_blob(id='1')     
        self.cdcs_v2.delete_blob(filename='test_blob.txt')

        # Test delete_blob() with invalid inputs
        with raises(ValueError):
            self.cdcs_v2.delete_blob(blob=blob, id='1')
        with raises(ValueError):
            self.cdcs_v2.delete_blob(blob=blob, filename='test_blob.txt')
        with raises(ValueError):
            self.cdcs_v2.delete_blob(id='1', filename='test_blob.txt')
