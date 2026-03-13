# IAC module to generate client and server certificates
# for a nominally mtls application. The CAs involved are defined
# in the `pki.tf` file

################################################################################
# Kakfa Broker Certificate - CA-signed
################################################################################
resource "tls_private_key" "kafka" {
  algorithm = local.cert_algorithm
}

resource "tls_cert_request" "kafka" {
  private_key_pem = tls_private_key.kafka.private_key_pem

  dns_names = [
    "localhost", "kafka", "kafka.${local.domain_name}"
  ]

  subject {
    common_name  = "kafka.${local.domain_name}"
    organization = local.organization
    organizational_unit = "brokers"
  }
}

resource "tls_locally_signed_cert" "kafka" {
  cert_request_pem   = tls_cert_request.kafka.cert_request_pem
  ca_private_key_pem = tls_private_key.server.private_key_pem
  ca_cert_pem        = tls_locally_signed_cert.server.cert_pem

  validity_period_hours = 168

  allowed_uses = [
    "content_commitment",
    "digital_signature",
    "key_agreement",
    "server_auth",
    "client_auth",
  ]
}

################################################################################
# Kakfa Producer Client Certificate - CA-signed
################################################################################
resource "tls_private_key" "producer" {
  algorithm = local.cert_algorithm
}

resource "tls_cert_request" "producer" {
  private_key_pem = tls_private_key.producer.private_key_pem

  subject {
    common_name  = "${local.organization} IOT Device"
    organization = local.organization
    organizational_unit = "producers"
  }
}

resource "tls_locally_signed_cert" "producer" {
  cert_request_pem   = tls_cert_request.producer.cert_request_pem
  ca_private_key_pem = tls_private_key.client.private_key_pem
  ca_cert_pem        = tls_locally_signed_cert.client.cert_pem

  validity_period_hours = 168

  allowed_uses = [
    "content_commitment",
    "digital_signature",
    "key_agreement",
    "client_auth",
    "server_auth",
  ]
}

################################################################################
# Kakfa Consumer Client Certificate - CA-signed
################################################################################
resource "tls_private_key" "consumer" {
  algorithm = local.cert_algorithm
}

resource "tls_cert_request" "consumer" {
  private_key_pem = tls_private_key.consumer.private_key_pem

  subject {
    common_name  = "${local.organization} Consumer"
    organization = local.organization
    organizational_unit = "consumers"
  }
}

resource "tls_locally_signed_cert" "consumer" {
  cert_request_pem   = tls_cert_request.consumer.cert_request_pem
  ca_private_key_pem = tls_private_key.client.private_key_pem
  ca_cert_pem        = tls_locally_signed_cert.client.cert_pem

  validity_period_hours = 168

  allowed_uses = [
    "content_commitment",
    "digital_signature",
    "key_agreement",
    "client_auth",
    "server_auth",
  ]
}

################################################################################
# Kakfa Admin Client Certificate - CA-signed
################################################################################
resource "tls_private_key" "admin" {
  algorithm = local.cert_algorithm
}

resource "tls_cert_request" "admin" {
  private_key_pem = tls_private_key.admin.private_key_pem

  subject {
    common_name  = "${local.organization} Admin"
    organization = local.organization
    organizational_unit = "admins"
  }
}

resource "tls_locally_signed_cert" "admin" {
  cert_request_pem   = tls_cert_request.admin.cert_request_pem
  ca_private_key_pem = tls_private_key.client.private_key_pem
  ca_cert_pem        = tls_locally_signed_cert.client.cert_pem

  validity_period_hours = 168

  allowed_uses = [
    "content_commitment",
    "digital_signature",
    "key_agreement",
    "client_auth",
    "server_auth",
  ]
}

################################################################################
# OUTPUTS
################################################################################
output kafka_broker_certificate {
    value = trimspace(tls_locally_signed_cert.kafka.cert_pem)
}

output kafka_producer_certificate {
    value = trimspace(tls_locally_signed_cert.producer.cert_pem)
}

################################################################################
# ARTIFACTS
################################################################################

# Files for `ssl.keystore.location` which should include the private key and
# certificate chain
resource "local_file" "kafka_broker_keystore" {
    content  = format(
        "%s%s%s",
        tls_private_key.kafka.private_key_pem_pkcs8,
        tls_locally_signed_cert.kafka.cert_pem,
        tls_locally_signed_cert.kafka.ca_cert_pem
    )
    filename = "${path.module}/../cert/broker_ssl_keystore_location.pem"
}

# Files for `ssl.truststore.location` which should be the CA chain for client
# and other server certificates
resource "local_file" "kafka_broker_truststore" {
    content  = format(
        "%s%s",
        tls_locally_signed_cert.client.cert_pem,
        tls_locally_signed_cert.server.cert_pem
    )
    filename = "${path.module}/../cert/broker_ssl_truststore_location.pem"
}

# Files for `ssl.ca.location` i.e. CA certificate chain
resource "local_file" "cacert" {
    content  = format(
        "%s%s%s",
        tls_locally_signed_cert.server.cert_pem,
        tls_locally_signed_cert.client.cert_pem,
        tls_self_signed_cert.root.cert_pem
    )
    filename = "${path.module}/../cert/cacert.pem"
}

# Files for client auth
resource "local_file" "producer_cert" {
    content  = format(
        "%s%s",
        tls_locally_signed_cert.producer.cert_pem,
        tls_locally_signed_cert.producer.ca_cert_pem
    )
    filename = "${path.module}/../cert/producer.pem"
}

resource "local_file" "producer_key" {
    content  = tls_private_key.producer.private_key_pem_pkcs8
    filename = "${path.module}/../cert/producer.key"
}

resource "local_file" "consumer_cert" {
    content  = format(
        "%s%s",
        tls_locally_signed_cert.consumer.cert_pem,
        tls_locally_signed_cert.consumer.ca_cert_pem
    )
    filename = "${path.module}/../cert/consumer.pem"
}

resource "local_file" "consumer_key" {
    content  = tls_private_key.consumer.private_key_pem_pkcs8
    filename = "${path.module}/../cert/consumer.key"
}

# A Keystore PEM file for use with the Kafka Admin Client
resource "local_file" "admin_keystore" {
    content  = format(
        "%s%s%s",
        tls_private_key.admin.private_key_pem_pkcs8,
        tls_locally_signed_cert.admin.cert_pem,
        tls_locally_signed_cert.admin.ca_cert_pem
    )
    filename = "${path.module}/../cert/admin_ssl_keystore_location.pem"
}
