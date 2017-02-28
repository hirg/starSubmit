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
            sandbox_files = '',
            input_files = [],
            output_files = [])

        badargs = set(kwargs) - set(self.config)
        if badargs:
            error_string = 'Job.__init__() got unexpected keyword arguments: {}' 
            raise TypeError(error_string.format( list(badargs) ))
        else:
            self.config.update(kwargs)


    
