import ConfigParser
from ConfigParser import NoOptionError, NoSectionError

from pyrevit import PyRevitException, PyRevitIOError

# noinspection PyUnresolvedReferences
from System.IO import IOException


KEY_VALUE_TRUE = "true"
KEY_VALUE_FALSE = "false"


class PyRevitConfigSectionParser(object):
    def __init__(self, config_parser, section_name):
        self._parser = config_parser
        self._section_name = section_name

    def __iter__(self):
        return self._parser.options(self._section_name)

    def __repr__(self):
        return '<PyRevitConfigSectionParser object at 0x{0:016x} config section \'{1}\'>'.format(id(self),
                                                                                                 self._section_name)

    def __getattr__(self, param_name):
        try:
            value = self._parser.get(self._section_name, param_name)
            try:
                # cleanup true, false values to eval statement
                if value.lower() == KEY_VALUE_TRUE:
                    value = 'True'
                elif value.lower() == KEY_VALUE_FALSE:
                    value = 'False'

                return eval(value)
            except:
                return value
        except (NoOptionError, NoSectionError):
            raise AttributeError('Parameter does not exist in config file.')

    def __setattr__(self, param_name, value):
        if param_name in ['_parser', '_section_name']:
            super(PyRevitConfigSectionParser, self).__setattr__(param_name, value)
        else:
            try:
                return self._parser.set(self._section_name, param_name, str(value))
            except Exception as set_err:
                raise PyRevitException('Error setting parameter value. | {}'.format(set_err))

    def get_option(self, op_name, default_value=None):
        try:
            return self.__getattr__(op_name)
        except Exception as opt_get_err:
            if default_value != None:
                self.__setattr__(op_name, default_value)
                return default_value
            else:
                raise opt_get_err


class PyRevitConfigParser(object):
    def __init__(self, cfg_file_path=None):
        self._parser = ConfigParser.ConfigParser()
        if cfg_file_path is not None:
            try:
                with open(cfg_file_path, 'r') as cfg_file:
                    self._parser.readfp(cfg_file)
            except (OSError, IOError):
                raise PyRevitIOError()
            except Exception as read_err:
                raise PyRevitException(read_err)

    def __getattr__(self, section_name):
        if self._parser.has_section(section_name):
            return PyRevitConfigSectionParser(self._parser, section_name)
        else:
            raise AttributeError('Section does not exist in config file.')

    def add_section(self, section_name):
        self._parser.add_section(section_name)
        return PyRevitConfigSectionParser(self._parser, section_name)

    def get_section(self, section_name):
        if self._parser.has_section(section_name):
            return PyRevitConfigSectionParser(self._parser, section_name)
        else:
            raise AttributeError('Section does not exist in config file.')

    def remove_section(self, section_name):
        self._parser.remove_section(section_name)
        return PyRevitConfigSectionParser(self._parser, section_name)

    def reload(self, cfg_file_path):
        try:
            with open(cfg_file_path, 'r') as cfg_file:
                self._parser.readfp(cfg_file)
        except (OSError, IOError):
            raise PyRevitIOError()

    def save(self, cfg_file_path):
        try:
            with open(cfg_file_path, 'w') as cfg_file:
                self._parser.write(cfg_file)
        except (OSError, IOError):
            raise PyRevitIOError()
