from geopy.distance import geodesic, great_circle
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()
import ai_engine

# ---baza---
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY") # service_role ključ
supabase: Client = create_client(url, key)

# ---konstante--- 
today = datetime.now().date()
belgrade = (44.7866, 20.4489)
nis = (43.3209, 21.8954)
novi_sad = (45.2396, 19.8227)
RADIUS = 92
MIN_PROFIT=1500
NABAVNA_CENA=80
PDV=0.1
GORIVO=35
PRODAJNA_CENA=180

def filtriraj_narudzbine(orders):
    filtrirano = {"belgrade": [], "nis": [], "novi_sad": []}

    for data in orders:
        
        order_timestamp = data.get("date_of_order")
        address = data.get("address_of_buyer") #Ocekuje se [lat,lng]
        
        if order_timestamp:
            # Ako je u bazi Timestamp, on već ima metodu .date()
            # Ako je slučajno string, moraćemo prvo da ga konvertujemo (vidi ispod)
            try:
                order_date = datetime.fromisoformat(order_timestamp.replace('Z', '+00:00')).date()
            except:
                order_date = today #Fallback za testiranje
            if order_date == today:
                if is_within_radius(*address, *belgrade, RADIUS):
                    filtrirano["belgrade"].append(data) 
                elif is_within_radius(*address, *nis, RADIUS):
                    filtrirano["nis"].append(data)
                elif is_within_radius(*address, *novi_sad, RADIUS):
                    filtrirano["novi_sad"].append(data)      
    return filtrirano

def filtriraj_farmere(farmers):
    filtrirano = {"belgrade": [],"nis": [],"novi_sad": []}
    
    for data in farmers:
        address = data.get("location")
        if is_within_radius(*address, *belgrade, RADIUS):
            filtrirano["belgrade"].append(data) 
        elif is_within_radius(*address, *nis,RADIUS):
            filtrirano["nis"].append(data)
        elif is_within_radius(*address, *novi_sad,RADIUS):
            filtrirano["novi_sad"].append(data)
    return filtrirano

# Proveravamo kome gradu pripada porudzbina
def is_within_radius(lat, lon, center_lat, center_lon, radius_km):
    return great_circle((center_lat, center_lon),(lat,lon)).km <= radius_km

# def izracunaj_udaljenost(tacka_a, tacka_b):
#     """_summary_
#         vraca udaljenosti 
#     Args:
#         tacka_a (_type_): latitude
#         tacka_b (_type_): longitude
#     """
#     return geodesic(tacka_a, tacka_b).km

def proveri_isplativost(litri,km):
    """Da li nam se isplati da palimo kamion"""
    zarada_po_litru=PRODAJNA_CENA*(1-PDV)-NABAVNA_CENA
    # Ako je zarada veca od troska vracamo True
    return (litri* zarada_po_litru - km*GORIVO)>MIN_PROFIT
    
def posalji_rutu(city_centers,ordered_orders,ordered_farmers):
    
    routes={}
    for city, coordinates in city_centers.items():
        buyers = ordered_orders.get(city, [])
        farmers = ordered_farmers.get(city, [])
        
        if buyers and farmers:
            print(f"\n Generišem rutu za {city.upper()} preko AI engine-a...")

            # Pozivamo AI engine
            route = ai_engine.generisi_rutu(coordinates,farmers,buyers)
            
            for buyer in buyers:
                try:
                    order_id = buyer.get('order.id') or buyer.get('id')
                    supabase.table("orders") \
                        .update({"status": "assigned"}) \
                        .eq("id", order_id)\
                        .execute()
                except Exception as e:
                    print(f"❌ Greška pri update-u narudžbine {order_id}: {e}")
            print(f"Ruta za {city.upper()} je spremna i narudzbine su rezervisane!")
            routes[city]=route
        else:
            print(f"Za {city.upper()} danas nema dovoljno podataka (kupaca ili farmera).")
            routes[city]=None
    return routes;

    
def azuriraj_stanje_mleka_u_bazi(route_data):
    """
    Prolazi kroz generisanu rutu i oduzima litre od farmera u Firebase-u.
    """
    
    if not route_data or 'delivery_order' not in route_data:
        print("⚠️ Nema podataka za ažuriranje.")
        return

    for stop in route_data['delivery_order']:
        doc_id = stop.get('id')
        liters = stop.get('liters', 0)
        stop_type = stop.get('type')

        if not doc_id or liters <= 0:
            continue

        try:
            if stop_type == 'farmer':
                # Oduzimamo od dostupnog mleka (Increment sa minusom)
                res = supabase.table("sellers").select("total_stock").eq("id", doc_id).single().execute()
                novo_stanje = res.data["total_stock"]-liters
                supabase.table("sellers").update({"total_stock": novo_stanje}).eq("id", doc_id).execute()
                print(f"Farmer {stop['name']}: Novo stanje {novo_stanje}L")
            elif stop_type == 'buyer':
                supabase.table("orders").update({
                    "status": "completed",
                    "delivered_liters": liters
                }).eq("id",doc_id).execute()
                print(f"Kupac {stop['name']}: Isporuceno")
        except Exception as e:
            print(f"❌ Greška pri ažuriranju dokumenta {doc_id}: {e}")