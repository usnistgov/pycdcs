# coding: utf-8

# Standard library imports
import json

# https://pandas.pydata.org/
import pandas as pd

# Local imports
from .. import aslist

def query(self, template=None, title=None, keyword=None,
          mongoquery=None, page=None):
    """
    Search all published local data records using either keyword or mongo-style
    queries. Note: specifying no parameters will return all records in the
    database!

    Arg:
        template: (list, str, pandas.Series or pandas.DataFrame, optional)
            One or more templates or template titles to limit the search by.
        title: (str, optional) Record title to limit the search by.
        keyword: (str or list, optional) Keyword(s) to use for a
            string-based search of record content.  Only records containing
            all keywords will be returned. keyword and mongoquery cannot both
            be given.
        mongoquery: (str or dict, optional) Mongodb find query to use in
            limiting searches by record element fields.  Note: only record
            parsing is supported, not field projection.  keyword and mongoquery
            cannot both be given.
        page: (int or None, optional) If an int, then will return results only
            for that page of 10 records.  If None (default), then results for
            all pages will be compiled and returned.

    Returns:
        pandas.DataFrame: All records matching the search request
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
                
                data['templates'].append({"id":t.id})
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

        # Repeat post until all content received
        params = {'page':2}
        while response_json['next'] is not None:
            response = self.post(rest_url, params=params, data=data)
            response_json = response.json()
            records.extend(response_json['results'])
            params['page'] += 1
        assert len(records) == response_json['count']
        records = pd.DataFrame(records)

    else:
        params = {'page':page}
        response = self.post(rest_url, params=params, data=data)
        response_json = response.json()
        records = pd.DataFrame(response_json['results'])

    # Set template titles
    def set_template_titles(series, templates):
        return templates[templates.id == series.template].iloc[0].title
    if len(records) > 0:
        records['template_title'] = records.apply(set_template_titles, args=[templates], axis=1)

    return records