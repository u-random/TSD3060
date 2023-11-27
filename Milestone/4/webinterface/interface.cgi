#!/bin/bash

# Tux surprise
hello_tux() {
echo "Content-Type: text/plain"
echo "Connection: close"
echo ""

cat << "EOF"
         _nnnn_
        dGGGGMMb     ,"""""""""""""".
       @p~qp~~qMb    | Linux Rules! |
       M|@||@) M|   _;..............'
       @,----.JM| -'
      JS^\__/  qKL
     dZP        qKRb
    dZP          qKKb
   fZP            SMMb
   HZM            MMMM
   FqM            MMMM
 __| ".        |\dS"qML
 |    `.       | `' \Zq
_)      \.___.,|     .'
\____   )MMMMMM|   .'
     `-'       `--'



Figure from: https://www.asciiart.eu/computers/linux
EOF
}


# Small function to write header
write_headers() {
    echo "Content-type: text/xml"
    echo ""
}


# MARK: - LOGIN OK
do_login() {
    # Use awk to parse the email and password values
    local email=$(echo "$HTTP_BODY" | awk -F'[=&]' '{for(i=1; i<=NF; i++) if ($i == "email") {print $(i+1); break}}')
    local password=$(echo "$HTTP_BODY" | awk -F'[=&]' '{for(i=1; i<=NF; i++) if ($i == "password") {print $(i+1); break}}')
    
    # Login and Write return to browser
    write_headers
    curl -c ~/cookies.txt -b ~/cookies.txt -X POST -H "Content-Type: text/xml" -d "<login><email>$email</email><password>$password</password></login>" restapi/login
}


# MARK: - LOGOUT OK
do_logout() {
    # Logout and Write return to browser
    write_headers
    curl -b ~/cookies.txt -X POST -H "Content-Type: text/xml" restapi/logout
}


# MARK: - GET DIKTS V
get_dikt() {
# Parse diktID from HTML form
local diktID=$(echo "$HTTP_BODY" | awk -F'[=&]' '{for(i=1; i<=NF; i++) if ($i == "diktID") {print $(i+1); break}}')

# Is DiktID defined
if [[ -n $diktID ]]; then
    # Validate that the variable is numeric
    if [[ $diktID =~ ^[0-9]+$ ]]; then
        write_headers
        curl "restapi/dikt/$diktID"
    fi
# If no ID specified, request all dikt
else
    write_headers
    curl restapi/dikt
fi
}


# MARK: - ADD NEW DIKT V
add_dikt() {
    # Parse new title
    local title=$(echo "$HTTP_BODY" | awk -F'[=&]' '{for(i=1; i<=NF; i++) if ($i == "title") {print $(i+1); break}}')

    # Add dikt and Write return to browser
    write_headers
    curl -b ~/cookies.txt -X POST -H "Content-Type: text/xml" -d "<title>$title</title>" restapi/dikt
}


# MARK: - EDIT DIKT V
edit_dikt_from_id() {
    # Parse new title
    local diktID=$(echo "$HTTP_BODY" | awk -F'[=&]' '{for(i=1; i<=NF; i++) if ($i == "diktID") {print $(i+1); break}}')
    local title=$(echo "$HTTP_BODY" | awk -F'[=&]' '{for(i=1; i<=NF; i++) if ($i == "title") {print $(i+1); break}}')

    # Edit dikt and Write return to browser
    write_headers
    curl -b ~/cookies.txt -X PUT -H "Content-Type: text/xml" -d "<dikt><title>$title</title></dikt>" "restapi/dikt/$diktID"
}


# MARK: - DELETE DIKT V
delete_dikt_from_id() {
    # Parse diktID
    local diktID=$(echo "$HTTP_BODY" | awk -F'[=&]' '{for(i=1; i<=NF; i++) if ($i == "diktID") {print $(i+1); break}}')
    # Delete dikt and Write reply to browser
    write_headers
    curl -b ~/cookies.txt -X DELETE "restapi/dikt/$diktID"
}


# GET info from headers
METHOD=$(echo "$REQUEST_METHOD")
URI=$(echo "$REQUEST_URI" | awk -F'?' '{print $1}')


# MARK: - CASE statement OK
read -r HTTP_BODY
case $METHOD in
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
                
            /surprise)
                # Run my surprise function
                hello_tux()
                ;;
        esac
        ;;

esac
