import xml.etree.ElementTree as et
import xml.dom.minidom as md
from job import Job

class Request(object):
    """An object that represents a single scheduler request"""

    def __init__(self, jobs = []):
        """Initialize some defaults"""
        self.jobs = []
        if isinstance(jobs, Job):
            self.jobs.append( jobs )
        elif isinstance(jobs, list):
            for job in jobs:
                if isinstance(job, Job):
                    self.jobs.append(job)

    def get_job_tree(self, job):
        """Turn a Job object into an xml element tree"""
        # The root of the job element tree
        root = et.Element('job')
        for attribute, value in job.config['attributes'].items():
            root.set(attribute, value)

        # Add commands
        commands = et.SubElement(root, 'command')
        commands.text = ''
        for com in job.config['commands']:
            commands.text += '\r\n\t\t' + com
        commands.text += '\r\n\t'

        # Add Generator stuff
        generator = et.SubElement(root, 'Generator')
        generator_location = et.SubElement(generator, 'Location')
        generator_location.text = job.config['generator_location']
        generator_report_location = et.SubElement(generator, 'ReportLocation')
        generator_report_location.text = job.config['generator_report_location']

        # Add Sandbox stuff
        sandbox = et.SubElement(root, 'Sandbox')
        sandbox.set('installer', job.config['sandbox_installer_option'])
        sandbox_package = et.SubElement(sandbox, 'Package')
        sandbox_package.set('name', job.config['sandbox_package_name'])
        for f in job.config['sandbox_files']:
            sandbox_files = et.SubElement(sandbox_package, 'File')
            sandbox_files.text = f

        # Add input files
        for f in job.config['input_files']:
            input_files = et.SubElement(root, 'input')
            input_files.set('URL', f)

        # Add output files
        for f in job.config['output_files']:
            output_files = et.SubElement(root, 'output')
            output_files.set('toURL', f)

        return root

    def make_xml(self):
        """Iterate over jobs and make and xml document out of them"""
        for job in self.jobs:
            self.tree = self.get_job_tree(job)
        
    def __str__(self):
        self.make_xml()
        dom = md.parseString( et.tostring(self.tree) ) 
        bytes_str = dom.toprettyxml(encoding = 'utf-8')
        return bytes_str.decode('utf-8')


