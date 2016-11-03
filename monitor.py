import psutil

def get_ps_list():
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

    print search_in_dict('launchd',array_of_processes)
    
# Run script if called directly
if __name__ == "__main__":
    get_ps_list()