KAFKA_VERSION := 3.9.2
KAFKA_SCALA_VERSION := 2.13

kafka_$(KAFKA_SCALA_VERSION)-$(KAFKA_VERSION):
	@curl -Ls https://archive.apache.org/dist/kafka/$(KAFKA_VERSION)/$@.tgz | tar xz

client: kafka_$(KAFKA_SCALA_VERSION)-$(KAFKA_VERSION)

.PHONY: clean
clean:
	rm -rf kafka_$(KAFKA_SCALA_VERSION)-$(KAFKA_VERSION)
