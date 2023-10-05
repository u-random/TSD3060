#!/bin/bash

# Representational state transfer API
echo "Content-Type: text/xml"
echo ""

METHOD=$(echo "$REQUEST_METHOD") # Http method, ex: GET, POST
URI=$(echo "$REQUEST_URI") # Uniform Resource Identifier, used for location or name of a resource

case "$METHOD" in
    GET)
        case "$URI" in
            /dikt/*)
                diktID=${URI#"/dikt/"}
                dikt=$(sqlite3 DiktDatabase.db "SELECT dikt FROM Dikt WHERE diktID=$diktID;")
                echo "<dikt>$dikt</dikt>"
                ;;
            *)
                echo "<error>Invalid request</error>"
                ;;
        esac
        ;;
    POST)
        case "$URI" in
            /login)
                read -r data
                epost=$(echo "$data" | grep -oP '<epost>\K[^<]+')
                passord=$(echo "$data" | grep -oP '<passord>\K[^<]+')
                valid_pass=$(sqlite3 DiktDatabase.db "SELECT passordhash FROM Bruker WHERE epostadresse='$epost';")
                if [ "$passord" == "$valid_pass" ]; then
                    sesjonsID="some_generated_session_id"
                    sqlite3 DiktDatabase.db "INSERT INTO Sesjon (sesjonsID, epostadresse) VALUES ('$sesjonsID', '$epost');"
                    echo "<sesjon>$sesjonsID</sesjon>"
                else
                    echo "<error>Invalid credentials</error>"
                fi
                ;;
            *)
                echo "<error>Invalid request</error>"
                ;;
        esac
        ;;
esac
