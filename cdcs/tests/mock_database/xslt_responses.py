import responses
from . import v2_convert

def xslt_responses(host, version=3):
    """Mock responses for xslt methods"""
    
    from .data import xslts

    if version == 2:
        xslts = v2_convert(xslts)

    # Get all xslts
    responses.add(responses.GET, f'{host}/rest/xslt/',
                  json=xslts, status=200)

    # Upload a new xslt
    data = {}
    data['name'] = 'template3-xsl1'
    data['filename'] = 'template3-xsl1.xsl'
    data['content'] = '<?xml version="1.0" encoding="UTF-8"?><xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns="http://www.w3.org/TR/xhtml1/strict"> <xsl:output method="html" encoding="utf-8" indent="yes" /></xsl:stylesheet>'
    responses.add(responses.POST, f'{host}/rest/xslt/',
                  match=[responses.matchers.urlencoded_params_matcher(data)],
                  json=xslts[3], status=201)
    
    # Modify the xslt
    data = {}
    data['name'] = 'template3-xsl1'
    data['filename'] = 'template3-xsl1.xsl'
    data['content'] = '<?xml version="1.0" encoding="UTF-8"?><xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns="http://www.w3.org/TR/xhtml1/strict"> <xsl:output method="html" encoding="utf-8" indent="yes" /></xsl:stylesheet>'
    responses.add(responses.PATCH, f'{host}/rest/xslt/4/',
                  match=[responses.matchers.urlencoded_params_matcher(data)],
                  json=xslts[3], status=201)

    # Delete xslt
    responses.add(responses.DELETE, f'{host}/rest/xslt/4/',
                  body=b'', status=204)