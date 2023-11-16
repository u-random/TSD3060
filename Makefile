
PROG=TSD3060
CC = clang
OS = $(shell uname|tr a-z A-Z)
DIST = Distribution

# Define variables
IMAGE_NAME_1=myapp
IMAGE_NAME_2=a
CONTAINER_NAME_1=myapp-container
CONTAINER_NAME_2=

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
		   
M4_OBJS	 = ./Milestone/4/Dockerfile \
		   ./Milestone/4/

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
	./TSD3060 -r Distribution -p 55566 -i

m2: $(PROG)
	./Milestone/2/unshare.sh
	
m3: $(M3_OBJS)
	chmod 666 ./Milestone/3/DiktDatabase.db
	cp -a $(M3_OBJS) $(CGIBINDIR)
	@echo "Use your browser and connect to localhost:80"

m4 start: $(M4_OBJS)
# Build the first Docker image
	docker build -t $(IMAGE_NAME_1) .
# Build the second Docker image
	docker build -t $(IMAGE_NAME_2) .
# Run the first container
	docker run -d --name $(CONTAINER_NAME_1) $(IMAGE_NAME_1)
# Run the second container
	docker run -d --name $(CONTAINER_NAME_2) $(IMAGE_NAME_2)

m4 stop: $(M4_OBJS)
# Stop the containers
	docker stop $(CONTAINER_NAME_1)
	docker stop $(CONTAINER_NAME_2)


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
#	docker rm $(CONTAINER_NAME)
#	docker rmi $(IMAGE_NAME)
