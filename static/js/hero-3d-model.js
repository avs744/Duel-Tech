// 3D Hero Model for DuelTech
class Hero3DModel {
    constructor() {
        this.scene = new THREE.Scene();
        this.camera = new THREE.PerspectiveCamera(75, 1, 0.1, 1000);
        this.renderer = new THREE.WebGLRenderer({
            antialias: true,
            alpha: true
        });
        this.clock = new THREE.Clock();
        this.init();
    }

    init() {
        const container = document.getElementById('hero-3d-model');
        if (!container) return;
        
        // Setup renderer
        this.renderer.setSize(container.clientWidth, container.clientHeight);
        this.renderer.setPixelRatio(window.devicePixelRatio);
        this.renderer.setClearColor(0x000000, 0);
        container.appendChild(this.renderer.domElement);

        // Setup camera
        this.camera.position.z = 5;
        this.camera.position.y = 1;

        // Add lights
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
        this.scene.add(ambientLight);

        const spotLight1 = new THREE.SpotLight(0x00ffbb, 1);
        spotLight1.position.set(5, 5, 5);
        spotLight1.castShadow = true;
        
        const spotLight2 = new THREE.SpotLight(0x4e00ff, 1);
        spotLight2.position.set(-5, -5, 5);
        spotLight2.castShadow = true;
        
        const spotLight3 = new THREE.SpotLight(0xff00aa, 0.8);
        spotLight3.position.set(0, 5, -5);
        spotLight3.castShadow = true;
        
        this.scene.add(spotLight1, spotLight2, spotLight3);

        // Create tech model
        this.createTechDevice();

        // Handle resize
        window.addEventListener('resize', () => {
            if (!container) return;
            this.camera.aspect = container.clientWidth / container.clientHeight;
            this.camera.updateProjectionMatrix();
            this.renderer.setSize(container.clientWidth, container.clientHeight);
        });

        this.animate();
    }

    createTechDevice() {
        // Create a device that looks like a futuristic tech device (tablet/smartphone)
        
        // Device body
        const bodyGeometry = new THREE.BoxGeometry(3, 2, 0.1);
        const bodyMaterial = new THREE.MeshPhongMaterial({
            color: 0x0a0a18,
            specular: 0x111133,
            shininess: 100
        });
        const deviceBody = new THREE.Mesh(bodyGeometry, bodyMaterial);
        this.scene.add(deviceBody);
        
        // Device screen
        const screenGeometry = new THREE.PlaneGeometry(2.8, 1.8);
        const screenMaterial = new THREE.MeshPhongMaterial({
            color: 0x00f7ff,
            emissive: 0x00f7ff,
            emissiveIntensity: 0.2,
            side: THREE.DoubleSide
        });
        const screen = new THREE.Mesh(screenGeometry, screenMaterial);
        screen.position.z = 0.051;
        deviceBody.add(screen);
        
        // Screen content - create a grid pattern
        const gridHelper = new THREE.GridHelper(2, 10, 0xffffff, 0x00ffbb);
        gridHelper.position.z = 0.052;
        gridHelper.rotation.x = Math.PI / 2;
        screen.add(gridHelper);
        
        // Add floating tech elements above the screen
        this.addFloatingElements(screen);
        
        // Add edges glow
        const edgesGeometry = new THREE.EdgesGeometry(bodyGeometry);
        const edgesMaterial = new THREE.LineBasicMaterial({ 
            color: 0x00ffbb,
            transparent: true,
            opacity: 0.8
        });
        const edges = new THREE.LineSegments(edgesGeometry, edgesMaterial);
        deviceBody.add(edges);
        
        // Store the device for animation
        this.techDevice = deviceBody;
        this.edges = edges;
        this.screen = screen;
    }
    
    addFloatingElements(parent) {
        // Add floating data cubes
        const elements = [];
        const colors = [0x00ffbb, 0x4e00ff, 0xff00aa, 0x00f7ff];
        
        for (let i = 0; i < 10; i++) {
            const size = 0.05 + Math.random() * 0.1;
            const geometry = Math.random() > 0.5 ? 
                new THREE.BoxGeometry(size, size, size) : 
                new THREE.SphereGeometry(size / 2, 8, 8);
            
            const material = new THREE.MeshPhongMaterial({
                color: colors[Math.floor(Math.random() * colors.length)],
                transparent: true,
                opacity: 0.8,
                specular: 0xffffff,
                shininess: 100
            });
            
            const element = new THREE.Mesh(geometry, material);
            element.position.set(
                (Math.random() - 0.5) * 2,
                (Math.random() - 0.5) * 1.2,
                0.1 + Math.random() * 0.3
            );
            
            element.userData = {
                originalPosition: element.position.clone(),
                floatSpeed: 0.5 + Math.random() * 1.5,
                floatHeight: 0.05 + Math.random() * 0.1,
                rotationSpeed: {
                    x: (Math.random() - 0.5) * 0.02,
                    y: (Math.random() - 0.5) * 0.02,
                    z: (Math.random() - 0.5) * 0.02
                },
                floatOffset: Math.random() * Math.PI * 2
            };
            
            parent.add(element);
            elements.push(element);
        }
        
        this.floatingElements = elements;
    }

    animate() {
        requestAnimationFrame(this.animate.bind(this));
        
        const time = this.clock.getElapsedTime();
        
        if (this.techDevice) {
            // Gentle floating motion for the device
            this.techDevice.position.y = Math.sin(time * 0.5) * 0.1;
            this.techDevice.rotation.x = Math.sin(time * 0.3) * 0.05;
            this.techDevice.rotation.y = Math.cos(time * 0.4) * 0.3 + Math.PI * 0.1;
            
            // Pulse the edge glow
            this.edges.material.opacity = 0.5 + Math.sin(time * 2) * 0.3;
            
            // Screen color animation
            const hue = (time * 0.05) % 1;
            const screenColor = new THREE.Color().setHSL(hue, 0.8, 0.5);
            this.screen.material.emissive.set(screenColor);
            this.screen.material.emissiveIntensity = 0.1 + Math.sin(time) * 0.05;
            
            // Animate floating elements
            if (this.floatingElements) {
                this.floatingElements.forEach(element => {
                    const userData = element.userData;
                    
                    // Float up and down
                    element.position.z = userData.originalPosition.z + 
                        Math.sin(time * userData.floatSpeed + userData.floatOffset) * userData.floatHeight;
                    
                    // Rotate
                    element.rotation.x += userData.rotationSpeed.x;
                    element.rotation.y += userData.rotationSpeed.y;
                    element.rotation.z += userData.rotationSpeed.z;
                    
                    // Pulse scale
                    const pulse = 1 + Math.sin(time * 2 + userData.floatOffset) * 0.2;
                    element.scale.set(pulse, pulse, pulse);
                });
            }
        }
        
        this.renderer.render(this.scene, this.camera);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('hero-3d-model')) {
        new Hero3DModel();
    }
});
