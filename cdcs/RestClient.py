# coding: utf-8

# Standard library imports
import getpass
from pathlib import Path
from typing import Optional, Union, Tuple


# http://docs.python-requests.org
import requests

# Ignore certification warnings (for now)
from requests.packages.urllib3.exceptions import InsecureRequestWarning 
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class RestClient(object):
    """
    Generic class for building REST calls to web databases in Python.
    """
    def __init__(self, host: str,
                 username: Optional[str] = None,
                 password: Optional[str] = None,
                 auth: Optional[Tuple[str]] = None,
                 cert: Union[str, Tuple[str], None] = None, 
                 certification: Union[str, Tuple[str], None] = None,
                 verify: Optional[bool] = True):
        """
        Class initializer. Tests and stores access information.
        
        Parameters
        ----------
        host : str
            URL for the database's server.
        username : str, optional
            Username of desired account on the server. A prompt will ask for
            the username if not given.
        password : str, optional
            Password of desired account on the server.  A prompt will ask for
            the password if not given.
        auth : tuple, optional
            Auth tuple to enable Basic/Digest/Custom HTTP Auth.  Alternative to
            giving username and password seperately.
        cert : str, optional
            if String, path to ssl client cert file (.pem). If Tuple,
            ('cert', 'key') pair.
        certification : str, optional
            Alias for cert. Retained for compatibility.
        verify : bool or str, optional
            Either a boolean, in which case it controls whether we verify the
            server's TLS certificate, or a string, in which case it must be a
            path to a CA bundle to use. Defaults to True.
        """
        # Set access information
        self.login(host, username=username, password=password,
                   auth=auth, cert=cert, certification=certification,
                   verify=verify)

    def __str__(self) -> str:
        """str: String representation gives username and host info."""
        return f'RestClient for {self.username} @ {self.host}'
        
    @property
    def host(self) -> str:
        """str: The host url for the server."""
        return self.__host
    
    @property
    def username(self) -> str:
        """str: The username to use for the server."""
        return self.__user
    
    @property
    def cert(self) -> Optional[str]:
        """str or None: The certification information."""
        return self.__cert

    @property
    def verify(self) -> bool:
        """bool: The verify setting for the database."""
        return self.__verify

    def login(self, host: str,
              username: Optional[str] = None,
              password: Optional[str] = None, 
              auth: Optional[Tuple[str]] = None,
              cert: Union[str, Tuple[str], None] = None, 
              certification: Union[str, Tuple[str], None] = None,
              verify: Optional[bool] = True):
        """
        Tests and stores access information.
        
        Parameters
        ----------
        host : str
            URL for the database's server.
        username : str, optional
            Username of desired account on the server. A prompt will ask for
            the username if not given.
        password : str, optional
            Password of desired account on the server.  A prompt will ask for
            the password if not given.
        auth : tuple, optional
            Auth tuple to enable Basic/Digest/Custom HTTP Auth.  Alternative to
            giving username and password seperately.
        cert : str, optional
            if String, path to ssl client cert file (.pem). If Tuple,
            ('cert', 'key') pair.
        certification : str, optional
            Alias for cert. Retained for compatibility.
        verify : bool or str, optional
            Either a boolean, in which case it controls whether we verify the
            server's TLS certificate, or a string, in which case it must be a
            path to a CA bundle to use. Defaults to True.
        """
        # Handle host
        host = host.strip('/')

        # Handle username and password
        if auth is None:

            # Handle username
            if username is None:
                username = input(f'Enter username for {host}:')
       
            # Handle non-anonymous 
            if username != '':

                # Handle password
                if password is None:
                    password = getpass.getpass(f'Enter password for {username} @ {host}:')
                auth = (username, password)
            
            # Handle anonymous
            else:
                username = None
                auth = None

        # Handle auth 
        else:
            assert username is None and password is None, 'auth cannot be given with username and password'
            username = auth[0]

        # Handle certification
        if certification is not None:
            if cert is not None:
                raise ValueError('Both certification and cert given - they are aliases of each other')
            cert = certification
        if isinstance(cert, str):
            cert = Path(cert)
            if cert.is_file():
                cert = str(cert.resolve())
            else:
                raise ValueError('Certification file not found!')
        elif isinstance(cert, (list, tuple)):
            assert len(cert) == 2
            if not Path(cert[0]).is_file() or not Path(cert[1].is_file()):
                raise ValueError('Certification file not found!')
            
        # Set object values
        self.__host = host
        self.__user = username
        self.__auth = auth
        self.__cert = cert
        self.__verify = verify

        # Test login info
        if self.__user is not None:
            self.testcall()
    
    def testcall(self):
        """Simple rest call to check if authentication parameters are valid."""
        # Default behavior is no test: must be set specific to database type
        pass

    def request(self, method: str,
                rest_url: str,
                checkstatus: bool = True,
                **kwargs) -> requests.Response:
        """
        Wrapper around requests.request that automatically sets any access
        parameters based on the stored login information.
        
        Parameters
        ----------
        method : str
            Method for the new Request object.
        rest_url : str
            The REST command URL, i.e. URL path after host.
        checkstatus : bool
            If True (default) then the response status of the call will be
            checked and an error thrown if bad.  Setting this to False will
            not automatically check the status.
        **kwargs : any, optional
            Any other arguments supported by requests.request() except for url.
            Default values for auth, verify, and cert will be used based on the
            values set during class initialization/login.
        
        Returns
        -------
        requests.Response
            The response object.

        Raises
        ------
        requests.HTTPError
            Any requests errors if the response code is not ok.
        """
        
        # Set url and access parameters
        url = self.host + '/' + rest_url.lstrip('/')
        
        auth = kwargs.pop('auth', self.__auth)
        cert = kwargs.pop('cert', self.cert)
        verify = kwargs.pop('verify', self.verify)
        
        # Send request
        response = requests.request(method, url, auth=auth, verify=verify,
                                    cert=cert, **kwargs)
        
        # Check for errors
        if checkstatus and not response.ok:
            try:
                print(response.json())
            except:
                print(response.text)
            response.raise_for_status()
        
        return response
    
    def head(self, rest_url: str,
             **kwargs) -> requests.Response:
        """
        Wrapper around requests.head that automatically sets any access
        parameters based on the stored login information.
        
        Parameters
        ----------
        rest_url : str
            The REST command URL, i.e. URL path after host.
        **kwargs : any, optional
            Any other arguments supported by requests.request() except for url.
            Default values for auth, verify, and cert will be used based on the
            values set during class initialization/login.
        
        Returns
        -------
        requests.Response
            The response object.

        Raises
        ------
        requests.HTTPError
            Any requests errors if the response code is not ok.
        """
        # Change default allow_redirects to reflect requests.head()
        if 'allow_redirects' not in kwargs:
            kwargs['allow_redirects'] = False
            
        return self.request('head', rest_url, **kwargs)
    
    def get(self, rest_url: str,
            **kwargs) -> requests.Response:
        """
        Wrapper around requests.get that automatically sets any access
        parameters based on the stored login information.
        
        Parameters
        ----------
        rest_url : str
            The REST command URL, i.e. URL path after host.
        **kwargs : any, optional
            Any other arguments supported by requests.request() except for url.
            Default values for auth, verify, and cert will be used based on the
            values set during class initialization/login.
        
        Returns
        -------
        requests.Response
            The response object.

        Raises
        ------
        requests.HTTPError
            Any requests errors if the response code is not ok.
        """
        return self.request('get', rest_url, **kwargs)
        
    def post(self, rest_url: str,
             data: Union[dict, bytes, None] = None,
             **kwargs) -> requests.Response:
        """
        Wrapper around requests.post that automatically sets any access
        parameters based on the stored login information.
        
        Parameters
        ----------
        rest_url : str
            The REST command URL, i.e. URL path after host.
        data : dict or bytes, optional
            Data to send in the body of the Request.
        **kwargs : any, optional
            Any other arguments supported by requests.request() except for url.
            Default values for auth, verify, and cert will be used based on the
            values set during class initialization/login.
        
        Returns
        -------
        requests.Response
            The response object.

        Raises
        ------
        requests.HTTPError
            Any requests errors if the response code is not ok.
        """
        return self.request('post', rest_url, data=data, **kwargs)
    
    def put(self, rest_url: str,
            data: Union[dict, bytes, None] = None,
            **kwargs) -> requests.Response:
        """
        Wrapper around requests.put that automatically sets any access
        parameters based on the stored login information.
        
        Parameters
        ----------
        rest_url : str
            The REST command URL, i.e. URL path after host.
        data : dict or bytes, optional
            Data to send in the body of the Request.
        **kwargs : any, optional
            Any other arguments supported by requests.request() except for url.
            Default values for auth, verify, and cert will be used based on the
            values set during class initialization/login.
        
        Returns
        -------
        requests.Response
            The response object.

        Raises
        ------
        requests.HTTPError
            Any requests errors if the response code is not ok.
        """
        return self.request('put', rest_url, data=data, **kwargs)
    
    def patch(self, rest_url: str,
              data: Union[dict, bytes, None] = None,
              **kwargs) -> requests.Response:
        """
        Wrapper around requests.patch that automatically sets any access
        parameters based on the stored login information.
        
        Parameters
        ----------
        rest_url : str
            The REST command URL, i.e. URL path after host.
        data : dict or bytes, optional
            Data to send in the body of the Request.
        **kwargs : any, optional
            Any other arguments supported by requests.request() except for url.
            Default values for auth, verify, and cert will be used based on the
            values set during class initialization/login.
        
        Returns
        -------
        requests.Response
            The response object.

        Raises
        ------
        requests.HTTPError
            Any requests errors if the response code is not ok.
        """
        return self.request('patch', rest_url, data=data, **kwargs)
    
    def delete(self, rest_url: str,
               **kwargs) -> requests.Response:
        """
        Wrapper around requests.delete that automatically sets any access
        parameters based on the stored login information.
        
        Parameters
        ----------
        rest_url : str
            The REST command URL, i.e. URL path after host.
        **kwargs : any, optional
            Any other arguments supported by requests.request() except for url.
            Default values for auth, verify, and cert will be used based on the
            values set during class initialization/login.
        
        Returns
        -------
        requests.Response
            The response object.

        Raises
        ------
        requests.HTTPError
            Any requests errors if the response code is not ok.
        """
        return self.request('delete', rest_url, **kwargs)