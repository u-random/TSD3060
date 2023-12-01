
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

M3_OBJS	 = ./Milestone/3/cgi.cgi \
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

# Keywords to run the milestones

m1: $(PROG)
# Run C Web Server interactible by default
	./TSD3060 -r Distribution -p 8080 -i

m2: $(PROG)
# Run the unshare container
	./Milestone/2/unshare.sh
	
m3: $(M3_OBJS)
	chmod 666 ./Milestone/3/DiktDatabase.db
	cp -a $(M3_OBJS) $(CGIBINDIR)
	@echo "Use your browser and connect to localhost:80"

m4: $(M3_OBJS) Milestone/4/SharedDockerfile
# Setup files for restapi
	cp -a $(M3_OBJS) ./Milestone/4/restapi/
# Build Image
	docker build -t cgi-image:base -f Milestone/4/SharedDockerfile Milestone/4
# Build with docker compose
	docker-compose -f Milestone/4/docker-compose.yml up --build

m4stop:
# Stop the containers
	docker-compose -f Milestone/4/docker-compose.yml stop

m4restart:
# Restart the containers without rebuilding them
	docker-compose -f Milestone/4/docker-compose.yml up

# Build the program from object files
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
# Cleanup Milestone 4 files
	rm -f Milestone/4/restapi/DiktDatabase.db
	rm -f Milestone/4/restapi/cgi.cgi
# Shutdown Milestone 4 docker compose containers and remove image
	docker-compose -f Milestone/4/docker-compose.yml down --volumes
	docker rmi cgi-image:base
