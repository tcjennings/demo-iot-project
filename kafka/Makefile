KAFKA_VERSION := 3.7.1
KAFKA_SCALA_VERSION := 2.13

kafka_$(KAFKA_SCALA_VERSION)-$(KAFKA_VERSION):
	@curl -Ls https://downloads.apache.org/kafka/$(KAFKA_VERSION)/$@.tgz | tar xz

client: kafka_$(KAFKA_SCALA_VERSION)-$(KAFKA_VERSION)
