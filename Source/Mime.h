//
//  Mime.h
//  TSD3060-Webserver-1
//
//  Created by Isak Lars Haukeland on 08/09/2023.
//

#ifndef Mime_h
#define Mime_h

// Read /etc/mime.types into a array
void Mime_initiate(void);
// Returns the correct mime-type string for the given file extension
const char *Mime_get(const char* extension);


#endif /* Mime_h */
