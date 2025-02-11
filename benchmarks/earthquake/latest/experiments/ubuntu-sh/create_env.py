#! /usr/bin/env python
import os
from pathlib import Path

import yaml
from cloudmesh.common.util import banner
from cloudmesh.common.util import readfile
from cloudmesh.common.util import writefile
from cloudmesh.common.console import Console

from cloudmesh.common.Shell import Shell
import glob

banner("CREATE ENV")
config = yaml.safe_load(readfile("ubuntu-config.yaml"))

for config_file in glob.glob("project/*/config.yaml"):
    print(config_file)
    directory = config_file.replace("/config.yaml", "")
    env_file = config_file.replace("config.yaml", "env.sh")
    config = yaml.safe_load(readfile(config_file))
    lines = []
    for key, value in config.items():
        if key in os.environ:
            Console.warning(f"{key} is already in env")
        else:
            print(".", end="")
        env = key.upper().replace(".", "_")
        lines.append(f"{env}={value}")
    print()
    lines = "\n".join(lines)
    writefile(env_file, lines)
    data_dir = str(Path("mlcommons-data-earthquake/data").resolve())
    os.system(f"ln -s {data_dir} {directory}")

