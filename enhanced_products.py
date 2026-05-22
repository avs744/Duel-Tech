from app import db, Product, ProductSpec, categories
import random

# Enhanced products with detailed specifications and real names
enhanced_products = {
    'laptops': [
        {
            'name': 'Apple MacBook Pro 16 (M3 Max, 2023)',
            'price': '₹3,49,900',
            'rating': 4.9,
            'brand': 'Apple',
            'specs': {
                'processor': 'Apple M3 Max 16-core CPU',
                'graphics': 'Apple M3 Max 40-core GPU',
                'memory': '64GB unified memory',
                'storage': '2TB SSD',
                'display': '16.2-inch Liquid Retina XDR display (3456 x 2234), 1600 nits peak brightness, ProMotion 120Hz',
                'battery': '100Wh lithium-polymer battery, up to 22 hours',
                'ports': '3x Thunderbolt 4, HDMI 2.1, SDXC card slot, MagSafe 3, 3.5mm headphone jack',
                'connectivity': 'Wi-Fi 6E (802.11ax), Bluetooth 5.3',
                'camera': '1080p FaceTime HD camera with advanced image signal processor',
                'audio': 'Six-speaker sound system with force-cancelling woofers, Spatial Audio support',
                'keyboard': 'Backlit Magic Keyboard with Touch ID, ambient light sensor',
                'dimensions': '1.68 x 35.57 x 24.81 cm',
                'weight': '2.16 kg',
                'color': 'Space Black',
                'operating_system': 'macOS Sonoma',
                'warranty': '1-year limited warranty with 90 days of technical support',
                'power_adapter': '140W USB-C Power Adapter',
                'in_the_box': 'MacBook Pro, USB-C to MagSafe 3 Cable, 140W USB-C Power Adapter'
            }
        },
        {
            'name': 'Dell XPS 17 9730 (2023)',
            'price': '₹2,89,990',
            'rating': 4.7,
            'brand': 'Dell',
            'specs': {
                'processor': '13th Gen Intel Core i9-13900H (24MB Cache, up to 5.4 GHz, 14 cores)',
                'graphics': 'NVIDIA GeForce RTX 4080 12GB GDDR6',
                'memory': '64GB DDR5 4800MHz (2x32GB)',
                'storage': '2TB M.2 PCIe NVMe SSD',
                'display': '17-inch UHD+ (3840 x 2400) InfinityEdge Touch Anti-Reflective 500-Nit Display',
                'battery': '97WHr battery, up to 14 hours',
                'ports': '4x Thunderbolt 4, 1x SD card reader v4.0, 1x 3.5mm headphone/microphone combo jack',
                'connectivity': 'Killer Wi-Fi 6E 1675 (AX211) 2x2, Bluetooth 5.3',
                'camera': 'HD 720p with Windows Hello IR camera',
                'audio': 'Quad-speaker design with Waves MaxxAudio Pro, 2.5W x2 woofers, 1.5W x2 tweeters',
                'keyboard': 'Backlit keyboard with fingerprint reader in power button',
                'dimensions': '1.99 x 37.4 x 24.8 cm',
                'weight': '2.53 kg',
                'color': 'Platinum Silver exterior, Black interior',
                'operating_system': 'Windows 11 Pro',
                'warranty': '1-year Premium Support',
                'power_adapter': '130W USB-C power adapter',
                'security': 'TPM 2.0, Windows Hello fingerprint reader and facial recognition'
            }
        },
        {
            'name': 'ASUS ROG Zephyrus G16 (2024)',
            'price': '₹2,24,990',
            'rating': 4.8,
            'brand': 'ASUS',
            'specs': {
                'processor': 'Intel Core Ultra 9 185H (16 cores, up to 5.1 GHz)',
                'graphics': 'NVIDIA GeForce RTX 4070 8GB GDDR6',
                'memory': '32GB DDR5 5600MHz (16GB onboard + 16GB SO-DIMM)',
                'storage': '1TB PCIe 4.0 NVMe M.2 SSD',
                'display': '16-inch ROG Nebula Display, QHD+ 2560 x 1600, 240Hz, 3ms, G-SYNC, Pantone Validated',
                'battery': '90WHr, up to 10 hours',
                'ports': '2x USB 3.2 Gen 2 Type-A, 2x USB 3.2 Gen 2 Type-C (with DisplayPort and Power Delivery), 1x HDMI 2.1, 1x 3.5mm Combo Audio Jack, 1x RJ45 LAN port',
                'connectivity': 'Wi-Fi 6E (802.11ax), Bluetooth 5.3',
                'camera': '1080p FHD IR camera with Windows Hello',
                'audio': 'Dolby Atmos, Smart Amp Technology, AI noise-cancellation, 6-speaker system with dual force-cancelling woofers',
                'keyboard': 'RGB per-key backlit chiclet keyboard, 1.7mm travel distance, N-key rollover',
                'cooling': 'ROG Intelligent Cooling, Thermal Grizzly liquid metal, Arc Flow fans, vapor chamber',
                'dimensions': '1.99 x 35.4 x 24.6 cm',
                'weight': '2.0 kg',
                'color': 'Eclipse Gray',
                'operating_system': 'Windows 11 Home',
                'warranty': '1-year global warranty',
                'power_adapter': '240W power adapter',
                'special_features': 'ROG Armory Crate, ROG Aura Sync, Dolby Vision HDR support'
            }
        },
        {
            'name': 'Lenovo ThinkPad X1 Carbon Gen 11',
            'price': '₹1,89,990',
            'rating': 4.7,
            'brand': 'Lenovo',
            'specs': {
                'processor': 'Intel Core i7-1365U vPro (10 cores, up to 5.2 GHz)',
                'graphics': 'Intel Iris Xe Graphics',
                'memory': '32GB LPDDR5 6400MHz (soldered)',
                'storage': '1TB PCIe Gen4 NVMe SSD',
                'display': '14-inch WUXGA (1920 x 1200) IPS, 400 nits, 100% sRGB, Low Blue Light',
                'battery': '57Wh, up to 15 hours',
                'ports': '2x Thunderbolt 4, 2x USB-A 3.2 Gen 1, 1x HDMI 2.0b, 1x 3.5mm combo jack',
                'connectivity': 'Wi-Fi 6E, Bluetooth 5.1, 5G (optional)',
                'camera': '1080p FHD + IR camera with privacy shutter',
                'audio': 'Dolby Atmos speaker system, 4x 360° far-field microphones',
                'keyboard': 'Spill-resistant backlit keyboard with TrackPoint',
                'dimensions': '15.36 x 315.6 x 222.5 mm',
                'weight': '1.12 kg',
                'color': 'Deep Black',
                'operating_system': 'Windows 11 Pro',
                'security': 'dTPM 2.0, Match-on-Chip Fingerprint Reader, IR camera for Windows Hello',
                'durability': 'MIL-STD-810H tested, spill-resistant keyboard',
                'warranty': '3-year Premier Support',
                'power_adapter': '65W USB-C slim adapter',
                'special_features': 'Human presence detection, Computer Vision features'
            }
        },
        {
            'name': 'MSI Stealth 16 Mercedes-AMG Edition',
            'price': '₹2,79,990',
            'rating': 4.8,
            'brand': 'MSI',
            'specs': {
                'processor': 'Intel Core i9-13900H (14 cores, up to 5.4 GHz)',
                'graphics': 'NVIDIA GeForce RTX 4070 8GB GDDR6',
                'memory': '32GB DDR5 5200MHz (16GB x2)',
                'storage': '2TB PCIe Gen4 NVMe SSD (1TB x2)',
                'display': '16-inch UHD+ (3840 x 2400) OLED, 100% DCI-P3, VESA DisplayHDR 600 True Black',
                'battery': '99.9Whr, up to 8 hours',
                'ports': '1x Thunderbolt 4, 2x USB-A 3.2 Gen 2, 1x USB-C 3.2 Gen 2, 1x HDMI 2.1, 1x 3.5mm combo jack, 1x SD card reader',
                'connectivity': 'Killer Wi-Fi 6E, Bluetooth 5.3',
                'camera': '1080p FHD IR camera',
                'audio': 'Dynaudio 6-speaker system, Hi-Res Audio certification',
                'keyboard': 'SteelSeries per-key RGB backlit keyboard',
                'dimensions': '19.95 x 355.8 x 259.7 mm',
                'weight': '1.99 kg',
                'color': 'Selenite Grey Magno',
                'operating_system': 'Windows 11 Pro',
                'cooling': 'Cooler Boost 5 technology, 2 fans, 6 heat pipes',
                'warranty': '2-year limited warranty',
                'power_adapter': '240W slim adapter',
                'special_features': 'Mercedes-AMG exclusive design elements, MSI Center Pro software'
            }
        }
    ],
    'smartphones': [
        {
            'name': 'Samsung Galaxy S24 Ultra',
            'price': '₹1,39,999',
            'rating': 4.8,
            'brand': 'Samsung',
            'specs': {
                'processor': 'Qualcomm Snapdragon 8 Gen 3 for Galaxy (4nm)',
                'memory': '12GB LPDDR5X RAM',
                'storage': '512GB UFS 4.0',
                'display': '6.8-inch Dynamic AMOLED 2X, QHD+ (3088 x 1440), 120Hz adaptive refresh rate, 2600 nits peak brightness',
                'main_camera': '200MP wide (f/1.7, OIS) + 12MP ultrawide (f/2.2, 120°) + 50MP telephoto (5x, f/3.4, OIS) + 10MP telephoto (3x, f/2.4, OIS)',
                'selfie_camera': '12MP (f/2.2, 80°, 4K video)',
                'battery': '5000mAh, 45W wired charging, 15W wireless charging, 4.5W reverse wireless charging',
                'operating_system': 'Android 14 with One UI 6.1, 7 years of OS updates',
                'connectivity': '5G, Wi-Fi 7, Bluetooth 5.3, NFC, UWB',
                'water_resistance': 'IP68 water and dust resistance (1.5m for 30 minutes)',
                's_pen': 'Built-in S Pen with 2.8ms latency, IP68 rated',
                'security': 'Ultrasonic fingerprint sensor, face recognition, Samsung Knox Vault',
                'dimensions': '162.3 x 79.0 x 8.6 mm',
                'weight': '232g',
                'build': 'Armor Aluminum frame, Corning Gorilla Glass Victus 2 front and back',
                'colors': 'Titanium Black, Titanium Gray, Titanium Violet, Titanium Yellow',
                'audio': 'Stereo speakers tuned by AKG, Dolby Atmos support, no 3.5mm headphone jack',
                'sensors': 'Accelerometer, Barometer, Fingerprint, Gyro, Geomagnetic, Hall, Light, Proximity',
                'special_features': 'Galaxy AI, Circle to Search, Live Translate, Note Assist, Photo Assist'
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
                'display': '6.7-inch Super Retina XDR OLED, 2796 x 1290 pixels, 120Hz ProMotion, 2000 nits peak brightness, Always-On display',
                'main_camera': '48MP main (f/1.78, OIS) + 12MP ultrawide (f/2.2, 120°) + 12MP telephoto (5x, f/2.8, OIS)',
                'selfie_camera': '12MP TrueDepth (f/1.9, autofocus)',
                'battery': '4441mAh, up to 29 hours video playback, 20W wired charging, 15W MagSafe wireless charging',
                'operating_system': 'iOS 17, guaranteed 5+ years of updates',
                'connectivity': '5G (sub-6GHz and mmWave), Wi-Fi 6E, Bluetooth 5.3, NFC, UWB',
                'water_resistance': 'IP68 water and dust resistance (6 meters for 30 minutes)',
                'security': 'Face ID',
                'dimensions': '159.9 x 76.7 x 8.25 mm',
                'weight': '221g',
                'build': 'Titanium frame, Ceramic Shield front, textured matte glass back',
                'colors': 'Natural Titanium, Blue Titanium, White Titanium, Black Titanium',
                'audio': 'Stereo speakers, Spatial Audio, no 3.5mm headphone jack',
                'sensors': 'Face ID, LiDAR Scanner, Barometer, High dynamic range gyro, High-g accelerometer, Proximity sensor, Dual ambient light sensors',
                'special_features': 'Action button, Emergency SOS, Crash Detection, Satellite connectivity, Dynamic Island'
            }
        },
        {
            'name': 'Google Pixel 8 Pro',
            'price': '₹1,06,999',
            'rating': 4.7,
            'brand': 'Google',
            'specs': {
                'processor': 'Google Tensor G3 with Titan M2 security coprocessor',
                'memory': '12GB LPDDR5X RAM',
                'storage': '256GB UFS 3.1',
                'display': '6.7-inch LTPO OLED, 1344 x 2992 pixels, 120Hz adaptive refresh rate, 2400 nits peak brightness, Gorilla Glass Victus 2',
                'main_camera': '50MP Octa PD wide (f/1.68, OIS) + 48MP Quad PD ultrawide (f/1.95, 125.5°) + 48MP Quad PD telephoto (5x, f/2.8, OIS)',
                'selfie_camera': '10.5MP dual PD (f/2.2, 95°, 4K video)',
                'battery': '5050mAh, 30W wired charging (50% in 30 min), 23W wireless charging',
                'operating_system': 'Android 14 with 7 years of OS and security updates',
                'connectivity': '5G, Wi-Fi 7, Bluetooth 5.3, NFC, UWB',
                'water_resistance': 'IP68 water and dust resistance',
                'security': 'In-display fingerprint sensor, face unlock, Titan M2 security chip',
                'dimensions': '162.6 x 76.5 x 8.8 mm',
                'weight': '213g',
                'build': 'Aluminum frame, Gorilla Glass Victus 2 front and back, matte finish',
                'colors': 'Obsidian, Porcelain, Bay',
                'audio': 'Stereo speakers, 3 microphones, noise suppression',
                'sensors': 'Proximity, Ambient light, Accelerometer, Gyrometer, Magnetometer, Barometer, Spectral and flicker sensor, Temperature sensor',
                'special_features': 'Google AI features, Magic Editor, Audio Magic Eraser, Best Take, Call Screen, Live Translate'
            }
        },
        {
            'name': 'Xiaomi 14 Ultra',
            'price': '₹99,999',
            'rating': 4.7,
            'brand': 'Xiaomi',
            'specs': {
                'processor': 'Qualcomm Snapdragon 8 Gen 3 (4nm)',
                'memory': '16GB LPDDR5X RAM',
                'storage': '512GB UFS 4.0',
                'display': '6.73-inch LTPO AMOLED, QHD+ (3200 x 1440), 1-120Hz adaptive refresh rate, 3000 nits peak brightness, Dolby Vision',
                'main_camera': 'Leica quad camera: 50MP main (f/1.63-f/4.0, variable aperture, OIS) + 50MP ultrawide (f/1.8, 122°) + 50MP telephoto (3.2x, f/1.8, OIS) + 50MP periscope (5x, f/2.5, OIS)',
                'selfie_camera': '32MP (f/2.0, HDR, 4K video)',
                'battery': '5000mAh, 90W wired charging, 80W wireless charging, 10W reverse wireless charging',
                'operating_system': 'Android 14 with HyperOS, 4 years of OS updates',
                'connectivity': '5G, Wi-Fi 7, Bluetooth 5.4, NFC, IR blaster',
                'water_resistance': 'IP68 water and dust resistance',
                'security': 'In-display ultrasonic fingerprint sensor, face recognition',
                'dimensions': '161.4 x 75.3 x 9.2 mm',
                'weight': '220g',
                'build': 'Aluminum frame, Xiaomi nano-tech vegan leather back, Gorilla Glass Victus 2 front',
                'colors': 'Black, White, Titanium',
                'audio': 'Stereo speakers tuned by Harman Kardon, Dolby Atmos support, no 3.5mm headphone jack',
                'sensors': 'Accelerometer, Gyro, Proximity, Compass, Color spectrum',
                'special_features': 'Leica professional photography modes, Light Fusion 900 imaging system, IP68 dust/water resistant'
            }
        },
        {
            'name': 'Nothing Phone (2a)',
            'price': '₹25,999',
            'rating': 4.6,
            'brand': 'Nothing',
            'specs': {
                'processor': 'MediaTek Dimensity 7200 Pro (4nm)',
                'memory': '8GB LPDDR5 RAM',
                'storage': '128GB UFS 3.1',
                'display': '6.7-inch AMOLED, FHD+ (2412 x 1080), 120Hz refresh rate, 1300 nits peak brightness',
                'main_camera': '50MP main (f/1.88, OIS) + 50MP ultrawide (f/2.2, 114°)',
                'selfie_camera': '32MP (f/2.2, 4K video)',
                'battery': '5000mAh, 45W wired charging',
                'operating_system': 'Nothing OS 2.5 based on Android 14, 3 years of OS updates',
                'connectivity': '5G, Wi-Fi 6, Bluetooth 5.3, NFC',
                'water_resistance': 'IP54 splash resistance',
                'security': 'In-display fingerprint sensor, face unlock',
                'dimensions': '161.7 x 76.3 x 8.5 mm',
                'weight': '190g',
                'build': 'Plastic frame, plastic back with transparent design elements, Gorilla Glass 5 front',
                'colors': 'Black, White, Milk',
                'audio': 'Stereo speakers, no 3.5mm headphone jack',
                'sensors': 'Accelerometer, Gyro, Proximity, Compass',
                'special_features': 'Glyph Interface with 8 customizable LED segments, ChatGPT integration'
            }
        }
    ],
    'cpus': [
        {
            'name': 'AMD Ryzen 9 7950X3D',
            'price': '₹64,999',
            'rating': 4.9,
            'brand': 'AMD',
            'specs': {
                'cores': '16 cores, 32 threads',
                'base_clock': '4.2 GHz',
                'boost_clock': 'Up to 5.7 GHz',
                'cache': '128MB L3 cache (64MB + 64MB 3D V-Cache), 16MB L2 cache',
                'tdp': '120W',
                'socket': 'AM5 (LGA 1718)',
                'architecture': 'Zen 4 with 3D V-Cache',
                'manufacturing_process': 'TSMC 5nm CCD, 6nm IOD',
                'memory_support': 'DDR5-5200 (up to 128GB)',
                'pcie_support': 'PCIe 5.0 (28 lanes)',
                'integrated_graphics': 'AMD Radeon Graphics (2 compute units, up to 2.2 GHz)',
                'max_temperature': '89°C',
                'unlocked': 'Yes, partially (limited due to 3D V-Cache)',
                'included_cooler': 'None',
                'release_date': 'February 2023',
                'power_features': 'Precision Boost 2, Precision Boost Overdrive 2, Curve Optimizer',
                'instruction_sets': 'SSE4.1, SSE4.2, AVX, AVX2, AVX-512, FMA3, SHA, AES',
                'virtualization': 'AMD-V, AMD SVM',
                'gaming_performance': 'Optimized for gaming with 3D V-Cache technology',
                'benchmark_score': 'Cinebench R23 multi-core: ~38,000 points'
            }
        },
        {
            'name': 'Intel Core i9-14900KS',
            'price': '₹69,999',
            'rating': 4.7,
            'brand': 'Intel',
            'specs': {
                'cores': '24 cores (8P + 16E), 32 threads',
                'base_clock': '3.2 GHz (P-cores), 2.4 GHz (E-cores)',
                'boost_clock': 'Up to 6.2 GHz (P-cores), 4.5 GHz (E-cores)',
                'cache': '36MB Intel Smart Cache (L3), 32MB L2 cache',
                'tdp': '150W (PL1), up to 320W (PL2)',
                'socket': 'LGA 1700',
                'architecture': 'Raptor Lake Refresh',
                'manufacturing_process': 'Intel 7 (10nm Enhanced SuperFin)',
                'memory_support': 'DDR5-5600, DDR4-3200 (up to 192GB)',
                'pcie_support': 'PCIe 5.0 (16 lanes) + PCIe 4.0 (4 lanes)',
                'integrated_graphics': 'Intel UHD Graphics 770',
                'max_temperature': '100°C (TJmax)',
                'unlocked': 'Yes, fully unlocked for overclocking',
                'included_cooler': 'None',
                'release_date': 'January 2024',
                'power_features': 'Intel Thermal Velocity Boost, Intel Adaptive Boost Technology',
                'instruction_sets': 'SSE4.1, SSE4.2, AVX, AVX2, AVX-512, FMA3, SHA, AES',
                'virtualization': 'Intel VT-x, Intel VT-d',
                'special_features': 'Intel Thread Director, Intel Speed Optimizer',
                'benchmark_score': 'Cinebench R23 multi-core: ~40,000 points'
            }
        }
    ],
    'gpus': [
        {
            'name': 'NVIDIA GeForce RTX 4090 Founders Edition',
            'price': '₹1,72,999',
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
                'max_resolution': '8K (7680 x 4320) @ 60Hz',
                'max_digital_resolution': '7680 x 4320',
                'directx_support': 'DirectX 12 Ultimate',
                'opengl_support': 'OpenGL 4.6',
                'vulkan_support': 'Vulkan 1.3',
                'ray_tracing': 'Yes, 2nd Gen RT Cores',
                'dlss': 'DLSS 3.5 with Frame Generation',
                'dimensions': '304 x 137 x 61 mm (3-slot)',
                'manufacturing_process': 'TSMC 4N',
                'cooling': 'Dual axial flow-through design',
                'max_gpu_temperature': '90°C',
                'benchmark_3dmark': '3DMark Time Spy Extreme: ~14,000 points',
                'power_efficiency': 'Ada Lovelace architecture with 2x power efficiency over Ampere'
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
                'max_resolution': '8K (7680 x 4320) @ 60Hz',
                'directx_support': 'DirectX 12 Ultimate',
                'opengl_support': 'OpenGL 4.6',
                'vulkan_support': 'Vulkan 1.3',
                'ray_tracing': 'Yes, 2nd Gen Ray Accelerators',
                'fsr': 'FSR 3.0 with Fluid Motion Frames',
                'dimensions': '287 x 123 x 51 mm (2.5-slot)',
                'manufacturing_process': 'TSMC 5nm + 6nm',
                'cooling': 'Triple-fan design with vapor chamber',
                'max_gpu_temperature': '95°C',
                'benchmark_3dmark': '3DMark Time Spy Extreme: ~11,000 points',
                'special_features': 'AMD Radiance Display Engine, AV1 encoding/decoding'
            }
        }
    ],
    'monitors': [
        {
            'name': 'LG UltraGear OLED 27GR95QE',
            'price': '₹89,999',
            'rating': 4.9,
            'brand': 'LG',
            'specs': {
                'screen_size': '26.5 inches',
                'panel_type': 'OLED',
                'resolution': '2560 x 1440 (QHD)',
                'aspect_ratio': '16:9',
                'refresh_rate': '240Hz',
                'response_time': '0.03ms GtG',
                'hdr': 'HDR10',
                'color_depth': '10-bit (1.07 billion colors)',
                'color_gamut': '98.5% DCI-P3, 135% sRGB',
                'contrast_ratio': '1,500,000:1 (static)',
                'brightness': '200 nits (typical), 800 nits (peak)',
                'viewing_angles': '178°/178°',
                'adaptive_sync': 'NVIDIA G-SYNC Compatible, AMD FreeSync Premium Pro',
                'inputs': '2x HDMI 2.1, 1x DisplayPort 1.4, 1x USB-B upstream, 2x USB-A 3.0 downstream',
                'audio': 'No built-in speakers, 3.5mm headphone jack',
                'ergonomics': 'Height (110mm), Tilt (-5° to 15°), Pivot (±90°), Swivel (±10°)',
                'vesa_mount': '100 x 100mm',
                'anti_glare': 'Yes, low reflection coating',
                'blue_light_filter': 'Yes, Reader Mode',
                'flicker_free': 'Yes',
                'dimensions': '605.8 x 380.6 x 224.8 mm (with stand)',
                'weight': '6.4 kg (with stand), 4.5 kg (without stand)',
                'power_consumption': '55W (typical), <0.5W (standby)',
                'special_features': 'Black Stabilizer, Dynamic Action Sync, Crosshair, FPS Counter',
                'warranty': '3-year limited warranty, 1-year panel warranty'
            }
        },
        {
            'name': 'Samsung Odyssey Neo G9 G95NC',
            'price': '₹1,99,999',
            'rating': 4.8,
            'brand': 'Samsung',
            'specs': {
                'screen_size': '57 inches',
                'panel_type': 'Quantum Mini-LED',
                'resolution': '7680 x 2160 (Dual 4K UHD)',
                'aspect_ratio': '32:9',
                'curvature': '1000R',
                'refresh_rate': '240Hz',
                'response_time': '1ms MPRT',
                'hdr': 'VESA DisplayHDR 1000',
                'local_dimming': '2,392 local dimming zones',
                'color_depth': '10-bit (1.07 billion colors)',
                'color_gamut': '95% DCI-P3, 125% sRGB',
                'contrast_ratio': '1,000,000:1 (static)',
                'brightness': '420 nits (typical), 1000 nits (peak)',
                'viewing_angles': '178°/178°',
                'adaptive_sync': 'NVIDIA G-SYNC Compatible, AMD FreeSync Premium Pro',
                'inputs': '1x DisplayPort 2.1, 2x HDMI 2.1, 1x USB-B upstream, 2x USB-A 3.0 downstream',
                'audio': 'No built-in speakers, 3.5mm headphone jack',
                'ergonomics': 'Height (120mm), Tilt (-3° to 13°), Swivel (±15°)',
                'vesa_mount': '100 x 100mm',
                'dimensions': '1,461.0 x 525.6 x 305.1 mm (with stand)',
                'weight': '16.5 kg (with stand), 14.1 kg (without stand)',
                'power_consumption': '120W (typical), <0.5W (standby)',
                'special_features': 'CoreSync lighting, Multi View (PBP/PIP), Auto Source Switch+',
                'warranty': '3-year limited warranty'
            }
        }
    ]
}

def add_enhanced_products():
    print("Adding enhanced products to the database...")
    products_added = 0
    
    for category_id, products in enhanced_products.items():
        for product_data in products:
            # Check if product already exists
            existing_product = Product.query.filter_by(name=product_data['name']).first()
            if existing_product:
                print(f"Product '{product_data['name']}' already exists, updating...")
                
                # Update existing product
                existing_product.price = product_data['price']
                existing_product.rating = product_data['rating']
                existing_product.brand = product_data['brand']
                
                # Delete existing specs
                ProductSpec.query.filter_by(product_id=existing_product.id).delete()
                
                # Add updated specs
                for key, value in product_data['specs'].items():
                    new_spec = ProductSpec(
                        product_id=existing_product.id,
                        spec_key=key,
                        spec_value=str(value)
                    )
                    db.session.add(new_spec)
                
                print(f"Updated {product_data['name']} in {category_id} category")
            else:
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
    print(f"Successfully added/updated products in the database!")

if __name__ == "__main__":
    add_enhanced_products()
