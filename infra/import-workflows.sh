#!/bin/bash

# n8n 워크플로우 수동 import 및 활성화 스크립트
# 사용법: ./import-workflows.sh

N8N_URL="http://localhost:5678"

echo "========================================="
echo "n8n Workflow Import & Activation Script"
echo "========================================="
echo ""

# n8n 서버 상태 확인
echo "Checking n8n server status..."
if ! curl -s "$N8N_URL/healthz" > /dev/null 2>&1; then
  echo "❌ Error: n8n is not running at $N8N_URL"
  echo "Please start n8n first with: docker-compose up"
  exit 1
fi
echo "✅ n8n server is running!"
echo ""

# workflows 디렉토리 확인
if [ ! -d "./workflows" ]; then
  echo "❌ Error: workflows directory not found"
  echo "Please run this script from the infra directory"
  exit 1
fi

# 워크플로우 파일 확인
workflow_count=$(ls -1 ./workflows/*.json 2>/dev/null | wc -l)
if [ "$workflow_count" -eq 0 ]; then
  echo "❌ No workflow files found in ./workflows/"
  exit 1
fi

echo "Found $workflow_count workflow files to import:"
ls -1 ./workflows/*.json | xargs -n1 basename
echo ""

# 사용자 확인
read -p "Do you want to import and activate all workflows? (y/n): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "Cancelled."
  exit 0
fi
echo ""

# 워크플로우 import 및 활성화
echo "Starting import process..."
echo "----------------------------------------"

imported_ids=""
failed_count=0

for workflow_file in ./workflows/*.json; do
  if [ -f "$workflow_file" ]; then
    filename=$(basename "$workflow_file")
    echo ""
    echo "📄 Processing: $filename"
    
    # Import workflow
    response=$(curl -s -X POST \
      -H "Content-Type: application/json" \
      -d "@$workflow_file" \
      "$N8N_URL/api/v1/workflows")
    
    # 성공 여부 확인
    if echo "$response" | grep -q '"id"'; then
      # ID 추출 (JSON 파싱)
      workflow_id=$(echo "$response" | grep -o '"id":"[^"]*' | head -1 | cut -d'"' -f4)
      
      if [ -z "$workflow_id" ]; then
        # 숫자형 ID인 경우
        workflow_id=$(echo "$response" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
      fi
      
      if [ -n "$workflow_id" ]; then
        echo "   ✅ Import successful (ID: $workflow_id)"
        imported_ids="$imported_ids $workflow_id"
        
        # 즉시 활성화
        echo "   🔄 Activating workflow..."
        activate_response=$(curl -s -X PATCH \
          -H "Content-Type: application/json" \
          -d '{"active": true}' \
          "$N8N_URL/api/v1/workflows/$workflow_id")
        
        if echo "$activate_response" | grep -q '"active":true'; then
          echo "   ✅ Workflow activated!"
        else
          echo "   ⚠️  Failed to activate (workflow imported but not active)"
        fi
      else
        echo "   ⚠️  Import succeeded but couldn't extract ID"
      fi
    else
      echo "   ❌ Import failed!"
      if [ -n "$response" ]; then
        echo "   Error: $response"
      fi
      failed_count=$((failed_count + 1))
    fi
  fi
done

# 결과 요약
echo ""
echo "========================================="
echo "Import Summary"
echo "========================================="

total_count=$(echo $imported_ids | wc -w)
echo "✅ Successfully imported: $total_count workflows"

if [ $failed_count -gt 0 ]; then
  echo "❌ Failed: $failed_count workflows"
fi

if [ -n "$imported_ids" ]; then
  echo ""
  echo "Imported Workflow IDs:"
  for id in $imported_ids; do
    echo "  - $id"
  done
fi

echo ""
echo "You can now access n8n at: $N8N_URL"
echo "========================================="