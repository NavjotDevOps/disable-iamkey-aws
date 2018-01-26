import datetime
import boto3
from dateutil import parser
from boto import iam

###set disable time(in days) on which you want to disable access key
disable_time_limit= 160
##set warning time(in days) on which script send warning e-mail to sender
warning_time_limit= 150

EMAIL_FROM="sender_email_id"
EMAIL_TO= "reciever_email_id"


def send_deactivate_email(username, age, access_key_id):
    print "Sending warning mail : Access Key " + access_key_id + " for Username " + username + " age: " + str(age)
    client = boto3.client('ses', region_name="us-west-2")
    response = client.send_email(
        Source=EMAIL_FROM,
        Destination={
            'ToAddresses': [EMAIL_TO]
        },
        Message={
            'Subject': {
                'Data': 'AWS IAM Access Key Rotation - Deactivation of Access Key : ' + access_key_id
            },
            'Body': {
                'Html': {
                'Data': 'The Access Key access_key_id belonging to User ' +  username + ' has been automatically deactivated due to it being ' + str(age) + ' age days old'
                }
            }
        })

def disable_access_key(access_key_id, username , age):
    print "Disabling Access Key " + access_key_id + " for Username " + username + " age "  + str(age)
    iam = boto3.client('iam')
    iam.update_access_key(
        AccessKeyId=access_key_id,
        Status='Inactive',
        UserName=username)

def enable_access_key(access_key_id, username , age):
    print "Disabling Access Key " + access_key_id + " for Username " + username + " age "  + str(age)
    iam = boto3.client('iam')
    iam.update_access_key(
        AccessKeyId=access_key_id,
        Status='Active',
        UserName=username)

def delete_access_key(access_key_id,username , age):
    print "Delete Access Key " + access_key_id + " for Username " + username + " age " + str(age)
    iam = boto3.client('iam')
    iam.delete_access_key(
        AccessKeyId=access_key_id,
        UserName=username
    )

def validate_iam_key():
 print "-------------------------------------------------------------"
 print "Access Keys Created Date" + "\t\t" + "Username"
 print "-------------------------------------------------------------"

 conn = iam.connect_to_region('eu-west-1')
 users = conn.get_all_users()
 exception_user_list = ["navjot"]

 for user in users.list_users_response.users:
    user_name =  user['user_name']
    if user_name in exception_user_list:
        continue

    accessKeys=conn.get_all_access_keys(user_name=user_name)
    print accessKeys
    for keysCreatedDate in accessKeys.list_access_keys_response.list_access_keys_result.access_key_metadata:
        user_name = user['user_name']
        create_date = keysCreatedDate['create_date']
        access_key_id = keysCreatedDate['access_key_id']
        date_delta = datetime.datetime.today() - datetime.datetime.strptime(create_date, '%Y-%m-%dT%H:%M:%SZ')
        age = date_delta.days

        if age >= warning_time_limit and age <=disable_time_limit:
            send_deactivate_email(user_name, age, access_key_id)
        elif age  >= disable_time_limit:
            disable_access_key(access_key_id, user_name,age)
            # enable_access_key(access_key_id, user_name, age)
            # delete_access_key(access_key_id, user_name, age)



def main_function():
    validate_iam_key()
