from boto import connect_rds, connect_ec2, connect_elb
# This feels incredibly ugly to have 3 (!!) RegionInfo imports
from boto.rds.regioninfo import RDSRegionInfo
from boto.ec2.regioninfo import RegionInfo as EC2RegionInfo
from boto.regioninfo import RegionInfo

from woolpack import import_settings


class ELBItem(object):
    """
    Represents an ELB within AWS.

    isnt = ELBItem(id='test-elb',
        env_type='prod',
        availability_zones=['eu-west-1'],
        listeners=[(80, 80, 'http')])
    inst.build()

    Get rid of the instance by calling:
    inst.destroy()

    """
    _connection = None

    def __init__(self, id, env_type, availability_zones, listeners):
        self.settings = import_settings(env_type)
        self.instance = None
        # I don't like the redefinition of credentials on each class.
        self._credentials = {
            "aws_access_key_id": self.settings['AWS_ACCESS_KEY_ID'],
            "aws_secret_access_key": self.settings['AWS_SECRET_ACCESS_KEY'],
            "region": RegionInfo(
                name=self.settings['AWS_REGION'],
                endpoint=self.settings['ELB_ENDPOINT'],
        )}
        # No VPC support yet.
        self.creation_data = {
            'name': id,  # I hate the inconsistency here.
            'zones': availability_zones,
            'listeners': listeners,
        }
        self.created = bool(self.instance)

    def add_health_check(self, health_check):
        """
        Configures the health check for the load balancer.

        :params:
            health_check: Expects a boto.HealthCheck instance.
        """
        self.instance.configure_health_check(health_check)

    def register_ec2_instances(self, ec2_instances):
        """
        Registers ec2 instances with itself.

        :params:
            ec2_instances: A list of ec2 instance ids.
        """
        self.instance.register_instances(ec2_instances)

    def deregister_ec2_instances(self, ec2_instances):
        self.instance.deregister_instances(ec2_instances)

    def connect(self):
        if self._connection is None:
            self._connection = connect_elb(**self._credentials)
        return self._connection

    def build(self):
        instance = self.connect().create_load_balancer(**self.creation_data)
        self.instance = instance
        return self.instance

    def destroy(self):
        """ Remove this load balancer. """
        self.instance.delete()
        self.instance = None


class EC2Item(object):

    _connection = None

    def __init__(self, image_id, key_name,
        instance_class, availability_zone, security_groups=None,
        user_data='', id=None, env_type=None, tags={}):
        self.settings = import_settings(env_type)
        self._credentials = {
            "aws_access_key_id": self.settings['AWS_ACCESS_KEY_ID'],
            "aws_secret_access_key": self.settings['AWS_SECRET_ACCESS_KEY'],
            "region": EC2RegionInfo(
                name=self.settings['AWS_REGION'],
                endpoint=self.settings['EC2_ENDPOINT'],
        )}
        self.creation_data = {
            'image_id': image_id,
            'key_name': key_name,
            'security_groups': security_groups,
            'user_data': user_data,
            'instance_type': instance_class,
            'placement': availability_zone
        }
        self.name = id
        self.instance = None
        self.tags = tags
        self.created = bool(self.instance)

    def __str__(self):
        return '<{0}:{1}>'.format(
            self.name,
            self.creation_data['instance_type']
        )

    __repr__ = __str__

    def connect(self):
        """ Creates an EC2Connection. """
        if self._connection is None:
            self._connection = connect_ec2(**self._credentials)
        return self._connection

    def build(self):
        """ Creates an EC2 instance. """
        reservation = self.connect().run_instances(**self.creation_data)
        # We're only creating one instance with this method, so we
        # just grab the first instance out of the Reservation object
        # instances list.
        self.instance = reservation.instances[0]
        # If you've specified a name then add it to the instance.
        if self.name:
            self.instance.add_tag('Name', self.name)
        # Add custom tags to the instance
        for key, value in self.tags.items():
            self.instance.add_tag(key, value)
        self.created = True
        return self.instance

    def destroy(self):
        """ Terminates an EC2 instance. """
        self.instance.terminate()
        self.instance = None


class RDSItem(object):

    INSTANCE_SIZES = {
        'small': 'db.m1.small',
        'large': 'db.m1.large',
    }
    _connection = None

    def __init__(self, id, allocated_storage, instance_class,
        master_username, master_password, env_type,
        instance_type=None, port=3306, engine='MySQL5.1',
        db_name=None, param_group=None, security_groups=None,
        availability_zone=None, preferred_maintenance_window=None,
        backup_retention_period=None, preferred_backup_window=None,
        multi_az=False, engine_version=None, auto_minor_version_upgrade=True):
        self.settings = import_settings(env_type)
        self._credentials = {
            "aws_access_key_id": self.settings['AWS_ACCESS_KEY_ID'],
            "aws_secret_access_key": self.settings['AWS_SECRET_ACCESS_KEY'],
            "region": RDSRegionInfo(
                name=self.settings['AWS_REGION'],
                endpoint=self.settings['RDS_ENDPOINT'],
        )}
        self.creation_data = {
            'id': id,
            'allocated_storage': allocated_storage,
            'instance_class': self.INSTANCE_SIZES[instance_class],
            'engine': engine,
            'master_username': master_username,
            'master_password': master_password,
            'port': port,
            'db_name': db_name,
            'param_group': param_group,
            'security_groups': security_groups,
            'availability_zone': availability_zone,
            'preferred_maintenance_window': preferred_maintenance_window,
            'backup_retention_period': backup_retention_period,
            'preferred_backup_window': preferred_backup_window,
            'multi_az': multi_az,
            'engine_version': engine_version,
            'auto_minor_version_upgrade': auto_minor_version_upgrade,
        }
        self.instance = None
        self.created = bool(self.instance)
        self.instance_type = instance_type

    def __str__(self):
        return '<{0}:{1}>'.format(
            self.creation_data['id'],
            self.instance_type
        )

    __repr__ = __str__

    def connect(self):
        """ Creates an RDSConnection instance. """
        if self._connection is None:
            self._connection = connect_rds(**self._credentials)
        return self._connection

    def build(self):
        """ Creates an rds instance. """
        self.instance = self._connect().create_dbinstance(**self.creation_data)
        self.created = True
        return self.instance

    def destroy(self):
        """ Terminates an rds instance """
        # Should allow you to specify that you don't want a final
        # snapshot to be taken.
        self.instance.stop()
        self.instance = None
