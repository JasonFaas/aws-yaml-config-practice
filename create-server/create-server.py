import boto3
import csv
import pprint

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
    # pp.pprint(response)
    instance_count = 0
    for reserv in response['Reservations']:
        instance_count += len(reserv['Instances'])
    print("Current Instance Count: {}".format(instance_count))


credentials = retreive_credentials()
ec2_client = create_boto_ec2_client(credentials)
print_current_instance_count(ec2_client)

ec2_resource = create_boto_ec2_resource(credentials)
ec2_resource.create_instances(
    ImageId='ami-000279759c4819ddf',
    MinCount=1,
    MaxCount=1,
    InstanceType='t3.micro'
)

print_current_instance_count(ec2_client)


# TODO: Create ec2 instance in us-west-1 {instance_type: t2.micro, ami_type: amzn2, architecture: x86_64, etc}

# TODO: Write more TODOs
