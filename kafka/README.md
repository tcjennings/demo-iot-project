# Kafka Client
This is a placeholder directory for the first-party Apache Kafka client, which can be downloaded and extracted with `make client`.

Assuming that a JRE/JDK is available and working, the Kafka client can be used in the usual way.
The top-level `config/admin_client.properties` may be used to configure the Kafka Client commands.

## List the topics / verify operation

```
./kafka/kafka_2.13-3.7.1/bin/kafka-topics.sh --bootstrap-server localhost:29092 \
--command-config config/admin_client.properties \
--list
```

## Add a topic and ACLs

If topic auto-creation is disabled, then a topic must be created by an admin user before any producer or consumer clients can use it.

```
./kafka/kafka_2.13-3.7.1/bin/kafka-topics.sh --bootstrap-server localhost:29092 \
--command-config config/admin_client.properties \
--topic local.iot.sensor.readings
```

## Add ACLs for Producers and Consumers

### Producers get WO
```
./kafka/kafka_2.13-3.7.1/bin/kafka-acls.sh --bootstrap-server localhost:29092 \
--command-config config/admin_client.properties \
--add --allow-principal "User:producers" \
--topic "*" \
--producer
```

### Consumers get RO
```
./kafka/kafka_2.13-3.7.1/bin/kafka-acls.sh --bootstrap-server localhost:29092 \
--command-config config/admin_client.properties \
--add --allow-principal "User:consumers" \
--topic "*" \
--consumer --group "*"
```

## Using Jikkou

The Docker Compose application stack includes a "kafka-init" service that uses [Jikkou](http://www.jikkou.io) to provision the Kafka topic and authorizations.
