from importlib.metadata import version

import toml

pyproject_path = "pyproject.toml"
package_remote_version = version("tickthon")

with open(pyproject_path, 'r') as file:
    pyproject_data = toml.load(file)

package_local_version = pyproject_data["project"]["version"]

package_remote_version_split = package_remote_version.split(".")
package_local_version_split = package_local_version.split(".")

package_version = package_local_version
if (package_remote_version_split[0] == package_local_version_split[0]) and \
        (package_remote_version_split[1] == package_local_version_split[1]):
    package_remote_version_split[2] = str(int(package_remote_version_split[2]) + 1)
    package_version = ".".join(package_remote_version_split)

pyproject_data["project"]["version"] = package_version

with open(pyproject_path, 'w') as file:
    toml.dump(pyproject_data, file)
