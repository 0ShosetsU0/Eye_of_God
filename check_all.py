#!/usr/bin/env python3
import requests
import sys


def check_service(name, url, expected_status=200):
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == expected_status:
            print(f"✅ {name}: OK")
            return True
        else:
            print(f"❌ {name}: Status {resp.status_code}")
            return False
    except Exception as e:
        print(f"❌ {name}: {e}")
        return False


def main():
    print("\n=== DefectVision Проверка ===\n")

    services = [
        ("Backend API", "http://localhost:8000/health"),
        ("ML Service", "http://localhost:8001/health"),
        ("Prometheus", "http://localhost:9090/-/healthy"),
        ("Grafana", "http://localhost:3001/api/health"),
        ("Elasticsearch", "http://localhost:9200/_cluster/health"),
        ("Kibana", "http://localhost:5601/api/status"),
        ("MinIO", "http://localhost:9001/minio/health/live"),
    ]

    results = []
    for name, url in services:
        results.append(check_service(name, url))

    print(f"\n=== Результат: {sum(results)}/{len(results)} сервисов работают ===\n")

    if sum(results) != len(results):
        print("Некоторые сервисы не запущены. Выполните:")
        print("docker-compose -f docker-compose.full.yml up -d")
        sys.exit(1)

    print("✅ Все сервисы работают корректно!")


if __name__ == "__main__":
    main()