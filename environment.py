import os
from io import StringIO

import consul
import requests
import yaml


def getProfileSuffix(profile: str):
    if profile is None or len(profile) < 1 or profile.lower() == 'production':
        return ''
    if profile.lower() == 'development':
        return ',dev'
    return ',' + profile.lower()

def deepMerge(dict1: dict, dict2: dict):
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deepMerge(result[key], value)
        else:
            result[key] = value
    return result

class Environment:

    def __init__(self, name: str):
        try:
            self.profile = getProfileSuffix(os.environ['PYTHON_PROFILE'])
        except KeyError:
            self.profile = ''
        self.values = None
        self.consul = None
        self.name = name

    def __getConsul(self):
        if self.consul is None:
            try:
                consulPort = os.environ['CONSUL_PORT']
            except KeyError:
                consulPort = 8500
            try:
                consulHost = os.environ['CONSUL_HOST']
            except KeyError:
                consulHost = 'consul'
            self.consul = consul.Consul(host=consulHost, port=consulPort, scheme='http')
        return self.consul

    def __getProfileConsul(self, source):
        consulPath = 'config/' + source + "/data"
        try:
            result = self.__getConsul().kv.get(consulPath)
            if result is None or result[1] is None:
                return None
            return result[1]['Value']
        except requests.exceptions.ConnectionError:
            print("Consul connection error ")
            return None

    def __getConfigFileName(self, fileName):
        if len(self.profile) > 0:
            fileName = fileName + self.profile
        return fileName.replace(',', '_') + ".yaml"

    def __mergeConsulValues(self, source):
        try:
            if self.values is None:
                self.values = yaml.safe_load(source)
            elif source is not None:
                self.values = deepMerge(self.values, yaml.safe_load(source))
        except yaml.YAMLError as e:
            print(f"Error parsing YAML file: {e}")

    def __mergeFileValues(self, source):
        try:
            with open(source, 'r') as file:
                if self.values is None:
                    self.values = yaml.safe_load(file)
                else:
                    values = yaml.safe_load(file)
                    for key, value in values.items():
                        self.values[key] = value
        except FileNotFoundError:
            pass

    def __process_config(self, name):
        try:
            consulConfig = self.__getProfileConsul(name)
            if consulConfig is None:
                self.__mergeFileValues(name + '.yaml')
                if len(self.profile) > 0:
                    self.__mergeFileValues(self.__getConfigFileName(name))
            else:
                self.__mergeConsulValues(consulConfig)
                if len(self.profile) > 0:
                    self.__mergeConsulValues(self.__getProfileConsul(name + self.profile))
        except yaml.YAMLError as e:
            print(f"Error parsing YAML file: {e}")

    def __getValues(self):
        if self.values is None:
            self.__process_config('application')
            self.__process_config(self.name)
        return self.values

    def get(self, name: str, defaultValue = None):
        i = 1
        try:
            path = name.split('.')
            if self.__getValues() is None:
                return defaultValue
            result = self.__getValues()[path[0]]
            while i < len(path):
                if result is None:
                    return defaultValue
                result = result[path[i]]
                i = i + 1
            return result
        except KeyError:
            return defaultValue

    def __saveValues(self):
        stringToSave = StringIO()
        yaml.dump(self.__getValues(), stringToSave, default_flow_style = False)
        consulPath = 'config/' + self.name + self.profile + "/data"
        try:
            self.__getConsul().kv.put(consulPath, stringToSave.getvalue())
        except requests.exceptions.ConnectionError:
            with open(self.__getConfigFileName(self.name), 'w') as file:
                file.write(stringToSave.getvalue())

    def set(self, name: str, value):
        path = name.split('.')
        item = self.__getValues()
        if item is None:
            item = {}
            self.values = item
        for i in range(len(path) - 1):
            element = item[path[i]]
            if element is None:
                element = {}
                item[path[i]] = element
            item = element
        item[path[len(path) - 1]] = value
        self.__saveValues()
