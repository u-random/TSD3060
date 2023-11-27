#!/bin/sh

# HEADERS
echo "Content-Type: text/html"
echo "Connection: close"
echo ""

# Fremdriftsmåte for interface

# 1. Show HTML forms for all REST actions

# 2. Do HTML form GET and POST to interface server
# - Parse out return from forms into XML
# - Send XML curl request to REST API

# 3. Recieve reply from REST API

# - Forward all replies to new XML page. To send new form, need to return to previous page.
# - Might have to store session cookie temporarily, or forward from browser and API


# MARK: - LOGIN V
# Function to check credentials and create a session
do_login() {
    echo "Login  called"
    
    # Input string from the HTML form post
    input_string="$HTTP_BODY"
    
    # Use awk to parse the email and password values
    email=$(echo "$input_string" | awk -F'&' '{split($1, a, "="); print a[2]}')
    password=$(echo "$input_string" | awk -F'&' '{split($2, a, "="); print a[2]}')

    # Print the parsed values
    echo "Email: $email"
    echo "Password: $password"

}


# MARK: - LOG USER OUT V
# Function to logout a user
do_logout() {
    
echo "Logout  called"
echo "Recieved: $HTTP_BODY"
}


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
echo "Get dikt called"
echo "Recieved: $HTTP_BODY"
diktID=
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
echo "ADD dikt called"
echo "Recieved: $HTTP_BODY"

title=
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
echo "Edit dikt called"
echo "Recieved: $HTTP_BODY"

diktID=&title=
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
echo "Delete dikt called"
echo "Recieved: $HTTP_BODY"

Parse diktID=X
}


# RESTful routing logic
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
