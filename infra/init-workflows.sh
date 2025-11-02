#!/bin/sh

# n8n이 백그라운드로 시작
echo "Starting n8n in background..."
n8n start &
N8N_PID=$!

# n8n 서버가 준비될 때까지 대기
echo "Waiting for n8n to be ready..."
max_retries=60
retry_count=0

while [ $retry_count -lt $max_retries ]; do
  if wget -q -O- http://localhost:5678/healthz > /dev/null 2>&1; then
    echo "n8n is ready!"
    sleep 5  # API가 완전히 준비되도록 추가 대기
    break
  fi
  retry_count=$((retry_count + 1))
  echo "Waiting for n8n... ($retry_count/$max_retries)"
  sleep 2
done

if [ $retry_count -eq $max_retries ]; then
  echo "ERROR: n8n failed to start"
  exit 1
fi

# workflows 폴더의 모든 JSON 파일 import 및 활성화
echo "Starting workflow import and activation..."

# 임포트된 워크플로우 ID를 저장할 배열
imported_workflow_ids=""

for workflow_file in ./workflows/*.json; do
  if [ -f "$workflow_file" ]; then
    echo "Importing workflow: $(basename $workflow_file)"
    
    # N8N API를 사용한 workflow import (인증 비활성화 상태)
    response=$(wget -q -O- --post-file="$workflow_file" \
      --header="Content-Type: application/json" \
      http://localhost:5678/api/v1/workflows 2>&1)
    
    if [ $? -eq 0 ]; then
      echo "✓ Successfully imported: $(basename $workflow_file)"
      
      # 응답에서 워크플로우 ID 추출 (JSON 파싱)
      workflow_id=$(echo "$response" | grep -o '"id":"[^"]*' | cut -d'"' -f4)
      if [ -n "$workflow_id" ]; then
        imported_workflow_ids="$imported_workflow_ids $workflow_id"
        echo "  → Workflow ID: $workflow_id"
      fi
    else
      echo "✗ Failed to import: $(basename $workflow_file)"
      echo "Error: $response"
    fi
  fi
done

echo "All workflows imported!"

# 모든 임포트된 워크플로우 활성화
if [ -n "$imported_workflow_ids" ]; then
  echo "Activating all imported workflows..."
  
  for workflow_id in $imported_workflow_ids; do
    echo "Activating workflow ID: $workflow_id"
    
    # 워크플로우 활성화 API 호출
    activate_response=$(wget -q -O- --method=PATCH \
      --header="Content-Type: application/json" \
      --body-data='{"active": true}' \
      "http://localhost:5678/api/v1/workflows/$workflow_id" 2>&1)
    
    if [ $? -eq 0 ]; then
      echo "✓ Successfully activated workflow: $workflow_id"
    else
      echo "✗ Failed to activate workflow: $workflow_id"
      echo "Error: $activate_response"
    fi
  done
  
  echo "All workflows activated!"
else
  echo "No workflows to activate"
fi

echo "Workflow setup completed!"

# n8n을 foreground로 유지
wait $N8N_PID