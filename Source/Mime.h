//
//  Mime.h
//  TSD3060-Webserver-1
//
//  Created by Isak Lars Haukeland on 08/09/2023.
//

#ifndef Mime_h
#define Mime_h

#include "Config.h"


// TODO: Read /var/blablabla/mimetypes.txt into a (hash) struct mimetabel_t {char *content_type; char *extention}: mimetable_t mime[2000]
void Mime_initiate(void);
// TODO: Given a file extension, example '.html' the table returns the correct mime-type string
//const char *Mime_get(const char *extension);


#endif /* Mime_h */
