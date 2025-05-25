#!/bin/sh
# Extract host and port from the first argument (e.g., backend:8000)
hostport="$1"
host=$(echo "$hostport" | cut -d':' -f1)
port=$(echo "$hostport" | cut -d':' -f2)
shift

# Check if the next argument is '--' and skip it
if [ "$1" = "--" ]; then
  shift
fi

cmd="$@"

until nc -z "$host" "$port"; do
  echo "Waiting for $host:$port..."
  sleep 1
done
exec $cmd