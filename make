CC = gcc
CFLAGS = -O3 -s -static -Wall -Wextra -pedantic
TARGET = GODMODE

all: $(TARGET)

$(TARGET): GODMODE.c
	$(CC) $(CFLAGS) -o $(TARGET) GODMODE.c

clean:
	rm -f $(TARGET) wendy.mem zulu.wal
