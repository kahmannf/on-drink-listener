import json, os, inspect

def get_config():

    server_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

    config_file_name = os.path.join(server_dir,'server_config.json')

    config_file = open(config_file_name, 'rU')

    server_config = json.load(config_file)

    return server_config
