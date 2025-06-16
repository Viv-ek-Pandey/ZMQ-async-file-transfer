package main

import (
	"database/sql"
	"flag"
	"fmt"
	"log"

	_ "github.com/go-sql-driver/mysql"
)

func main() {
	vmName := flag.String("vm", "", "VM name")
	planID := flag.Int("plan", 0, "Protection plan ID")
	flag.Parse()

	if *vmName == "" || *planID == 0 {
		log.Fatal("Both -vm and -plan parameters are required")
	}

	dsn := "root:321@evitomataD@tcp(127.0.0.1:3308)/datamotive"
	db, err := sql.Open("mysql", dsn)
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}
	defer db.Close()

	queries := []string{
		fmt.Sprintf(`UPDATE disk_replication_job_infos SET reset_iteration = 0 WHERE vm_name='%s' AND reset_iteration = 1`, *vmName),
		fmt.Sprintf(`UPDATE vm_replication_job_infos SET reset_iteration = 0 WHERE vm_name='%s' AND reset_iteration = 1`, *vmName),
		fmt.Sprintf(`UPDATE vm_recovery_job_infos SET status='failed',failure_message='Recovery status reset by the user' WHERE vm_name='%s' AND status='completed' ORDER BY id DESC LIMIT 1`, *vmName),
		fmt.Sprintf(`UPDATE protection_plan_recovery_job_infos SET status='partially-completed' WHERE protection_plan_id=%d ORDER BY id DESC LIMIT 1`, *planID),
		fmt.Sprintf(`UPDATE virtual_machines SET recovery_status = '' WHERE name='%s'`, *vmName),
		fmt.Sprintf(`UPDATE protection_plans SET recovery_status = '' WHERE id=%d`, *planID),
	}

	for _, query := range queries {
		res, err := db.Exec(query)
		if err != nil {
			log.Printf("Error executing query: %s\nError: %v", query, err)
		} else {
			affected, _ := res.RowsAffected()
			log.Printf("Query successful: %s\nRows affected: %d", query, affected)
		}
	}
}

