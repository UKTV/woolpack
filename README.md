woolpack
========

Allows you to build up stacks in the cloud (AWS for now)

Creating an EC2 instance:

```python
from woolpack.items import EC2Item

item1 = EC2Item(image_id='ami-edc6fe99',
    key_name='key',
    instance_class='t1.micro',
    availability_zone='eu-west-1a',
    security_groups=['web_server'],
    id='minilnk-test',
    env_type='prod',
    tags={
        'app': 'test-appserver-1',
        'type': 'prod'
    })
item1.build() # Creates the instance and then attaches it to .instance.
item1.instance.id # Returns the unique ID associated with your instance.
```

You can also create an Elastic Load Balancer and associate it with the
instance:

```python
from boto.ec2.elb import HealthCheck
from woolpack.items import ELBItem

elb_item1 = ELBItem(id='test-elb',
    env_type='prod',
    availability_zones=['eu-west-1'],
    listeners=[(80, 80, 'http')])
elb_item1.build()

hc = HealthCheck(
    interval=20,
    healthy_threshold=3,
    unhealthy_threshold=5,
    target='HTTP:80/')

elb_item1.configure_health_check(hc)
elb_item1.register_ec2_instances([item1.instance.id])
```

Now you have an EC2 instance successfully configured through a load balancer.

If you'd like to throw an RDS instance into the mix, you can do it like so:

```python
from woolpack.items import RDSItem

rds_item1 = RDSItem(id='testrds1',
	allocated_storage=20,
	instance_class='db.m1.small',
	master_username='woot',
	master_password='woot',
	env_type='prod',
	security_groups=['default'],
	param_group=['prod'])

rds_item1.build()
```
