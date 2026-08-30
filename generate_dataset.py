import numpy as np
import pandas as pd

np.random.seed(42)

N = 1000

companies = ["Dell", "HP", "Lenovo", "Asus", "Acer", "Apple", "MSI"]
company_weights = [0.20, 0.20, 0.18, 0.15, 0.12, 0.07, 0.08]

types = ["Notebook", "Ultrabook", "Gaming", "2 in 1 Convertible", "Netbook"]
type_weights = [0.40, 0.20, 0.20, 0.15, 0.05]

cpu_brands = ["Intel Core i3", "Intel Core i5", "Intel Core i7", "AMD Ryzen 5", "AMD Ryzen 7"]
cpu_weights = [0.15, 0.35, 0.25, 0.15, 0.10]

gpu_brands = ["Intel Integrated", "AMD Radeon", "Nvidia GeForce"]
gpu_weights = [0.45, 0.20, 0.35]

# Specific GPU model names per brand, with a price premium for each
# (higher-tier GPUs cost more, just like in real laptops).
gpu_names_by_brand = {
    "Intel Integrated": {
        "Intel UHD Graphics": 0,
        "Intel Iris Xe Graphics": 2000,
    },
    "AMD Radeon": {
        "AMD Radeon Vega 8": 0,
        "AMD Radeon RX 6500M": 5000,
        "AMD Radeon RX 6600M": 9000,
    },
    "Nvidia GeForce": {
        "Nvidia GeForce MX450": 3000,
        "Nvidia GeForce GTX 1650": 8000,
        "Nvidia GeForce RTX 3050": 14000,
        "Nvidia GeForce RTX 3060": 20000,
        "Nvidia GeForce RTX 4060": 28000,
    },
}

os_list = ["Windows", "Mac", "Linux", "No OS"]
os_weights = [0.75, 0.07, 0.10, 0.08]

ram_options = [4, 8, 16, 32, 64]
ram_weights = [0.10, 0.35, 0.35, 0.15, 0.05]

storage_options = [128, 256, 512, 1024, 2048]
storage_weights = [0.10, 0.30, 0.35, 0.20, 0.05]

rows = []
for _ in range(N):
    company = np.random.choice(companies, p=company_weights)
    typename = np.random.choice(types, p=type_weights)
    inches = round(np.random.uniform(11.6, 17.3), 1)
    ram = int(np.random.choice(ram_options, p=ram_weights))
    weight = round(np.random.uniform(1.1, 3.0), 2)
    touchscreen = np.random.choice([0, 1], p=[0.8, 0.2])
    ips = np.random.choice([0, 1], p=[0.55, 0.45])
    ppi = round(np.random.uniform(100, 220), 1)  # pixels per inch (screen sharpness)
    cpu = np.random.choice(cpu_brands, p=cpu_weights)
    ssd = int(np.random.choice(storage_options, p=storage_weights))
    hdd = int(np.random.choice([0, 500, 1024, 2048], p=[0.55, 0.20, 0.20, 0.05]))
    gpu = np.random.choice(gpu_brands, p=gpu_weights)
    gpu_options = gpu_names_by_brand[gpu]
    gpu_name = np.random.choice(list(gpu_options.keys()))
    os_ = np.random.choice(os_list, p=os_weights)

    # ---- Realistic price logic (this is the "ground truth" formula) ----
    # Base price
    price = 20000

    # Brand premium
    brand_premium = {"Apple": 45000, "MSI": 12000, "Dell": 5000, "HP": 3000,
                      "Lenovo": 4000, "Asus": 4000, "Acer": 0}
    price += brand_premium[company]

    # Type premium
    type_premium = {"Gaming": 20000, "Ultrabook": 12000, "2 in 1 Convertible": 8000,
                     "Notebook": 0, "Netbook": -5000}
    price += type_premium[typename]

    # RAM, storage, screen contribute directly
    price += ram * 900
    price += ssd * 12
    price += hdd * 2
    price += (ppi - 100) * 60
    price += touchscreen * 3500
    price += ips * 2500
    price -= (weight - 1.1) * 1500  # lighter laptops cost a bit more

    # CPU premium
    cpu_premium = {"Intel Core i3": 0, "Intel Core i5": 8000, "Intel Core i7": 18000,
                    "AMD Ryzen 5": 7000, "AMD Ryzen 7": 15000}
    price += cpu_premium[cpu]

    # GPU premium (specific model matters more than just brand)
    price += gpu_options[gpu_name]

    # OS premium
    os_premium = {"Windows": 3000, "Mac": 0, "Linux": 0, "No OS": -3000}
    price += os_premium[os_]

    # Random noise so the model has something real to learn (not a perfect formula)
    price += np.random.normal(0, 4000)
    price = max(15000, round(price, -2))  # floor price, round to nearest 100

    rows.append([company, typename, inches, ram, weight, touchscreen, ips, ppi,
                 cpu, hdd, ssd, gpu, gpu_name, os_, price])

df = pd.DataFrame(rows, columns=[
    "Company", "TypeName", "Inches", "Ram", "Weight", "Touchscreen", "IPS",
    "PPI", "Cpu_brand", "HDD", "SSD", "Gpu_brand", "Gpu_name", "OpSys", "Price"
])

df.to_csv("laptop_data.csv", index=False)
print(f"Saved laptop_data.csv with {len(df)} rows and {len(df.columns)} columns.")
print(df.head())
