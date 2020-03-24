package kafka_poc


import (
    "bytes"
    "encoding/json"
    "io/ioutil"
    "os/exec"
    "strconv"
    "strings"

    "some-repo/services/meridian_utils"
)


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


func GetKafkaInfo() string {
    // Ping ADS to get Kafka service JSON
    cmd := exec.Command("curl", "-XGET", "http://some-cluster-ip/config/kafka.json")

    // Get the output ...
    var out bytes.Buffer
    cmd.Stdout = &out
    err := cmd.Run()
    meridian_utils.Check(err)
    return out.String()
}


func GetKafkaConn(kafkaStr string) string {
    // Parse ADS Kafka JSON to get host and port
    kafkaJson := &ADSKafkaJson{}
    json.Unmarshal([]byte(kafkaStr), &kafkaJson)
    host := kafkaJson.Kafka.Nodes[0].Host
    port := strconv.Itoa(kafkaJson.Kafka.Nodes[0].Port)
    kafkaConnArray := []string{host, port}
    return strings.Join(kafkaConnArray, ":")
}


func GetKafkaTopic() string {
    // Get the Kafka topic name
    // The topic is a shared K8S secret stored in a
    // volume mount.
    dat, err := ioutil.ReadFile("/etc/config/topic")
    meridian_utils.Check(err)
    return string(dat)
}
