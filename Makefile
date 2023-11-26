
PROG=TSD3060
CC = clang
OS = $(shell uname|tr a-z A-Z)
DIST = Distribution

# Compiling setup
CFLAGS = -g -Wall -D$(OS)

# Default to dynamic linking
LDFLAGS := -I./Source

SRCS =  Source/main.c \
        Source/Config.c \
        Source/ArgumentParser.c \
        Source/HttpStatus.c \
        Source/Mime.c \
        Source/Server.c \
        Source/Http.c \
        Source/File.c
OBJS = $(SRCS:.c=.o)

M3_OBJS	 = ./Milestone/3/rest.cgi \
		   ./Milestone/3/DiktDatabase.db
		   
		   
# For macOS
CGIBINDIR = /Library/WebServer/CGI-Executables

# Conditional logic for Linux
ifeq ($(OS),LINUX)
	CGIBINDIR = /usr/lib/cgi-bin
	CFLAGS += -DUNSHARE
    LDFLAGS += -static
endif

# Targets
all: $(PROG)

# kommandoer for å starte milestones

m1: $(PROG)
	./TSD3060 -r Distribution -p 8080 -i

m2: $(PROG)
	./Milestone/2/unshare.sh
	
m3: $(M3_OBJS)
	chmod 666 ./Milestone/3/DiktDatabase.db
	cp -a $(M3_OBJS) $(CGIBINDIR)
	@echo "Use your browser and connect to localhost:80"

m4: $(M3_OBJS)
# Setup files to use
	cp -a $(M3_OBJS) ./Milestone/4/restapi/
# Build with docker compose
	docker-compose -f /Milestone/4/docker-compose.yml up -d


m4stop: $(M4_OBJS)
# Stop the containers
	docker-compose  -f /Milestone/4/docker-compose.yml stop


$(PROG): $(OBJS)
	$(CC) $(LDFLAGS) -o $@ $^


# Only builds/rebuilds the database if sql is changed
./Milestone/3/DiktDatabase.db: ./Milestone/3/DiktDatabase.sql
	sqlite3 $@ < $^


.c.o:
	$(CC) $(CFLAGS) -c $< -o $@


.PHONY: clean
clean:
	rm -f $(OBJS) $(PROG) $(DIST)/bin/*
	rm -rf tmp/
	rm -f Milestone/3/DiktDatabase.db
	rm -f /usr/lib/cgi-bin/*
	rm -f Milestone/4/restapi/DiktDatabase.db
	rm -f Milestone/4/restapi/rest.cgi
	docker-compose -f /Milestone/4/docker-compose.yml down --volumes
