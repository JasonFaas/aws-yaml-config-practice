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

def print_current_instance_count(ec2_client):
    response = ec2_client.describe_instances()
    pp.pprint(response)
    print("Current Instance Count: {}".format(len(response['Reservations'][0]['Instances'])))


credentials = retreive_credentials()
ec2_client = create_boto_ec2_client(credentials)
print_current_instance_count(ec2_client)


# TODO: Create ec2 instance is uw-west-1 micro

# TODO: Write more TODOs
