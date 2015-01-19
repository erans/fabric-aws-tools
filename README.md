# fabric-aws-tools - Tools to integrate Fabric with Amazon Web Services (AWS)

Tools to better integrate Fabric with Amazon Web Services (AWS)

- Automagically assign Fabric roles based on tags set on EC2 instances. For example, deploy code only to web servers (see example below)

## Installation
* `pip install fabric-aws-tools`

## Example fabfile
```python
from fabric.api import *
from fabric_aws_tools import *

@roles("webserver")
def deploy_webserver():
    run("do something")

    
# Runs every time you run "fab something".
# Add it at the end of the file to make sure it runs each time.
#
# This will set the Fabric roles to all values available on all
# instances who has the tag "Role"
update_roles_aws("Role")
```
