import * as THREE from 'three';

export interface CelestialBodyConfig {
    name: string;
    radius: number;
    distance: number; // Distance from parent (or sun)
    color: number | string;
    rotationSpeed: number; // Radians per frame (self rotation)
    orbitSpeed: number; // Radians per frame (orbit around parent)
    parent?: THREE.Object3D; // Parent object to orbit around
    ring?: { innerRadius: number; outerRadius: number; color: number };
    texturePath?: string;
    inclination?: number; // Orbit inclination in radians
}

export class CelestialBody {
    public mesh: THREE.Mesh;
    public orbitGroup: THREE.Group; // Group to handle orbit rotation
    private config: CelestialBodyConfig;
    private angle: number = 0;

    constructor(config: CelestialBodyConfig) {
        this.config = config;
        this.angle = Math.random() * Math.PI * 2; // Random start angle

        // 1. Create Mesh
        const geometry = new THREE.SphereGeometry(config.radius, 32, 32);
        let material: THREE.Material;

        if (config.texturePath) {
            const textureLoader = new THREE.TextureLoader();
            const texture = textureLoader.load(config.texturePath);
            material = new THREE.MeshStandardMaterial({
                map: texture,
                roughness: 0.8,
                metalness: 0.1,
                color: 0xffffff // Ensure base color is white so texture shows true colors
            });
        } else {
            material = new THREE.MeshStandardMaterial({
                color: config.color,
                roughness: 0.7,
                metalness: 0.1,
            });
        }
        this.mesh = new THREE.Mesh(geometry, material);
        this.mesh.name = config.name;
        this.mesh.castShadow = true;
        this.mesh.receiveShadow = true;

        // 2. Create Orbit Group (Pivot)
        this.orbitGroup = new THREE.Group();
        if (config.parent) {
            config.parent.add(this.orbitGroup);
        }

        // Apply inclination (tilt the orbit plane)
        if (config.inclination) {
            this.orbitGroup.rotation.z = config.inclination;
        }

        // Position mesh relative to orbit center
        this.mesh.position.x = config.distance;
        this.orbitGroup.add(this.mesh);

        // Set initial angle
        this.orbitGroup.rotation.y = this.angle;

        // Create Ring if configured
        if (config.ring) {
            const ringGeo = new THREE.RingGeometry(config.ring.innerRadius, config.ring.outerRadius, 64);
            const ringMat = new THREE.MeshBasicMaterial({
                color: config.ring.color,
                side: THREE.DoubleSide,
                transparent: true,
                opacity: 0.8
            });
            const ringMesh = new THREE.Mesh(ringGeo, ringMat);
            ringMesh.rotation.x = Math.PI / 2;
            this.mesh.add(ringMesh);
        }

        // Add orbit trail (optional, simple ring)
        if (config.distance > 0) {
            this.createOrbitLine(config.distance);
        }
    }

    private createOrbitLine(radius: number) {
        const points = [];
        const segments = 128; // Smoother circle
        for (let i = 0; i <= segments; i++) {
            const theta = (i / segments) * Math.PI * 2;
            points.push(new THREE.Vector3(Math.cos(theta) * radius, 0, Math.sin(theta) * radius));
        }
        const geometry = new THREE.BufferGeometry().setFromPoints(points);
        // Reduced opacity to 0.05 to make it very subtle
        const material = new THREE.LineBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.05 });
        const orbitLine = new THREE.Line(geometry, material);
        // orbitLine.rotation.x = Math.PI / 2; // REMOVED: This was causing the lines to stand up vertically

        // The orbit line should be static relative to the parent, but tilted if the orbit is tilted.
        // If we add it to parent directly, it won't be tilted.
        // We should add it to a non-rotating group that is tilted?
        // Or just add it to the parent and apply the same rotation Z.

        if (this.config.parent) {
            // Create a container for the line to apply inclination
            const lineGroup = new THREE.Group();
            if (this.config.inclination) {
                lineGroup.rotation.z = this.config.inclination;
            }
            lineGroup.add(orbitLine);
            this.config.parent.add(lineGroup);
        }
    }

    public update(deltaTime: number) {
        // Self rotation
        this.mesh.rotation.y += this.config.rotationSpeed * deltaTime;

        // Orbit rotation
        this.orbitGroup.rotation.y += this.config.orbitSpeed * deltaTime;
    }

    public getPosition(): THREE.Vector3 {
        const pos = new THREE.Vector3();
        this.mesh.getWorldPosition(pos);
        return pos;
    }
}
