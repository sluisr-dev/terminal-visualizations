import './style.css'
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { SolarSystem } from './SolarSystem';
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass.js';

class MainScene {
  private scene: THREE.Scene;
  private camera: THREE.PerspectiveCamera;
  private renderer: THREE.WebGLRenderer;
  private controls: OrbitControls;
  private solarSystem: SolarSystem;
  private composer: EffectComposer;

  constructor() {
    // 1. Scene
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x000000);

    // 2. Camera
    this.camera = new THREE.PerspectiveCamera(
      60, // Wider FOV
      window.innerWidth / window.innerHeight,
      0.1,
      10000
    );
    this.camera.position.set(0, 100, 200);

    // 3. Renderer
    // Disable antialias in renderer constructor when using EffectComposer to save performance, 
    // or keep it if using MSAA render targets (complex). For now, let's disable it to gain FPS.
    this.renderer = new THREE.WebGLRenderer({ antialias: false, powerPreference: "high-performance" });
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    // Limit pixel ratio to 2 to avoid huge buffers on retina screens (3x/4x)
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.toneMapping = THREE.ReinhardToneMapping;
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap; // Keep soft shadows but we'll reduce map size
    document.body.appendChild(this.renderer.domElement);

    // 4. Controls
    this.controls = new OrbitControls(this.camera, this.renderer.domElement);
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.05;
    this.controls.maxDistance = 1000;
    this.controls.minDistance = 20;

    // 5. Lights
    const ambientLight = new THREE.AmbientLight(0x404040, 2); // Soft white light, increased intensity
    this.scene.add(ambientLight);

    // 6. Solar System
    this.solarSystem = new SolarSystem(this.scene);
    this.createLabels();

    // 7. Post-processing (Bloom)
    const renderScene = new RenderPass(this.scene, this.camera);

    // Resolution for bloom can be lower than screen to save performance
    const bloomPass = new UnrealBloomPass(
      new THREE.Vector2(window.innerWidth / 2, window.innerHeight / 2), // Half resolution for bloom
      2.5, // strength (increased)
      0.5, // radius
      0.2 // threshold (lowered significantly to ensure glow)
    );
    bloomPass.strength = 2.5;
    bloomPass.radius = 0.5;
    bloomPass.threshold = 0.2; // Make it glow easily // Only very bright things (Sun) will glow

    this.composer = new EffectComposer(this.renderer);
    this.composer.addPass(renderScene);
    this.composer.addPass(bloomPass);

    // Resize handler
    window.addEventListener('resize', this.onWindowResize.bind(this));

    // Start loop
    this.animate();
  }

  private labels: { element: HTMLDivElement; body: any }[] = [];

  private createLabels() {
    const uiContainer = document.getElementById('ui');
    if (!uiContainer) return;

    const bodies = this.solarSystem.getBodies();
    bodies.forEach(body => {
      const label = document.createElement('div');
      label.className = 'planet-label';
      label.textContent = body.mesh.name;
      uiContainer.appendChild(label);
      this.labels.push({ element: label, body: body });
    });
  }

  private updateLabels() {
    this.labels.forEach(item => {
      const position = item.body.getPosition();
      position.project(this.camera);

      const x = (position.x * .5 + .5) * window.innerWidth;
      const y = (position.y * -.5 + .5) * window.innerHeight;

      // Hide if behind camera
      if (position.z > 1) {
        item.element.style.display = 'none';
      } else {
        item.element.style.display = 'block';
        item.element.style.transform = `translate(-50%, -50%) translate(${x}px, ${y}px)`;
      }
    });
  }

  private onWindowResize() {
    this.camera.aspect = window.innerWidth / window.innerHeight;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    this.composer.setSize(window.innerWidth, window.innerHeight);
  }

  private animate() {
    requestAnimationFrame(this.animate.bind(this));

    const deltaTime = 1; // Fixed step for now, or use clock
    this.solarSystem.update(deltaTime);
    this.updateLabels();

    this.controls.update();
    // this.renderer.render(this.scene, this.camera); // Replaced by composer
    this.composer.render();
  }
}

new MainScene();
