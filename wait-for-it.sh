#!/usr/bin/env bash
# wait-for-it.sh

host="$1"
port="$2"
shift 2
cmd="$@"

timeout=60
start_time=$(date +%s)

while ! nc -z -w 2 "$host" "$port"; do
  echo "Attente de $host:$port"
  sleep 2
  now=$(date +%s)
  if [ $((now - start_time)) -ge $timeout ]; then
    echo "Timeout de $timeout secondes dépassé, échec de la connexion à $host:$port"
    exit 1
  fi
done

echo "$host:$port est prêt. Lancement de : $cmd"
exec $cmd
