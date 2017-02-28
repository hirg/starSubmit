class Job(object):
    """Object that describes one job request. 
    This object describes everything that appears inside one set of
    <job>...</job> tags in an xml file.
    """

    def __init__(self, **kwargs):
        """Set some variables"""
        self.config = dict(
            attributes = {'simulateSubmission' : 'true',
                          'fileListSyntax' : 'xrootd' },
            commands = [],
            generator_location = '',
            generator_report_location = '',
            sandbox_installer_option = 'ZIP',
            sandbox_package_name = '',
            sandbox_files = [],
            input_files = [],
            output_files = [])

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
       if isinstance(new_files, str):
           self.config[list_name].append(new_files)
       elif isinstance(new_files, list):
           for f in new_files:
               self.config[list_name].append(f)
        
