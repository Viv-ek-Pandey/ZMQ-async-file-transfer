package main

import (
	"fmt"
	"log"

	"github.com/jinzhu/gorm"
	_ "github.com/jinzhu/gorm/dialects/mysql"
	"go.uber.org/zap"
)

var (
	mysqlDB *gorm.DB
	logger  *zap.SugaredLogger
)


/* 
	Run this utility on the management node to remove all the AWS inbuilt tag associations from the system
*/

func main() {
	// Set up Zap logger
	zapLogger, _ := zap.NewProduction()
	defer zapLogger.Sync()
	logger = zapLogger.Sugar()

	// Hardcoded database connection details
	dbUser := "root"
	dbPassword := "321@vitomataD"
	dbHost := "127.0.0.1"
	dbPort := "3308"
	dbName := "datamotive"

	// Connect to DB
	err := connectDB(dbUser, dbPassword, dbHost, dbPort, dbName)
	if err != nil {
		logger.Fatalf("Database connection failed: %v", err)
	}
	defer closeDB()

	// Delete rows with key = "aws"
	if err := deleteAWSKeys(); err != nil {
		logger.Fatalf("Failed to delete rows: %v", err)
	}

	logger.Info("Deleted rows with key = 'aws:' from tags table successfully.")
}

func connectDB(user, password, host, port, dbName string) error {
	connStr := fmt.Sprintf("%s:%s@tcp(%s:%s)/%s?charset=utf8&parseTime=True",
		user, password, host, port, dbName)

	var err error
	mysqlDB, err = gorm.Open("mysql", connStr)
	if err != nil {
		log.Printf("Failed to connect to database: %v", err)
		return err
	}
	logger.Info("Connected to database successfully.")
	return nil
}

func deleteAWSKeys() error {
	result := mysqlDB.Where("`key` LIKE ?", "aws:%").Delete(&mos.Tags{})
	if result.Error != nil {
		return result.Error
	}
	logger.Infof("Deleted %d rows from tags table where key starts with 'aws:'", result.RowsAffected)
	return nil
}

func closeDB() {
	if err := mysqlDB.Close(); err != nil {
		logger.Errorf("Failed to close DB: %v", err)
	}
}
