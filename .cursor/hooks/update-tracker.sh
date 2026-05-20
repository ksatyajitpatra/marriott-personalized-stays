#!/bin/bash
# update-tracker.sh
# After any file edit, checks if a feature component was created/modified
# and injects a reminder to update the PRD tracker.

input=$(cat)
file_path=$(echo "$input" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('path',''))" 2>/dev/null || echo "")

if [[ -z "$file_path" ]]; then
  echo '{}' && exit 0
fi

context=""

# Check which feature area was touched and build a context hint
if [[ "$file_path" == *"/eco/"* ]] || [[ "$file_path" == *"eco_service"* ]] || [[ "$file_path" == *"EcoScore"* ]]; then
  context="An Eco Rating file was just modified: $file_path. Remind the agent to check off the relevant Eco Rating item in Section 15 of APP_PRD.md."
elif [[ "$file_path" == *"/brief/"* ]] || [[ "$file_path" == *"brief_service"* ]] || [[ "$file_path" == *"ArrivalBrief"* ]] || [[ "$file_path" == *"llm_service"* ]]; then
  context="An Arrival Brief file was just modified: $file_path. Remind the agent to check off the relevant Arrival Brief item in Section 15 of APP_PRD.md."
elif [[ "$file_path" == *"/map/"* ]] || [[ "$file_path" == *"LocalPartner"* ]] || [[ "$file_path" == *"partners"* ]] || [[ "$file_path" == *"/pet/"* ]] || [[ "$file_path" == *"PetProfile"* ]]; then
  context="A Pet / Local Partner Map file was just modified: $file_path. Remind the agent to check off the relevant Pet + Map item in Section 15 of APP_PRD.md."
elif [[ "$file_path" == *"docker-compose"* ]] || [[ "$file_path" == *"Dockerfile"* ]] || [[ "$file_path" == *"requirements.txt"* ]] || [[ "$file_path" == *"package.json"* ]]; then
  context="An infrastructure file was just modified: $file_path. Check if this completes a Core Infrastructure item in Section 15 of APP_PRD.md and check it off."
fi

if [[ -n "$context" ]]; then
  printf '{"additional_context": "%s"}' "$context"
else
  echo '{}'
fi

exit 0
