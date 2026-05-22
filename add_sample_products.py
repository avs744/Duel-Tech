from app import db, Product, ProductSpec, categories
import random

# Clear existing data - uncomment if you want to start fresh
# ProductSpec.query.delete()
# Product.query.delete()
# db.session.commit()

# Sample products with detailed specifications
sample_products = {
    'laptops': [
        {
            'name': 'Apple MacBook Pro 16-inch M2 Pro',
            'price': '₹2,29,900',
            'rating': 4.8,
            'brand': 'Apple',
            'specs': {
                'processor': 'Apple M2 Pro 12-core CPU',
                'graphics': 'Apple M2 Pro 19-core GPU',
                'memory': '16GB unified memory',
                'storage': '512GB SSD',
                'display': '16.2-inch Liquid Retina XDR display (3456 x 2234)',
                'battery': 'Up to 22 hours',
                'operating_system': 'macOS Ventura',
                'ports': '3 Thunderbolt 4 ports, HDMI port, SDXC card slot, MagSafe 3 port',
                'weight': '2.15 kg',
                'dimensions': '1.68 x 35.57 x 24.81 cm',
                'camera': '1080p FaceTime HD camera',
                'audio': 'Six-speaker sound system with force-cancelling woofers',
                'keyboard': 'Backlit Magic Keyboard with Touch ID',
                'wireless': 'Wi-Fi 6E (802.11ax), Bluetooth 5.3'
            }
        },
        {
            'name': 'Dell XPS 15 (9530)',
            'price': '₹1,79,990',
            'rating': 4.7,
            'brand': 'Dell',
            'specs': {
                'processor': '13th Gen Intel Core i9-13900H (24MB Cache, up to 5.4 GHz)',
                'graphics': 'NVIDIA GeForce RTX 4070 8GB GDDR6',
                'memory': '32GB DDR5 4800MHz',
                'storage': '1TB M.2 PCIe NVMe SSD',
                'display': '15.6-inch 3.5K (3456 x 2160) OLED touch display',
                'battery': '86Whr battery, up to 12 hours',
                'operating_system': 'Windows 11 Pro',
                'ports': '2x Thunderbolt 4, 1x USB-C 3.2, SD card reader, 3.5mm headphone jack',
                'weight': '1.92 kg',
                'dimensions': '1.77 x 34.42 x 23.07 cm',
                'camera': '720p HD camera with Windows Hello',
                'audio': 'Quad-speaker design with Waves MaxxAudio Pro',
                'keyboard': 'Backlit keyboard with fingerprint reader',
                'wireless': 'Killer Wi-Fi 6E AX1675, Bluetooth 5.3'
            }
        },
        {
            'name': 'Lenovo ThinkPad X1 Carbon Gen 11',
            'price': '₹1,54,990',
            'rating': 4.6,
            'brand': 'Lenovo',
            'specs': {
                'processor': '13th Gen Intel Core i7-1355U (12 cores, up to 5.0GHz)',
                'graphics': 'Intel Iris Xe Graphics',
                'memory': '16GB LPDDR5 6400MHz',
                'storage': '512GB PCIe Gen4 SSD',
                'display': '14-inch 2.8K (2880 x 1800) OLED, 400 nits, 100% DCI-P3',
                'battery': '57Whr battery, up to 15 hours',
                'operating_system': 'Windows 11 Pro',
                'ports': '2x Thunderbolt 4, 2x USB-A 3.2, HDMI 2.0, 3.5mm combo jack',
                'weight': '1.12 kg',
                'dimensions': '1.55 x 31.5 x 22.2 cm',
                'camera': '1080p FHD + IR camera with privacy shutter',
                'audio': 'Dolby Atmos speaker system',
                'keyboard': 'Spill-resistant backlit keyboard with TrackPoint',
                'wireless': 'Intel Wi-Fi 6E AX211, Bluetooth 5.3',
                'security': 'Fingerprint reader, dTPM 2.0, Kensington lock slot'
            }
        }
    ],
    'smartphones': [
        {
            'name': 'Samsung Galaxy S24 Ultra',
            'price': '₹1,29,999',
            'rating': 4.7,
            'brand': 'Samsung',
            'specs': {
                'processor': 'Snapdragon 8 Gen 3 for Galaxy',
                'memory': '12GB LPDDR5X RAM',
                'storage': '512GB UFS 4.0',
                'display': '6.8-inch Dynamic AMOLED 2X, 120Hz, 3120 x 1440 pixels, 2600 nits peak',
                'main_camera': '200MP wide (f/1.7) + 12MP ultrawide (f/2.2) + 50MP telephoto (5x, f/3.4) + 10MP telephoto (3x, f/2.4)',
                'selfie_camera': '12MP (f/2.2)',
                'battery': '5000mAh, 45W wired charging, 15W wireless charging',
                'operating_system': 'Android 14 with One UI 6.1',
                'connectivity': '5G, Wi-Fi 7, Bluetooth 5.3, NFC, UWB',
                'dimensions': '162.3 x 79.0 x 8.6 mm',
                'weight': '232g',
                'water_resistance': 'IP68 water and dust resistance',
                's_pen': 'Built-in S Pen with 2.8ms latency',
                'security': 'Ultrasonic fingerprint sensor, face recognition',
                'colors': 'Titanium Black, Titanium Gray, Titanium Violet, Titanium Yellow',
                'special_features': 'Galaxy AI, 7 years of OS updates, Ray Tracing for gaming'
            }
        },
        {
            'name': 'Apple iPhone 15 Pro Max',
            'price': '₹1,59,900',
            'rating': 4.8,
            'brand': 'Apple',
            'specs': {
                'processor': 'A17 Pro chip with 6-core CPU, 6-core GPU, 16-core Neural Engine',
                'memory': '8GB RAM',
                'storage': '256GB',
                'display': '6.7-inch Super Retina XDR OLED, 120Hz ProMotion, 2796 x 1290 pixels, 2000 nits peak',
                'main_camera': '48MP main (f/1.78) + 12MP ultrawide (f/2.2) + 12MP telephoto (5x, f/2.8)',
                'selfie_camera': '12MP TrueDepth (f/1.9)',
                'battery': 'Up to 29 hours video playback, 20W wired charging, 15W MagSafe wireless charging',
                'operating_system': 'iOS 17',
                'connectivity': '5G, Wi-Fi 6E, Bluetooth 5.3, NFC, UWB',
                'dimensions': '159.9 x 76.7 x 8.25 mm',
                'weight': '221g',
                'water_resistance': 'IP68 water and dust resistance (6 meters for 30 minutes)',
                'security': 'Face ID',
                'colors': 'Natural Titanium, Blue Titanium, White Titanium, Black Titanium',
                'special_features': 'Action button, USB-C port, Ceramic Shield front, Titanium design'
            }
        },
        {
            'name': 'Google Pixel 8 Pro',
            'price': '₹1,06,999',
            'rating': 4.6,
            'brand': 'Google',
            'specs': {
                'processor': 'Google Tensor G3',
                'memory': '12GB LPDDR5X RAM',
                'storage': '256GB UFS 3.1',
                'display': '6.7-inch LTPO OLED, 120Hz, 2992 x 1344 pixels, 2400 nits peak',
                'main_camera': '50MP wide (f/1.68) + 48MP ultrawide (f/1.95) + 48MP telephoto (5x, f/2.8)',
                'selfie_camera': '10.5MP (f/2.2)',
                'battery': '5050mAh, 30W wired charging, 23W wireless charging',
                'operating_system': 'Android 14 with 7 years of updates',
                'connectivity': '5G, Wi-Fi 7, Bluetooth 5.3, NFC, UWB',
                'dimensions': '162.6 x 76.5 x 8.8 mm',
                'weight': '213g',
                'water_resistance': 'IP68 water and dust resistance',
                'security': 'In-display fingerprint sensor, face unlock',
                'colors': 'Obsidian, Porcelain, Bay',
                'special_features': 'Google AI features, Magic Editor, Audio Magic Eraser, Temperature sensor'
            }
        }
    ],
    'tablets': [
        {
            'name': 'Apple iPad Pro 12.9-inch M2',
            'price': '₹1,12,900',
            'rating': 4.8,
            'brand': 'Apple',
            'specs': {
                'processor': 'Apple M2 chip with 8-core CPU, 10-core GPU',
                'memory': '8GB RAM (16GB for 1TB and 2TB models)',
                'storage': '256GB',
                'display': '12.9-inch Liquid Retina XDR mini-LED, 120Hz ProMotion, 2732 x 2048 pixels, 1600 nits peak',
                'main_camera': '12MP wide (f/1.8) + 10MP ultrawide (f/2.4)',
                'selfie_camera': '12MP TrueDepth (f/2.4) with Center Stage',
                'battery': 'Up to 10 hours web browsing on Wi-Fi',
                'operating_system': 'iPadOS 17',
                'connectivity': '5G (optional), Wi-Fi 6E, Bluetooth 5.3, USB-C (Thunderbolt 4)',
                'dimensions': '280.6 x 214.9 x 6.4 mm',
                'weight': '682g (Wi-Fi), 684g (Wi-Fi + Cellular)',
                'audio': 'Four-speaker audio system',
                'security': 'Face ID',
                'colors': 'Silver, Space Gray',
                'accessories_support': 'Apple Pencil 2, Magic Keyboard, Smart Keyboard Folio'
            }
        },
        {
            'name': 'Samsung Galaxy Tab S9 Ultra',
            'price': '₹1,08,999',
            'rating': 4.7,
            'brand': 'Samsung',
            'specs': {
                'processor': 'Snapdragon 8 Gen 2 for Galaxy',
                'memory': '12GB RAM',
                'storage': '256GB, expandable up to 1TB via microSD',
                'display': '14.6-inch Dynamic AMOLED 2X, 120Hz, 2960 x 1848 pixels, HDR10+',
                'main_camera': '13MP wide (f/2.0) + 8MP ultrawide (f/2.2)',
                'selfie_camera': '12MP wide (f/2.2) + 12MP ultrawide (f/2.4)',
                'battery': '11,200mAh, 45W fast charging',
                'operating_system': 'Android 13 with One UI 5.1',
                'connectivity': '5G (optional), Wi-Fi 6E, Bluetooth 5.3, USB-C 3.2',
                'dimensions': '326.4 x 208.6 x 5.5 mm',
                'weight': '732g (Wi-Fi), 737g (5G)',
                'audio': 'Quad speakers tuned by AKG, Dolby Atmos',
                'security': 'In-display fingerprint sensor',
                'colors': 'Graphite, Beige',
                'accessories_support': 'S Pen included, Book Cover Keyboard',
                'special_features': 'IP68 water and dust resistance, Samsung DeX'
            }
        }
    ],
    'cpus': [
        {
            'name': 'AMD Ryzen 9 7950X',
            'price': '₹59,999',
            'rating': 4.8,
            'brand': 'AMD',
            'specs': {
                'cores': '16 cores, 32 threads',
                'base_clock': '4.5 GHz',
                'boost_clock': 'Up to 5.7 GHz',
                'cache': '64MB L3 cache, 16MB L2 cache',
                'tdp': '170W',
                'socket': 'AM5',
                'architecture': 'Zen 4',
                'manufacturing_process': 'TSMC 5nm',
                'memory_support': 'DDR5-5200, up to 128GB',
                'pcie_support': 'PCIe 5.0',
                'integrated_graphics': 'AMD Radeon Graphics (2 cores, 2.2 GHz)',
                'max_temperature': '95°C',
                'unlocked': 'Yes, fully unlocked for overclocking',
                'included_cooler': 'None',
                'release_date': 'September 2022'
            }
        },
        {
            'name': 'Intel Core i9-13900K',
            'price': '₹54,999',
            'rating': 4.7,
            'brand': 'Intel',
            'specs': {
                'cores': '24 cores (8P + 16E), 32 threads',
                'base_clock': '3.0 GHz (P-cores), 2.2 GHz (E-cores)',
                'boost_clock': 'Up to 5.8 GHz (P-cores), 4.3 GHz (E-cores)',
                'cache': '36MB Intel Smart Cache, 32MB L2 cache',
                'tdp': '125W (PL1), up to 253W (PL2)',
                'socket': 'LGA 1700',
                'architecture': 'Raptor Lake',
                'manufacturing_process': 'Intel 7 (10nm Enhanced SuperFin)',
                'memory_support': 'DDR5-5600, DDR4-3200, up to 128GB',
                'pcie_support': 'PCIe 5.0 x16, PCIe 4.0 x4',
                'integrated_graphics': 'Intel UHD Graphics 770',
                'max_temperature': '100°C',
                'unlocked': 'Yes, fully unlocked for overclocking',
                'included_cooler': 'None',
                'release_date': 'October 2022'
            }
        }
    ],
    'gpus': [
        {
            'name': 'NVIDIA GeForce RTX 4090',
            'price': '₹1,69,999',
            'rating': 4.9,
            'brand': 'NVIDIA',
            'specs': {
                'gpu': 'NVIDIA Ada Lovelace AD102',
                'cuda_cores': '16,384',
                'tensor_cores': '512 (4th Gen)',
                'rt_cores': '128 (3rd Gen)',
                'base_clock': '2.23 GHz',
                'boost_clock': '2.52 GHz',
                'memory': '24GB GDDR6X',
                'memory_speed': '21 Gbps',
                'memory_bus': '384-bit',
                'memory_bandwidth': '1,008 GB/s',
                'tdp': '450W',
                'power_connectors': '1x 16-pin (12VHPWR)',
                'recommended_psu': '850W',
                'interface': 'PCIe 4.0 x16',
                'display_outputs': '1x HDMI 2.1, 3x DisplayPort 1.4a',
                'max_resolution': '8K (7680 x 4320)',
                'directx_support': 'DirectX 12 Ultimate',
                'ray_tracing': 'Yes, hardware-accelerated',
                'dlss': 'DLSS 3.5 with Frame Generation',
                'dimensions': '304 x 137 x 61 mm (3-slot)',
                'manufacturing_process': 'TSMC 4N'
            }
        },
        {
            'name': 'AMD Radeon RX 7900 XTX',
            'price': '₹1,09,999',
            'rating': 4.7,
            'brand': 'AMD',
            'specs': {
                'gpu': 'AMD RDNA 3 Navi 31',
                'stream_processors': '12,288',
                'ray_accelerators': '96 (2nd Gen)',
                'ai_accelerators': '192 (2nd Gen)',
                'game_clock': '2.3 GHz',
                'boost_clock': '2.5 GHz',
                'memory': '24GB GDDR6',
                'memory_speed': '20 Gbps',
                'memory_bus': '384-bit',
                'memory_bandwidth': '960 GB/s',
                'infinity_cache': '96MB',
                'tdp': '355W',
                'power_connectors': '2x 8-pin',
                'recommended_psu': '800W',
                'interface': 'PCIe 4.0 x16',
                'display_outputs': '1x HDMI 2.1, 2x DisplayPort 2.1',
                'max_resolution': '8K (7680 x 4320)',
                'directx_support': 'DirectX 12 Ultimate',
                'ray_tracing': 'Yes, hardware-accelerated',
                'fsr': 'FSR 3.0 with Fluid Motion Frames',
                'dimensions': '287 x 123 x 51 mm (2.5-slot)',
                'manufacturing_process': 'TSMC 5nm + 6nm'
            }
        }
    ],
    'storage': [
        {
            'name': 'Samsung 990 PRO 2TB NVMe SSD',
            'price': '₹22,999',
            'rating': 4.9,
            'brand': 'Samsung',
            'specs': {
                'capacity': '2TB',
                'form_factor': 'M.2 2280',
                'interface': 'PCIe 4.0 x4, NVMe 2.0',
                'controller': 'Samsung in-house controller',
                'nand_type': 'Samsung V-NAND 3-bit MLC (TLC)',
                'dram_cache': 'Yes, 2GB LPDDR4',
                'sequential_read': 'Up to 7,450 MB/s',
                'sequential_write': 'Up to 6,900 MB/s',
                'random_read': 'Up to 1,400K IOPS',
                'random_write': 'Up to 1,550K IOPS',
                'endurance': '1,200 TBW (Terabytes Written)',
                'mtbf': '1.5 million hours',
                'encryption': 'AES 256-bit hardware-based encryption',
                'power_consumption': '7.8W (active), 50mW (idle)',
                'warranty': '5 years limited warranty',
                'software': 'Samsung Magician Software'
            }
        },
        {
            'name': 'WD Black SN850X 1TB NVMe SSD',
            'price': '₹13,999',
            'rating': 4.8,
            'brand': 'Western Digital',
            'specs': {
                'capacity': '1TB',
                'form_factor': 'M.2 2280',
                'interface': 'PCIe 4.0 x4, NVMe 1.4',
                'controller': 'WD in-house controller',
                'nand_type': '3D TLC NAND',
                'dram_cache': 'Yes, DDR4',
                'sequential_read': 'Up to 7,300 MB/s',
                'sequential_write': 'Up to 6,300 MB/s',
                'random_read': 'Up to 1,200K IOPS',
                'random_write': 'Up to 1,100K IOPS',
                'endurance': '600 TBW (Terabytes Written)',
                'mtbf': '1.75 million hours',
                'encryption': 'AES 256-bit hardware-based encryption',
                'power_consumption': '9.65W (active), 70mW (idle)',
                'warranty': '5 years limited warranty',
                'software': 'WD Dashboard with Game Mode 2.0'
            }
        }
    ],
    'monitors': [
        {
            'name': 'LG UltraGear 27GP950-B',
            'price': '₹69,999',
            'rating': 4.7,
            'brand': 'LG',
            'specs': {
                'screen_size': '27 inches',
                'resolution': '3840 x 2160 (4K UHD)',
                'panel_type': 'Nano IPS',
                'refresh_rate': '160Hz (overclocked), 144Hz (native)',
                'response_time': '1ms GtG',
                'hdr': 'VESA DisplayHDR 600',
                'color_depth': '10-bit (1.07 billion colors)',
                'color_gamut': '98% DCI-P3, 135% sRGB',
                'contrast_ratio': '1000:1 (static)',
                'brightness': '400 nits (typical), 600 nits (peak)',
                'viewing_angles': '178°/178°',
                'adaptive_sync': 'NVIDIA G-SYNC Compatible, AMD FreeSync Premium Pro',
                'inputs': '2x HDMI 2.1, 1x DisplayPort 1.4, 1x USB-B upstream, 2x USB-A downstream',
                'audio': 'No built-in speakers, 3.5mm headphone jack',
                'ergonomics': 'Height, Tilt, Pivot adjustments',
                'vesa_mount': '100 x 100mm',
                'special_features': 'RGB Sphere Lighting 2.0, Black Stabilizer, Dynamic Action Sync'
            }
        },
        {
            'name': 'Samsung Odyssey G7 (C32G75T)',
            'price': '₹54,999',
            'rating': 4.6,
            'brand': 'Samsung',
            'specs': {
                'screen_size': '32 inches',
                'resolution': '2560 x 1440 (WQHD)',
                'panel_type': 'VA (Quantum Dot)',
                'curvature': '1000R',
                'refresh_rate': '240Hz',
                'response_time': '1ms MPRT',
                'hdr': 'HDR600',
                'color_depth': '10-bit (1.07 billion colors)',
                'color_gamut': '95% DCI-P3, 125% sRGB',
                'contrast_ratio': '2500:1 (static)',
                'brightness': '350 nits (typical), 600 nits (peak)',
                'viewing_angles': '178°/178°',
                'adaptive_sync': 'NVIDIA G-SYNC Compatible, AMD FreeSync Premium Pro',
                'inputs': '1x HDMI 2.0, 2x DisplayPort 1.4, 2x USB 3.0',
                'audio': 'No built-in speakers, 3.5mm headphone jack',
                'ergonomics': 'Height, Tilt, Swivel adjustments',
                'vesa_mount': '100 x 100mm',
                'special_features': 'Infinity Core Lighting, Eye Saver Mode, Low Input Lag Mode'
            }
        }
    ]
}

def add_products():
    print("Adding sample products to the database...")
    products_added = 0
    
    for category_id, products in sample_products.items():
        for product_data in products:
            # Check if product already exists
            existing_product = Product.query.filter_by(name=product_data['name']).first()
            if existing_product:
                print(f"Product '{product_data['name']}' already exists, skipping...")
                continue
                
            # Generate a unique product ID
            product_id = f"{category_id}{Product.query.filter_by(category_id=category_id).count() + 1}"
            
            # Create new product
            new_product = Product(
                id=product_id,
                name=product_data['name'],
                price=product_data['price'],
                rating=product_data['rating'],
                brand=product_data['brand'],
                category_id=category_id
            )
            
            db.session.add(new_product)
            
            # Add product specifications
            for key, value in product_data['specs'].items():
                new_spec = ProductSpec(
                    product_id=product_id,
                    spec_key=key,
                    spec_value=str(value)
                )
                db.session.add(new_spec)
            
            products_added += 1
            print(f"Added {product_data['name']} to {category_id} category")
    
    db.session.commit()
    print(f"Successfully added {products_added} new products to the database!")

if __name__ == "__main__":
    add_products()
