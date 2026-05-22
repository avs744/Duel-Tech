class SocialIcons3D {
    constructor() {
        this.scene = new THREE.Scene();
        this.camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        this.renderer = new THREE.WebGLRenderer({
            antialias: true,
            alpha: true
        });
        this.clock = new THREE.Clock();
        this.icons = [];
        this.init();
    }

    init() {
        // Setup renderer
        this.renderer.setSize(window.innerWidth, 200); // Height for footer
        this.renderer.setPixelRatio(window.devicePixelRatio);
        this.renderer.setClearColor(0x000000, 0);
        document.getElementById('social-icons-3d').appendChild(this.renderer.domElement);

        // Setup camera
        this.camera.position.z = 15;

        // Add lights
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
        this.scene.add(ambientLight);

        const pointLight1 = new THREE.PointLight(0x2ecc71, 2, 50);
        const pointLight2 = new THREE.PointLight(0x3498db, 2, 50);
        pointLight1.position.set(10, 10, 10);
        pointLight2.position.set(-10, -10, -10);
        this.scene.add(pointLight1, pointLight2);

        // Create social media icons
        this.createSocialIcons();

        // Handle window resize
        window.addEventListener('resize', () => {
            this.renderer.setSize(window.innerWidth, 200);
            this.camera.aspect = window.innerWidth / 200;
            this.camera.updateProjectionMatrix();
        });

        // Add hover effects
        this.addHoverEffects();

        this.animate();
    }

    createSocialIcons() {
        const iconData = [
            { name: 'facebook', color: 0x3b5998, link: '#' },
            { name: 'twitter', color: 0x1da1f2, link: '#' },
            { name: 'instagram', color: 0xe1306c, link: '#' },
            { name: 'linkedin', color: 0x0077b5, link: '#' },
            { name: 'youtube', color: 0xff0000, link: '#' }
        ];

        const spacing = 5;
        const startX = -(spacing * (iconData.length - 1)) / 2;

        iconData.forEach((icon, index) => {
            // Create icon geometry
            const geometry = new THREE.BoxGeometry(2, 2, 2);
            const material = new THREE.MeshPhongMaterial({
                color: icon.color,
                specular: 0xffffff,
                shininess: 100,
                transparent: true,
                opacity: 0.9
            });

            const mesh = new THREE.Mesh(geometry, material);
            mesh.position.x = startX + index * spacing;
            mesh.userData = {
                name: icon.name,
                link: icon.link,
                originalScale: mesh.scale.clone(),
                originalColor: material.color.getHex()
            };

            // Add glow effect
            const glowMaterial = new THREE.MeshPhongMaterial({
                color: icon.color,
                transparent: true,
                opacity: 0.3,
                side: THREE.BackSide
            });
            const glowMesh = new THREE.Mesh(geometry.clone(), glowMaterial);
            glowMesh.scale.multiplyScalar(1.2);
            mesh.add(glowMesh);

            this.icons.push(mesh);
            this.scene.add(mesh);

            // Add icon symbol
            const symbolGeometry = new THREE.TextGeometry(icon.name[0].toUpperCase(), {
                font: new THREE.Font(), // You'll need to load a font
                size: 0.5,
                height: 0.1
            });
            const symbolMaterial = new THREE.MeshPhongMaterial({ color: 0xffffff });
            const symbol = new THREE.Mesh(symbolGeometry, symbolMaterial);
            symbol.position.set(-0.25, -0.25, 1.1);
            mesh.add(symbol);
        });
    }

    addHoverEffects() {
        const raycaster = new THREE.Raycaster();
        const mouse = new THREE.Vector2();
        let hoveredIcon = null;

        const onMouseMove = (event) => {
            const rect = this.renderer.domElement.getBoundingClientRect();
            mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
            mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

            raycaster.setFromCamera(mouse, this.camera);
            const intersects = raycaster.intersectObjects(this.icons);

            if (intersects.length > 0) {
                const icon = intersects[0].object;
                if (hoveredIcon !== icon) {
                    if (hoveredIcon) {
                        this.resetIconAnimation(hoveredIcon);
                    }
                    this.animateIconHover(icon);
                    hoveredIcon = icon;
                    document.body.style.cursor = 'pointer';
                }
            } else if (hoveredIcon) {
                this.resetIconAnimation(hoveredIcon);
                hoveredIcon = null;
                document.body.style.cursor = 'default';
            }
        };

        const onClick = () => {
            if (hoveredIcon) {
                window.open(hoveredIcon.userData.link, '_blank');
            }
        };

        this.renderer.domElement.addEventListener('mousemove', onMouseMove);
        this.renderer.domElement.addEventListener('click', onClick);
    }

    animateIconHover(icon) {
        gsap.to(icon.scale, {
            x: 1.2,
            y: 1.2,
            z: 1.2,
            duration: 0.3,
            ease: 'power2.out'
        });

        gsap.to(icon.material.color, {
            r: 1,
            g: 1,
            b: 1,
            duration: 0.3
        });

        gsap.to(icon.material, {
            opacity: 1,
            duration: 0.3
        });
    }

    resetIconAnimation(icon) {
        gsap.to(icon.scale, {
            x: icon.userData.originalScale.x,
            y: icon.userData.originalScale.y,
            z: icon.userData.originalScale.z,
            duration: 0.3,
            ease: 'power2.out'
        });

        const color = new THREE.Color(icon.userData.originalColor);
        gsap.to(icon.material.color, {
            r: color.r,
            g: color.g,
            b: color.b,
            duration: 0.3
        });

        gsap.to(icon.material, {
            opacity: 0.9,
            duration: 0.3
        });
    }

    animate() {
        requestAnimationFrame(() => this.animate());

        const time = this.clock.getElapsedTime();

        // Animate icons
        this.icons.forEach((icon, index) => {
            icon.rotation.y = Math.sin(time * 0.5 + index) * 0.2;
            icon.rotation.x = Math.cos(time * 0.5 + index) * 0.2;
            icon.position.y = Math.sin(time + index) * 0.2;
        });

        this.renderer.render(this.scene, this.camera);
    }
}

// Initialize animation when document is loaded
document.addEventListener('DOMContentLoaded', () => {
    new SocialIcons3D();
});
