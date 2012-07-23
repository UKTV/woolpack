# Make sure you put your settings in either ~/woolpack_config.py or
# /etc/woolpack/woolpack_config.py

settings = {
    'dev': {
        'AWS_ACCESS_KEY_ID': '',
        'AWS_SECRET_ACCESS_KEY': '',
        'AWS_USER_ID': None,
        'AWS_REGION': 'eu-west-1',
        'EC2_ENDPOINT': 'eu-west-1.ec2.amazonaws.com',
        'RDS_ENDPOINT': 'rds.eu-west-1.amazonaws.com',
        'ELB_ENDPOINT': 'elasticloadbalancing.eu-west-1.amazonaws.com',
    },
    'prod': {
        'AWS_ACCESS_KEY_ID': '',
        'AWS_SECRET_ACCESS_KEY': '',
        'AWS_USER_ID': None,
        'AWS_REGION': 'eu-west-1',
        'EC2_ENDPOINT': 'eu-west-1.ec2.amazonaws.com',
        'RDS_ENDPOINT': 'rds.eu-west-1.amazonaws.com',
        'ELB_ENDPOINT': 'elasticloadbalancing.eu-west-1.amazonaws.com',
    },
}