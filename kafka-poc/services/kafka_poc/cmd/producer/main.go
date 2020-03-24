package main


import (
    "fmt"

    "some-repo/services/kafka_poc"
)


func main() {
    // Get Kafka service info from ADS
    kafkaStr := kafka_poc.GetKafkaInfo()
    kafkaConn := kafka_poc.GetKafkaConn(kafkaStr)

    // Get topic
    topic := kafka_poc.GetKafkaTopic()

    // Create a producer
    producer, err := kafka_poc.NewProducer(kafkaConn)
    if err != nil {
        fmt.Println("Failed to start Sarama producer:", err)
    }

    // Publish a message
    input_msg := &kafka_poc.Hello{}
    input_msg.Hello = "Hello, world!"
    kafka_poc.Publish(topic, input_msg, producer)
}
