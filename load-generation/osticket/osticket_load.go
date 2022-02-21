package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"time"
)

/**
Readme
This script will generate 5 tickets per minute on osticket system.
- For random ticket, data.json is loaded.
- primaryNodeURL : URL on which ticket will get generated.
- secondaryNodeURL: URL used if primary server is down.
-----------------------------------------------------------------------
Prerequisite
  Before starting the script.
	  - Generate API key in the osticket system
		- Add IP address from where script is going to execute in the allowed IPs of osticket API-Key.
		- Replace X-API-Key value with new API-key value
*/
var jsonData DummyData = DummyData{}
var primaryNodeURL = "http://52.13.175.40/osticket/api/tickets.json"
var secondaryNodeURL = "http://3.232.103.246/osticket/api/tickets.json"
var activeNode string = "Primary"
var index int = 0

func main() {
	file, err := os.OpenFile("automation.log", os.O_CREATE|os.O_APPEND|os.O_WRONLY, 0644)
	if err != nil {
		log.Fatal(err)
	}
	defer file.Close()

	log.SetOutput(file)
	log.Print("Logging to a file in Go!")
	i := 1
	fmt.Println("Starting ticket automation")
	LoadData()
	for i > 0 {
		for j := 1; j < 5; j++ {
			err := createTicket()
			if err != nil {
				changeSite()
			}
		}
		time.Sleep(1 * time.Minute)
	}
}

func createTicket() error {
	client := &http.Client{}
	url := primaryNodeURL
	if activeNode != "Primary" {
		url = secondaryNodeURL
	}
	log.Print("Creating new ticket on: ", url)
	payload := GetPayload()
	var jsonD = []byte(`{
		"alert": true,
		"autorespond": true,
		"source": "API",
		"name": "Datamotive",
		"email": "api@osticket.com",
		"phone": "3185558634X123",
		"ip": "123.211.233.122",
		"attachments": [],
		"message": "data:text/html,MESSAGE <b>` + payload.Message + `</b>",
		"subject": "` + payload.Subject + `"
	}`)

	req, err := http.NewRequest("POST", url, bytes.NewBuffer(jsonD))
	if err != nil {
		log.Println(err)
		return err
	}
	req.Header.Set("X-API-Key", "70D7A5F41E1053BDFC6E59CFC96995B4")
	req.Header.Add("Content-Type", "application/json; charset=UTF-8")

	response, err := client.Do(req)
	if err != nil {
		log.Println("ERROR: failed to connect ", url)
		return err
	} else {
		log.Println("Response ", response)
	}
	response.Body.Close()
	return nil
}

func changeSite() {
	if activeNode == "Primary" {
		activeNode = "Secondary"
		log.Print("Primary site not available, using secondary site")
	} else {
		activeNode = "Primary"
		log.Print("Secondary site not available, using primary site")
	}
}
func LoadData() {
	log.Print("loading json data")
	jsonFile, err := os.Open("data.json")
	// if we os.Open returns an error then handle it
	if err != nil {
		fmt.Println(err)
	}
	// defer the closing of our jsonFile so that we can parse it later on
	defer jsonFile.Close()

	// read our opened xmlFile as a byte array.
	byteValue, _ := ioutil.ReadAll(jsonFile)

	// we unmarshal our byteArray which contains our
	// jsonFile's content into 'users' which we defined above
	json.Unmarshal(byteValue, &jsonData.Data)
	log.Print("Json data loaded")
}

func GetPayload() TicketPayload {
	payload := TicketPayload{}
	index = index + 1
	if index > 200 {
		log.Print("Index limit reached resetting the limits")
		index = 0
	}
	payload.Subject = jsonData.Data[index].Title
	return payload
}

// Structs

type TicketPayload struct {
	Alert       bool     `json:"alert"`
	Autorespond bool     `json:"autorespond"`
	Source      string   `json:"source"`
	Name        string   `json:"name"`
	Email       string   `json:"email"`
	Phone       string   `json:"phone"`
	Subject     string   `json:"subject"`
	Ip          string   `json:"ip"`
	Message     string   `json:"Message"`
	Attachments []string `json:"attachments"`
}

type JSONData struct {
	Title      string
	Resolution string
}

type DummyData struct {
	Data []JSONData `json:"jSONData"`
}
