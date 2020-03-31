package kafka_poc


import (
    "encoding/json"
    "errors"
    "fmt"
    "net/http"
    "os"
    "strconv"
    "strings"
)


var client = http.DefaultClient
var topic = os.Getenv("TOPIC")
var aruba_discovery_service = os.Getenv("ARUBA_DISCOVERY_SERVICE")


// Create an error type to tell us a bit about erroring requests
type reqErr struct {
    status_code int
}
func (e *reqErr) Error() string {
    return fmt.Sprintf("Request returned status code %d", e.status_code)
}


// Structure to store Kafka service info
type ADSKafkaJson struct {
    Kafka struct {
        Nodes []struct {
            Host      string `json:"host"`
            Port      int    `json:"port"`
            Clusterip string `json:"clusterip"`
        } `json:"nodes"`
        MonPostfix string `json:"mon_postfix"`
    } `json:"kafka"`
}


func GetKafkaInfo() (ADSKafkaJson, error) {
    var adsKafkaJson ADSKafkaJson
    kafka_conf := 'http://' + aruba_discovery_service + '/config/kafka.json'

    // Ping ADS to get Kafka service JSON
    req, err := http.NewRequest(
        http.MethodGet,
	kafka_conf,
	nil,
    )
    if err != nil {
        return adsKafkaJson, nil
    }

    // Make the request and check it
    resp, err := client.Do(req)
    if err != nil {
        return adsKafkaJson, nil
    }

    if resp.StatusCode > 399 {
	return adsKafkaJson, &reqErr{resp.StatusCode}
    }

    // Read from request body and close when done
    defer resp.Body.Close()
    decoder := json.NewDecoder(resp.Body)

    err = decoder.Decode(&adsKafkaJson)
    if err != nil {
        return adsKafkaJson, nil
    }

    return adsKafkaJson, nil
}


func GetKafkaConn(adsKafkaJson ADSKafkaJson) (string, error) {
    // Parse ADS Kafka JSON to get host and port
    // Make sure we have nodes
    if len(adsKafkaJson.Kafka.Nodes) < 1 {
        err := errors.New("No nodes given in ADS output.")
	return "", err
    }

    // Get the host and port
    host := adsKafkaJson.Kafka.Nodes[0].Host
    port := strconv.Itoa(adsKafkaJson.Kafka.Nodes[0].Port)

    // Concatenate into a final string host:port
    kafkaConnArray := []string{host, port}
    return strings.Join(kafkaConnArray, ":"), nil
}


func GetKafkaTopic() (string, error) {
    // Log fatal error if no env variable
    if len(topic) == 0 {
      err := errors.New("No value for env var TOPIC.")
      return "", err
    }

    return topic, nil
}
