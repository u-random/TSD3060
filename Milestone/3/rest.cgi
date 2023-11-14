#!/bin/bash

# HEADERS
echo "Content-Type: text/xml"


# MARK: - OK!
# Function to parse XML using xmllint and xpath
parse_xml() {
    # $1 is expected to be the XML input
    # $2 is expected to be the XPath expression
    # Execute xmllint and check for errors
    
    # Debug: Echo input XML and XPath
    #echo "XML Input: $1"
    #echo "XPath: $2"

    # Check if xmllint is available
    if ! command -v xmllint &> /dev/null; then
        write_body "Error: xmllint not found"
        return 1
    fi

    # Execute xmllint and capture any errors
    local result=$(echo "$1" | xmllint --xpath "$2" -)
    if [ $? -ne 0 ]; then
        write_body "xmllint error: $result"
        return 1
    fi

    echo "$result"
}


# MARK: - TODO!
# TODO: This could be used more in the following functions
# Special XML characters should be replaced
escape_xml() {
    local string="$1"
    string="${string//&/&amp;}"
    string="${string//</&lt;}"
    string="${string//>/&gt;}"
    string="${string//\"/&quot;}"
    string="${string//\'/&apos;}"
    echo "$string"
}


# MARK: - LOGIN
# Function to check credentials and create a session
do_login() {
    # Extract email and password from XML body
    local email=$(parse_xml "$HTTP_BODY" "//email/text()")
    local password=$(parse_xml "$HTTP_BODY" "//password/text()")
    local password_hash=$(echo -n $password | sha256sum | cut -d ' ' -f 1)

    # Check credentials against the database
    local valid_credentials=$(sqlite3 $DATABASE_PATH "SELECT COUNT(*) FROM Bruker WHERE epostadresse='$email' AND passordhash='$password_hash';")
    
    if [[ $valid_credentials -eq 1 ]]; then
        # Check if user is logged in
        if is_logged_in; then
            # Never sent
            write_body "<message>Hello, '$email'! You're already logged in!</message>"
        else
            # Generate a session ID token with UUIDGEN
            local session_cookie=$(uuidgen)
            
            # Set a cookie HEADER with the session_id
            echo "Set-Cookie: session_id=$session_cookie; Path=/; HttpOnly; Secure"

            # Store session ID in the database for the user
            sqlite3 $DATABASE_PATH "UPDATE Sesjon SET sesjonsID='$session_cookie' WHERE epostadresse='$email';"
            
            # Write welcome message
            write_body "<message>Welcome back, '$email'! You're logged in!</message>"
            echo "<debug>Cookie set with uuid: '$session_cookie'</debug>"
        fi
    else
        write_body "<error>Invalid credentials</error>"
    fi
}


# MARK: - OK!
# Function to logout a user
do_logout() {
    # Get the session cookie and user email from get_user function
    local user_data=$(get_user)
    # Get session id from cookie
    local session_cookie=$(echo "$user_data" | awk '{print $1}')
    # Get user belonging to session
    local email=$(echo "$user_data" | awk '{print $2}')
    
    # If user is logged in
    if is_logged_in; then
        # Invalidate the session in the database
        sqlite3 $DATABASE_PATH "UPDATE Sesjon SET sesjonsID=NULL WHERE sesjonsID='$session_cookie';"
        # Send a header to remove the cookie
        echo "Set-Cookie: session_id=; Path=/; HttpOnly; Secure; Expires=Thu, 01 Jan 1970 00:00:00 GMT"
        # Respond to confirm the user has been logged out
        write_body "<message>User '$email' logged out.</message>"
    else
        # Respond to confirm the user has been logged out
        write_body "<message>No session detected.</message>"
    fi
}


# MARK: - OK!
# Test if user is logged in and session is valid
is_logged_in() {
    # Get session id from cookie
    local session_cookie=$(printf "%s\n" "$HTTP_COOKIE" | grep -o 'session_id=[^;]*' | sed 's/session_id=//')
    
    # Check if session_cookie is set
    if [ -z "$session_cookie" ]; then
        return 1 # Not logged in if the session cookie is empty
    fi

    # Get user belonging to session
    local email=$(sqlite3 $DATABASE_PATH "SELECT epostadresse FROM Sesjon WHERE sesjonsID='$session_cookie';")

    # Check if session is set in database
    local valid_session=$(sqlite3 $DATABASE_PATH "SELECT COUNT(*) FROM Sesjon WHERE epostadresse='$email' AND sesjonsID='$session_cookie';")

    # If the user is logged in
    if [[ $valid_session -eq 1 ]]; then
        return 0 # Logged in
    else
        return 1 # Not logged in
    fi
}


# TODO: - Fix error handling
# Get the current User based on session id in HTTP header
get_user() {
    # Get session id from cookie environment variable
    local session_cookie=$(printf "%s\n" "$HTTP_COOKIE" | grep -o 'session_id=[^;]*' | sed 's/session_id=//')

    # Check if session_cookie is set
    if [ -z "$session_cookie" ]; then
        return 1
    fi

    # Get user belonging to session
    local email=$(sqlite3 $DATABASE_PATH "SELECT epostadresse FROM Sesjon WHERE sesjonsID='$session_cookie';")

    # Check if email is retrieved
    if [ -z "$email" ]; then
        return 1
    fi

    echo "$session_cookie $email"
}


# MARK: - GET DIKT
# Function to get a dikt from ID and return proper XML
get_dikt() {
    # Extract diktID from array variable Bash_rematch with result of regex match
    local diktID=${BASH_REMATCH[2]}
    # Fetch the dikt with DiktID
    if [[ -n $diktID ]]; then
        # Validate that the variable is numeric
        if [[ $diktID =~ ^[0-9]+$ ]]; then
            local single_output=$(sqlite3 $DATABASE_PATH "SELECT diktID, dikt, epostadresse FROM Dikt WHERE diktID=$diktID;")
            # Prints Dikt if exists, error if not
            if [ -n "$single_output" ]; then
                write_dikt "$single_output"
            else
                write_body "<error>Dikt not found</error>"
            fi
        # Prints errormessage if diktID is not a number
        else
            write_body "<error>Invalid Dikt ID. It has to be a number.</error>"
        fi
    # If no ID specified, send all dikt
    else
        local all_output=$(sqlite3 $DATABASE_PATH "SELECT diktID, dikt, epostadresse FROM Dikt;")
        write_dikt "$all_output"
    fi
}


# Small function for writing XML tables
write_dikt() {
    # Write root element with space above, to seperate from header
    write_body "<dikt>"
    # SQLITE is pipe-seperated
    while IFS='|' read -r diktID dikt email; do
        dikt=$(escape_xml "$dikt")
        echo "<id>$diktID</id><tittel>$dikt</tittel><epost>$email</epost>"
    done <<< "$1"
    echo "</dikt>"
}


# MARK: - ADD A NEW DIKT
add_dikt() {
    # Get session id from cookie environment variable
    local session_cookie=$(printf "%s\n" "$HTTP_COOKIE" | grep -o 'session_id=[^;]*' | sed 's/session_id=//')
    local new_title=$(parse_xml "$HTTP_BODY" "//title/text()")
    # Get user belonging to session
    local email=$(sqlite3 $DATABASE_PATH "SELECT epostadresse FROM Sesjon WHERE sesjonsID='$session_cookie';")
    
    # If the user is logged in
    if is_logged_in; then
        # Insert the new dikt into the database
        sqlite3 $DATABASE_PATH "INSERT INTO Dikt (dikt, epostadresse) VALUES ('$new_title', '$email');"
        
        write_body "<message>SQLite database updated.</message>"
    else
        write_body "<error>You're not logged in. Log in to add a new dikt.</error>"
    fi
}


# MARK: - EDIT EXISTING DIKT
edit_dikt_from_id() {
    # Extract diktID from array variable Bash_rematch with result of regex match
    local diktID=${BASH_REMATCH[2]}
    local new_title=$(parse_xml "$HTTP_BODY" "//title/text()")
    
    # Get the session cookie and user email from get_user function
    local user_data=$(get_user)
    # Get user belonging to session
    local email=$(echo "$user_data" | awk '{print $2}')
        
    # Check if user is owner of dikt with ID = diktID
    local user_match=$(sqlite3 $DATABASE_PATH "SELECT COUNT(*) FROM Dikt WHERE epostadresse='$email' AND diktID='$diktID';")

    # If the user is logged in
    if is_logged_in; then
        if [[ $user_match -eq 1 ]]; then
            # Update dikt with new information
            sqlite3 $DATABASE_PATH "UPDATE Dikt (dikt, epostadresse) VALUES ('$new_dikt', '$email');"
            
            write_body "<message>SQLite database updated.</message>"
        else
            write_body "<error>You can't change someone elses dikt.</error>"
        fi
    else
        write_body "<error>You're not logged in. Log in to edit dikts.</error>"
    fi
}


# MARK: - OK!
# This function is made to delete single dikts based on id
delete_dikt_from_id() {
    local diktID="$1"
    # Get session id from cookie
    local session_cookie=$(get_user | awk '{print $1}')
    # Get user belonging to session
    local email=$(get_user | awk '{print $2}')
    # Check if user is owner of dikt with ID = diktID. 1 if vaild
    local user_match=$(sqlite3 $DATABASE_PATH "SELECT COUNT(*) FROM Dikt WHERE epostadresse='$email' AND diktID='$diktID';")

    # If the user is logged in
    if is_logged_in; then
        if [[ $user_match -eq 1 ]]; then
            # Delete given dikt
            sqlite3 $DATABASE_PATH "DELETE FROM Dikt WHERE diktID=$diktID AND epostadresse='$email';"
            
            echo "<message>SQLite entry deleted.</message>"
        else
            echo "<error>You can't delete someone elses dikt.</error>"
        fi
    else
        echo "<error>You're not logged in. Log in to delete dikts.</error>"
    fi
}




write_body() {
    # Blank line to separate from header
    echo ""
    # First argument to function is message
    echo "$1"
}


# Data directory paths
DATA_DIR="./"
DATABASE_PATH="$DATA_DIR/DiktDatabase.db"

# RESTful routing logic
METHOD=$(echo "$REQUEST_METHOD")
URI=$(echo "$REQUEST_URI" | awk -F'?' '{print $1}')


# MARK: - CASE statement
# REST API logic
case $METHOD in
    # MARK: - HTTP GET request. Matches SQL: SELECT
    GET)
        # REGEX for URI to match: /dikt, /dikt/ and /dikt/{id} where {id} is a number.
        if [[ "$URI" =~ ^/dikt(/([0-9]+))?/?$ ]]; then
            # Run my function to get dikts
            get_dikt
        else
            write_body "<error>Invalid request. Use /dikt for all dikts or /dikt/{id} for a specific dikt.</error>"
        fi
        ;;
    
    
    # MARK: - HTTP POST request. Matches SQL: INSERT
    POST)
        read -r HTTP_BODY
        case "$URI" in
            /login)
                # Run my log in function
                do_login
                ;;

            /logout)
                # Run my log out function
                do_logout
                ;;
    
            /dikt)
                # Run my add new dikt function
                add_dikt
                ;;
        esac
        ;;


    # MARK: - HTTP PUT request. Matches SQL: UPDATE
    PUT)
        read -r HTTP_BODY
        # REGEX for URI to match: only when {id} is a number
        if [[ "$URI" =~ ^/dikt(/([0-9]+))$ ]]; then
            # Run my edit function
            edit_dikt_from_id
        else
            write_body "<error>Unable to update. {id} for dikt/{id} has to be a number.</error>"
        fi
        ;;


    # MARK: - HTTP DELETE request. Matches SQL: DELETE
    DELETE)
        read -r HTTP_BODY
        
        # Should match only when {id} is a number
        if [[ "$URI" =~ ^/dikt(/([0-9]+))$ ]]; then
            # Extract diktID if provided
            diktID=${BASH_REMATCH[2]}
            # Run my delete function
            delete_dikt_from_id "$diktID"
        else
            echo "<error>Cannot delete all dikts at once. {id} for dikt/{id} has to be a number.</error>"
        fi
        ;;
esac

