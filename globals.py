# -*- coding:utf-8 -*-

import os
from misc.genconfig import GenConfig


class GlobalConfig(GenConfig):
    """全局配置解析"""
    _global_cfg_ = os.path.join(os.environ.get('HOME'), '.winning', 'global')

    def __init__(self):
        GenConfig.__init__(self, self._global_cfg_)

    def get_config_dir(self):
        return os.path.dirname(self._global_cfg_)

    def get_work_dir(self):
        return self.getSecOption('globals', 'work_dir')

    def get_test_data_dir(self):
        return self.getSecOption('globals', 'test_data_dir')

    def get_log_dir(self):
        return self.getSecOption('globals', 'log_dir')
