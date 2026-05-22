class LoginAnimation {
    constructor() {
        this.scene = new THREE.Scene();
        this.camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        this.renderer = new THREE.WebGLRenderer({ 
            antialias: true,
            alpha: true 
        });
        this.clock = new THREE.Clock();
        this.init();
    }

    init() {
        // Setup renderer
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.setPixelRatio(window.devicePixelRatio);
        document.getElementById('login-animation').appendChild(this.renderer.domElement);

        // Setup camera
        this.camera.position.z = 30;

        // Add lights
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
        this.scene.add(ambientLight);

        const pointLight1 = new THREE.PointLight(0x2ecc71, 2, 50);
        const pointLight2 = new THREE.PointLight(0x3498db, 2, 50);
        pointLight1.position.set(10, 10, 10);
        pointLight2.position.set(-10, -10, -10);
        this.scene.add(pointLight1, pointLight2);

        // Create DNA helix
        this.createDNAHelix();

        // Create floating particles
        this.createParticles();

        // Create energy field
        this.createEnergyField();

        // Add mouse interaction
        this.addMouseInteraction();

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

    createDNAHelix() {
        const curve = new THREE.CatmullRomCurve3([
            new THREE.Vector3(-10, -10, 0),
            new THREE.Vector3(-5, 0, 10),
            new THREE.Vector3(0, 10, 0),
            new THREE.Vector3(5, 0, -10),
            new THREE.Vector3(10, -10, 0)
        ]);

        const points = curve.getPoints(50);
        const geometry = new THREE.BufferGeometry().setFromPoints(points);
        
        const material = new THREE.LineBasicMaterial({
            color: 0x2ecc71,
            transparent: true,
            opacity: 0.5
        });

        this.dnaHelix = new THREE.Line(geometry, material);
        this.scene.add(this.dnaHelix);

        // Add spheres along the curve
        const sphereGeometry = new THREE.SphereGeometry(0.2, 16, 16);
        const sphereMaterial = new THREE.MeshPhongMaterial({
            color: 0x3498db,
            emissive: 0x3498db,
            emissiveIntensity: 0.5
        });

        this.spheres = [];
        points.forEach(point => {
            const sphere = new THREE.Mesh(sphereGeometry, sphereMaterial);
            sphere.position.copy(point);
            this.scene.add(sphere);
            this.spheres.push(sphere);
        });
    }

    createParticles() {
        const geometry = new THREE.BufferGeometry();
        const particleCount = 200;
        const positions = new Float32Array(particleCount * 3);
        const colors = new Float32Array(particleCount * 3);
        const sizes = new Float32Array(particleCount);

        const color1 = new THREE.Color(0x2ecc71);
        const color2 = new THREE.Color(0x3498db);

        for (let i = 0; i < particleCount; i++) {
            positions[i * 3] = (Math.random() - 0.5) * 50;
            positions[i * 3 + 1] = (Math.random() - 0.5) * 50;
            positions[i * 3 + 2] = (Math.random() - 0.5) * 50;

            const mixedColor = color1.clone().lerp(color2, Math.random());
            colors[i * 3] = mixedColor.r;
            colors[i * 3 + 1] = mixedColor.g;
            colors[i * 3 + 2] = mixedColor.b;

            sizes[i] = Math.random() * 2;
        }

        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
        geometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));

        const material = new THREE.PointsMaterial({
            size: 0.1,
            vertexColors: true,
            transparent: true,
            opacity: 0.8,
            blending: THREE.AdditiveBlending
        });

        this.particles = new THREE.Points(geometry, material);
        this.scene.add(this.particles);
    }

    createEnergyField() {
        const geometry = new THREE.TorusKnotGeometry(10, 1, 100, 16);
        const material = new THREE.MeshPhongMaterial({
            color: 0x2ecc71,
            wireframe: true,
            transparent: true,
            opacity: 0.3
        });

        this.energyField = new THREE.Mesh(geometry, material);
        this.scene.add(this.energyField);
    }

    addMouseInteraction() {
        const mouse = new THREE.Vector2();
        let isMouseDown = false;

        window.addEventListener('mousemove', (event) => {
            mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
            mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

            if (isMouseDown) {
                this.energyField.rotation.x += mouse.y * 0.1;
                this.energyField.rotation.y += mouse.x * 0.1;
            }
        });

        window.addEventListener('mousedown', () => {
            isMouseDown = true;
        });

        window.addEventListener('mouseup', () => {
            isMouseDown = false;
        });
    }

    animate() {
        requestAnimationFrame(() => this.animate());

        const time = this.clock.getElapsedTime();

        // Rotate DNA helix
        if (this.dnaHelix) {
            this.dnaHelix.rotation.y += 0.005;
            this.spheres.forEach((sphere, i) => {
                sphere.position.y += Math.sin(time * 2 + i * 0.1) * 0.02;
            });
        }

        // Animate particles
        if (this.particles) {
            const positions = this.particles.geometry.attributes.position.array;
            for (let i = 0; i < positions.length; i += 3) {
                positions[i + 1] += Math.sin(time + positions[i]) * 0.01;
            }
            this.particles.geometry.attributes.position.needsUpdate = true;
            this.particles.rotation.y += 0.001;
        }

        // Animate energy field
        if (this.energyField) {
            this.energyField.rotation.x += 0.001;
            this.energyField.rotation.y += 0.002;
            this.energyField.scale.x = 1 + Math.sin(time) * 0.1;
            this.energyField.scale.y = 1 + Math.cos(time) * 0.1;
        }

        this.renderer.render(this.scene, this.camera);
    }
}

// Initialize animation when document is loaded
document.addEventListener('DOMContentLoaded', () => {
    new LoginAnimation();
});
