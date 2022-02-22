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
    def test_upload_blob(self, tmpdir):
        """Tests upload_blob()"""

        # Add Mock responses
        blob_responses(self.host)
        workspace_responses(self.host)

        # Create file to upload
        filename = Path(tmpdir, 'test_blob.txt')
        with open(filename, 'w') as f:
            f.write('This is my blob for testing')

        # Test upload_blob() from a file object
        with open(filename, 'rb') as f:
            handle = self.cdcs.upload_blob(filename=filename, blobbytes=f)
        assert handle == f'{self.host}/rest/blob/download/randomblobhash/'

        # Test upload_blob() from only the filename
        handle = self.cdcs.upload_blob(filename=filename)
        assert handle == f'{self.host}/rest/blob/download/randomblobhash/'
    
        # Test upload_blob() with workspace
        handle = self.cdcs.upload_blob(filename=filename,
                                       workspace='Global Public Workspace')
        assert handle == f'{self.host}/rest/blob/download/randomblobhash/'

    @responses.activate
    def test_get_blobs(self):
        """Tests get_blobs()"""

        # Add Mock responses
        blob_responses(self.host)

        # Test get_blobs() with no arguments
        blobs = self.cdcs.get_blobs()
        assert blobs.id.tolist() == ['randomblobhash', 'otherblobhash']
        assert blobs.filename.tolist() == ['test_blob.txt', 'no_blob.txt']

    @responses.activate
    def test_get_blob(self):
        """Tests get_blob()"""

        # Add Mock responses
        blob_responses(self.host)

        # Test get_blob() with filename
        blob = self.cdcs.get_blob(filename='test_blob.txt')
        assert blob.id == 'randomblobhash'
        assert blob.filename == 'test_blob.txt'

        # Test get_blob() with id
        blob = self.cdcs.get_blob(id='randomblobhash')
        assert blob.id == 'randomblobhash'
        assert blob.filename == 'test_blob.txt'

        # Test get_blob() errors for multiple, no matches
        with raises(ValueError):
            blob = self.cdcs.get_blob()
        with raises(ValueError):
            blob = self.cdcs.get_blob(filename='fake.txt')
        with raises(ValueError):
            blob = self.cdcs.get_blob(filename='fake.txt', id='yo!')

    @responses.activate
    def test_assign_blobs(self):
        """Tests assign_blobs()"""

        # Add Mock responses
        blob_responses(self.host)
        workspace_responses(self.host)

        # Get blob(s) for testing below
        blobs = self.cdcs.get_blobs()
        blob = self.cdcs.get_blob(filename='test_blob.txt')

        # Test assign_blobs() with valid inputs
        self.cdcs.assign_blobs(workspace='Global Public Workspace',
                               filename='test_blob.txt')
        self.cdcs.assign_blobs(workspace='Global Public Workspace',
                               ids='randomblobhash')
        self.cdcs.assign_blobs(workspace='Global Public Workspace',
                               ids=['randomblobhash', 'otherblobhash'])
        self.cdcs.assign_blobs(workspace='Global Public Workspace',
                               blobs=blobs)
        self.cdcs.assign_blobs(workspace='Global Public Workspace',
                               blobs=blob)

        # Test assign_blobs() with invalid inputs
        with raises(ValueError):
            self.cdcs.assign_blobs(workspace='Global Public Workspace',
                                   filename='test_blob.txt',
                                   ids='randomblobhash')
        with raises(ValueError):
            self.cdcs.assign_blobs(workspace='Global Public Workspace',
                                   filename='test_blob.txt',
                                   blobs=blobs)
        with raises(ValueError):
            self.cdcs.assign_blobs(workspace='Global Public Workspace',
                                   ids='randomblobhash',
                                   blobs=blobs)
        with raises(TypeError):
            self.cdcs.assign_blobs(workspace='Global Public Workspace',
                                   blobs='not blobs')
        with raises(ValueError):
            self.cdcs.assign_blobs(workspace='Global Public Workspace')

    @responses.activate
    def test_get_blob_contents(self):
        """Tests get_blob_contents()"""

        # Add Mock responses
        blob_responses(self.host)

        # Get blob for testing below
        blob = self.cdcs.get_blob(filename='test_blob.txt')

        # Test get_blob_contents()
        content = self.cdcs.get_blob_contents(blob=blob)
        assert content == b'This is my blob for testing'
        content = self.cdcs.get_blob_contents(id='randomblobhash')
        assert content == b'This is my blob for testing'       
        content = self.cdcs.get_blob_contents(filename='test_blob.txt')
        assert content == b'This is my blob for testing'
        
        # Test get_blob_contents() with invalid inputs
        with raises(ValueError):
            content = self.cdcs.get_blob_contents(blob=blob, id='randomblobhash')
        with raises(ValueError):
            content = self.cdcs.get_blob_contents(blob=blob, filename='test_blob.txt')
        with raises(ValueError):
            content = self.cdcs.get_blob_contents(id='randomblobhash', filename='test_blob.txt')

    @responses.activate
    def test_download_blob(self, tmpdir):
        """Tests download_blob()"""

        # Add Mock responses
        blob_responses(self.host)

        # Get blob for testing below
        blob = self.cdcs.get_blob(filename='test_blob.txt')

        # Set filename
        filename = Path(tmpdir, 'test_blob.txt')

        # Test download_blob() from blob
        self.cdcs.download_blob(blob=blob, savedir=tmpdir)
        with open(filename) as f:
            assert f.read() == 'This is my blob for testing'
        filename.unlink()

        # Test download_blob() from id
        self.cdcs.download_blob(id='randomblobhash', savedir=tmpdir)
        with open(filename) as f:
            assert f.read() == 'This is my blob for testing'
        filename.unlink()

        # Test download_blob() from filename
        self.cdcs.download_blob(filename='test_blob.txt', savedir=tmpdir)
        with open(filename) as f:
            assert f.read() == 'This is my blob for testing'
        filename.unlink()

        # Test download_blob() with invalid inputs
        with raises(ValueError):
            self.cdcs.download_blob(blob=blob, id='randomblobhash')
        with raises(ValueError):
            self.cdcs.download_blob(blob=blob, filename='test_blob.txt')
        with raises(ValueError):
            self.cdcs.download_blob(id='randomblobhash', filename='test_blob.txt')

    @responses.activate
    def test_delete_blob(self):
        """Tests delete_blob()"""

        # Add Mock responses
        blob_responses(self.host)

        # Get blob for testing below
        blob = self.cdcs.get_blob(filename='test_blob.txt')

        # Test delete_blob()
        self.cdcs.delete_blob(blob=blob)        
        self.cdcs.delete_blob(id='randomblobhash')     
        self.cdcs.delete_blob(filename='test_blob.txt')

        # Test delete_blob() with invalid inputs
        with raises(ValueError):
            self.cdcs.delete_blob(blob=blob, id='randomblobhash')
        with raises(ValueError):
            self.cdcs.delete_blob(blob=blob, filename='test_blob.txt')
        with raises(ValueError):
            self.cdcs.delete_blob(id='randomblobhash', filename='test_blob.txt')