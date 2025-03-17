import re
import json


content = '{"time_range": "2025-03-17 13:00:00 - 2025-03-17 14:00:00", "meeting_type": "Interview meeting", participants": "Ross, Jack"}'

result = json.loads(content)
print(result)
