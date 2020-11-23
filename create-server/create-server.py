import boto3
import csv
import pprint
from yaml import load, dump
from yaml import Loader, Dumper

print("Starting Fetch test to create servers")

pp = pprint.PrettyPrinter(indent=2)

def retreive_credentials():
    with open('/Users/jasonfaas/Downloads/new_user_credentials.csv', mode='r') as file:
        csv_file = csv.reader(file)
        csv_lines = []
        for line in csv_file:
            csv_lines.append(line)
        credentials = {
            'id': csv_lines[1][2],
            'secret': csv_lines[1][3],
        }
    return credentials

def create_boto_ec2_client(credentials):
    ec2_client = boto3.client(
        'ec2',
        region_name='us-west-1',
        aws_access_key_id=credentials['id'],
        aws_secret_access_key=credentials['secret'],
    )
    return ec2_client

def create_boto_ec2_resource(credentials):
    ec2_client = boto3.resource(
        'ec2',
        region_name='us-west-1',
        aws_access_key_id=credentials['id'],
        aws_secret_access_key=credentials['secret'],
    )
    return ec2_client

def print_current_instance_count(ec2_client):
    response = ec2_client.describe_instances()
    pp.pprint(response)
    instance_count = 0
    for reserv in response['Reservations']:
        instance_count += len(reserv['Instances'])
    print("Current Instance Count: {}".format(instance_count))


credentials = retreive_credentials()
ec2_client = create_boto_ec2_client(credentials)
print_current_instance_count(ec2_client)

with open('create-server/complicated_server_specifications.yml') as stream:
    yaml_server_spec = load(stream, Loader=Loader)
    # pp.pprint(data)
server_spec = yaml_server_spec['server']

try:
    ec2_resource = create_boto_ec2_resource(credentials)

    create_instance_dict = {}
    create_instance_dict['ImageId'] = server_spec['ami_type']
    create_instance_dict['MinCount'] = server_spec['min_count']
    create_instance_dict['MaxCount']= server_spec['max_count']
    create_instance_dict['InstanceType'] = server_spec['instance_type']

    if 'root_device_type' in server_spec and 'volumes' in server_spec:
        create_instance_dict['BlockDeviceMappings'] = []
        for vol in server_spec['volumes']:
            block_map = {
                'DeviceName': vol['device'],
                'Ebs': {
                    'VolumeSize': vol['size_gb'],
                    'VolumeType': vol['type'],
                }
            }
            if vol['type'] not in ['standard', 'gp2', 'sc1', 'st1']:
                block_map['Ebs']['Iops'] = 100
            create_instance_dict['BlockDeviceMappings'].append(block_map)

    ec2_resource.create_instances(
        **create_instance_dict
    )
    # Note unused variables
    # # architecture
    # # virtualization_type

    # Note not yet used variables
    # # root_device_type
    # # volume -> mount
except KeyError as e:
    print("Invalid key reference\n{}".format(e))
    exit(0)

print_current_instance_count(ec2_client)


# TODO: Create ec2 instance in us-west-1 {instance_type: t2.micro, ami_type: amzn2, architecture: x86_64, etc}

# TODO: Write more TODOs
