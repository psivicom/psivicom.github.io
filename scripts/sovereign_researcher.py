import requests
import json
import os
import time
from datetime import datetime, timezone

def execute_literature_search():
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    
    # The Scout's current focus areas (from the Epistemic Drift)
    queries = [
        "honeybee foraging geomagnetic storms",
        "apiary microclimate thermal shadows",
        "propolis resin botanical origins coastal"
    ]
    
    research_log = []
    
    for query in queries:
        # OpenAlex API: 100% free, open-science, no API key required
        url = f"https://api.openalex.org/works?search={query.replace(' ', '%20')}&select=id,doi,title,publication_year&per_page=1"
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data.get('results'):
                paper = data['results'][0]
                research_log.append({
                    "query": query,
                    "title": paper.get('title', 'Unknown'),
                    "doi": paper.get('doi', 'N/A'),
                    "year": paper.get('publication_year', 'N/A'),
                    "status": "Literature_Crystallized"
                })
            else:
                research_log.append({"query": query, "status": "No_Open_Data_Found"})
                
        except requests.exceptions.RequestException as e:
            research_log.append({"query": query, "status": f"Uplink_Failed: {str(e)}"})
            
        time.sleep(1) # Respectful rate limiting for open-science servers

    output_dir = "data/aether"
    os.makedirs(output_dir, exist_ok=True)
    
    with open(f"{output_dir}/literature_search.json", "w") as f:
        json.dump({"timestamp": timestamp, "research": research_log}, f, indent=2)
        
    print(f"📚 [WENDY] Sovereign Literature Search completed at {timestamp}")

if __name__ == '__main__':
    execute_literature_search()
