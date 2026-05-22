class GreetingAnimation {
    constructor() {
        this.scene = new THREE.Scene();
        this.camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        this.renderer = new THREE.WebGLRenderer({ 
            antialias: true,
            alpha: true
        });
        this.clock = new THREE.Clock();
        this.particles = [];
        this.init();
    }

    init() {
        // Setup renderer
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.setClearColor(0x000000, 0);
        document.getElementById('greeting-animation').appendChild(this.renderer.domElement);

        // Setup camera
        this.camera.position.z = 20;

        // Add lights
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
        this.scene.add(ambientLight);

        const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
        directionalLight.position.set(5, 5, 5);
        this.scene.add(directionalLight);

        // Add point lights for dynamic lighting
        const colors = [0x2ecc71, 0x3498db, 0xe74c3c, 0xf1c40f];
        colors.forEach((color, i) => {
            const light = new THREE.PointLight(color, 1, 50);
            light.position.set(
                Math.sin(i * Math.PI * 0.5) * 10,
                Math.cos(i * Math.PI * 0.5) * 10,
                5
            );
            this.scene.add(light);
            gsap.to(light.position, {
                x: Math.sin((i + 2) * Math.PI * 0.5) * 10,
                y: Math.cos((i + 2) * Math.PI * 0.5) * 10,
                duration: 2,
                repeat: -1,
                yoyo: true,
                ease: "power1.inOut"
            });
        });

        // Create text
        const loader = new THREE.FontLoader();
        loader.load('/static/fonts/helvetiker_regular.typeface.json', (font) => {
            // Welcome text
            const welcomeGeometry = new THREE.TextGeometry('Welcome to', {
                font: font,
                size: 2,
                height: 0.2,
                curveSegments: 12,
                bevelEnabled: true,
                bevelThickness: 0.05,
                bevelSize: 0.02,
                bevelOffset: 0,
                bevelSegments: 5
            });

            // DuelTech text
            const duelTechGeometry = new THREE.TextGeometry('DuelTech', {
                font: font,
                size: 3,
                height: 0.4,
                curveSegments: 12,
                bevelEnabled: true,
                bevelThickness: 0.1,
                bevelSize: 0.05,
                bevelOffset: 0,
                bevelSegments: 5
            });

            // Create materials with gradients
            const welcomeMaterial = new THREE.MeshPhongMaterial({
                color: 0x2ecc71,
                specular: 0xffffff,
                shininess: 100,
                emissive: 0x2ecc71,
                emissiveIntensity: 0.5
            });

            const duelTechMaterial = new THREE.MeshPhongMaterial({
                color: 0x3498db,
                specular: 0xffffff,
                shininess: 100,
                emissive: 0x3498db,
                emissiveIntensity: 0.5
            });

            // Center and position texts
            welcomeGeometry.computeBoundingBox();
            const welcomeWidth = welcomeGeometry.boundingBox.max.x - welcomeGeometry.boundingBox.min.x;
            const welcomeMesh = new THREE.Mesh(welcomeGeometry, welcomeMaterial);
            welcomeMesh.position.x = -welcomeWidth / 2;
            welcomeMesh.position.y = 3;
            this.scene.add(welcomeMesh);

            duelTechGeometry.computeBoundingBox();
            const duelTechWidth = duelTechGeometry.boundingBox.max.x - duelTechGeometry.boundingBox.min.x;
            const duelTechMesh = new THREE.Mesh(duelTechGeometry, duelTechMaterial);
            duelTechMesh.position.x = -duelTechWidth / 2;
            duelTechMesh.position.y = -1;
            this.scene.add(duelTechMesh);

            // Add particle effects
            this.createParticles();

            // Initial animations
            welcomeMesh.position.z = -50;
            duelTechMesh.position.z = -50;
            welcomeMesh.rotation.x = Math.PI;
            duelTechMesh.rotation.x = Math.PI;

            // Welcome text animation
            gsap.to(welcomeMesh.position, {
                z: 0,
                duration: 2,
                ease: "elastic.out(1, 0.5)"
            });
            gsap.to(welcomeMesh.rotation, {
                x: 0,
                duration: 2,
                ease: "elastic.out(1, 0.5)"
            });

            // DuelTech text animation
            gsap.to(duelTechMesh.position, {
                z: 0,
                duration: 2,
                delay: 0.3,
                ease: "elastic.out(1, 0.5)"
            });
            gsap.to(duelTechMesh.rotation, {
                x: 0,
                duration: 2,
                delay: 0.3,
                ease: "elastic.out(1, 0.5)"
            });

            // Floating animation
            gsap.to([welcomeMesh.position, duelTechMesh.position], {
                y: "+=0.3",
                duration: 2,
                yoyo: true,
                repeat: -1,
                ease: "power1.inOut"
            });

            // Color animation
            const colors = [0x2ecc71, 0x3498db, 0xe74c3c, 0xf1c40f];
            let colorIndex = 0;
            setInterval(() => {
                colorIndex = (colorIndex + 1) % colors.length;
                gsap.to(welcomeMaterial.color, {
                    r: (colors[colorIndex] >> 16) / 255,
                    g: ((colors[colorIndex] >> 8) & 0xff) / 255,
                    b: (colors[colorIndex] & 0xff) / 255,
                    duration: 1
                });
                gsap.to(welcomeMaterial.emissive, {
                    r: (colors[colorIndex] >> 16) / 255,
                    g: ((colors[colorIndex] >> 8) & 0xff) / 255,
                    b: (colors[colorIndex] & 0xff) / 255,
                    duration: 1
                });
            }, 2000);

            // Fade out animation
            setTimeout(() => {
                gsap.to([welcomeMaterial, duelTechMaterial], {
                    opacity: 0,
                    duration: 1.5,
                    onComplete: () => {
                        this.scene.remove(welcomeMesh);
                        this.scene.remove(duelTechMesh);
                        setTimeout(() => {
                            // Properly clean up Three.js resources
                            this.scene.traverse((object) => {
                                if (object.geometry) object.geometry.dispose();
                                if (object.material) {
                                    if (Array.isArray(object.material)) {
                                        object.material.forEach(material => material.dispose());
                                    } else {
                                        object.material.dispose();
                                    }
                                }
                            });
                            this.renderer.dispose();
                            cancelAnimationFrame(this.animationFrame);
                            
                            // Remove the animation container completely
                            const container = document.getElementById('greeting-animation');
                            container.classList.add('fade-out');
                            setTimeout(() => container.remove(), 1000);
                            
                            // Ensure main content is visible
                            document.querySelector('.main-content').style.opacity = '1';
                        }, 500);
                    }
                });
            }, 5000);
        });

        // Handle window resize
        window.addEventListener('resize', () => {
            const width = window.innerWidth;
            const height = window.innerHeight;
            this.camera.aspect = width / height;
            this.camera.updateProjectionMatrix();
            this.renderer.setSize(width, height);
        });

        this.animate();
    }

    createParticles() {
        const geometry = new THREE.BufferGeometry();
        const positions = [];
        const colors = [];
        const sizes = [];

        const colorChoices = [
            new THREE.Color(0x2ecc71),
            new THREE.Color(0x3498db),
            new THREE.Color(0xe74c3c),
            new THREE.Color(0xf1c40f)
        ];

        for (let i = 0; i < 1000; i++) {
            positions.push(
                (Math.random() - 0.5) * 50,
                (Math.random() - 0.5) * 50,
                (Math.random() - 0.5) * 50
            );

            const color = colorChoices[Math.floor(Math.random() * colorChoices.length)];
            colors.push(color.r, color.g, color.b);
            sizes.push(Math.random() * 2);
        }

        geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
        geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
        geometry.setAttribute('size', new THREE.Float32BufferAttribute(sizes, 1));

        const material = new THREE.PointsMaterial({
            size: 0.1,
            vertexColors: true,
            transparent: true,
            opacity: 0.8,
            blending: THREE.AdditiveBlending
        });

        const particles = new THREE.Points(geometry, material);
        this.scene.add(particles);

        // Particle animation
        gsap.to(particles.rotation, {
            y: Math.PI * 2,
            duration: 10,
            repeat: -1,
            ease: "none"
        });
    }

    animate() {
        this.animationFrame = requestAnimationFrame(() => this.animate());
        const delta = this.clock.getDelta();

        // Update particles
        this.scene.children.forEach(child => {
            if (child instanceof THREE.Points) {
                child.rotation.y += delta * 0.1;
                const positions = child.geometry.attributes.position.array;
                for (let i = 0; i < positions.length; i += 3) {
                    positions[i + 1] += Math.sin(Date.now() * 0.001 + positions[i]) * 0.01;
                }
                child.geometry.attributes.position.needsUpdate = true;
            }
        });

        this.renderer.render(this.scene, this.camera);
    }
}

// Initialize animation when document is loaded
document.addEventListener('DOMContentLoaded', () => {
    new GreetingAnimation();
});
