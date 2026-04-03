import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

#koristimo Service_key koji cuvamo u .env
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url,key)


def sacuvaj_rutu_u_bazu(city, route_data):
    if not route_data:
        return None
    try:
        # Pripremamo podatke za SQL tabelu 'routes'
        # Supabase ce generisati default stvari koje ne ubacimo u tabelu
        insert_data = {
            "city": city.lower(),
            "actions": route_data.get("actions"), #JSONB kolona
            "delivery_order": route_data.get("deliver_order"),
            "status": "active"
        }
        #SupaBase insert
        response =  supabase.table("routes").insert(insert_data).execute()
        
        #provera da li je upis uspeo
        if response.data:
            new_route_id = response.data[0]['id']
            print(f"Ruta za {city.upper()} je uspesno sacuvana u SupaBase! ID: {new_route_id}")
            return new_route_id
        else:
            print(f"Problem pri snimanju rute za {city.upper()}.")
            return None
    except Exception as e:
        print(f"Greška pri snimanju rute za {city.upper()}: {e}")
        return None
