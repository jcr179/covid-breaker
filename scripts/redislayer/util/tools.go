package util

import (
	"fmt"
	"github.com/gomodule/redigo/redis"
	"encoding/json"
)

type SetIn struct {
	Key 		string
	Val 		interface{}
}

type Paragraph struct {
	Title 		string
	Authors 	string 
	Abstract 	string
	Text 		string
	Text_vector [3]float64 // 768
	Paper_id 	string
}

func CreatePool(idle int, active int) *redis.Pool {
	return &redis.Pool{
		// Maximum number of idle connections in the pool.
		MaxIdle: idle, // 10
		// max number of connections
		MaxActive: active, // 100
		// Dial is an application supplied function for creating and
		// configuring a connection.
		Dial: func() (redis.Conn, error) {
			c, err := redis.Dial("tcp", ":6379")
			if err != nil {
				panic(err.Error())
			}
			return c, err
		},
	}
}

// Test connectivity for redis (PONG should be returned)
func Ping(c redis.Conn) error {

	s, err := redis.String(c.Do("PING"))
	if err != nil {
		return err
	}

	fmt.Printf("Response: %s\n", s)

	return nil
}

// Set key/value
func Set(c redis.Conn, s SetIn) error {
	
	json, err0 := json.Marshal(s.Val)
	
	if err0 != nil {
		return fmt.Errorf("Error marshalling key '%s': %v\n", s.Key, err0)
	}
	
	_, err := c.Do("SET", s.Key, json)
	
	if err != nil {
		return fmt.Errorf("Error setting key '%s': %v\n", s.Key, err)
	}
	
	return nil
}

// Set key/value WITH expire time
func SetExp(c redis.Conn, s SetIn, expire_time int) error {
	
	json, err0 := json.Marshal(s.Val)
	
	if err0 != nil {
		return fmt.Errorf("Error marshalling key '%s': %v\n", s.Key, err0)
	}
	
	_, err := c.Do("SET", s.Key, json, "EX", expire_time)
	
	if err != nil {
		return fmt.Errorf("Error setting key '%s': %v\n", s.Key, err)
	}
	
	return nil
	
}

// Get key as byte array
func Get(c redis.Conn, key string) ([]byte, error) {

	val, err := redis.Bytes(c.Do("GET", key))
	
	if err != nil {
		return nil, fmt.Errorf("Error getting key '%s': %v\n", key, err)
	}
	
	return val, err
}

// Check if key exists
func Exists(c redis.Conn, key string) (bool, error) {

    ok, err := redis.Bool(c.Do("EXISTS", key))
    if err != nil {
        return ok, fmt.Errorf("Error checking if key '%s' exists: %v\n", key, err)
    }
    return ok, err
}

// Delete key
func Delete(c redis.Conn, key string) error {

    _, err := c.Do("DEL", key)
    if err != nil {
        return fmt.Errorf("Error deleting key '%s': %v\n", key, err)
    }
    return err
}


// s := strings.TrimSpace("\t Hello world!\n ") to trim leading/trailing whitespace 
