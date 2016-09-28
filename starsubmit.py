import xml.etree.ElementTree as et
import xml.dom.minidom as md
from configparser import ConfigParser as cp
from configparser import ExtendedInterpolation
from argparse import ArgumentParser as ap

class SubmissionFile(object):
    """An object that represents an XML file for an RCF submission"""

    def __init__(self, file_name = 'submission.xml'):
        """Initialize some sensible defaults"""
        self.job = et.Element('job')
        self.command = et.SubElement(self.job, 'command')

        self.stout = et.SubElement(self.job, 'stdout')
        self.stout.set('discard', 'true')
        self.stderr = et.SubElement(self.job, 'stderr')

        self.generator = et.SubElement(self.job, 'Generator')
        self.location = et.SubElement(self.generator, 'Location')
        self.report_location = et.SubElement(self.generator, 'ReportLocation')

        self.tree = et.ElementTree(self.job)

    def create_package(self):
        """Create the package sub element"""
        self.sandbox = et.SubElement(self.job, 'SandBox')
        self.sandbox.set('installer', 'ZIP')
        self.package = et.SubElement(self.sandbox, 'Package')

    def set_location(self, location):
        """Set the attribute of the location element"""
        self.location.text = location

    def set_report_location(self, location):
        """Set the attribute of the report_location element"""
        self.report_location.text = location

    def set_stderr(self, url):
        """Set the attribute of the stderr element"""
        self.stderr.set('URL', 'file:' + url)

    def add_input(self, input_list):
        """Add an input list"""
        for inputs in input_list:
            (specifier, n_files, file_or_catalog) = inputs
            if file_or_catalog == 'f':
                URL = 'file:'
            else:
                URL = 'catalog:star.bnl.gov?'
            input_list = et.SubElement(self.job, 'input')
            input_list.set('URL', URL + specifier)
            input_list.set('nFiles', n_files)

    def add_output(self, output_list):
        """Add an output condition"""
        for output in output_list:
            (glob, to_url) = output
            element = et.SubElement(self.job, 'output')
            element.set('fromScratch', glob)
            element.set('toURL', 'file:' + to_url)

    def add_command(self, commands):
        """Add a command to the command sub-element"""
        if type(commands) is list:
            for command in commands:
                if self.command.text is None:
                    self.command.text = '\r\n\t\t' + command + '\r\n\t\t'
                else:
                    self.command.text += command + '\r\n\t\t'
        else:
            if self.command.text is None:
                self.command.text = '\r\n\t\t' + commands + '\r\n\t\t'
            else:
                self.command.text += commands + '\r\n\t\t'


    def add_package_file(self, files):
        """Add a file or files to the package"""
        try:
            self.package
        except AttributeError:
            self.create_package()

        if type(files) is list:
            for path in files:
                element = et.SubElement(self.package, 'File')
                element.text = 'file:' + path
        else:
            element = et.SubElement(self.package, 'File')
            element.text = files

    def __str__(self):
        dom = md.parseString( et.tostring(self.job) ) 
        bytes_str = dom.toprettyxml(encoding = 'utf-8')
        return bytes_str.decode('utf-8')

class Submission(object):
    """Object to represent a job submission on rcf."""

    def __init__(self, config_file):
        self.major_split = ';' # String to split up list items
        self.minor_split = ',' # String to split up tuple items with a list item
        self.subfile = SubmissionFile()

        config  = cp(interpolation=ExtendedInterpolation())
        config.optionxform = lambda option: option # Keep keys as they are
        config.read(config_file)

        self.stderr =  config['output']['stderr_path']
        self.generator_location = config['generator']['location']
        self.report_location = config['generator']['report_location']
        self.job_attributes = config['job_attributes']

        # Convert output['outputs'] from string to list of tuples
        self.output_list = []
        for pairs in config['output']['list'].split(self.major_split):
            (glob, location) = pairs.split(self.minor_split)
            self.output_list.append( (glob.strip(), location.strip()) )

        self.input_list = []
        for files in config['input']['files'].split(self.major_split):
            (specifier, n_files, file_or_catalog) = files.split(self.minor_split)
            self.input_list.append( ( specifier.strip(), 
                                      n_files.strip(), 
                                      file_or_catalog.strip()) )

        self.commands = []
        for command in config['input']['commands'].split(self.major_split):
            self.commands.append(command.strip())

        self.package_files = []
        if config.has_option('package', 'files'):
            for files in config['package']['files'].split(self.major_split):
                if len(files) >= 1:
                    self.package_files.append(files.strip())

    def make_xml(self):
        """Make an xml file"""
        self.subfile.set_location(self.generator_location)
        self.subfile.set_report_location(self.report_location)
        self.subfile.set_stderr(self.stderr)

        self.subfile.add_input(self.input_list)
        self.subfile.add_output(self.output_list)
        self.subfile.add_command(self.commands)
        if len(self.package_files) >= 1:
            self.subfile.add_package_file(self.package_files)

        for key in self.job_attributes:
            self.subfile.job.set(key, self.job_attributes[key])

    def write_xml(self, file_name = 'default.xml'):
        """Write out an xml file"""
        with open(file_name, 'w') as outfile:
            outfile.write(self.subfile.__str__())
            

if __name__ == '__main__':

    argparser = ap()
    argparser.add_argument('config_file')
    args = argparser.parse_args()

    sub = Submission(args.config_file)
    sub.make_xml()
    print(sub.subfile)

