from setuptools import setup, find_packages

def getreadme():
    with open('README.md') as readme_file:
        return readme_file.read()
   
setup(name = 'cdcs',
      version = '0.1.4',
      description = 'Python API client for performing REST calls to configurable data curation system (CDCS) databases',
      long_description = getreadme(),
      classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Scientific/Engineering :: Physics'
      ],
      keywords = [
        'CDCS', 
        'database', 
        'rest API', 
        'configurable data curation system',
      ], 
      url = 'https://github.com/usnistgov/pycdcs',
      author = 'Lucas Hale',
      author_email = 'lucas.hale@nist.gov',
      packages = find_packages(),
      install_requires = [
        'requests',
        'numpy', 
        'pandas'
      ],
      package_data={'': ['*']},
      zip_safe = False)