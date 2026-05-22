// Background Animation with Three.js
function initBackground() {
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    const canvas = document.getElementById('bg-canvas');
    const renderer = new THREE.WebGLRenderer({
        canvas: canvas,
        alpha: true
    });

    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);

    // Create a torus knot
    const geometry = new THREE.TorusKnotGeometry(10, 3, 100, 16);
    const material = new THREE.MeshStandardMaterial({
        color: 0x6495ed,
        wireframe: true
    });
    const torusKnot = new THREE.Mesh(geometry, material);

    // Add lights
    const pointLight = new THREE.PointLight(0xffffff);
    pointLight.position.set(5, 5, 5);
    const ambientLight = new THREE.AmbientLight(0xffffff);
    scene.add(pointLight, ambientLight);

    // Add stars
    function addStar() {
        const geometry = new THREE.SphereGeometry(0.25, 24, 24);
        const material = new THREE.MeshStandardMaterial({ color: 0xffffff });
        const star = new THREE.Mesh(geometry, material);

        const [x, y, z] = Array(3).fill().map(() => THREE.MathUtils.randFloatSpread(100));
        star.position.set(x, y, z);
        scene.add(star);
    }
    Array(200).fill().forEach(addStar);

    scene.add(torusKnot);
    camera.position.z = 30;

    // Animation
    function animate() {
        requestAnimationFrame(animate);

        torusKnot.rotation.x += 0.01;
        torusKnot.rotation.y += 0.005;
        torusKnot.rotation.z += 0.01;

        renderer.render(scene, camera);
    }

    // Handle window resize
    window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });

    // Mouse movement effect
    document.addEventListener('mousemove', (event) => {
        const mouseX = (event.clientX / window.innerWidth) * 2 - 1;
        const mouseY = -(event.clientY / window.innerHeight) * 2 + 1;

        torusKnot.rotation.x += mouseY * 0.01;
        torusKnot.rotation.y += mouseX * 0.01;
    });

    animate();
}

// Initialize animations when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    initBackground();
});
