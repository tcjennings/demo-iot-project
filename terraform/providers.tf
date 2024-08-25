terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }

    tls = {
      source = "hashicorp/tls"
      version = "~> 4.0"
    }
  }
}

# Configure the AWS Provider for use with Localstack's AWS APIs
# where the access key is the "account id" and the secret doesn't
# matter.
provider "aws" {
  alias = "localstack"
  region = "us-west-2"
  access_key = "123456789012"
  secret_key = "swordfish"

  endpoints {
    acm    = "http://localhost:4566"
    acmpca = "http://localhost:4566"
    iam    = "http://localhost:4566"
    sts    = "http://localhost:4566"
  }
}
