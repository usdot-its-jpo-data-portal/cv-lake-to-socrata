# cv-lake-to-socrata
This repository contains code to ingest samples of data from the ITS Connected Vehicle Pilot Data Sandbox to their corresponding Socrata datasets on data.transportation.gov.

# Prerequisites
These instructions will get you a copy of the project up and running on your local machine for use, development, and testing purposes, or deploy this to your AWS environment.

1. Have access to Python 3.6+. You can check your python version by entering python --version and python3 --version in command line.
2. Have access to the command line of a machine. If you're using a Mac, the command line can be accessed via the Terminal, which comes with Mac OS. If you're using a PC, the command line can be accessed via the Command Prompt, which comes with Windows, or via Cygwin64, a suite of open source tools that allow you to run something similar to Linux on Windows.
3. Have your own Free Amazon Web Services account.
   - Create one at http://aws.amazon.com
4. Obtain Access Keys:
   - On your Amazon account, go to your profile (at the top right)
   - My Security Credentials > Access Keys > Create New Access Key
   - Record the Access Key ID and Secret Access Key ID (you will need them in step 4)
5. Save your AWS credentials in your local machine, using one of the following method:
   - shared credentials file: instructions at https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html#shared-credentials-file.
   - environmental variables: instructions at https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html#environment-variables
6. Have [Docker](https://www.docker.com/) installed. 

# Usage

## Building

Build Docker image:
```
docker build -t cv-lake-to-socrata .
```

To build the image without cache, run:
```
docker build -t cv-lake-to-socrata . --no-cache
```

## Execution

The script requires the following environment variables:
- `AUTH`: Stringified JSON object containing Socrata authentication information. Sample JSON object: 
```
    {
        "domain": "datahub.transportation.gov",
        "username": "someUsername",
        "password": "somePassword"
    }
```

- `EVENT`: Stringified JSON object containing information about what sample to write to Socrata. Sample JSON object:
```
{
    "overwrite": true,
    "num_hours_backtrack": 72,
    "s3_source_bucket": "usdot-its-cvpilot-public-data",
    "s3_source_prefix": "wydot/BSM",
    "socrata_dataset_id": "xxxx-xxxx",
    "float_fields": [],
    "data_sample_length": "day",
    "permission": "private"
 }
```

Run the Docker container and pass in the environment variables:
```
docker run cv-lake-to-socrata --env AUTH={"domain": "datahub.transportation.gov", "username": "someUsername", "password": "somePassword"} --env EVENT={"overwrite": true, "num_hours_backtrack": 72, "s3_source_bucket": "usdot-its-cvpilot-public-data", "s3_source_prefix": "wydot/BSM", "socrata_dataset_id": "xxxx-xxxx", "float_fields": [], "data_sample_length": "day", "permission": "private"}
```

## Deployment
Deploy built Docker image to AWS Elastic Container Registry (ECR). Steps 2-5 are also available via AWS Console when you select your ECR repository and click on "View push commands". Replace all reference of `$AWS_ACCOUNT_NUMBER` with your own AWS account number.

1. If repository does not exist yet, create repository in AWS Console or using AWS Command Line Tool

2. Retrieve an authentication token and authenticate your Docker client to your registry.
    ```
    aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $AWS_ACCOUNT_NUMBER.dkr.ecr.us-east-1.amazonaws.com
    ```

3. If you've already built your container, tag your image so you can push the image to this repository:
    ```
    docker tag cv-lake-to-socrata:latest $AWS_ACCOUNT_NUMBER.dkr.ecr.us-east-1.amazonaws.com/cv-lake-to-socrata:latest
    ```

4. Run the following command to push this image to your newly created AWS repository:
    ```
    docker push $AWS_ACCOUNT_NUMBER.dkr.ecr.us-east-1.amazonaws.com/cv-lake-to-socrata:latest
    ```


# Version History and Retention

**Status:** This project is in the release phase.

**Release Frequency:** This project is updated irregularly.

**Release History: See [CHANGELOG.md](CHANGELOG.md)**

**Retention:** This project will remain publicly accessible for a minimum of five years (until at least 07/19/2026).

# License

This project is licensed under the Creative Commons 1.0 Universal (CC0 1.0) License - see the [LICENSE](LICENSE) for more details. 

# Contributions

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our Code of Conduct, the process for submitting pull requests to us, and how contributions will be released.

# Contact Information

Contact Name: ITS JPO

Contact Information: data.itsjpo@dot.gov

# Acknowledgements

When you copy or adapt from this code, please include the original URL you copied the source code from and date of retrieval as a comment in your code.

## Contributors
Shout out to [PurpleBooth](https://gist.github.com/PurpleBooth/109311bb0361f32d87a2) for their README template.