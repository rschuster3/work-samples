package main


import (
    "log"

    "github.com/golang/protobuf/proto"
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

    // Get Kafka service host:port
    kafkaConn, err := kafka_poc.GetKafkaConn(adsKafkaJson)
    if err != nil {
        log.Fatal(err)
    }

    // Get Kafka topic name
    topic, err := kafka_poc.GetKafkaTopic()
    if err != nil {
        log.Fatal(err)
    }

    // Create a consumer
    partitionConsumer, err := kafka_poc.NewConsumer(topic, kafkaConn)
    if err != nil {
        log.Fatal(err)
    }

    logger.Infow(
	"Waiting for messages...",
        "type", "status_update",
    )

    for {
        select {
        // Grab the message
        case outputMsg := <-partitionConsumer.Messages():
            receivedHello := &messages.Hello{}
            err := proto.Unmarshal(outputMsg.Value, receivedHello)
	    if err != nil {
                log.Fatal(err)
            }

            // Write message to the logs 
	    logger.Infow(
                receivedHello.GetHello(),
                "type", "kafka_message",
            )
        }
    }
}
