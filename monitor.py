import psutil
import yaml
import syslog
import click

# TODO: Refactor fromcrom to escape all messages when running from cron
# TODO: refactor suppressed_messages_from_cron
# TODO: Change click options to  work globally by passing context

@click.command()
@click.option('-c', '--config', help='Provide configuration file')
@click.option('--fromcron', is_flag=True, help="Silence stdout")
def runner_main(config,fromcron):
    
    try:
        config = get_configuration(config)
        
        if isinstance(config, list):
            get_ps_list(config)
        else: 
            print "Config is not a list"    
    except TypeError:
        suppressed_message_from_cron("ERROR: No configuration file provided for process monitor",fromcron)
        syslog.syslog(syslog.LOG_ALERT, "ERROR: No configuration file for process monitor")

def get_configuration(config_file):
    try:
        with open(config_file, 'r') as ymlfile:
            configuration = yaml.load(ymlfile)

        return configuration["processes"]

    except IOError: 
        suppressed_message_from_cron ("No such file or directory",fromcron)

def get_ps_list(array_of_process_names):
    # call class process
    array_of_processes = []
    
    
    #Iterating over proess list
    for proc in psutil.process_iter():
        try:
            pinfo = proc.as_dict(attrs=['pid', 'name', 'status'])
            array_of_processes.append(pinfo)            
        except psutil.NoSuchProcess:
            pass
    

    def search_in_dict(name, processes):
        return [element for element in processes if element['name'] == name]

    for element in array_of_process_names:
        result_of_search = search_in_dict(element,array_of_processes) 
        if len(result_of_search) != 0:
            for record in result_of_search:
                message = 'PID: {r[pid]}, NAME {r[name]}, STATUS: {r[status]} '.format(r = record)
                syslog.openlog("Python")
                syslog.syslog(syslog.LOG_ALERT,message)
                suppressed_message_from_cron("To syslog logged {}".format(message),fromcron)
        else: 
            suppressed_message_from_cron("Process not found",fromcron)
            suppressed_message_from_cron("EXITING",fromcron)

def suppressed_message_from_cron(message,fromcron):
    if fromcron == False:
        print message
    else:
        pass


# Run script if called directly
if __name__ == "__main__":
    runner_main()