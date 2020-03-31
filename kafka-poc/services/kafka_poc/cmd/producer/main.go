package main


import (
    "log"

    "go.uber.org/zap"

    "stash.arubanetworks.com/ac/meridian-positioning-service/services/kafka_poc"
    "stash.arubanetworks.com/ac/meridian-positioning-service/services/kafka_poc/messages"
)


var (
    np, _ = zap.NewProduction()
    logger = np.Sugar()
)


func main() {
    // Get Kafka service info from ADS
    adsKafkaJson, err := kafka_poc.GetKafkaInfo()
    if err != nil {
        log.Fatal(err)
    }

    // Get the host:port of the Kafka service
    kafkaConn, err := kafka_poc.GetKafkaConn(adsKafkaJson)
    if err != nil {
        log.Fatal(err)
    }

    // Get Kafka topic name
    topic, err := kafka_poc.GetKafkaTopic()
    if err != nil {
        log.Fatal(err)
    }

    // Create a producer
    producer, err := kafka_poc.NewProducer(kafkaConn)
    if err != nil {
        log.Fatal(err)
    }

    // Publish a message
    logger.Infow(
        "Publishing messages to Kafka ...",
        "type", "status_update",
    )

    input_msg := messages.Hello{
        Hello: "Hello, world!",
    }
    for {
        err := kafka_poc.Publish(topic, input_msg, producer)
        if err != nil {
            log.Fatal(err)
        }
    }
}
