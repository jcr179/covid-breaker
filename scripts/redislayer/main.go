package main 

import (
	"redislayer/util"
	"encoding/json"
	"fmt"
	"os/exec"
	"os"
	"path"
	"reflect"
	"log"
	
	"context"
	"strings"
	"bytes"
	"github.com/elastic/go-elasticsearch/v8"
	//"github.com/elastic/go-elasticsearch/v8/esapi"	
)

func main() {
	
	// Make sure to have a Redis instance running; run 'redis-server' !
	
	pool := util.CreatePool(10, 100)
	conn := pool.Get()
	defer conn.Close() // close connection when main() ends
	
	testKey := "key0"
	var testVec [768]float64
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
	
	
	// START: Testing redis as cache 
	numHits := 5
	testKey = "attenuation strategies" 
	//var testVec [768]float64
	//testValJson = util.Paragraph{Title: "Watchmen", Authors: "Alan Moore", Abstract: "Who watches the Watchmen?", Text: "The Comedian is dead", Text_vector: testVec, Paper_id: "112358j"}
	//testVal = util.SetIn{testKey, testValJson}	
	
	// Check if key1 (a search query) exists (it should not)
	exists, err := util.Exists(conn, testKey)
	fmt.Println(exists)
	
	// Since key1 doesn't exist, return the result from ES and set key1 in redis 
	// get embedding vector of testKey
	wd, err := os.Getwd()
	cmd := exec.Command(path.Join(wd, "get_embeddings.sh"), testKey) // append the key as command line argument
	out, err := cmd.Output()

	if err != nil {
		fmt.Println(err.Error())
		return
	}

	//fmt.Println("Output from Python script:")
	//fmt.Println(string(out))

	// do similarity search and return top 5 results
	es, err := elasticsearch.NewDefaultClient()
	if err != nil {
		log.Fatalf("Error creating the client: %s", err)
	}
	
	var mapResp map[string]interface{}
	var buf bytes.Buffer
	
	var json_query = `{
  "query": {
    "script_score": {
	"query": {"match_all": {}},
      "script": {
        "source": "cosineSimilarity(params.query_vector, \u0027text_vector\u0027) + 1.0", 
        "params": {
          "query_vector": ` + string(out) + `}
      }
    }
  }
}
`

	// array to hold new hits to make new value
	newHits := make([]util.Paragraph, numHits)

	// Concatenate a string from query for reading
	var b strings.Builder
	b.WriteString(json_query)
	read := strings.NewReader(b.String())
	
	if err2 := json.NewEncoder(&buf).Encode(read); err2 != nil {
	log.Fatalf("Error encoding query: %s", err2)

	// Query is a valid JSON object
	}
	
	ctx := context.Background()
	
	res, err := es.Search(
	es.Search.WithContext(ctx),
	es.Search.WithIndex("test_bert"),
	es.Search.WithBody(read),
	es.Search.WithTrackTotalHits(true),
	es.Search.WithPretty(),
	es.Search.WithSize(numHits),
	)
	
	// Check for any errors returned by API call to Elasticsearch
	if err != nil {
	log.Fatalf("Elasticsearch Search() API ERROR:", err)

	// If no errors are returned, parse esapi.Response object
	} else {
	fmt.Println("res TYPE:", reflect.TypeOf(res))

	// Close the result body when the function call is complete
	defer res.Body.Close()

	// Decode the JSON response and using a pointer
	if err := json.NewDecoder(res.Body).Decode(&mapResp); err != nil {
	log.Fatalf("Error parsing the response body: %s", err)

	// If no error, then convert response to a map[string]interface
	} else {
	fmt.Println("mapResp TYPE:", reflect.TypeOf(mapResp), "\n")


	// what are the keys in the response
	//for a, b := range mapResp {
	//	fmt.Println(a, b)
	//}





	// Iterate the document "hits" returned by API call
	for idx, hit := range mapResp["hits"].(map[string]interface{})["hits"].([]interface{}) {

	// Parse the attributes/fields of the document
	doc := hit.(map[string]interface{})

	// The "_source" data is another map interface nested inside of doc
	source := doc["_source"]
	fmt.Println("doc _source:", reflect.TypeOf(source))

	// Get the document's _id and print it out along with _source data
	docID := doc["_id"]
	fmt.Println("docID:", docID)
	//fmt.Println("_source:", source, "\n")
	
	b, err := json.Marshal(source)
	
	if err != nil {
		fmt.Println("marshal error")
	}
	
	answer = util.Paragraph{}
	err = json.Unmarshal(b, &answer)
	if err != nil {
		  fmt.Println("unmarshal error")
	}

	//fmt.Println(answer.Title)
	//fmt.Println(answer.Text)
	//fmt.Println(answer.Paper_id)
	
	newHits[idx] = answer
	
	
	} // end of response iteration
	
	
}}

	// add new thing to redis cache
	
	// todo: so, you get top 5 results back. what do you actually cache for each key/search term?
	fmt.Println("newHits:")
	for _, ans := range newHits {
		fmt.Println(ans.Text)
	}
	
	newStoreValues := make([]util.StoreValue, numHits)
	
	for idx := 0; idx < numHits; idx++ {
		newStoreValues[idx] = util.StoreValue{newHits[idx].Title, newHits[idx].Authors, newHits[idx].Abstract, newHits[idx].Text}
	}
	
	for idx := 0; idx < numHits; idx++ {
		fmt.Println(newStoreValues[idx])
	}
	
	testVal = util.SetIn{testKey, newStoreValues}
	
	// set it
	err = util.Set(conn, testVal)
	if err != nil {
		fmt.Println(err)
	}
	
	
	
	// it should exist now 
	exists, err = util.Exists(conn, testKey)
	fmt.Println("exists: ", exists)
	
	// get and print
	ret_val, err = util.Get(conn, testKey)
	if err != nil {
		fmt.Println(err)
	}
	
	fmt.Println(string(ret_val))
	
	// map[string]interface{} to json:
	/*
	enc := json.NewEncoder(os.Stdout)
	err = enc.Encode(m)
	if err != nil {
		fmt.Println(err.Error())
	}
	fmt.Println(enc)
	*/
}
