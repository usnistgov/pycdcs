# Standard library imports
import getpass
from pathlib import Path

# http://docs.python-requests.org
import requests

# Ignore certification warnings (for now)
from requests.packages.urllib3.exceptions import InsecureRequestWarning # pylint: disable=import-error
requests.packages.urllib3.disable_warnings(InsecureRequestWarning) # pylint: disable=no-member

class RestClient(object):
    """
    Generic class for building REST calls to web databases in Python.
    """
    def __init__(self, host, username=None, password=None, certification=None,
                 **kwargs):
        """
        Class initializer. Tests and stores access information.
        
        Args:
            host: (str) URL for the database's server.
            username: (str, optional) Username of desired account on the
                server. A prompt will ask for the username if not given.
            password: (str, optional) Password of desired account on the
                server.  A prompt will ask for the password if not given.
            certification: (str, optional) Path to an authentication
                certificate, if needed, to access the database's server.
        """
        # Set access information
        self.login(host, username=username, password=password,
                   certification=certification, **kwargs)

    def __str__(self):
        """
        String representation.
        """
        return f'RestClient for {self.username} @ {self.host}'
        
    @property
    def host(self):
        """str: The host url for the server."""
        return self.__host
    
    @property
    def username(self):
        """str: The username to use for the server."""
        return self.__user
    
    @property
    def certification(self):
        """str or None: The path to the certification file."""
        return self.__cert

    def login(self, host, username=None, password=None, certification=None):
        """
        Tests and stores access information.
        
        Args:
            host: (str) URL for the database's server.
            username: (str, optional) Username of desired account on the MDCS
                server. A prompt will ask for the username if not given.
            password: (str, optional) Password of desired account on the MDCS
                server.  A prompt will ask for the password if not given.
            certification: (str, optional) Path to an authentication
                certificate, if needed, to access the database's server.
        """
        # Handle host
        host = host.strip('/')

        # Handle username
        if username is None:
            username = input(f'Enter username for {host}:')
       
        # Handle non-anonymous 
        if username != '':

            # Handle password
            if password is None:
                password = getpass.getpass(f'Enter password for {username} @ {host}:')

            # Handle certification
            if certification is not None:
                certification = Path(certification)
                if certification.is_file():
                    certification = str(certification.resolve())
                else:
                    raise ValueError('Certification file not found!')
        
        # Handle anonymous
        else:
            username = None
            password = None
            certification = None
        
        # Set object values
        self.__host = host
        self.__user = username
        self.__pswd = password
        self.__cert = certification

        # Test login info
        if self.__user is not None:
            self.testcall()
    
    def testcall(self):
        """
        Simple rest call to check if authentication parameters are valid.
        """
        # Default behavior is no test: must be set specific to database type
        pass

    def request(self, method, rest_url, **kwargs):
        """
        Wrapper around requests.request that automatically sets any access
        parameters based on the stored login information.
        
        Args:
            method: (str) Method for the new Request object.
            rest_url: (str) The REST command URL, i.e. URL path after host.
            **kwargs: (any, optional) Any other arguments supported by
                requests.request() except for url, auth, verify, and cert.
        
        Returns:
            requests.Response
        
        Raises:
            Any requests errors if the response code is not ok.
        """
        
        # Set url and access parameters
        url = self.host + '/' + rest_url.lstrip('/')
        if self.username is not None:
            auth = (self.username, self.__pswd)
        else:
            auth = None
        cert = self.certification
        if cert is None:
            verify = False
        else:
            verify = True
        
        # Send request
        response = requests.request(method, url, auth=auth, verify=verify,
                                    cert=cert, **kwargs)
        
        # Check for errors
        if not response.ok:
            try:
                print(response.json())
            except:
                print(response.text)
            response.raise_for_status()
        
        return response
    
    def head(self, rest_url, **kwargs):
        """
        Wrapper around requests.head that automatically sets any access
        parameters based on the stored login information.
        
        Args:
            rest_url: (str) The REST command URL, i.e. URL path after host.
            **kwargs: (any, optional) Any other arguments supported by
                requests.request() except for url, auth, verify, and cert.
        
        Returns:
            requests.Response: The response
        
        Raises:
            Any requests errors if the response code is not ok.
        """
        return self.request('head', rest_url, **kwargs)
    
    def get(self, rest_url, **kwargs):
        """
        Wrapper around requests.get that automatically sets any access
        parameters based on the stored login information.
        
        Args:
            rest_url: (str) The REST command URL, i.e. URL path after host.
            **kwargs: (any, optional) Any other arguments supported by
                requests.request() except for url, auth, verify, and cert.
        
        Returns:
            requests.Response: The response
        
        Raises:
            Any requests errors if the response code is not ok.
        """
        return self.request('get', rest_url, **kwargs)
        
    def post(self, rest_url, data=None, **kwargs):
        """
        Wrapper around requests.post that automatically sets any access
        parameters based on the stored login information.
        
        Args:
            rest_url: (str) The REST command URL, i.e. URL path after host.
            data: (dict or bytes, optional) Data to send in the body of the
                Request.
            **kwargs: (any, optional) Any other arguments supported by
                requests.request() except for url, auth, verify, and cert.
        
        Returns:
            requests.Response: The response
        
        Raises:
            Any requests errors if the response code is not ok.
        """
        return self.request('post', rest_url, data=data, **kwargs)
    
    def put(self, rest_url, data=None, **kwargs):
        """
        Wrapper around requests.put that automatically sets any access
        parameters based on the stored login information.
        
        Args:
            rest_url: (str) The REST command URL, i.e. URL path after host.
            data: (dict or bytes, optional) Data to send in the body of the
                Request.
            **kwargs: (any, optional) Any other arguments supported by
                requests.request() except for url, auth, verify, and cert.
        
        Returns:
            requests.Response: The response
        
        Raises:
            Any requests errors if the response code is not ok.
        """
        return self.request('put', rest_url, data=data, **kwargs)
    
    def patch(self, rest_url, data=None,**kwargs):
        """
        Wrapper around requests.patch that automatically sets any access
        parameters based on the stored login information.
        
        Args:
            rest_url: (str) The REST command URL, i.e. URL path after host.
            data: (dict or bytes, optional) Data to send in the body of the
                Request.
            **kwargs: (any, optional) Any other arguments supported by
                requests.request() except for url, auth, verify, and cert.
        
        Returns:
            requests.Response: The response
        
        Raises:
            Any requests errors if the response code is not ok.
        """
        return self.request('patch', rest_url, data=data, **kwargs)
    
    def delete(self, rest_url, **kwargs):
        """
        Wrapper around requests.delete that automatically sets any access
        parameters based on the stored login information.
        
        Args:
            rest_url: (str) The REST command URL, i.e. URL path after host.
            **kwargs: (any, optional) Any other arguments supported by
                requests.request() except for url, auth, verify, and cert.
        
        Returns:
            requests.Response: The response
        
        Raises:
            Any requests errors if the response code is not ok.
        """
        return self.request('delete', rest_url, **kwargs)