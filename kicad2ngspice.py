"""initialize and run Kicad cli to generate Ngspice netlist"""

import os
import subprocess
import tomllib
from pathlib import Path
from subprocess import CompletedProcess

# tell me where to find the config file
CONFIG_FILENAME = Path("/workspaces/kicad_ngspice/ki2ng.toml")

# which schematic to netlist, settings must be present in config toml file
# WHICH_SCH = "default"
WHICH_SCH = "rectifier"

# read in the config file, toml format
with open(CONFIG_FILENAME, "rb") as file:
    config = tomllib.load(file)

# set these constants from the config file
KICAD_CMD = Path(config[WHICH_SCH]["kicadCmd"])
SCH_LOCATION = Path(config[WHICH_SCH]["schematicLoc"])
SCH_FILENAME = SCH_LOCATION / config[WHICH_SCH]["schematicName"]
NETLIST_LOCATION = Path(config[WHICH_SCH]["netlistLoc"])
NETLIST_FILENAME = NETLIST_LOCATION / config[WHICH_SCH]["netlistName"]
DELETE_FORWARD_SLASHES: bool = config[WHICH_SCH]["deleteForwardSlashes"]

# kicad command uses relative paths
PROGRAM_PATH = Path(os.curdir)
SCH_FILENAME_REL = Path(os.path.relpath(SCH_FILENAME, PROGRAM_PATH))
NETLIST_FILENAME_REL = Path(os.path.relpath(NETLIST_FILENAME, PROGRAM_PATH))


class KicadNetlist:
    """KiCad cmd"""

    def __init__(
        self, kicad_cmd: Path, sch_filename: Path, netlist_filename: Path
    ) -> None:
        self.kicad_cmd: Path = kicad_cmd
        self.sch_filename: Path = sch_filename
        self.netlist_filename: Path = netlist_filename

        # construct the command
        self.cmd_args = [f"{self.kicad_cmd}"]
        self.cmd_args.append("sch")
        self.cmd_args.append("export")
        self.cmd_args.append("netlist")
        self.cmd_args.append(f"--output")
        self.cmd_args.append(f"{self.netlist_filename}")
        self.cmd_args.append("--format")
        self.cmd_args.append("spice")
        self.cmd_args.append(f"{self.sch_filename}")
        self.cmd: str = " ".join(str(item) for item in self.cmd_args)

    def __str__(self) -> str:
        """print out the constructed KiCad cmd

        Returns:
            str: the cmd that has been contructed
        """
        return self.cmd

    def run(self) -> CompletedProcess[bytes]:
        """execute the kicad cmd"""
        return subprocess.run(self.cmd_args, check=False)

    def delete_forward_slashes(self) -> None:
        """Delete forward slashes from all node names in the netlist file."""

        # Open the file for reading and writing
        with open(self.netlist_filename, "r+") as file:
            lines = file.readlines()  # Read the lines
            file.seek(0)  # Move the file pointer back to the beginning

            # Iterate through each line
            for line in lines:
                # Check if the line starts with a letter
                if line[0].isalpha():
                    # Split the line into words
                    words = line.split()
                    # Remove the forward slash from each word that starts with it
                    words = [
                        word[1:] if word.startswith("/") else word for word in words
                    ]
                    # Join the words back together into a line
                    line = " ".join(words) + "\n"
                # Write the modified line back to the file
                file.write(line)

            # Truncate the file to the current position to remove any leftover content
            file.truncate()


def main() -> None:
    """main"""

    # construct the kicad cmd
    my_kicadcmd = KicadNetlist(KICAD_CMD, SCH_FILENAME_REL, NETLIST_FILENAME_REL)
    print(my_kicadcmd)  # print out the kicad cmd, though not necessary

    my_kicadcmd.run()  # run the kicad cmd
    if DELETE_FORWARD_SLASHES:
        my_kicadcmd.delete_forward_slashes()  # delete forward slashes in node names


if __name__ == "__main__":
    main()
