import os
import datetime
import boto3
import argparse
import time
from infrastructure import Terraform
from aws_ses_test import ses_send_email


SES_SSM_PARAMETER = '/ses'
SMTP_USER_SSM_PARAMETER = '/smtp_user'
SMTP_PASSWORD_SSM_PARAMETER = '/smtp_password'
SSM_ACCESS_KEY_VERSION = '/smtp/access_key/latest_version'
TERRAFORM_FOLDER = "infrastructure"
TEMPLATE_FOLDER = "infrastructure/template"


ssm = boto3.client("ssm")


def get_file_name_from_pattern(list_files, pattern):
    import re

    result = [x for x in list_files if re.match(pattern, x)]

    if len(result) > 0:
        return result[0]
    else:
        raise Exception(f"The file with pattern {pattern} not exist. Files {list_files}")


def delete_file(file):
    if os.path.exists(file):
        os.remove(file)


def is_file_from_template(file, template_list):
    for template in template_list:
        if template in file:
            return True
    return False


def get_file_name(folder, file, version):
    file_path = "main.tf" if file == "main" else f"{file}-{version}.tf"
    return f"{TERRAFORM_FOLDER}/{file_path}"


def remove_configuration(template_files, folder):
    list_files = os.listdir(folder)
    files_to_delete = [
        x for x in list_files if is_file_from_template(x, template_files)
    ]
    [delete_file(f"{folder}/{x}") for x in files_to_delete]


def create_access_key_file(source_file, dest_file, suffix):
    with open(source_file, "rt") as template:
        with open(dest_file, "wt") as new_access_key:
            for line in template:
                new_access_key.write(line.replace("{date}", suffix)
                                         .replace("{ssm_parameter_user}", SMTP_USER_SSM_PARAMETER)
                                         .replace("{ssm_parameter_password}", SMTP_PASSWORD_SSM_PARAMETER)
                                         .replace("{ssm_parameter_ses}", SES_SSM_PARAMETER)
                                    )


def create_configuration(template_files, version):
    for file in template_files:
        create_access_key_file(
            f"{TEMPLATE_FOLDER}/{file}",
            get_file_name(TERRAFORM_FOLDER, file, version),
            version,
        )


def apply_infrastructure(terraform_dir, backend_file, variables_file):
    try:
        terraform = Terraform(terraform_dir)
        terraform.init(backend_file, variables_file)
        terraform.plan(variables_file)
        terraform.apply(variables_file)
    except Exception as e:
        raise Exception(f"Error updating infrastructure. Error: {e}")


def get_ssm_secret(parameter_name):
    secret = ssm.get_parameter(Name=parameter_name, WithDecryption=True)
    return secret.get("Parameter").get("Value")


def put_ssm_secret(parameter_name, value):
    ssm.put_parameter(Name= parameter_name, Value= value
                    ,Type= 'SecureString', Overwrite=True)


def get_params():
    parser = argparse.ArgumentParser(description='Params to ses rotation key.')
    parser.add_argument('--sender-test', dest='sender_test', help='Sender email to test.')
    parser.add_argument('--recipient-test', dest='recipient_test', help='Recipient Email to test.')
    return parser.parse_args()



def main():
    try:
        params = get_params()

        terraform_files = os.listdir(TERRAFORM_FOLDER)
        template_files = os.listdir(TEMPLATE_FOLDER)

        variables_file = get_file_name_from_pattern(terraform_files, "variables_[a-z]{1,10}.tfvars")
        backend_file = get_file_name_from_pattern(terraform_files, "backend_[a-z]{1,10}.tfvars")

        latest_version = get_ssm_secret(SSM_ACCESS_KEY_VERSION)
        new_version = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

        create_configuration(template_files, latest_version)
        create_configuration(template_files, new_version)

        apply_infrastructure(TERRAFORM_FOLDER, backend_file, variables_file)

        smtp_user = get_ssm_secret(SMTP_USER_SSM_PARAMETER)
        smtp_password = get_ssm_secret(SMTP_PASSWORD_SSM_PARAMETER)
        
        time.sleep(10)
        result = ses_send_email(smtp_user, smtp_password, params.recipient_test, params.sender_test)
        print(result)

        remove_configuration(template_files, TERRAFORM_FOLDER)

        if result[0]:
            put_ssm_secret(SSM_ACCESS_KEY_VERSION, new_version)
            create_configuration(template_files, new_version)
            apply_infrastructure(TERRAFORM_FOLDER, backend_file, variables_file)
        else:
            create_configuration(template_files, latest_version)
            apply_infrastructure(TERRAFORM_FOLDER, backend_file, variables_file)
            raise Exception(f"Error sending . Error: {result[1]}")    

    except Exception as e:
        raise Exception(f"Error in ses rotation-key. Error: {e}")
    finally:
        remove_configuration(template_files, TERRAFORM_FOLDER)


main()