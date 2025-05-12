#!/usr/bin/env bash
# wait-for-it.sh

host="$1"
port="$2"
shift 2
cmd="$@"

until nc -z "$host" "$port"; do
  echo "Attente de $host:$port"
  sleep 2
done

echo "$host:$port est prêt. Lancement de : $cmd"
exec $cmd
