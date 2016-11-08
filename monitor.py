import psutil
import yaml
import syslog
import click

# TODO: Refactor fromcrom to escape all messages when running from cron
# TODO: refactor suppressed_messages_from_cron
# TODO: Change click options to  work globally by passing context

@click.command()
@click.option('-c', '--config', help='Provide configuration file')
@click.option('-p', '--pid', is_flag=True, help='switch monitor to be based on PID instead of process names')
def runner_main(config, pid=False):
    try:
        config = get_configuration(config, pid)
        if isinstance(config, list):
            get_ps_list(config, pid)
        else: 
            print "Config is not a list"    
    except TypeError:
        print "ERROR: No configuration file provided for process monitor" 
        #syslog.syslog(syslog.LOG_ALERT, "ERROR: No configuration file for process monitor")

#@click.pass_context
def get_configuration(config_file, pid=False):
    try:
        if pid == True:
            with open(config_file, 'r') as ymlfile:
                configuration = yaml.load(ymlfile)

                return configuration["pid"]
        else:
            with open(config_file, 'r') as ymlfile:
                configuration = yaml.load(ymlfile)

                return configuration["processes"]
    except IOError: 
        print "No such file or directory"

def get_ps_list(array_of_process_identificators, is_pid_true):
    # Process identificator can be PID or Name
    
    array_of_processes = []
    
    #Iterating over proess list
    for proc in psutil.process_iter():
        try:
            pinfo = proc.as_dict(attrs=['pid', 'name', 'status'])
            array_of_processes.append(pinfo)            
        except psutil.NoSuchProcess:
            pass
    

    def search_in_dict_name(identificator, processes):
        return [element for element in processes if element['name'] == identificator]
     
    def search_in_dict_pid(identificator, processes):
        return [element for element in processes if element['pid'] == identificator]

    if is_pid_true:
        for element in array_of_process_identificators:
            result_of_search = search_in_dict_pid(element,array_of_processes) 
            if len(result_of_search) != 0:
                for record in result_of_search:
                    message = 'PID: {r[pid]}, NAME {r[name]}, STATUS: {r[status]} '.format(r = record)
                    
                    syslog.openlog("Python")
                    syslog.syslog(syslog.LOG_ALERT,message)
                    print "To syslog logged {}".format(message)
            else: 
                print "Processes not found"


    else:
        for element in array_of_process_identificators:
            result_of_search = search_in_dict_name(element,array_of_processes) 
            if len(result_of_search) != 0:
                for record in result_of_search:
                    message = 'PID: {r[pid]}, NAME {r[name]}, STATUS: {r[status]} '.format(r = record)
                    
                    syslog.openlog("Python")
                    syslog.syslog(syslog.LOG_ALERT,message)
                    print "To syslog logged {}".format(message)
            else: 
                print "Processes not found"


# Run script if called directly
if __name__ == "__main__":
    runner_main()