/**
 * 3D Interactive Vowel Space Visualization
 * =========================================
 * 
 * Visualizes F1, F2, F3 formant frequencies in interactive 3D space using Three.js.
 * Allows rotation, zooming, and hovering to explore acoustic properties of names.
 */

class VowelSpace3D {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        this.dataPoints = [];
        
        this.init();
    }
    
    init() {
        // Scene
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0xf5f5f5);
        
        // Camera
        this.camera = new THREE.PerspectiveCamera(
            75, 
            this.container.clientWidth / this.container.clientHeight,
            0.1,
            1000
        );
        this.camera.position.set(50, 50, 100);
        
        // Renderer
        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
        this.container.appendChild(this.renderer.domElement);
        
        // Controls (OrbitControls)
        this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.05;
        
        // Axes (F1, F2, F3)
        this.addAxes();
        
        // Grid
        const gridHelper = new THREE.GridHelper(100, 10);
        this.scene.add(gridHelper);
        
        // Lights
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        this.scene.add(ambientLight);
        
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.4);
        directionalLight.position.set(10, 10, 10);
        this.scene.add(directionalLight);
        
        // Start animation loop
        this.animate();
    }
    
    addAxes() {
        // F1 axis (Red)
        const f1Material = new THREE.LineBasicMaterial({ color: 0xff0000 });
        const f1Points = [
            new THREE.Vector3(0, 0, 0),
            new THREE.Vector3(100, 0, 0)
        ];
        const f1Geometry = new THREE.BufferGeometry().setFromPoints(f1Points);
        const f1Line = new THREE.Line(f1Geometry, f1Material);
        this.scene.add(f1Line);
        
        // F2 axis (Green)
        const f2Material = new THREE.LineBasicMaterial({ color: 0x00ff00 });
        const f2Points = [
            new THREE.Vector3(0, 0, 0),
            new THREE.Vector3(0, 100, 0)
        ];
        const f2Geometry = new THREE.BufferGeometry().setFromPoints(f2Points);
        const f2Line = new THREE.Line(f2Geometry, f2Material);
        this.scene.add(f2Line);
        
        // F3 axis (Blue)
        const f3Material = new THREE.LineBasicMaterial({ color: 0x0000ff });
        const f3Points = [
            new THREE.Vector3(0, 0, 0),
            new THREE.Vector3(0, 0, 100)
        ];
        const f3Geometry = new THREE.BufferGeometry().setFromPoints(f3Points);
        const f3Line = new THREE.Line(f3Geometry, f3Material);
        this.scene.add(f3Line);
        
        // Labels (would use THREE.TextGeometry in production)
        this.addAxisLabel('F1 (Hz)', 110, 0, 0, 0xff0000);
        this.addAxisLabel('F2 (Hz)', 0, 110, 0, 0x00ff00);
        this.addAxisLabel('F3 (Hz)', 0, 0, 110, 0x0000ff);
    }
    
    addAxisLabel(text, x, y, z, color) {
        // Simplified label (in production, use TextGeometry)
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        canvas.width = 256;
        canvas.height = 64;
        
        context.fillStyle = '#' + color.toString(16).padStart(6, '0');
        context.font = 'Bold 32px Arial';
        context.textAlign = 'center';
        context.fillText(text, 128, 40);
        
        const texture = new THREE.CanvasTexture(canvas);
        const material = new THREE.SpriteMaterial({ map: texture });
        const sprite = new THREE.Sprite(material);
        sprite.position.set(x, y, z);
        sprite.scale.set(20, 5, 1);
        
        this.scene.add(sprite);
    }
    
    addDataPoint(f1, f2, f3, name, color = 0x3498db) {
        // Scale formants to fit in scene (divide by 30 for reasonable scale)
        const x = f1 / 30;
        const y = f2 / 30;
        const z = f3 / 30;
        
        const geometry = new THREE.SphereGeometry(2, 16, 16);
        const material = new THREE.MeshPhongMaterial({ color: color });
        const sphere = new THREE.Mesh(geometry, material);
        
        sphere.position.set(x, y, z);
        sphere.userData = { name: name, f1: f1, f2: f2, f3: f3 };
        
        this.scene.add(sphere);
        this.dataPoints.push(sphere);
    }
    
    clearDataPoints() {
        this.dataPoints.forEach(point => {
            this.scene.remove(point);
        });
        this.dataPoints = [];
    }
    
    animate() {
        requestAnimationFrame(() => this.animate());
        
        this.controls.update();
        this.renderer.render(this.scene, this.camera);
    }
    
    onWindowResize() {
        this.camera.aspect = this.container.clientWidth / this.container.clientHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
    }
}

// Usage:
// const vowelSpace = new VowelSpace3D('vowelSpaceContainer');
// vowelSpace.addDataPoint(250, 2300, 3000, 'i');  // Add vowel 'i'
// vowelSpace.addDataPoint(750, 1200, 2500, 'a');  // Add vowel 'a'

