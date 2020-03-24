package kafka_poc


import (
    "log"
    "os"

    "github.com/Shopify/sarama"

    "some-repo/services/meridian_utils"
)


func NewProducer(kafkaConn string) (sarama.SyncProducer, error) {
    // setup sarama log to stdout
    sarama.Logger = log.New(os.Stdout, "", log.Ltime)

    // producer config
    config := sarama.NewConfig()
    config.Producer.Retry.Max = 5
    config.Producer.RequiredAcks = sarama.WaitForAll
    config.Producer.Return.Successes = true

    // sync producer
    prd, err := sarama.NewSyncProducer([]string{kafkaConn}, config)

    return prd, err
}


func Publish(topic string, message *Hello, producer sarama.SyncProducer) {
    // Have a producer publish a message to a Kafka topic
    msg := &sarama.ProducerMessage {
        Topic: topic,
        Value: sarama.StringEncoder(message.Hello),
    }

    _, _, err := producer.SendMessage(msg)
    meridian_utils.Check(err)
}
