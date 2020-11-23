import boto3
import csv
import pprint
from yaml import load, Loader

print("Starting Fetch test to create servers")

pp = pprint.PrettyPrinter(indent=2)

debug_print = True


def retrieve_credentials():
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
    client = boto3.client(
        'ec2',
        region_name='us-west-1',
        aws_access_key_id=credentials['id'],
        aws_secret_access_key=credentials['secret'],
    )
    return client


def create_boto_ec2_resource(credentials):
    resource = boto3.resource(
        'ec2',
        region_name='us-west-1',
        aws_access_key_id=credentials['id'],
        aws_secret_access_key=credentials['secret'],
    )
    return resource


def print_current_instance_count(client):
    response = client.describe_instances()
    if debug_print:
        print('\nDescribe Instances:')
        pp.pprint(response)
    instance_count = 0
    for reserve in response['Reservations']:
        for instance in reserve['Instances']:
            if instance['State']['Name'] not in ['terminated', 'stopped']:
                instance_count += 1
    print("Running Instance Count: {}".format(instance_count))
    
    
def get_server_detail_from_yaml(path):
    with open(path) as stream:
        yaml_server_spec = load(stream, Loader=Loader)
        if debug_print:
            print('\nYaml Full:')
            pp.pprint(yaml_server_spec)
    spec = yaml_server_spec['server']
    return spec


def create_kwars_dictionary_for_create_instance(spec):
    create_instance_dict = {}
    try:
        create_instance_dict['ImageId'] = spec['ami_type']
        create_instance_dict['MinCount'] = spec['min_count']
        create_instance_dict['MaxCount'] = spec['max_count']
        create_instance_dict['InstanceType'] = spec['instance_type']

        if 'root_device_type' in spec and 'volumes' in spec:
            create_instance_dict['BlockDeviceMappings'] = []
            for vol in spec['volumes']:
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
        # Note unused variables
        # # architecture
        # # virtualization_type

        # Note not yet used variables
        # # root_device_type
        # # volume -> mount
        
        # TODO: Utilize users info
    except KeyError as e:
        print("Invalid key reference\n{}".format(e))
        exit(0)
    return create_instance_dict


# Retrieve Yaml Info
server_spec = get_server_detail_from_yaml('create-server/complicated_server_specifications.yml')

# Set up boto resources
credentials = retrieve_credentials()
ec2_client = create_boto_ec2_client(credentials)
ec2_resource = create_boto_ec2_resource(credentials)

# Print current state
print_current_instance_count(ec2_client)

# Use Yaml info to create instances
create_instance_dict = create_kwars_dictionary_for_create_instance(server_spec)
ec2_resource.create_instances(
    **create_instance_dict
)

# Print updated state
print_current_instance_count(ec2_client)

# TODO: Write more TODOs
