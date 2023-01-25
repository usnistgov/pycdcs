from copy import deepcopy

def v2_convert(data):
    """
    Converts mock database data into v2 compliant content by converting
    int values into str values.
    """
    # Create a safe copy
    data = deepcopy(data)

    # Change single entry content
    if isinstance(data, dict):
        for k in data:
            if isinstance(data[k], int) and not isinstance(data[k], bool):
                data[k] = str(data[k])
    else:
        # Change multi entry content
        for i in range(len(data)):
            for k in data[i]:
                if isinstance(data[i][k], int) and not isinstance(data[i][k], bool):
                    data[i][k] = str(data[i][k])
    return data

from .workspace_responses import workspace_responses
from .template_manager_responses import template_manager_responses
from .template_responses import template_responses
from .query_responses import query_responses
from .blob_responses import blob_responses
from .record_responses import record_responses
from .xslt_responses import xslt_responses
from .pid_xpath_responses import pid_xpath_responses