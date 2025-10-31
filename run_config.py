"""
Open and read the CES config file
================================

"""
import yaml

def open_config():
    try:
        with open('config.yaml', 'r') as config_stream:
            config_data = yaml.safe_load(config_stream)
        return config_data
    except:
        print("No config file found!")
        return None

def main():
    config_data = open_config()
    print(config_data)

if __name__ == '__main__':
    main()