# Updates

*Version 0.2.3* Code cleanup that should have no effect except that Python < 3.7 no longer supported. The ability to toggle the auto_set_pid added and integrated into upload_record() and update_record() methods.  A retry504 option added to RestClient.requests to retry a REST call if the connection is poor.  Bug fixes related to CDCS version 3 databases.  Default column titles added for when get_templates and get_template_managers finds no matches to help avoid bugs.

*Version 0.2.2* Updated tests. Minor upkeep to fix depreciation warnings.

*Version 0.2.1* Bug fixes related to guessing the CDCS version when not given and removing generator exit warning messages.

*Version 0.2.0* Code updated to support CDCS versions 3.x.x.

*Version 0.1.9* Automatic interpretation of datetime fields into Python objects added to get and query methods for records and templates.  Progress bar added to query.  Template operations extended to include administration capabilities such uploading, updating, disabling and restoring.  Operations for uploading, modifying and deleting XSLT files and PID XPATHs added.

*Version 0.1.8* Package requirements cleaned up.  An inadvertent unused package import removed.

*Version 0.1.7*: Code cleanup and revision - typing added to the code and validation tests added.

*Version 0.1.6*: Default CDCS database value updated to 2.15.0.  RestAPI.request() now takes a checkstatus parameter to turn off automatically raising an error for bad html returns.

*Version 0.1.5*: The RestClient and CDCS classes have been updated to support more authentication options.  Package version now viewable in Python using cdcs.\_\_version\_\_.

*Version 0.1.4*: CDCS class now tracks the version of CDCS being interacted with to allow for version-specific methods if needed.  "page" option added to query.  Bug fixes and code cleanup.

*Version 0.1.3*: Workspace assignment methods changed and integrated into upload/update methods

*Version 0.1.2*: Added "verbose" option to many of the methods.  Minor code management changes.

*Version 0.1.1*: Template handling in get_records() updated - might depend on CDCS version.

*Version 0.1.0*: Package first uploaded and complete.
