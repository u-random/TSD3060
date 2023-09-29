//
//  Mime.c
//  TSD3060-Webserver-1
//
//  Created by Isak Lars Haukeland on 08/09/2023.
//

#include "Config.h"

#include "Mime.h"


// MARK: - Definition

#define MAX_MIME_TYPES 2286

// Define a structure for mime type data
typedef struct {
    char *mime_type;
    char *file_extensions;
} MimeEntry;

// Define a structure for the mime table
typedef struct {
    MimeEntry entries[MAX_MIME_TYPES]; // VLA?
    size_t size;
} MimeTable;

// Setup and clear our local mime_table
static MimeTable mime_table = {};


// -------------------------------------------------------------------------------------


// MARK: - Read mime.types file into shared memory hash table
void Mime_initiate(void) {
    char t[PATH_MAX] = {};
    snprintf(t, PATH_MAX, "%s/etc/mime.types", Server.distribution_root);
    FILE *mime_file = fopen(t, "r");
    if (!mime_file) {
        Config_error(stderr, "Failed to open mime.types file");
    }

    // Parse mime.types file and populate the hash table
    char line[512];
    char mime_type[STRLEN];
    char file_extensions[STRLEN];
    //
    while (fgets(line, sizeof(line), mime_file)) {
        if (line[0] == '#' || isspace(line[0]))
            continue;
        if (sscanf(line, "%s %[^\n]", mime_type, file_extensions) != 2) {
            continue;
        }
        // Check if there are spaces in the file_extensions string
        char *has_space = strchr(file_extensions, ' ');
        if (has_space == NULL) {
            // No space found, treat the whole string as a single extension
            if (mime_table.size >= MAX_MIME_TYPES) {
                Config_error(stderr, "Too many mime types, increase MAX_MIME_TYPES\n");
            }
            MimeEntry *entry = &mime_table.entries[mime_table.size];
            entry->file_extensions = strdup(file_extensions);
            entry->mime_type = strdup(mime_type);
            mime_table.size++;
        } else {
            // Split and process space-separated extensions
            char *token = strtok(file_extensions, " ");
            while (token != NULL) {
                if (mime_table.size >= MAX_MIME_TYPES) {
                    Config_error(stderr, "Too many mime types, increase MAX_MIME_TYPES\n");
                }
                MimeEntry *entry = &mime_table.entries[mime_table.size];
                entry->file_extensions = strdup(token);
                entry->mime_type = strdup(mime_type);
                mime_table.size++;
                // Get the next extension
                token = strtok(NULL, " ");
            }
        }
    }
    fclose(mime_file);
}


// MARK: - Get current mimetype from request extention
const char *Mime_get(const char* extension) {
    if (STRING_UNDEFINED(extension)) {
        return NULL;
    }

    // Working through the mime table to find matching extention
    for (size_t i = 0; i < mime_table.size; i++) {
        MimeEntry entry = mime_table.entries[i];
        if (strcasecmp(entry.file_extensions, extension) == 0) {
            return entry.mime_type;
        }
    }

    // Return a default mime-type if not found
    return "text/plain";
}
