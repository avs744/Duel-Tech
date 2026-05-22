class BackgroundAnimation {
    constructor() {
        this.scene = new THREE.Scene();
        this.camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        this.renderer = new THREE.WebGLRenderer({
            antialias: true,
            alpha: true
        });
        this.clock = new THREE.Clock();
        this.particles = [];
        this.cubes = [];
        this.waves = [];
        this.mouseX = 0;
        this.mouseY = 0;
        this.init();
    }

    init() {
        // Setup renderer
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.setPixelRatio(window.devicePixelRatio);
        this.renderer.setClearColor(0x000000, 0);
        document.getElementById('background-animation').appendChild(this.renderer.domElement);

        // Setup camera
        this.camera.position.z = 30;

        // Add lights
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
        this.scene.add(ambientLight);

        const pointLight1 = new THREE.PointLight(0x00ffbb, 2, 50);
        const pointLight2 = new THREE.PointLight(0x4e00ff, 2, 50);
        const pointLight3 = new THREE.PointLight(0xff00aa, 2, 50);
        pointLight1.position.set(10, 10, 10);
        pointLight2.position.set(-10, -10, -10);
        pointLight3.position.set(0, 15, 5);
        this.scene.add(pointLight1, pointLight2, pointLight3);

        // Create particles
        this.createParticles();

        // Create floating cubes
        this.createFloatingCubes();

        // Create energy waves
        this.createEnergyWaves();
        
        // Create digital grid
        this.createDigitalGrid();

        // Handle window resize
        window.addEventListener('resize', () => {
            const width = window.innerWidth;
            const height = window.innerHeight;
            this.camera.aspect = width / height;
            this.camera.updateProjectionMatrix();
            this.renderer.setSize(width, height);
        });

        // Add mouse interaction
        this.addMouseInteraction();

        this.animate();
    }

    createParticles() {
        const geometry = new THREE.BufferGeometry();
        const particleCount = 500;
        const positions = new Float32Array(particleCount * 3);
        const colors = new Float32Array(particleCount * 3);
        const sizes = new Float32Array(particleCount);

        const color1 = new THREE.Color(0x00ffbb);
        const color2 = new THREE.Color(0x4e00ff);
        const color3 = new THREE.Color(0xff00aa);

        for (let i = 0; i < particleCount; i++) {
            positions[i * 3] = (Math.random() - 0.5) * 80;
            positions[i * 3 + 1] = (Math.random() - 0.5) * 80;
            positions[i * 3 + 2] = (Math.random() - 0.5) * 80;

            const mixFactor = Math.random();
            const mixedColor = color1.clone()
                .lerp(color2, mixFactor)
                .lerp(color3, Math.random() * 0.5);
            
            colors[i * 3] = mixedColor.r;
            colors[i * 3 + 1] = mixedColor.g;
            colors[i * 3 + 2] = mixedColor.b;

            sizes[i] = Math.random() * 3;
        }

        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
        geometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));

        const material = new THREE.PointsMaterial({
            size: 0.15,
            vertexColors: true,
            transparent: true,
            opacity: 0.8,
            sizeAttenuation: true
        });

        const particleSystem = new THREE.Points(geometry, material);
        this.scene.add(particleSystem);
        this.particles.push(particleSystem);
    }

    createFloatingCubes() {
        const count = 10;
        const cubeGeometry = new THREE.BoxGeometry(1, 1, 1);

        for (let i = 0; i < count; i++) {
            // Create gradient material for the cube with transparent faces
            const materials = [
                new THREE.MeshPhongMaterial({
                    color: 0x00ffbb,
                    transparent: true,
                    opacity: 0.2,
                    specular: 0xffffff,
                    shininess: 100
                }),
                new THREE.MeshPhongMaterial({
                    color: 0x4e00ff,
                    transparent: true,
                    opacity: 0.2,
                    specular: 0xffffff,
                    shininess: 100
                }),
                new THREE.MeshPhongMaterial({
                    color: 0xff00aa,
                    transparent: true,
                    opacity: 0.2,
                    specular: 0xffffff,
                    shininess: 100
                }),
                new THREE.MeshPhongMaterial({
                    color: 0x00f7ff,
                    transparent: true,
                    opacity: 0.2,
                    specular: 0xffffff,
                    shininess: 100
                }),
                new THREE.MeshPhongMaterial({
                    color: 0x00ffbb,
                    transparent: true,
                    opacity: 0.2,
                    specular: 0xffffff,
                    shininess: 100
                }),
                new THREE.MeshPhongMaterial({
                    color: 0x4e00ff,
                    transparent: true,
                    opacity: 0.2,
                    specular: 0xffffff,
                    shininess: 100
                })
            ];

            const edgesGeometry = new THREE.EdgesGeometry(cubeGeometry);
            const lineMaterial = new THREE.LineBasicMaterial({
                color: 0x00f7ff,
                transparent: true,
                opacity: 0.8
            });
            
            const cube = new THREE.Mesh(cubeGeometry, materials);
            cube.position.set(
                (Math.random() - 0.5) * 40,
                (Math.random() - 0.5) * 40,
                (Math.random() - 0.5) * 40
            );
            cube.scale.set(
                Math.random() * 2 + 1,
                Math.random() * 2 + 1,
                Math.random() * 2 + 1
            );
            cube.rotation.set(
                Math.random() * Math.PI,
                Math.random() * Math.PI,
                Math.random() * Math.PI
            );
            
            // Add wireframe edges
            const edges = new THREE.LineSegments(edgesGeometry, lineMaterial);
            cube.add(edges);
            
            // Store animation parameters
            cube.userData = {
                rotationSpeed: {
                    x: (Math.random() - 0.5) * 0.01,
                    y: (Math.random() - 0.5) * 0.01,
                    z: (Math.random() - 0.5) * 0.01
                },
                floatSpeed: 0.005 + Math.random() * 0.01,
                floatHeight: Math.random() * 2,
                originalY: cube.position.y,
                floatOffset: Math.random() * Math.PI * 2
            };
            
            this.scene.add(cube);
            this.cubes.push(cube);
        }
    }

    createEnergyWaves() {
        const waveCount = 3;
        
        for (let i = 0; i < waveCount; i++) {
            const ringGeometry = new THREE.RingGeometry(5 + i * 3, 5.5 + i * 3, 32);
            const waveMaterial = new THREE.MeshBasicMaterial({
                color: i === 0 ? 0x00ffbb : i === 1 ? 0x4e00ff : 0xff00aa,
                transparent: true,
                opacity: 0.3,
                side: THREE.DoubleSide
            });
            
            const wave = new THREE.Mesh(ringGeometry, waveMaterial);
            wave.rotation.x = Math.PI / 2;
            wave.userData = {
                pulseSpeed: 0.5 + Math.random() * 0.5,
                pulseOffset: i * (Math.PI / waveCount)
            };
            
            this.scene.add(wave);
            this.waves.push(wave);
        }
    }
    
    createDigitalGrid() {
        // Create horizontal grid
        const gridSize = 40;
        const gridDivisions = 20;
        const gridMaterial = new THREE.LineBasicMaterial({
            color: 0x00f7ff,
            transparent: true,
            opacity: 0.15
        });
        
        // Horizontal grid
        const horizontalGrid = new THREE.GridHelper(gridSize, gridDivisions, 0x00f7ff, 0x00f7ff);
        horizontalGrid.material = gridMaterial;
        horizontalGrid.position.y = -15;
        this.scene.add(horizontalGrid);
        
        // Vertical grid
        const verticalGrid = new THREE.GridHelper(gridSize, gridDivisions, 0x00f7ff, 0x00f7ff);
        verticalGrid.material = gridMaterial;
        verticalGrid.rotation.x = Math.PI / 2;
        verticalGrid.position.z = -15;
        this.scene.add(verticalGrid);
    }

    addMouseInteraction() {
        document.addEventListener('mousemove', (event) => {
            this.mouseX = (event.clientX / window.innerWidth) * 2 - 1;
            this.mouseY = -(event.clientY / window.innerHeight) * 2 + 1;
        });
        
        // For mobile devices
        document.addEventListener('touchmove', (event) => {
            if (event.touches.length > 0) {
                this.mouseX = (event.touches[0].clientX / window.innerWidth) * 2 - 1;
                this.mouseY = -(event.touches[0].clientY / window.innerHeight) * 2 + 1;
            }
        });
    }

    animate() {
        requestAnimationFrame(this.animate.bind(this));
        
        // Update camera based on mouse position
        this.camera.position.x += (this.mouseX * 5 - this.camera.position.x) * 0.05;
        this.camera.position.y += (this.mouseY * 5 - this.camera.position.y) * 0.05;
        this.camera.lookAt(this.scene.position);
        
        const time = this.clock.getElapsedTime();
        
        // Animate particles
        this.particles.forEach(particle => {
            particle.rotation.x = time * 0.1;
            particle.rotation.y = time * 0.15;
        });
        
        // Animate cubes
        this.cubes.forEach(cube => {
            const userData = cube.userData;
            
            // Rotate
            cube.rotation.x += userData.rotationSpeed.x;
            cube.rotation.y += userData.rotationSpeed.y;
            cube.rotation.z += userData.rotationSpeed.z;
            
            // Float up and down
            cube.position.y = userData.originalY + 
                Math.sin(time * userData.floatSpeed + userData.floatOffset) * userData.floatHeight;
            
            // Pulse scale
            const pulse = 1 + Math.sin(time * 0.5) * 0.05;
            cube.scale.set(pulse, pulse, pulse);
            
            // Pulse opacity of edges
            const edges = cube.children[0];
            edges.material.opacity = 0.5 + Math.sin(time * 2 + userData.floatOffset) * 0.2;
        });
        
        // Animate waves
        this.waves.forEach(wave => {
            const userData = wave.userData;
            
            // Pulse scale
            const pulseScale = 1 + 0.2 * Math.sin(time * userData.pulseSpeed + userData.pulseOffset);
            wave.scale.set(pulseScale, pulseScale, pulseScale);
            
            // Pulse opacity
            wave.material.opacity = 0.2 + 0.1 * Math.abs(Math.sin(time * userData.pulseSpeed + userData.pulseOffset));
            
            // Rotate slowly
            wave.rotation.z = time * 0.1;
        });
        
        this.renderer.render(this.scene, this.camera);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new BackgroundAnimation();
});
