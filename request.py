import xml.etree.ElementTree as et
import xml.dom.minidom as md
from job import Job
from argparse import ArgumentParser as ap
import subprocess

class Request(object):
    """An object that represents a single scheduler request"""

    def __init__(self, job = Job()):
        """Initialize some defaults"""
        self.job = job

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
        for url, n_files in job.config['input_files']:
            input_files = et.SubElement(root, 'input')
            input_files.set('URL', url)
            input_files.set('nFiles', n_files)

        # Add output files
        for toUrl, from_scratch in job.config['output_files']:
            output_files = et.SubElement(root, 'output')
            output_files.set('toURL', toUrl)
            output_files.set('fromScratch', from_scratch)

        # Specify stdout and stderr
        stdout = et.SubElement(root, 'stdout')
        stdout.set('discard', 'true')
        stderr = et.SubElement(root, 'stderr')
        stderr.set('URL', job.config['stderr_path'])

        return root

    def make_xml(self):
        """Iterate over jobs and make and xml document out of them"""
        self.tree = self.get_job_tree(self.job)
        
    def __str__(self):
        self.make_xml()
        dom = md.parseString( et.tostring(self.tree) ) 
        bytes_str = dom.toprettyxml(encoding = 'utf-8')
        return bytes_str.decode('utf-8')


if __name__ == '__main__':

    argparser = ap()
    argparser.add_argument('config_file')
    argparser.add_argument('-f', '--file', help='Name of xml file to write to')
    argparser.add_argument('-s', '--submit',  help='Submit xml file after writing',
                            action='store_true')
    args = argparser.parse_args()

    job = Job(config_file=args.config_file)
    req = Request(job)

    if args.file:
        with open(args.file, 'w') as f:
            f.write(req.__str__())
    else:
        print(req)

    if args.submit and args.file:
        subprocess.call(['star-submit', args.file])
    elif args.submit:
        print('User invoked --submit but did not specify an xml file with --file')

