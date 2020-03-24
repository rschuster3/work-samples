package kafka_poc


import (
    "github.com/Shopify/sarama"

    "some-repo/services/meridian_utils"
)


func NewConsumer(topic string, kafkaConn string) (sarama.PartitionConsumer, error) {
    conf := sarama.NewConfig()
    consumer, err := sarama.NewConsumer([]string{kafkaConn}, conf)
    meridian_utils.Check(err)

    partitionConsumer, err := consumer.ConsumePartition(topic, 0, sarama.OffsetOldest)
    meridian_utils.Check(err)

    return partitionConsumer, err
}
