// Popular Brand Animations

class BrandAnimations {
    constructor() {
        this.container = document.getElementById('brands-container');
        if (!this.container) return;
        
        this.scene = new THREE.Scene();
        this.camera = new THREE.PerspectiveCamera(70, this.container.clientWidth / this.container.clientHeight, 0.1, 1000);
        this.renderer = new THREE.WebGLRenderer({ 
            antialias: true,
            alpha: true
        });
        
        this.brands = [
            { name: 'NVIDIA', color: '#76b900', position: [-7, 0, 0] },
            { name: 'APPLE', color: '#A2AAAD', position: [-3.5, 0, 0] },
            { name: 'SAMSUNG', color: '#1428a0', position: [0, 0, 0] },
            { name: 'INTEL', color: '#0071c5', position: [3.5, 0, 0] },
            { name: 'AMD', color: '#ED1C24', position: [7, 0, 0] }
        ];
        
        this.brandObjects = [];
        this.clock = new THREE.Clock();
        this.init();
    }
    
    init() {
        // Setup renderer
        this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
        this.renderer.setClearColor(0x000000, 0);
        this.container.appendChild(this.renderer.domElement);
        
        // Setup camera
        this.camera.position.z = 10;
        
        // Add lights
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
        this.scene.add(ambientLight);
        
        const spotLight1 = new THREE.SpotLight(0x00ffbb, 1);
        spotLight1.position.set(5, 5, 5);
        
        const spotLight2 = new THREE.SpotLight(0x4e00ff, 1);
        spotLight2.position.set(-5, 5, 5);
        
        const spotLight3 = new THREE.SpotLight(0xff00aa, 0.8);
        spotLight3.position.set(0, -5, 5);
        
        this.scene.add(spotLight1, spotLight2, spotLight3);
        
        // Create brands
        this.createBrands();
        
        // Handle resize
        window.addEventListener('resize', () => {
            if (!this.container) return;
            this.camera.aspect = this.container.clientWidth / this.container.clientHeight;
            this.camera.updateProjectionMatrix();
            this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
        });
        
        // Start animation
        this.animate();
    }
    
    createBrands() {
        const fontLoader = new THREE.FontLoader();
        
        // Load font
        fontLoader.load('https://threejs.org/examples/fonts/helvetiker_bold.typeface.json', (font) => {
            this.brands.forEach(brand => {
                // Create text geometry
                const textGeo = new THREE.TextGeometry(brand.name, {
                    font: font,
                    size: 0.8,
                    height: 0.2,
                    curveSegments: 12,
                    bevelEnabled: true,
                    bevelThickness: 0.03,
                    bevelSize: 0.02,
                    bevelOffset: 0,
                    bevelSegments: 5
                });
                
                textGeo.computeBoundingBox();
                
                // Center the text
                const centerOffset = -0.5 * (textGeo.boundingBox.max.x - textGeo.boundingBox.min.x);
                
                // Create materials
                const mainMaterial = new THREE.MeshPhongMaterial({
                    color: brand.color,
                    specular: 0xffffff,
                    shininess: 100
                });
                
                const edgesMaterial = new THREE.LineBasicMaterial({
                    color: 0xffffff,
                    transparent: true,
                    opacity: 0.5
                });
                
                // Create text mesh
                const textMesh = new THREE.Mesh(textGeo, mainMaterial);
                textMesh.position.set(
                    brand.position[0] + centerOffset, 
                    brand.position[1], 
                    brand.position[2]
                );
                textMesh.userData = {
                    originalPosition: [...brand.position],
                    centerOffset: centerOffset,
                    floatSpeed: 0.5 + Math.random() * 0.5,
                    rotationSpeed: {
                        x: (Math.random() - 0.5) * 0.01,
                        y: (Math.random() - 0.5) * 0.01,
                        z: (Math.random() - 0.5) * 0.005
                    },
                    floatOffset: Math.random() * Math.PI * 2
                };
                
                // Add edges for better 3D effect
                const edges = new THREE.EdgesGeometry(textGeo);
                const line = new THREE.LineSegments(edges, edgesMaterial);
                line.position.copy(textMesh.position);
                
                // Create group for easier manipulation
                const brandGroup = new THREE.Group();
                brandGroup.add(textMesh);
                brandGroup.add(line);
                
                this.scene.add(brandGroup);
                this.brandObjects.push({
                    group: brandGroup,
                    text: textMesh,
                    edges: line
                });
            });
        });
    }
    
    animate() {
        requestAnimationFrame(this.animate.bind(this));
        
        const time = this.clock.getElapsedTime();
        
        // Animate brand objects
        this.brandObjects.forEach(brandObj => {
            const userData = brandObj.text.userData;
            const group = brandObj.group;
            
            // Float up and down
            group.position.y = Math.sin(time * userData.floatSpeed + userData.floatOffset) * 0.3;
            
            // Subtle rotation
            group.rotation.x = Math.sin(time * 0.3) * 0.1;
            group.rotation.y = Math.sin(time * 0.5) * 0.15;
            
            // Subtle edge glow effect
            brandObj.edges.material.opacity = 0.3 + Math.sin(time * 2 + userData.floatOffset) * 0.2;
        });
        
        // Render scene
        this.renderer.render(this.scene, this.camera);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('brands-container')) {
        new BrandAnimations();
    }
});
