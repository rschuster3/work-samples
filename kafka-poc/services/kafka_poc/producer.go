package kafka_poc


import (
    "log"
    "os"

    "github.com/golang/protobuf/proto"
    "github.com/Shopify/sarama"

    "stash.arubanetworks.com/ac/meridian-positioning-service/services/kafka_poc/messages"
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


func Publish(topic string, message messages.Hello, producer sarama.SyncProducer) error {
    messageToSendBytes, err := proto.Marshal(&message)
    if err != nil {
        return err
    }

    // Have a producer publish a message to a Kafka topic
    msg := &sarama.ProducerMessage {
        Topic: topic,
        Value: sarama.ByteEncoder(messageToSendBytes),
    }

    _, _, err = producer.SendMessage(msg)

    return err
}
