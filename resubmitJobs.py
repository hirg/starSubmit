import re
import argparse
import subprocess

def n_jobs(session_file):
    """ Reads a session file and returns the number of jobs described in it """

    job_index_match = (r'\<void property=\"jobIndex\"\>\n' +
                   r'\s*\<int\>(\d+)\</int\>')
    with open(session_file, 'r') as f:
        session_text = f.read()
        matches = re.findall(job_index_match, session_text)
        return len(matches) + 1 # jobIndex zero is not explicitly defined
                                # in the xml file, so the regex match
                                # misses it. We add it in manually

def log_directory(session_file):
    """ Finds the directory where *.condor.log files are kept """
    directory_match = (r'\<void property\=\"listLocation\"\>\n' +
                       r'\s*\<string\>(.*)\</string\>' )
    with open(session_file, 'r') as f:
        session_text = f.read()
        directory = re.search(directory_match, session_text).group(1)

    return directory

def session_id(the_string):
    """ Searches a string for a valid session id and returns it """
    session_match = '[0-9A-F]{32}'
    match = re.search(session_match, the_string).group(0)
    return match

def log_file(log_directory, session_id, job_index):
    """ Return a log file name corresponding to function arguments """

    file_name = '{}/sched{}_{}.condor.log'.format(log_directory,
                                                  session_id, job_index)

    return file_name

def output_dir(session_file):
    """ Scans a session file to determine where it puts its output """

    directory_match = ( 
             r'\<void property="fromScratch"\>\n' + 
             r'\s*\<string\>\*\.root\</string\>\n' +
             r'\s*\</void\>\n' + 
             r'\s*\<void property="toURLString"\>\n' + 
             r'\s*\<string\>file:(.*)</string\>'
                    )
    with open(session_file, 'r') as f:
        session_text = f.read()
        directory = re.search(directory_match, session_text).group(1)

    return directory

def has_output(directory, job_id):
    """ Looks for output in the form *[jobId]*.root """
    glob = '{}*{}*.root'.format(directory, job_id)
    return_code = subprocess.call(['ls {}'.format(glob)], shell=True,
                            stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    if return_code == 0:
        return True
    else:
        return False

def was_evicted(log_file):
    """ Examines a log file to determine whether a job was evicted """

    fail_line = -1
    terminate_line = -1
    abort_match = 'Job was aborted by the user'
    terminate_match = 'Job terminated'

    with open(log_file, 'r') as f:
        log_text = f.read()

        for i, line in enumerate(log_text.splitlines()):
            if re.search(abort_match, line):
                fail_line = i
            elif re.search(terminate_match, line):
                terminate_line = i

    # If we didn't find any mentions of evictions or terminations,
    # that's bad
    if fail_line == terminate_line == -1:
        error_string = 'Found no mention of evictions or terminations in log: '
        error_string += log_file
        raise AttributeError(error_string)
    elif terminate_line > fail_line:
        return False
    elif terminate_line < fail_line:
        return True
    else:
        raise Exception('Could not determine if job was evicted: ' + log_file)

def resubmit_jobs(session_file, jobs):
    """Given a session file and list of job indices, resubmit those jobs"""
    job_index_string = ''
    for job in jobs:
        job_index_string += '{}, '.format(job)

    job_index_string = job_index_string[:-2]

    resubmit_string = 'star-submit -r {} {}'.format(job_index_string, session_file)
    subprocess.call([resubmit_string], shell=True)
    # print(resubmit_string)
        

# Main portion of script
parser = argparse.ArgumentParser()
parser.add_argument('files', nargs='+', help='A list of files to scan')
parser.add_argument('-r', '--resubmit',  help='Do the resubmission (Default off)',
                    action='store_true')
args = parser.parse_args()

n_failed = 0
resubmit_dict = {}
for f in args.files:
    evicted_jobs = []
    for job_index in range(0, n_jobs(f)):
        job_id = '{}_{}'.format(session_id(f), job_index)
        log = log_file(log_directory(f), session_id(f), job_index)
        if was_evicted(log) or not has_output(output_dir(f), job_id):
            evicted_jobs.append(job_index)
            n_failed += 1

    if evicted_jobs:
        output_str = 'Session {} found {} job(s) for resubmission: {}'
        output_str = output_str.format(session_id(f), len(evicted_jobs), str(evicted_jobs))
        print(output_str)
        resubmit_dict[f] = evicted_jobs

print( 'Found {} failed jobs.'.format(n_failed))

if args.resubmit:
    confirm = input('Are you sure you want to resubmit these jobs? (y/n): ')
    proceed = (confirm == 'y') or (confirm == 'yes')

    if proceed:
        for session, job_index in resubmit_dict.items():
            resubmit_jobs(session, job_index)
    else:
        print('Quitting without resubmitting.')
else:
    output_str = 'Quitting without resubmitting. '
    output_str += 'Invoke with -r if you want to resubmit.'
    print(output_str)
