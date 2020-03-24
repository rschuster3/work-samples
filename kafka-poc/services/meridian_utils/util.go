package meridian_utils


import (
    "fmt"
)


func Check(e error) {
    if e != nil {
        LogError(e)
    }
}


func LogError(e error) {
    fmt.Println(e)
}
