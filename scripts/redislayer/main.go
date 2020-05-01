package main 

import (
	"redislayer/util"
	"encoding/json"
	"fmt"
)

func main() {
	
	// Make sure to have a Redis instance running; run 'redis-server' !
	
	pool := util.CreatePool(10, 100)
	conn := pool.Get()
	defer conn.Close() // close connection when main() ends
	
	testKey := "key0"
	testVec := [3]float64{3.14, -1.2, 0.0}
	testValJson := util.Paragraph{Title: "test title", Authors: "test authors", Abstract: "test abstract", Text: "test text", Text_vector: testVec, Paper_id: "test paper_id"}
	testVal := util.SetIn{testKey, testValJson}

	// call Redis PING command to test connectivity
	err := util.Ping(conn)
	if err != nil {
		fmt.Println(err)
	}

	// set demonstrates the redis SET command using a simple
	// string key:value pair
	err = util.Set(conn, testVal)
	if err != nil {
		fmt.Println(err)
	}

	// set demonstrates the redis GET command
	ret_val, err := util.Get(conn, testKey)
	if err != nil {
		fmt.Println(err)
	}
	
	answer := util.Paragraph{}
	err = json.Unmarshal(ret_val, &answer)
	fmt.Println(answer.Title)
	fmt.Println(answer.Authors)
	fmt.Println(answer.Abstract)
	fmt.Println(answer.Text)
	fmt.Println(answer.Text_vector)
	fmt.Println(answer.Paper_id)

}
