import clickhouse_connect
from app.config import config
from app.models import Client
from typing import List

class ClickHouseService:
    def __init__(self):
        try:
            self.client = clickhouse_connect.get_client(
                host=config.CLICKHOUSE_HOST,
                port=config.CLICKHOUSE_PORT,
                username=config.CLICKHOUSE_USER,
                password=config.CLICKHOUSE_PASSWORD
            )
        except Exception as e:
            print(f"Failed to connect to ClickHouse: {e}")
            self.client = None

    def get_clients(self) -> List[Client]:
        if not self.client:
            return []

        try:
            query = "SELECT id, client_name FROM transform.Clients WHERE client_name IS NOT NULL"
            result = self.client.query(query)
            
            clients = []
            seen_names = set()
            
            for row in result.result_rows:
                client_id, client_name = row
                
                # Edge Case: Empty string check (though query handles NULL)
                if not client_name or not client_name.strip():
                    continue
                    
                # Edge Case: Duplicates
                # If name exists, append ID to make it unique for display
                display_name = client_name
                if client_name in seen_names:
                    display_name = f"{client_name} ({client_id})"
                
                seen_names.add(client_name)
                clients.append(Client(id=client_id, client_name=display_name))
                
            return clients
            
        except Exception as e:
            print(f"Error fetching clients: {e}")
            return []

clickhouse_service = ClickHouseService()
