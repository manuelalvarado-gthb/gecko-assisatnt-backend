#!/bin/bash

echo "=== Testing GECO RAG System ==="
echo ""

echo "1. Testing RAG query about rivers:"
curl -s -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "¿Qué información hay sobre el río?", "limit": 2}' | jq .

echo ""
echo "2. Testing semantic search:"
curl -s -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "medicina salud", "limit": 2}' | jq .

echo ""
echo "3. Testing health check:"
curl -s http://localhost:8000/health | jq .
