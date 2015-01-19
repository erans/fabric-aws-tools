# The MIT License (MIT)
#
# Copyright (c) 2015 Eran Sandler
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import absolute_import
import os
try:
    import simplejson as json
except ImportError:
    import json

from boto import ec2
from fabric.api import env

def _get_environment_value(key):
    if key is None:
        raise ValueError("key must be set")

    if key in os.environ: return os.environ[key]
    if key in env: return env[key]

    return None

def update_roles_aws(tag, tag_value=None, aws_access_key_id=None, aws_secret_access_key=None, ip_address_field_to_return="public_dns_name"):
    """
    Dynamically update fabric's roles by using the specified tag that was used
    to tag each EC2 instance.

    - Setting tag to '__all__' will return ALL instances.

    - Setting only tag without tag_value will return all instance who has that tag.
      The role name in Fabric will be the value of the tag as specified on the instance.

    - Setting tag and tag_value will return all instances who has that tag and its value
      equals tag_value. The Fabric role will be set to tag_value

    AWS access key and secret access key can be specified as parameters to this
    function or can be set using the environment variables
    AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY.

    If you are using IAM roles, simply pass None (or nothing at all) and make sure
    that the environment variables are not set.

    If you wish to return the internal IP address (for example, when using VPC),
    set the ip_address_field_to_return to "private_dns_name" or "private_ip_address"
    """

    if tag is None:
        raise ValueError("tag must be set")

    if aws_access_key_id is None:
        aws_access_key_id = _get_environment_value("AWS_ACCESS_KEY_ID")

    if aws_secret_access_key is None:
        aws_secret_access_key = _get_environment_value("AWS_SECRET_ACCESS_KEY")

    ec2_connection = ec2.connection.EC2Connection(aws_access_key_id, aws_secret_access_key)

    if tag == "__all__":
        filters = None
    else:
        if tag_value is not None:
            filters = { "tag:{0}".format(tag) : tag_value }
        else:
            filters = { "tag-key" : tag }

    reservations = ec2_connection.get_all_instances(filters=filters)
    instances = [i for r in reservations for i in r.instances]

    roles = {}
    role_name = "__all__" if tag == "__all__" else None

    for i in instances:
        # add only running instances. No point in running remote commands if it not running!
        if i.state == "running":
            # Trick to access the IP address field by name instead
            # of using the hardwired property
            ip_address = i.__dict__[ip_address_field_to_return]

            if tag != "__all__":
                role_name = i.tags[tag]

            if not role_name in roles:
                roles[role_name] = []

            roles[role_name].append(ip_address)

    if tag == "__all__":
        # In the case of using __all__. We add all instances to the hosts
        # collection so it won't be related to a specific role.
        env.hosts = roles["__all__"] if len(roles) > 0 else None
    else:
        env.roledefs.update(roles)


__all__ = ["update_roles_aws"]
