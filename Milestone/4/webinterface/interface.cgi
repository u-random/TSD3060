#!/bin/bash

# HEADERS
#echo "Content-Type: text/plain"
#echo "Connection: close"
#echo ""

# Fremdriftsmåte for interface

# 1. Show HTML forms for all REST actions

# 2. Do HTML form GET and POST to interface server
# - Parse out return from forms into XML
# - Send XML curl request to REST API

# 3. Recieve reply from REST API

# - Forward all replies to new XML page. To send new form, need to return to previous page.
# - Might have to store session cookie temporarily, or forward from browser and API


# The HTML forms sends a message with body in this format:
# application/x-www-form-urlencoded

# MARK: - LOGIN V
# Function to check credentials and create a session
do_login() {
    # TODO: Login does not save cookie
    #echo "Login called"
    
# ChatGPT AWK command description
#-F'[=&]'                   :   Sets the field separator to either = or &, effectively
#                               splitting the string into fields based on these
#                               delimiters, commonly used in URL query parameters.
#{for(i=1; i<=NF; i++) ... }:   Iterates over all fields in the input string.
#if ($i == "title")         :   Checks if the current field equals "title".
#{print $(i+1); break}      :   If "title" is found, prints the next field (which is the
#                               value of "title") and then exits the loop (for
#                               efficiency).
    
    # Use awk to parse the email and password values
    #local email=$(echo "$HTTP_BODY" | awk -F'&' '{split($1, a, "="); print a[2]}')
    local email=$(echo "$HTTP_BODY" | awk -F'[=&]' '{for(i=1; i<=NF; i++) if ($i == "email") {print $(i+1); break}}')
    #local password=$(echo "$HTTP_BODY" | awk -F'&' '{split($2, a, "="); print a[2]}')
    local password=$(echo "$HTTP_BODY" | awk -F'[=&]' '{for(i=1; i<=NF; i++) if ($i == "password") {print $(i+1); break}}')
    
    # Run curl post login
    echo "$(curl -c ~/cookies.txt -b ~/cookies.txt -X POST -H "Content-Type: text/xml" -d "<login><email>$email</email><password>$password</password></login>" restapi/login)"
    
    #DEBUG
    # Print the parsed values
    #echo "Email: $email"
    #echo "Password: $password"

}


# MARK: - LOG USER OUT V
# Function to logout a user
do_logout() {
    
#echo "Logout  called"
#echo "Recieved: $HTTP_BODY"

    # Run curl post logout
    echo "$(curl -b ~/cookies.txt -X POST -H "Content-Type: text/xml" http://localhost/logout)"
}


# MARK: - Parse out cookie V
# Function to logout a user
#parse_cookie() {
#
#
#
#}




# TODO: - How to check for logged in status?

# MARK: - GET DIKT, ONE OR ALL V
# Function to get a dikt from ID and return proper XML
get_dikt() {
# What to do:
# BEGIN
# 1. Check if dikt ID is provided from html form
# - If it is, send curl get with id to restapi
# - Forward reply from api to browser
# 2. If no dikt id
# - Send curl get with all dikts
# - Forward reply from api to browser
# END
#echo "Get dikt called"
#echo "Recieved: $HTTP_BODY"

# Parse diktid
#local diktID=$(echo "$HTTP_BODY" | awk -F'&' '{split($1, a, "="); print a[2]}')
local diktID=$(echo "$HTTP_BODY" | awk -F'[=&]' '{for(i=1; i<=NF; i++) if ($i == "diktID") {print $(i+1); break}}')

# Is DiktID defined
if [[ -n $diktID ]]; then
    # Validate that the variable is numeric
    if [[ $diktID =~ ^[0-9]+$ ]]; then
        local single_dikt = $(curl -i "restapi/dikt/$diktID")
        echo "$single_dikt"
    fi
# If no ID specified, request all dikt
else
    local all_dikt = $(curl -i restapi/dikt)
    echo "$all_dikt"
fi
}


# MARK: - ADD A NEW DIKT V
add_dikt() {
# What to do:
# BEGIN
# 1. Find title from HTML form
# - send curl post with title to restapi
# - Forward reply from api to browser
# - If empty, restapi will provide xml error message
# END
#echo "ADD dikt called"
#echo "Recieved: $HTTP_BODY"

# Parse new title
local title=$(echo "$HTTP_BODY" | awk -F'[=&]' '{for(i=1; i<=NF; i++) if ($i == "title") {print $(i+1); break}}')

# Run curl post dikt
echo "$(curl -b ~/cookies.txt -X POST -H "Content-Type: text/xml" -d "<title>$title</title>" restapi/dikt)"

}


# MARK: - EDIT AN EXISTING DIKT V
edit_dikt_from_id() {
# What to do:
# BEGIN
# 1. Find title and ID from HTML form
# - send curl put with title and id to restapi
# - Forward reply from api to browser
# - If empty slots, restapi will provide xml error message
# END
#echo "Edit dikt called"
#echo "Recieved: $HTTP_BODY"

# Parse new title
local diktID=$(echo "$HTTP_BODY" | awk -F'[=&]' '{for(i=1; i<=NF; i++) if ($i == "diktID") {print $(i+1); break}}')
local title=$(echo "$HTTP_BODY" | awk -F'[=&]' '{for(i=1; i<=NF; i++) if ($i == "title") {print $(i+1); break}}')

# Run curl Put dikt
echo "$(curl -b ~/cookies.txt -X PUT -H "Content-Type: text/xml" -d "<dikt><title>$title</title></dikt>" "restapi/dikt/$diktID")"
}


# MARK: - DELETE A DIKT V
# This function is made to delete single dikts based on id
delete_dikt_from_id() {
# What to do:
# BEGIN
# 1. Find ID from HTML form
# - send curl DELETE with id to restapi
# - Forward reply from api to browser
# - If empty slots, restapi will delete all belonging to user
# END
#echo "Delete dikt called"
#echo "Recieved: $HTTP_BODY"

# Parse diktID
local diktID=$(echo "$HTTP_BODY" | awk -F'[=&]' '{for(i=1; i<=NF; i++) if ($i == "diktID") {print $(i+1); break}}')

echo "$(curl -b ~/cookies.txt -X DELETE "restapi/dikt/$diktID")"

}


# GET info from headers
METHOD=$(echo "$REQUEST_METHOD")
URI=$(echo "$REQUEST_URI" | awk -F'?' '{print $1}')


# MARK: - CASE statement V
# REST API logic
read -r HTTP_BODY
case $METHOD in
    # MARK: - HTTP POST request.
    POST)
        case "$URI" in
            /login)
                # Run my log in function
                do_login
                ;;

            /logout)
                # Run my log out function
                do_logout
                ;;
    
            /dikt/get)
                # Run my function to get dikts
                get_dikt
                ;;
            /dikt/add)
                # Run my add new dikt function
                add_dikt
                ;;

            /dikt/edit)
                # Run my edit function
                edit_dikt_from_id
                ;;

            /dikt/delete)
                # Run my delete function
                delete_dikt_from_id
                ;;
        esac
        ;;

esac
