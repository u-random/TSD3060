#!/bin/bash

# Funksjonalitet:
# Hente alle dikt (GET /dikt)
# Legge til nytt dikt (POST /dikt)
# Endre eget dikt (PUT /dikt/{diktID})
# Slette eget dikt (DELETE /dikt/{diktID})
# Slette alle egne dikt (DELETE /dikt)

# Representational state transfer API
echo "Content-Type: text/xml"
echo ""

METHOD=$(echo "$REQUEST_METHOD") # Http method, ex: GET, POST
URI=$(echo "$REQUEST_URI") # Uniform Resource Identifier, used for location or name of a resource
DATA_DIR="./../../" # Adjust to the correct data directory path
DATABASE_PATH="$DATA_DIR/DiktDatabase.db"


# Function to check if a user is logged in and return the email address
is_logged_in() {
    # Logic to determine if there's a valid session.
    # This would likely involve checking a file or a database for a valid session ID.
    # Placeholder for session check:
    session_id=$1
    epostadresse=$(sqlite3 $DATABASE_PATH "SELECT epostadresse FROM Sesjon WHERE sesjonsID='$session_id';")
    echo "$epostadresse"
}

# Function to hash the password
hash_password() {
    echo -n $1 | sha256sum | awk '{print $1}'
}



# REST API logic
case "$METHOD" in
    GET)
        case "$URI" in
            /dikt/*)
                diktID=${URI#"/dikt/"}
                if [[ $diktID =~ ^[0-9]+$ ]]; then
                    dikt=$(sqlite3 DiktDatabase.db "SELECT dikt FROM Dikt WHERE diktID=$diktID;")
                    if [ -n "$dikt" ]; then
                        echo "<dikt>$dikt</dikt>"
                    else
                        echo "<error>Dikt not found</error>"
                    fi
                else
                    echo "<error>Invalid Dikt ID</error>"
                fi
                ;;
            /dikt)
                dikter=$(sqlite3 DiktDatabase.db "SELECT diktID, dikt FROM Dikt;")
                echo "<dikter>"
                echo "$dikter" | while read -r diktID dikt; do
                    echo "<dikt id=\"$diktID\">$dikt</dikt>"
                done
                echo "</dikter>"
                ;;
            *)
                echo "<error>Invalid request</error>"
                ;;
        esac
        ;;
    # Handle POST request
    POST)
        read -r data
    
        # Login functionality
        case "$URI" in
            /login)
                epost=$(echo "$data" | grep -oP '<epost>\K[^<]+')
                passord=$(echo "$data" | grep -oP '<passord>\K[^<]+')
    
                # Hash the password provided by the user
                hashed_passord=$(hash_password "$passord")
    
                # Retrieve the stored password hash from the database
                stored_hash=$(sqlite3 $DATABASE_PATH "SELECT passordhash FROM Bruker WHERE  epostadresse='$epost';")
    
                # Compare the provided hash with the stored hash
                if [ "$hashed_passord" == "$stored_hash" ]; then
                    # Generate a new session ID
                    sesjonsID=$(generate_session_id)
                    # Store the new session in the database
                    sqlite3 $DATABASE_PATH "INSERT INTO Sesjon (sesjonsID, epostadresse) VALUES     ('$sesjonsID', '$epost');"
                    # Respond with the new session ID
                    echo "<sesjon>$sesjonsID</sesjon>"
                else
                    # Respond with an error if the credentials are invalid
                    echo "<error>Invalid credentials</error>"
                fi
                ;;
    
            # Adding a new poem functionality
            /dikt)
                # Extract the session ID from the request
                session_id=$(echo "$data" | grep -oP '<sesjon>\K[^<]+')
                # Check if the user is logged in
                user_email=$(is_logged_in "$session_id")
    
                if [ -n "$user_email" ]; then
                    # Extract the poem content from the request
                    dikt_content=$(echo "$data" | grep -oP '<dikt>\K[^<]+')
                    # Insert the new poem into the database
                    sqlite3 $DATABASE_PATH "INSERT INTO Dikt (dikt, epostadresse) VALUES    ('$dikt_content', '$user_email');"
                    # Respond with a success message
                    echo "<success>Dikt added</success>"
                else
                    # Respond with an error if the user is not logged in
                    echo "<error>User not logged in or session invalid</error>"
                fi
                ;;
            *)
                # Respond with an error for any other POST URIs
                echo "<error>Invalid request</error>"
                ;;
        esac
        ;;
    # Handle PUT request
    PUT)
        read -r data
        session_id=$(echo "$data" | grep -oP '<sesjon>\K[^<]+')
        user_email=$(is_logged_in "$session_id")
        diktID=$(echo "$URI" | grep -oP 'dikt/\K[0-9]+')

        if [ -n "$user_email" ] && [[ $diktID =~ ^[0-9]+$ ]]; then
            dikt_content=$(echo "$data" | grep -oP '<dikt>\K[^<]+')
            # Update poem in the database
            sqlite3 $DATABASE_PATH "UPDATE Dikt SET dikt='$dikt_content' WHERE diktID=$diktID AND epostadresse='$user_email';"
            echo "<success>Dikt updated</success>"
        else
            echo "<error>User not logged in or invalid diktID</error>"
        fi
        ;;

    # Handle DELETE request
    DELETE)
        read -r data
        session_id=$(echo "$data" | grep -oP '<sesjon>\K[^<]+')
        user_email=$(is_logged_in "$session_id")
        diktID=$(echo "$URI" | grep -oP 'dikt/\K[0-9]+')

        if [ -n "$user_email" ]; then
            if [[ $diktID =~ ^[0-9]+$ ]]; then
                # Delete specific poem from the database
                sqlite3 $DATABASE_PATH "DELETE FROM Dikt WHERE diktID=$diktID AND epostadresse='$user_email';"
                echo "<success>Dikt deleted</success>"
            else
                # Delete all poems from the user
                sqlite3 $DATABASE_PATH "DELETE FROM Dikt WHERE epostadresse='$user_email';"
                echo "<success>All dikter deleted</success>"
            fi
        else
            echo "<error>User not logged in or invalid session</error>"
        fi
        ;;
esac
