"""Pydantic models for librdkafka stats callback.

See: https://github.com/confluentinc/librdkafka/blob/master/STATISTICS.md

Use of the `MISSING` sentinel (pydantic >= 2.12) differentiates between "field
value is null" and "field value is not present", i.e., some statistics are only
generated in some specific cases, so it is neither an error if that field is
not present in the statistics object nor is it correct to say that the value of
such a field is null. This is the case for some statistics that apply, e.g.,
only to idempotent producers.

The use of specific annotated types to differentiate between Counter and Gauge
integer values is to provide an immediate clue about what the value may represent
and to explain how it may be expected to change over time.

When appropriate, the specific units represented by a field's value are added
to the `json_schema_extra` metadata.
"""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StrictBool, computed_field
from pydantic.experimental.missing_sentinel import MISSING

CounterInt = Annotated[int, Field(json_schema_extra={"integer_type": "counter"})]
""""Integer counter (64 bits wide). Ever increasing. Should be >=0 but is not worth validating."""

GaugeInt = Annotated[int, Field(json_schema_extra={"integer_type": "gauge"})]
"""Integer gauge (64 bits wide). Will be reset to 0 on each stats emit. Should be >=0 but is not worth validating."""

NotSet = Annotated[
    Literal[-1],
    Field(
        description="A literal -1 is often used in rdkafka statistics for a bootstrap or integer value that is not yet set."
    ),
]

OffsetInvalid = Annotated[
    Literal[-1001],
    Field(
        description="A literal -1001 is an offset value that is either invalid or has never been consumed/committed."
    ),
]


class _RdKafkaBaseModel(BaseModel):
    """Base class for RdKakfa Statistics Model.

    Sets common model config dict.
    """

    model_config = ConfigDict(extra="allow")


class _RdKafkaStats(_RdKafkaBaseModel):
    """Top-level rdkafka statistics model."""

    name: Annotated[str, Field(description="Handle instance name")]
    client_id: Annotated[
        str, Field(description="The configured (or default) client.id")
    ]
    type: Annotated[Literal["producer", "consumer"], Field(description="Instance type")]
    ts: Annotated[
        CounterInt,
        Field(
            description="librdkafka's internal monotonic clock",
            json_schema_extra={"units": "usec"},
        ),
    ]
    time: Annotated[
        CounterInt,
        Field(
            description="Wall clock time in seconds since the epoch",
            json_schema_extra={"units": "sec"},
        ),
    ]
    age: Annotated[
        CounterInt,
        Field(
            description="Time since this client instance was created",
            json_schema_extra={"units": "usec"},
        ),
    ]
    replyq: Annotated[
        GaugeInt,
        Field(
            description="Number of ops (callbacks, events, etc) waiting in queue for application to serve with rd_kafka_poll()"
        ),
    ]
    msg_cnt: Annotated[
        GaugeInt, Field(description="Current number of messages in producer queues")
    ]
    msg_size: Annotated[
        GaugeInt, Field(description="Current total size of messages in producer queues")
    ]
    msg_max: Annotated[
        GaugeInt,
        Field(
            description="Threshold: maximum number of messages allowed allowed on the producer queues"
        ),
    ]
    msg_size_max: Annotated[
        GaugeInt,
        Field(
            description="Threshold: maximum total size of messages allowed on the producer queues"
        ),
    ]
    tx: CounterInt
    tx_bytes: CounterInt
    rx: CounterInt
    rx_bytes: CounterInt
    txmsgs: CounterInt
    txmsg_bytes: CounterInt
    rxmsgs: CounterInt
    rxmsg_bytes: CounterInt
    simple_cnt: GaugeInt
    metadata_cache_cnt: GaugeInt
    brokers: Annotated[dict[str, _BrokerStats], Field()]
    topics: Annotated[dict[str, _TopicStats], Field()]
    cgrp: Annotated[dict[str, _ConsumerGroupStats], Field()] | MISSING = MISSING  # type: ignore[valid-type]
    eos: Annotated[dict[str, _EosProducerStats], Field()] | MISSING = MISSING  # type: ignore[valid-type]


class _BrokerStats(_RdKafkaBaseModel):
    """Per-broker statistics"""

    name: str
    nodeid: int
    nodename: str
    source: str
    state: Literal[
        "INIT",
        "DOWN",
        "CONNECT",
        "AUTH",
        "APIVERSION_QUERY",
        "AUTH_HANDSHAKE",
        "UP",
        "UPDATE",
    ]
    stateage: GaugeInt
    outbuf_cnt: GaugeInt
    outbuf_msg_cnt: GaugeInt
    waitresp_cnt: GaugeInt
    waitresp_msg_cnt: GaugeInt
    tx: CounterInt
    txbytes: CounterInt
    txerrs: CounterInt
    txretries: CounterInt
    txidle: CounterInt
    req_timeouts: CounterInt
    rx: CounterInt
    rxbytes: CounterInt
    rxerrs: CounterInt
    rxcorriderrs: CounterInt
    rxpartial: CounterInt
    rxidle: (
        Annotated[
            CounterInt,
            Field(
                description="Microseconds since last socket receive",
                json_schema_extra={"units": "usec"},
            ),
        ]
        | Annotated[NotSet, Field(description="No receives yet for current connection")]
    )
    req: Annotated[
        dict[str, int],
        Field(
            description="Request type counters. Object key is the request name, value is the number of requests sent."
        ),
    ]
    zbuf_grow: CounterInt
    buf_grow: CounterInt
    wakeups: CounterInt
    connects: CounterInt
    disconnects: CounterInt
    int_latency: Annotated[
        _WindowStats,
        Field(
            description="Internal producer queue latency in microseconds",
            json_schema_extra={"units": "usec"},
        ),
    ]
    outbuf_latency: Annotated[
        _WindowStats,
        Field(
            description="Internal request queue latency in microseconds",
            json_schema_extra={"units": "usec"},
        ),
    ]
    rtt: Annotated[
        _WindowStats,
        Field(
            description="Broker latency / round-trip time in microseconds",
            json_schema_extra={"units": "usec"},
        ),
    ]
    throttle: Annotated[
        _WindowStats,
        Field(
            description="Broker throttling time in milliseconds",
            json_schema_extra={"units": "msec"},
        ),
    ]
    toppars: dict[str, _TopicPartitions]


class _TopicStats(_RdKafkaBaseModel):
    """Per-topic stats"""

    topic: Annotated[str, Field(description="Topic name")]
    age: Annotated[
        GaugeInt,
        Field(
            description="Age of client's topic object",
            json_schema_extra={"units": "msec"},
        ),
    ]
    metadata_age: Annotated[
        GaugeInt,
        Field(
            description="Age of metadata from broker for this topic",
            json_schema_extra={"units": "msec"},
        ),
    ]
    batchsize: Annotated[
        _WindowStats,
        Field(description="Batch sizes in bytes", json_schema_extra={"units": "bytes"}),
    ]
    batchcnt: Annotated[_WindowStats, Field(description="Batch message counts")]
    partitions: dict[str, _PartitionStats]


class _PartitionStats(_RdKafkaBaseModel):
    partition: (
        Annotated[int, Field(ge=0)]
        | Annotated[
            NotSet, Field(description="-1 for internal UA/UnAssigned partition)")
        ]
    )
    broker: Annotated[int, Field(ge=0)] | NotSet
    leader: Annotated[int, Field(ge=0)] | NotSet
    desired: StrictBool
    unknown: StrictBool
    msgq_cnt: GaugeInt
    msgq_bytes: GaugeInt
    xmit_msgq_cnt: GaugeInt
    xmit_msgq_bytes: GaugeInt
    fetchq_cnt: GaugeInt
    fetchq_size: GaugeInt
    fetch_state: Literal[
        "none", "stopping", "stopped", "offset-query", "offset-wait", "active"
    ]
    query_offset: GaugeInt | OffsetInvalid
    next_offset: GaugeInt | OffsetInvalid
    app_offset: GaugeInt | OffsetInvalid
    stored_offset: GaugeInt | OffsetInvalid
    stored_leader_epoch: int | NotSet
    committed_offset: GaugeInt | OffsetInvalid
    committed_leader_epoch: int | NotSet
    eof_offset: GaugeInt | OffsetInvalid
    lo_offset: GaugeInt | OffsetInvalid
    hi_offset: GaugeInt | OffsetInvalid
    ls_offset: GaugeInt | OffsetInvalid
    consumer_lag: GaugeInt | NotSet
    consumer_lag_stored: GaugeInt | NotSet
    leader_epoch: (
        Annotated[int, Field(description="Last known partition leader epoch")]
        | Annotated[NotSet, Field(description="Leader epoch unknown")]
    )
    txmsgs: CounterInt
    txbytes: CounterInt
    rxmsgs: CounterInt
    rxbytes: CounterInt
    msgs: CounterInt
    rx_ver_drops: CounterInt
    msgs_inflight: GaugeInt
    next_ack_seq: Annotated[
        GaugeInt | MISSING,
        Field(description="Next expected acked sequence (idempotent producer)"),
    ] = MISSING  # type: ignore[valid-type]
    next_err_seq: Annotated[
        GaugeInt | MISSING,
        Field(description="Next expected errored sequence (idempotent producer)"),
    ] = MISSING  # type: ignore[valid-type]
    acked_msgid: Annotated[
        int | MISSING,
        Field(description="Last acked internal message id (idempotent producer)"),
    ] = MISSING  # type: ignore[valid-type]


class _ConsumerGroupStats(_RdKafkaBaseModel):
    """Consumer group stats model. May be `MISSING`."""

    state: str
    stageage: Annotated[GaugeInt, Field(json_schema_extra={"units": "msec"})]
    join_state: str
    rebalance_age: Annotated[GaugeInt, Field(json_schema_extra={"units": "msec"})]
    rebalance_cnt: CounterInt
    rebalance_reason: str
    assignment_size: GaugeInt


class _EosProducerStats(_RdKafkaBaseModel):
    """Stats model for idempotent/exactly-once producers. May be `MISSING`."""

    idemp_state: str
    idemp_stateage: Annotated[GaugeInt, Field(json_schema_extra={"units": "msec"})]
    txn_state: str
    txn_stageage: Annotated[GaugeInt, Field(json_schema_extra={"units": "msec"})]
    txn_may_enq: StrictBool
    producer_id: Annotated[int, Field(ge=0)] | NotSet
    producer_epoch: Annotated[int, Field(ge=0)] | NotSet
    epoch_cnt: int


class _WindowStats(_RdKafkaBaseModel):
    """Rolling window statistics. The values are in microseconds unless otherwise stated."""

    min: GaugeInt
    max: GaugeInt
    avg: GaugeInt
    sum: GaugeInt
    cnt: GaugeInt
    stddev: GaugeInt
    hdrsize: GaugeInt
    p50: GaugeInt
    p75: GaugeInt
    p90: GaugeInt
    p95: GaugeInt
    p99: GaugeInt
    p99_99: GaugeInt
    outofrange: GaugeInt


class _TopicPartitions(_RdKafkaBaseModel):
    """Topic partition assigned to broker."""

    topic: str
    partition: int


class RdKafkaStats(_RdKafkaStats):
    """This class exists primarily to be subclassed for the implementation of
    application-specific derived metrics, which can be added to the model
    via new fields, properties, or `@computed_props`.
    """

    @computed_field
    @property
    def total_consumer_lag(self) -> dict[str, int]:
        """Computed field calculating the total consumer lag for each topic
        reported in statistics.
        """
        return {
            topic: sum(
                partition.consumer_lag
                for partition in tstats.partitions.values()
                if partition.consumer_lag != NotSet
            )
            for topic, tstats in self.topics.items()
        }
