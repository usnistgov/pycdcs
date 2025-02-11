import requests
import responses
from pytest import raises
from pathlib import Path

from cdcs import RestClient

class TestRestClient():

    @property
    def host(self):
        """str: A fake host url for testing"""
        return 'https://fakeurl.fake'

    def test_init(self, tmpdir):
        """
        This function tests parameter setting with RestClient inits.  Since
        the init calls login(), it also serves to check login().
        """
        
        # Test #1: anonymous user
        client = RestClient(host=self.host, username='')
        assert client.host == self.host
        assert client.username is None
        assert client.cert is None
        assert client.verify is True

        # Test #2: authenticated user
        client = RestClient(host=self.host, username='user', password='pswd',
                            verify=False)
        assert client.host == self.host
        assert client.username == 'user'
        assert client.cert is None
        assert client.verify is False

        # Test #3 missing cert file
        with raises(ValueError):
            client = RestClient(host=self.host, username='user', password='pswd',
                                cert='certfile.pem')
        
        # Test #4 existing cert file
        cert = Path(tmpdir, 'certfile.pem')
        with open(cert, 'w') as f:
            f.write('This is certifiable!')
        client = RestClient(host=self.host, username='user', password='pswd',
                            cert=cert)
        assert client.host == self.host
        assert client.username == 'user'
        assert client.cert == cert
        assert client.verify is True

    def test_request(self):
        """Test generic requests and auto status code checking"""
        client = RestClient(host=self.host, username='')
        rest_url = 'some/url/'

        # Mock good get response
        with responses.RequestsMock() as rsps:
            rsps.add(responses.GET, f'{self.host}/{rest_url}', status=200,
                     json={'value':"good!"})
            r = client.request('get', rest_url)
            assert r.status_code == 200
            assert r.json()['value'] == 'good!'
        
        # Mock bad get response
        with responses.RequestsMock() as rsps:
            rsps.add(responses.GET, f'{self.host}/{rest_url}', status=401,
                     json={'value':"bad!"})
            with raises(requests.HTTPError):
                r = client.request('get', rest_url)
            r = client.request('get', rest_url, checkstatus=False)
            assert r.status_code == 401
            assert r.json()['value'] == 'bad!'

            
    def test_head(self):
        """Test that head performs a head request"""
        client = RestClient(host=self.host, username='')
        rest_url = 'some/url/'
        
        # Mock good response
        with responses.RequestsMock() as rsps:
            rsps.add(responses.HEAD, f'{self.host}/{rest_url}', status=200)
            r = client.head(rest_url)

    def test_get(self):
        """Test that get performs a get request"""
        client = RestClient(host=self.host, username='')
        rest_url = 'some/url/'
        
        # Mock good response
        with responses.RequestsMock() as rsps:
            rsps.add(responses.GET, f'{self.host}/{rest_url}', status=200,
                     json={'value':"good!"})
            r = client.get(rest_url)

    def test_post(self):
        """Test that post performs a post request"""
        client = RestClient(host=self.host, username='')
        rest_url = 'some/url/'
        
        # Mock good response
        with responses.RequestsMock() as rsps:
            rsps.add(responses.POST, f'{self.host}/{rest_url}', status=200,
                     json={'value':"good!"})
            r = client.post(rest_url)

    def test_put(self):
        """Test that put performs a put request"""
        client = RestClient(host=self.host, username='')
        rest_url = 'some/url/'
        
        # Mock good response
        with responses.RequestsMock() as rsps:
            rsps.add(responses.PUT, f'{self.host}/{rest_url}', status=200,
                     json={'value':"good!"})
            r = client.put(rest_url)

    def test_patch(self):
        """Test that patch performs a patch request"""
        client = RestClient(host=self.host, username='')
        rest_url = 'some/url/'
        
        # Mock good response
        with responses.RequestsMock() as rsps:
            rsps.add(responses.PATCH, f'{self.host}/{rest_url}', status=200,
                     json={'value':"good!"})
            r = client.patch(rest_url)

    def test_delete(self):
        """Test that delete performs a delete request"""
        client = RestClient(host=self.host, username='')
        rest_url = 'some/url/'
        
        # Mock good response
        with responses.RequestsMock() as rsps:
            rsps.add(responses.DELETE, f'{self.host}/{rest_url}', status=200,
                     json={'value':"good!"})
            r = client.delete(rest_url)