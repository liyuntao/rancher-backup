#!/usr/bin/python
import os
import re
import sys
import time
import yaml
from rancher_metadata import MetadataAPI

__author__ = 'Disaster <linuxworkgroup@hotmail.com>'



class ServiceRun():


    def run(self):

        list_services = self._get_link_services()
        settings = self._get_settings()
        self._run_backup_container(list_services, settings)


    def _get_link_services(self):
        """
        Permit to get all info needed to backup all linked services
        """

        metadata_manager = MetadataAPI()
        list_services = metadata_manager.get_service_links()
        list_containers = []
        for service in list_services:
            container = {}
            container['service_name'] = list_services[service]
            container['service_name_env'] = list_services[service].upper().replace('-', '_')
            container['service_path'] = service
            list_containers.append(container)


        return list_containers


    def _get_settings(self):
        """
        Permit to load setting from setting.yml file
        """
        return yaml.load(open('setting.yml'))

    def _replace_macro_env(self, service, setting):

        list_env = {}

        for env in setting["environment"]:
            regex_env = re.search('^([^:]+):(.*)$', env)
            if regex_env:
                list_env[regex_env.group(1)] = regex_env.group(2).replace('%service_name_env%', service['service_name_env']).replace('%service_name%', service['service_name']).replace('%service_path%', service['service_path'])
                print("Key : %s, value : %s" % (regex_env.group(1), list_env[regex_env.group(1)]))

        return list_env


    def _run_backup_container(self, list_services, settings):
        """
        Permit to run docker container to try to backup linked services
        """

        for service in list_services:
            for key, value in settings.items():
                if re.search(value['regex'], service['service_name']):
                    print("Linked container found to backup it -> %s" % service["service_path"])
                    list_env = self._replace_macro_env(service, value)

                    command = "docker run --rm"
                    for env, env_value in list_env.items():
                        command += " -e '%s:%s'" % (env, os.getenv(env_value, env_value))
                    command  += " %s" % value['image']

                    os.system("docker pull %s" % value['image'])
                    print("Command : %s", command)



if __name__ == '__main__':
    # Start


    service = ServiceRun()
    service.run()