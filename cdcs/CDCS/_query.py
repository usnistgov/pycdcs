# coding: utf-8

# Standard library imports
from typing import Optional, Union
from tqdm import tqdm

# Standard library imports
import json

# https://pandas.pydata.org/
import pandas as pd

# Local imports
from .. import aslist, date_parser

query_keys = ['id', 'template', 'workspace', 'user_id', 'title', 'xml_content',
              'creation_date', 'last_modification_date', 'last_change_date',
              'template_title']

def query(self,
          template: Union[list, str, pd.Series, pd.DataFrame, None] = None,
          title: Optional[str] = None,
          keyword: Union[str, list, None] = None,
          mongoquery: Union[str, dict, None] = None,
          page: Optional[int] = None,
          parse_dates: bool = True,
          progress_bar: bool = True) -> pd.DataFrame:
    """
    Search all published local data records using either keyword or mongo-style
    queries. Note: specifying no parameters will return all records in the
    database!

    Parameters
    ----------
    template : list, str, pandas.Series or pandas.DataFrame, optional
        One or more templates or template titles to limit the search by.
    title : str, optional
        Record title to limit the search by.
    keyword : str or list, optional
        Keyword(s) to use for a string-based search of record content.  Only
        records containing all keywords will be returned. keyword and
        mongoquery cannot both be given.
    mongoquery : str or dict, optional
        Mongodb find query to use in limiting searches by record element
        fields.  Note: only record parsing is supported, not field projection.
        keyword and mongoquery cannot both be given.
    page : int or None, optional
        If an int, then will return results only for that page of 10 records.
        If None (default), then results for all pages will be compiled and
        returned.
    parse_dates : bool, optional
        If True (default) then date fields will automatically be parsed into
        pandas.Timestamp objects.  If False they will be left as str values.
    progress_bar : bool, optional
        If True (default) a progress bar will be displayed for multi-page
        query results.
    Returns
    -------
    pandas.DataFrame
        All records matching the search request.
    
    Raises
    ------
    ValueError
        If query and keyword are both given.
    """  
    # Set data based on arguments
    data = {'all': 'true'} 
    data = {}
    
    # Manage query field and rest_url
    if keyword is not None:
        rest_url = '/rest/data/query/keyword/'
        if mongoquery is not None:
            raise ValueError('keyword and mongoquery cannot both be given')
        data['query'] = keyword
        
    elif mongoquery is not None:
        rest_url = '/rest/data/query/'
        if not isinstance(mongoquery, str):
            data['query'] = json.dumps(mongoquery)
        else:
            data['query'] = mongoquery
    else:
        rest_url = '/rest/data/query/'
        data['query'] = '{}'
    
    # Manage template 
    if template is not None:
        data['templates'] = []
        
        # Handle DataFrames
        if isinstance(template, pd.DataFrame):
            templates = template
            for template_id in template.id.values:
                data['templates'].append({"id":template_id})
        else:
            for t in aslist(template):
                templates = []
                if not isinstance(t, pd.Series):
                    t = self.get_template(title=t)
                t_id = t.id
                if self.cdcsversion[0] > 2:
                    t_id = int(t_id)
                data['templates'].append({"id":t_id})
                templates.append(t)
            templates = pd.DataFrame(templates)
                    
        data['templates'] = json.dumps(data['templates'])
    else:
        templates = self.get_templates()

    # Manage title
    if title is not None:
        data['title'] = title

    # Get results from all pages
    if page is None:

        # Get response
        response = self.post(rest_url, data=data)
        response_json = response.json()
        records = response_json['results']

        if len(records) < response_json['count']:
            
            if progress_bar:
                pbar = tqdm(total=response_json['count'], initial=len(records))
            
            # Repeat post until all content received
            params = {'page':2}
            while response_json['next'] is not None:
                response = self.post(rest_url, params=params, data=data)
                response_json = response.json()
                newrecords = response_json['results']
                records.extend(newrecords)
                params['page'] += 1

                if progress_bar:
                    pbar.update(len(newrecords))
            
            if progress_bar:
                pbar.close()

            assert len(records) == response_json['count']
        
        records = pd.DataFrame(records)

    else:
        params = {'page':page}
        response = self.post(rest_url, params=params, data=data)
        response_json = response.json()
        records = pd.DataFrame(response_json['results'])

    if len(records) == 0:
        records = pd.DataFrame(columns=query_keys)

    # Set template titles
    def set_template_titles(series, templates):
        return templates[templates.id == series.template].iloc[0].title
    if len(records) > 0:
        records['template_title'] = records.apply(set_template_titles, args=[templates], axis=1)

    # Parse date fields
    if parse_dates and len(records) > 0:
        for key in ['creation_date', 'last_modification_date', 'last_change_date']:
            records[key] = records.apply(date_parser, args=[key], axis=1)
    
    return records

def query_count(self,
                template: Union[list, str, pd.Series, pd.DataFrame, None] = None,
                title: Optional[str] = None,
                keyword: Union[str, list, None] = None,
                mongoquery: Union[str, dict, None] = None,
                ) -> pd.DataFrame:
    """
    Search all published local data records using either keyword or mongo-style
    queries and return only the total count of matching records.

    Parameters
    ----------
    template : list, str, pandas.Series or pandas.DataFrame, optional
        One or more templates or template titles to limit the search by.
    title : str, optional
        Record title to limit the search by.
    keyword : str or list, optional
        Keyword(s) to use for a string-based search of record content.  Only
        records containing all keywords will be returned. keyword and
        mongoquery cannot both be given.
    mongoquery : str or dict, optional
        Mongodb find query to use in limiting searches by record element
        fields.  Note: only record parsing is supported, not field projection.
        keyword and mongoquery cannot both be given.

    Returns
    -------
    int
        The number of records matching the search request.
    
    Raises
    ------
    ValueError
        If query and keyword are both given.
    """
    # Set data based on arguments
    data = {'all': 'true'} 
    data = {}
    
    # Manage query field and rest_url
    if keyword is not None:
        rest_url = '/rest/data/query/keyword/'
        if mongoquery is not None:
            raise ValueError('keyword and mongoquery cannot both be given')
        data['query'] = keyword
        
    elif mongoquery is not None:
        rest_url = '/rest/data/query/'
        if not isinstance(mongoquery, str):
            data['query'] = json.dumps(mongoquery)
        else:
            data['query'] = mongoquery
    else:
        rest_url = '/rest/data/query/'
        data['query'] = '{}'
    
    # Manage template 
    if template is not None:
        data['templates'] = []
        
        # Handle DataFrames
        if isinstance(template, pd.DataFrame):
            templates = template
            for template_id in template.id.values:
                data['templates'].append({"id":template_id})
        else:
            for t in aslist(template):
                templates = []
                if not isinstance(t, pd.Series):
                    t = self.get_template(title=t)
                t_id = t.id
                if self.cdcsversion[0] > 2:
                    t_id = int(t_id)
                data['templates'].append({"id":t_id})
                templates.append(t)
            templates = pd.DataFrame(templates)    
                    
        data['templates'] = json.dumps(data['templates'])
    else:
        templates = self.get_templates()

    # Manage title
    if title is not None:
        data['title'] = title

    # Get response
    response = self.post(rest_url, data=data)
    response_json = response.json()

    return response_json['count']

def query_ipyparallel(self,
                      client,
                      template: Union[list, str, pd.Series, pd.DataFrame, None] = None,
                      title: Optional[str] = None,
                      keyword: Union[str, list, None] = None,
                      mongoquery: Union[str, dict, None] = None
                      ) -> pd.DataFrame:
    """
    Search all published local data records using either keyword or mongo-style
    queries. Note: specifying no parameters will return all records in the
    database!

    Parameters
    ----------
    client : ipyparallel.client.client.Client
        An ipyparallel Client object to use for performing multiple
        parallel web requests.
    template : list, str, pandas.Series or pandas.DataFrame, optional
        One or more templates or template titles to limit the search by.
    title : str, optional
        Record title to limit the search by.
    keyword : str or list, optional
        Keyword(s) to use for a string-based search of record content.  Only
        records containing all keywords will be returned. keyword and
        mongoquery cannot both be given.
    mongoquery : str or dict, optional
        Mongodb find query to use in limiting searches by record element
        fields.  Note: only record parsing is supported, not field projection.
        keyword and mongoquery cannot both be given.

    Returns
    -------
    pandas.DataFrame
        All records matching the search request.
    
    Raises
    ------
    ValueError
        If query and keyword are both given.
    """  
    raise NotImplementedError('Still need to finish')
    # Create direct and load balanced views
    dview = client[:]
    lview = client.load_balanced_view()

    # Set data based on arguments
    data = {'all': 'true'} 
    data = {}
    
    # Manage query field and rest_url
    if keyword is not None:
        rest_url = '/rest/data/query/keyword/'
        if mongoquery is not None:
            raise ValueError('keyword and mongoquery cannot both be given')
        data['query'] = keyword
        
    elif mongoquery is not None:
        rest_url = '/rest/data/query/'
        if not isinstance(mongoquery, str):
            data['query'] = json.dumps(mongoquery)
        else:
            data['query'] = mongoquery
    else:
        rest_url = '/rest/data/query/'
        data['query'] = '{}'
    
    # Manage template 
    if template is not None:
        data['templates'] = []
        
        # Handle DataFrames
        if isinstance(template, pd.DataFrame):
            templates = template
            for template_id in template.id.values:
                data['templates'].append({"id":template_id})
        else:
            for t in aslist(template):
                templates = []
                if not isinstance(t, pd.Series):
                    t = self.get_template(title=t)
                
                data['templates'].append({"id":t.id})
                templates.append(t)
            templates = pd.DataFrame(templates)    
                    
        data['templates'] = json.dumps(data['templates'])
    else:
        templates = self.get_templates()

    # Manage title
    if title is not None:
        data['title'] = title

    # Get response for page 1
    response = self.post(rest_url, data=data)
    response_json = response.json()
    records = response_json['results']

    numpages = response_json['count'] / len(records)
    pages = list(range(2, numpages+1))
    if numpages > 1:

        dview.push(dict(self=self, data=data))
        
        def post_page(page):
            params = {'page':page}
            response = self.post(rest_url, params=params, data=data)
            response_json = response.json()
            return response_json['results']

        results = lview.map_async(post_page, pages)
        assert len(records) == response_json['count']
        records = pd.DataFrame(records)

    # Set template titles
    def set_template_titles(series, templates):
        return templates[templates.id == series.template].iloc[0].title
    if len(records) > 0:
        records['template_title'] = records.apply(set_template_titles, args=[templates], axis=1)

    return records