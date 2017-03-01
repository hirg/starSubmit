from configparser import ConfigParser as cp
from configparser import ExtendedInterpolation

class Job(object):
    """Object that describes one job request. 
    This object describes everything that appears inside one set of
    <job>...</job> tags in an xml file.
    """

    def __init__(self, config_file = None, **kwargs):
        """Set some variables"""
        self.config = dict(
            attributes = {'simulateSubmission' : 'false',
                          'fileListSyntax' : 'xrootd' },
            commands = [],
            generator_location = '',
            generator_report_location = '',
            sandbox_installer_option = 'ZIP',
            sandbox_package_name = '',
            sandbox_files = [],
            input_files = [],
            output_files = [],
            stderr_path = '')
        
        if config_file:
            self.read_config_file(config_file)

        badargs = set(kwargs) - set(self.config)
        if badargs:
            error_string = 'Job.__init__() got unexpected keyword arguments: {}' 
            raise TypeError(error_string.format( list(badargs) ))
        else:
            self.config.update(kwargs)


    def add_job_attribute(self, attribute, value):
       """Add an attribute/value pair to the job attributes dictionary"""
       new_attribute = { str(attribute) : '"{}"'.format(value) }
       self.config['attributes'].update( new_attribute )
        
    def add_commands(self, new_commands):
       """Add a command or list of commands to the job command list"""
       if isinstance(new_commands, str):
           self.config['commands'].append(new_commands)
       elif isinstance(new_commands, list):
           for com in new_commands:
               self.config['commands'].append(com)
        
    def add_files(self, new_files, list_name):
       """Add a file or list of files to one of several config options
       'list_name' option should be one of: 'sandbox_files', 
                                            'input_files', 
                                            'output_files'
       
       """
       if isinstance(new_files, tuple) or isinstance(new_files, str):
           self.config[list_name].append(new_files)
       elif isinstance(new_files, list):
           for f in new_files:
               self.config[list_name].append(f)
        
    def read_config_file(self, file_name):
        """Read a plain text config file and return a dictionary of parameters"""
        major_split = ';' # String to split up list items
        minor_split = ',' # String to split up tuple items with a list item

        config = cp(interpolation=ExtendedInterpolation())
        config.optionxform = lambda option: option # Keep keys as they are
        config.read(file_name)

        if config['job_attributes']:
            self.config['attributes'].update(config['job_attributes'])

        # Generator/Report information
        if config['generator']['location']:
            self.config['generator_location'] = config['generator']['location']
        if config['generator']['report_location']:
            self.config['generator_report_location'] = config['generator']['report_location']

        # Add sandbox info
        if config['sandbox']['files']:
            for files in config['sandbox']['files'].split(major_split):
                self.add_files(files.strip(), 'sandbox_files')
        if config['sandbox']['package_name']:
            self.config['sandbox_package_name'] = config['sandbox']['package_name']
        if config['sandbox']['installer_option']:
            self.config['sandbox_installer_option'] = config['sandbox']['installer_option']


        # Add commands and input files
        if config['input']['commands']:
            for command in config['input']['commands'].split(major_split):
                self.add_commands(command.strip())
        if config['input']['files']:
            for pair in config['input']['files'].split(major_split):
                (url, n_files) = pair.split(minor_split)
                self.add_files( (url.strip(), n_files.strip()), 'input_files')

        # Add output and stderr paths
        if config['output']['paths']:
            for pair in config['output']['paths'].split(major_split):
                (url, glob) = pair.split(minor_split)
                self.add_files( (url.strip(), glob.strip()), 'output_files')
        if config['output']['stderr_path']:
            self.config['stderr_path'] = config['output']['stderr_path']
