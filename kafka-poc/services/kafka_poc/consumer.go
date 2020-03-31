package kafka_poc


import (
    "github.com/Shopify/sarama"
)


func NewConsumer(topic string, kafkaConn string) (sarama.PartitionConsumer, error) {
    var partitionConsumer sarama.PartitionConsumer

    conf := sarama.NewConfig()
    consumer, err := sarama.NewConsumer([]string{kafkaConn}, conf)
    if err != nil {
        return partitionConsumer, err
    }

    partitionConsumer, err = consumer.ConsumePartition(topic, 0, sarama.OffsetOldest)

    return partitionConsumer, err
}
