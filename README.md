# Mlečni Put - Pametna Logistika Distribucije Mleka (Supabase SQL)

## 📋 Opis Projekta
**Mlečni Put** je hakaton projekt za optimizaciju ruta dostave mleka. 
Ova grana (`sql-version`) koristi Supabase PostgreSQL (SQL) umesto Firebase Firestore (NoSQL) kao bazu podataka. AI engine koristi Google Gemini za generisanje profitabilnih ruta.

### Ključne Karakteristike
- **SQL entiteti**: `sellers`, `buyers`, `orders`, `routes`.
- **Geografsko filtriranje**: Beograd, Niš, Novi Sad radius 92km.
- **AI-optimizovane rute**: Gemini procena profita i prioritet isporuke.
- **Status transakcija**: `orders.status` prelazi iz `pending` u `assigned`, `routes.status` = `active`.
- **Zalihe**: Mleko se umanjuje iz `sellers.total_stock`.

## 🛠 Tehnologije
- **Backend**: Python 3.13
- **Baza**: Supabase PostgreSQL
- **AI**: Google Gemini 1.5
- **Biblioteke**: `supabase`, `google-generativeai`, `python-dotenv`, `geopy`

## 🚀 Instalacija i Podešavanje

### 1. Kloniraj Repozitorijum
```bash
git clone [repo URL]
cd MlecniPut
```

### 2. Kreiraj Virtual Environment
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# ili source .venv/bin/activate  # Linux/Mac
```

### 3. Instaliraj Zavisnosti
```bash
pip install supabase python-dotenv geopy google-generativeai
```

### 4. .env konfiguracija
U root folderu kreiraj `.env` fajl i dodaj:
```
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_KEY=your-supabase-service-role-key
GEMINI_API_KEY=your-gemini-api-key
```

### 5. Supabase Setup
1. Kreiraj Supabase projekat na https://app.supabase.com.
2. Otvori SQL editor i kreiraj tabele (primer SQL ispod).
3. (Opcionalno) Omogući Row Level Security (RLS) po potrebi.

#### Primer SQL tabele
```sql
CREATE TABLE sellers (
  id serial PRIMARY KEY,
  name text NOT NULL,
  location point NOT NULL,
  city text NOT NULL,
  total_stock int NOT NULL,
  created_at timestamptz DEFAULT now()
);

CREATE TABLE buyers (
  id serial PRIMARY KEY,
  name text NOT NULL,
  address text NOT NULL,
  location point NOT NULL,
  city text NOT NULL,
  created_at timestamptz DEFAULT now()
);

CREATE TABLE orders (
  id serial PRIMARY KEY,
  buyer_id int REFERENCES buyers(id),
  milk_liters int NOT NULL,
  status text NOT NULL DEFAULT 'pending',
  date_of_order date NOT NULL,
  created_at timestamptz DEFAULT now()
);

CREATE TABLE routes (
  id serial PRIMARY KEY,
  city text NOT NULL,
  actions jsonb NOT NULL,
  delivery_order jsonb NOT NULL,
  total_profit numeric NOT NULL,
  status text NOT NULL DEFAULT 'active',
  created_at timestamptz DEFAULT now()
);
```

## 🎯 Pokretanje

### 1) Dodavanje test podataka
do db inicijalne baze:
```bash
python src/db_seeder.py
```

### 2) Generisanje i čuvanje ruta
```bash
python src/main.py
```

### Šta se očekuje
- Učitani `pending` orders iz tabele `orders`.
- Filtrirani farmari iz tabele `sellers` po gradovima i radijusu.
- Generisanje rute putem AI (Gemini) u `logic.py`.
- Snimanje `routes` u Supabase u `db_manager.py`.
- Ažuriranje `orders.status` u `assigned` i `sellers.total_stock`.

## 📁 Struktura Projekta (sql-version)
```
MlecniPut/
├── src/
│   ├── main.py
│   ├── logic.py
│   ├── ai_engine.py
│   ├── db_manager.py
│   └── db_seeder.py
├── .env
├── .gitignore
└── README.md
```

## 🐛 Troubleshooting
- **Invalid Supabase URL/Key**: proveri `.env` i ponovo pokreni.
- **no data found for city**: dodaj više `orders` / `sellers` preko `db_seeder.py`.
- **Gemini API error**: proveri `GEMINI_API_KEY`, rate-limit i status.
- **JSON decode error**: u `ai_engine.py` proveri da API vraća validan JSON.

## 📞 Kontakt
- **Autor**: Miloš Kostić
- **Email**: milos.kostic.programiranje@gmail.com

---

*Ovaj README je za granu kotirana kao `sql-version` koja koristi Supabase SQL.*