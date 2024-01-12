# isort:imports-stdlib
import logging
import smtplib
import sys
import traceback
from email.mime.text import MIMEText

# isort:imports-thirdparty
import dill
import pkg_resources


# isort:imports-firstparty
from project_paths import REQUIREMENTS_PATH


def write_pickle(data, path):
    with open(path, "wb") as out_strm:
        dill.dump(data, out_strm)
    return


def read_pickle(path):
    with open(path, "rb") as in_strm:
        data = dill.load(in_strm)
    return data


def check_python_version(assert_on_failure: bool = False):
    installed_python_version = (
        f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    )

    python_versions_allowed = ["3.9.2", "3.8.10"]  # For sagemaker testing

    result = installed_python_version in python_versions_allowed

    message = f"Supports Python version {python_versions_allowed}"
    logging.info(message)

    message = f"Installed Python version : {installed_python_version}"
    logging.info(message)

    if assert_on_failure is True:
        assert (
            result
        ), f"Supports Python version {python_versions_allowed}, but {installed_python_version} is installed"

    return result


def check_package_versions(
    assert_on_failure: bool = False,
    return_dict: bool = False,
    return_failed_only: bool = False,
    return_cli_command: bool = False,
):
    requirements = pkg_resources.parse_requirements(REQUIREMENTS_PATH.open())

    result_dict = {}
    result = []
    cli_command = f"pip3 install"

    for requirement in requirements:
        requirement = str(requirement)

        # Get package version from requirements.txt
        pkg_name, version_required = requirement.split("==")
        # Get package version installed
        try:
            version_installed = pkg_resources.get_distribution(
                pkg_name).version
        except:
            version_installed = ""

        result_package = version_required == version_installed
        message = f"{pkg_name} (Pass: {result_package}) {version_required} required, {version_installed} installed"
        logging.info(message)

        if assert_on_failure is True:
            assert result_package, message

        result.append(result_package)

        if result_package is False:
            cli_command += f" {pkg_name}=={version_required}"

        if return_failed_only is True:
            if result_package is False:
                result_dict[pkg_name] = {
                    "status": result_package,
                    "required": version_required,
                    "installed": version_installed,
                }
        else:
            result_dict[pkg_name] = {
                "status": result_package,
                "required": version_required,
                "installed": version_installed,
            }

    if return_dict is True:
        return result_dict
    else:
        if return_cli_command is True:
            return cli_command
        else:
            return all(result)


def email_on_failure(sender_email, password, recipient_email, subject=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # format the error message and traceback
                err_msg = f"Error: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"

                # create the email message
                message = MIMEText(err_msg)
                if subject is None:
                    message["Subject"] = f"{func.__name__} failed"
                else:
                    message["Subject"] = subject
                message["From"] = sender_email
                message["To"] = recipient_email

                # send the email
                with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                    smtp.login(sender_email, password)
                    smtp.sendmail(sender_email, recipient_email,
                                  message.as_string())

                # re-raise the exception
                raise

        return wrapper

    return decorator
