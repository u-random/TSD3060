#!/bin/bash

# HEADERS
echo "Content-Type: text/xml"
echo ""

#printf()




# MARK: - OK!
# Function to parse XML using xmllint and xpath
parse_xml() {
    # $1 is expected to be the XML input
    # $2 is expected to be the XPath expression
    
    # XPath views the XML document as a tree of nodes
    echo "$1" | xmllint --xpath "$2" -
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


# MARK: - OK!
# Function to check credentials and create a session
login() {
    # Extract email and password from XML body
    local email=$(parse_xml "$HTTP_BODY" "//email/text()")
    local password=$(parse_xml "$HTTP_BODY" "//password/text()")
    local hashed_password=$(echo -n $password | sha256sum | cut -d ' ' -f 1)

    # Check credentials against the database
    local valid_credentials=$(sqlite3 $DATABASE_PATH "SELECT COUNT(*) FROM Bruker WHERE epostadresse='$email' AND passordhash='$hashed_password';")

    if [[ $valid_credentials -eq 1 ]]; then
        # Generate a session ID token with UUIDGEN
        local session_id=$(uuidgen)
        
        # Set a cookie header with the session_id
        echo "Set-Cookie: session_id=$session_id; Path=/; HttpOnly; Secure"

        # Store session ID in the database for the user
        sqlite3 $DATABASE_PATH "UPDATE Sesjon SET sesjonsID='$session_id' WHERE epostadresse='$email';"
        echo "<session>Logged in with sessionID: '$session_id'. Cookie set.</session>"
    else
        echo "<test>Dette er email: $email</test>"
        echo "<test>Dette er pass: $password</test>"
        echo "<test>Dette er hashen: $hashed_password</test>"
        echo "<error>Invalid credentials</error>"
    fi
}


# MARK: - OK!
# Function to logout a user
do_logout() {
    # Get session id from cookie
    local session_cookie=$(get_user | awk '{print $1}')
    # Get user belonging to session
    local user=$(get_user | awk '{print $2}')
    
    if [[ -n $session_cookie ]]; then
        # Invalidate the session in the database
        sqlite3 $DATABASE_PATH "UPDATE Sesjon SET sesjonsID=NULL WHERE sesjonsID='$session_id';"
        # Send a header to remove the cookie
        echo "Set-Cookie: session_id=; Path=/; HttpOnly; Secure; Expires=Thu, 01 Jan 1970 00:00:00 GMT"
        # Respond to confirm the user has been logged out
        echo "<response>User '$user' logged out</response>"
    fi
}


# MARK: - OK!
# Function to get a dikt from ID and return proper XML
get_dikt_from_id() {
    local diktID="$1"
    # Fetch the dikt with DiktID
    if [[ -n $diktID ]]; then
        # Validate that the variable is numeric
        if [[ $diktID =~ ^[0-9]+$ ]]; then
            local dikt=$(sqlite3 $DATABASE_PATH "SELECT dikt FROM Dikt WHERE diktID=$diktID;")
            # Prints Dikt if exists, error if not
            if [ -n "$dikt" ]; then
                dikt=$(escape_xml "$dikt")
                echo "<dikt id=\"$diktID\">$dikt</dikt>"
            else
                echo "<error>Dikt not found</error>"
            fi
        # Prints errormessage if diktID is not a number
        else
            echo "<error>Invalid Dikt ID. It has to be a number.</error>"
        fi
    # If no ID specified, send all dikt
    else
        local dikts=$(sqlite3 $DATABASE_PATH "SELECT diktID, dikt FROM Dikt;")
        echo "<diktene>"
        # SQLITE is pipe-seperated
        while IFS='|' read -r diktID dikt; do
            dikt=$(escape_xml "$dikt")
            echo "<dikt id=\"$diktID\">$dikt</dikt>"
        done <<< "$dikts"
        echo "</diktene>"
    fi
}


# MARK: - OK!
# Function to add a new dikt
add_dikt() {
    local new_dikt="$1"
    # Get user belonging to session
    local email=$(get_user | awk '{print $2}')
    
    # If the user is logged in
    if is_logged_in; then
        # Insert the new dikt into the database
        sqlite3 $DATABASE_PATH "INSERT INTO Dikt (dikt, epostadresse) VALUES ('$new_dikt', '$email');"
        
        echo "<message>SQLite database updated.</message>"
    else
        echo "<error>You're not logged in. Log in to add a new dikt.</error>"
    fi
}


# MARK: - OK!
# Function edit existing dikt
edit_dikt_from_id() {
    local diktID="$1"
    local new_title="$1"
    # Get session id from cookie
    local session_cookie=$(get_user | awk '{print $1}')
    # Get user belonging to session
    local email=$(get_user | awk '{print $2}')
    # Check if user is owner of dikt with ID = diktID
    local user_match=$(sqlite3 $DATABASE_PATH "SELECT COUNT(*) FROM Dikt WHERE epostadresse='$email' AND diktID='$diktID';")

    # If the user is logged in
    if is_logged_in; then
        if [[ $user_match -eq 1 ]]; then
            # Update dikt with new information
            sqlite3 $DATABASE_PATH "UPDATE Dikt (dikt, epostadresse) VALUES ('$new_dikt', '$email');"
            
            echo "<message>SQLite database updated.</message>"
        else
            echo "<error>You can't change someone elses dikt.</error>"
        fi
    else
        echo "<error>You're not logged in. Log in to edit dikts.</error>"
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

    # Check credentials against the database
    local valid_credentials=$(sqlite3 $DATABASE_PATH "SELECT COUNT(*) FROM Sesjon WHERE epostadresse='$email' AND sesjonsID='$session_cookie';")

    # If the user is logged in
    if [[ $valid_credentials -eq 1 ]]; then
        return 0 # Logged in
    else
        return 1 # Not logged in
    fi
}

# MARK: - OK!
# Get the current User based on session id in HTTP header
get_user() {
    # Get session id from cookie
        local session_cookie=$(printf "%s\n" "$HTTP_COOKIE" | grep -o 'session_id=[^;]*' | sed 's/session_id=//')

        # Check if session_cookie is set
        if [ -z "$session_cookie" ]; then
            echo "<error>No session</error>"
            return 1
        fi

        # Get user belonging to session
        local email=$(sqlite3 $DATABASE_PATH "SELECT epostadresse FROM Sesjon WHERE sesjonsID='$session_cookie';")

        # Check if email is retrieved
        if [ -z "$email" ]; then
            echo "<error>No user found</error>"
            return 1
        fi

        echo "$session_cookie $email"
}


DATA_DIR="./" # Data directory path
DATABASE_PATH="$DATA_DIR/DiktDatabase.db"

# RESTful routing logic
METHOD=$(echo "$REQUEST_METHOD")
URI=$(echo "$REQUEST_URI" | awk -F'?' '{print $1}')
QUERY_STRING=$(echo "$REQUEST_URI" | awk -F'?' '{print $2}')


# REST API logic
case $METHOD in
    # HTTP GET request. Matches SQL: SELECT
    GET)
        # Matches both /dikt and /dikt/{id} where {id} is a number
        if [[ "$URI" =~ ^/dikt(/([0-9]+))?$ ]]; then
            # Extract diktID if provided, else this will be an empty string
            diktID=${BASH_REMATCH[2]}
            get_dikt_from_id "$diktID"
        else
            echo "<error>Invalid request. Use /dikt for all dikts or /dikt/{id} for a specific dikt.</error>"
        fi
        ;;
    
    
    # HTTP POST request. Matches SQL: INSERT
    POST)
        read -r data
        # Login functionality
        case "$URI" in
            # Logoin logic
            /login)
                # Extract email and password from XML body
                EMAIL=$(parse_xml "$HTTP_BODY" "//email/text()")
                PASSWORD=$(parse_xml "$HTTP_BODY" "//password/text()")
                # Run my log-in function
                login "$EMAIL" "$PASSWORD"
                ;;


            # Logout logic
            /logout)
                # Run my logout function
                do_logout
                ;;
    

            # Adding a new dikt functionality
            /dikt)
                TITLE=$(parse_xml "$HTTP_BODY" "//dikt/text()")
                # Run my add function
                add_dikt "$TITLE"
                ;;

        esac
        ;;


    # HTTP PUT request. Matches SQL: UPDATE
    PUT)
        read -r data

        # Should match only when {id} is a number
        if [[ "$URI" =~ ^/dikt(/([0-9]+))$ ]]; then
            # Extract diktID if provided
            diktID=${BASH_REMATCH[2]}
            TITLE=$(parse_xml "$HTTP_BODY" "//dikt/text()")
            # Run my edit function
            edit_dikt_from_id "$diktID" "$TITLE"
        else
            echo "<error>Unable to update. {id} for dikt/{id} has to be a number.</error>"
        fi
        ;;


    # HTTP DELETE request. Matches SQL: DELETE
    DELETE)
        read -r data
        
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

