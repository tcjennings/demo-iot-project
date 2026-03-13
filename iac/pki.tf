# IAC module for creating an offline PKI with a root CA and two subordinate
# CAs, one for servers and one for clients, to approximate the requirements of an
# mTLS application

################################################################################
# DATA, VARS, and LOCALS
################################################################################
locals {
    cert_algorithm = "RSA"
    domain_name = "iot.local"
    organization = "IOT Sample Project"
}

################################################################################
# Root CA - Self-signed
################################################################################
resource "tls_private_key" "root" {
  algorithm = local.cert_algorithm
}

resource "tls_self_signed_cert" "root" {
  private_key_pem = tls_private_key.root.private_key_pem
  is_ca_certificate = true
  validity_period_hours = 168

  subject {
    common_name  = "${local.organization} Root CA"
    organization = local.organization
  }

  allowed_uses = [
    "content_commitment",
    "digital_signature",
    "key_agreement",
    "cert_signing",
    "crl_signing",
  ]
}

################################################################################
# Server CA - Root-signed
################################################################################
resource "tls_private_key" "server" {
  algorithm = local.cert_algorithm
}

resource "tls_cert_request" "server" {
  private_key_pem = tls_private_key.server.private_key_pem

  subject {
    common_name  = "${local.organization} Server CA"
    organization = local.organization
  }
}

resource "tls_locally_signed_cert" "server" {
  cert_request_pem      = tls_cert_request.server.cert_request_pem
  ca_private_key_pem    = tls_private_key.root.private_key_pem
  ca_cert_pem           = tls_self_signed_cert.root.cert_pem
  is_ca_certificate     = true
  validity_period_hours = 168

  allowed_uses = [
    "content_commitment",
    "digital_signature",
    "key_agreement",
    "cert_signing",
    "crl_signing",
  ]
}

################################################################################
# Client CA - Root-signed
################################################################################
resource "tls_private_key" "client" {
  algorithm = local.cert_algorithm
}

resource "tls_cert_request" "client" {
  private_key_pem = tls_private_key.client.private_key_pem

  subject {
    common_name  = "${local.organization} Client CA"
    organization = local.organization
  }
}

resource "tls_locally_signed_cert" "client" {
  cert_request_pem      = tls_cert_request.client.cert_request_pem
  ca_private_key_pem    = tls_private_key.root.private_key_pem
  ca_cert_pem           = tls_self_signed_cert.root.cert_pem
  is_ca_certificate     = true
  validity_period_hours = 168

  allowed_uses = [
    "content_commitment",
    "digital_signature",
    "key_agreement",
    "cert_signing",
    "crl_signing",
  ]
}

################################################################################
# Add CA Certificates to AWS ACM
################################################################################
# TBD, Optional

################################################################################
# OUTPUTS
################################################################################
output root_ca_certificate {
    value = trimspace(tls_self_signed_cert.root.cert_pem)
}

output server_ca_certificate {
    value = trimspace(tls_locally_signed_cert.server.cert_pem)
}

output client_ca_certificate {
    value = trimspace(tls_locally_signed_cert.client.cert_pem)
}

output server_ca_chain {
    value = format("%s%s", tls_locally_signed_cert.server.cert_pem, tls_locally_signed_cert.server.ca_cert_pem)
}

output client_ca_chain {
    value = format("%s%s", tls_locally_signed_cert.client.cert_pem, tls_locally_signed_cert.client.ca_cert_pem)
}
