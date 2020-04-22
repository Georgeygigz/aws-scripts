import requests
import tzlocal
import pytz
import boto3
import sys
from datetime import datetime, timedelta, timezone

ec2 = boto3.client('ec2')

def get_delete_days():
    delete_date = []
    string_delete_date = []

    for i in range(1,21):
        delete_date_time= datetime.now(tz=timezone.utc) - timedelta(days=i)
        delete_date.append(delete_date_time.date())
        string_delete_date.append(delete_date_time.date().strftime('%Y-%m-%d'))
    return delete_date, string_delete_date


def delete_snapshots():
    """
    Delete all snapshots owned by the current
    account and for a specific date
    Args:
        None
    Return:
        none
    """
    delete_date, _ = get_delete_days()
    snapshots = ec2.describe_snapshots(OwnerIds=['self'])
    for snapshot in snapshots['Snapshots']:
        date_snapshot_tobe_deleted = snapshot['StartTime'].date()
        if date_snapshot_tobe_deleted in delete_date:
            ec2.delete_snapshot(SnapshotId=snapshot['SnapshotId'])


def get_ami_ids():
    """
    Get the amis for all the running
    instances
    Args:
        none
    Returns:
        instance_ami_ids(list): list of all
                aims id in running instance
    """
    instance_ami_ids = []
    list_of_amis = ec2.describe_instances()
    for amis in list_of_amis['Reservations']:
        for instance in amis['Instances']:
            if instance['ImageId'] not in instance_ami_ids:
                instance_ami_ids.append(instance['ImageId'])
    return instance_ami_ids


def get_all_custom_aims():
    """
    function to get all the custom
    aims
    Args:
        none
    Returns:
        None
    """
    custom_images = ec2.describe_images(
            Filters=[{
                'Name': 'state',
                'Values': ['available',]
            },],
            Owners=['self',])
    return custom_images


def deregister_custom_ami():
    """
    Function that deregisters a custom
    ami
    Args:
        None
    Returns:
        None
    """
    instance_ami_ids = get_ami_ids()
    _, string_delete_date =  get_delete_days()
    custom_images = get_all_custom_aims()
    for custom_image in custom_images['Images']:
        if (custom_image['ImageId'] not in instance_ami_ids) and (custom_image['CreationDate'].partition('T')[0] in string_delete_date ):
            print('<<<<<Deregistering>>>>>>')
            ec2.deregister_image(ImageId=custom_image['ImageId'])
            print('<<<<<Deregistering>>>>>>')
deregister_custom_ami()
if __name__ == '__main__':
    delete_snapshots()
    deregister_custom_ami()
