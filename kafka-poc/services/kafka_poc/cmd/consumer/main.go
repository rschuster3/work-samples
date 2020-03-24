package main


import (
    "fmt"
    "os"

    "some-repo/services/kafka_poc"
)


func main() {
    // Get Kafka service info from ADS
    kafkaStr := kafka_poc.GetKafkaInfo()
    kafkaConn := kafka_poc.GetKafkaConn(kafkaStr)

    // Get topic
    topic := kafka_poc.GetKafkaTopic()

    // Create a consumer
    partitionConsumer, err := kafka_poc.NewConsumer(topic, kafkaConn)
    if err != nil {
        fmt.Println("Failed to create Sarama partition consumer:", err)
    }

    fmt.Println("Waiting for messages...")

    // Grab the message
    output_msg := <-partitionConsumer.Messages()

    // Write message to a file we can pick up later
    f, err := os.Create("hello.txt")
    if err !=nil {
	fmt.Println(err)
	return
    }
    _, err = f.WriteString(string(output_msg.Value))
    if err != nil {
	fmt.Println(err)
	f.Close()
	return
    }
    err = f.Close()
    if err != nil {
        fmt.Println(err)
	return
    }
}
