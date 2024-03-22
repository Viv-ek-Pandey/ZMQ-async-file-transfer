#!/bin/bash
# prerequisite
# Deploy sample database classicmodels
# Set the DB_HOST, DB_USER and DB_PASS
# To start multiple thread, change the START_CUSTOMER_NUMBER and START_EMPLOYEE_NUMBER as per thread and then start

DB_USER=""
DB_PASS=""
DB_NAME="classicmodels"
DB_HOST=""

# Initial customerNumber
START_CUSTOMER_NUMBER=60000
START_EMPLOYEE_NUMBER=60000

# Function to generate and insert records
generate_records() {
    local customerNumber=$START_CUSTOMER_NUMBER
    local employeeNumber
    for i in {1..300}; do
        customerName="Sample Customer $i"
        contactLastName="Doe $i"
        contactFirstName="John $i"
        phone="555-1234-$i"
        addressLine1="123 Sample Street $i"
        addressLine2="Suite $i"
        city="Sample City"
        state="CA"
        postalCode="12345"
        country="USA"
        salesRepEmployeeNumber=1370  # Assuming a valid salesRepEmployeeNumber
        creditLimit="21000.00"


        lastName="Doe$i"
        firstName="John$i"
        extension="x$i"
        email="john.doe$i@example.com"
        officeCode="1"  # Assuming a valid officeCode exists
        reportsTo=1002   # Assuming this manager exists; adjust as needed
        jobTitle="Sales Rep"

        mysql -u"$DB_USER" -p"$DB_PASS" -h"$DB_HOST" "$DB_NAME" -e "INSERT INTO employees (employeeNumber, lastName, firstName, extension, email, officeCode, reportsTo, jobTitle) VALUES ('$employeeNumber', '$lastName', '$firstName', '$extension', '$email', '$officeCode', '$reportsTo', '$jobTitle');"
        ((employeeNumber++))


        # Insert SQL command
        mysql -u$DB_USER -p$DB_PASS -h$DB_HOST $DB_NAME -e "INSERT INTO customers (customerNumber, customerName, contactLastName, contactFirstName, phone, addressLine1, addressLine2, city, state, postalCode, country, salesRepEmployeeNumber, creditLimit) VALUES ('$customerNumber', '$customerName', '$contactLastName', '$contactFirstName', '$phone', '$addressLine1', '$addressLine2', '$city', '$state', '$postalCode', '$country', '$salesRepEmployeeNumber', '$creditLimit');" 
        # Increment customerNumber for next record
        ((customerNumber++))
    done
}

# Function to delete the records
delete_records() {
    # Adjust WHERE clause as necessary. This example targets the generated range.
    mysql -u$DB_USER -p$DB_PASS -h$DB_HOST $DB_NAME -e "DELETE FROM customers WHERE customerNumber >= $START_CUSTOMER_NUMBER AND customerNumber < $((START_CUSTOMER_NUMBER + 30000));"
    mysql -u"$DB_USER" -p"$DB_PASS" -h"$DB_HOST" "$DB_NAME" -e "DELETE FROM employees WHERE employeeNumber >= $START_EMPLOYEE_NUMBER AND employeeNumber < $(($START_EMPLOYEE_NUMBER + 30000));" 
}

# Main loop
while true; do
    generate_records
    echo "3000 records inserted."
    sleep 60 # Adjust sleep time as necessary for your use case

    delete_records
    echo "Records deleted."
    sleep 60 # Adjust sleep time as necessary for your use case
    # comment exit 
    exit 0
done

