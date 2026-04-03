import os
from dotenv import load_dotenv
import logic
import ai_engine
import db_manager
from supabase import create_client, Client

# Učitavamo .env    
load_dotenv()

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

#definisemo centrove grada
city_centers = {
    "belgrade": (44.7866, 20.4489),
    "nis": (43.3209, 21.8954),
    "novi_sad": (45.2396, 19.8227)
}



def main():
    #Uzimamo samo narudzbine koje su pending
    orders_res = supabase.table("orders").select("*").eq("status", "pending").execute()
    
    #Uzimamo sve aktivne farme
    farmers_res = supabase.table("sellers").select("*").eq("is_active",True).execute()
    
    ordered_orders = logic.filtriraj_narudzbine(orders_res.data)
    ordered_farmers = logic.filtriraj_farmere(farmers_res.data)
    
    print(f"Danas u Beogradu imamo {len(ordered_orders['belgrade'])} narudzbine.")
    print("\n --AI ANALIZA I GENERISANJE RUTA--")
    
    routes= logic.posalji_rutu(city_centers, ordered_orders, ordered_farmers)
    
    for city in city_centers:
        if routes.get(city):
            db_manager.sacuvaj_rutu_u_bazu(city, routes[city])
            
            logic.azuriraj_stanje_mleka_u_bazi(routes[city])
            
if __name__ == "__main__":
    main()
