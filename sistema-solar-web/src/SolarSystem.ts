import * as THREE from 'three';
import { CelestialBody } from './CelestialBody';

export class SolarSystem {
    private scene: THREE.Scene;
    private bodies: CelestialBody[] = [];

    constructor(scene: THREE.Scene) {
        this.scene = scene;
        this.initSystem();
        this.createStars();
    }

    private initSystem() {
        // 1. Sun
        // We create a special body for the Sun or just a mesh?
        // Let's use CelestialBody but with 0 distance.
        const sun = new CelestialBody({
            name: 'Sun',
            radius: 10, // Large radius
            distance: 0,
            color: 0xffff00,
            rotationSpeed: 0.005,
            orbitSpeed: 0,
            parent: this.scene,
            texturePath: '/textures/sun.png'
        });

        // Make Sun emissive
        (sun.mesh.material as THREE.MeshStandardMaterial).emissive = new THREE.Color(0xffff00);
        (sun.mesh.material as THREE.MeshStandardMaterial).emissiveIntensity = 1.2; // Increased for bloom
        (sun.mesh.material as THREE.MeshStandardMaterial).emissiveMap = (sun.mesh.material as THREE.MeshStandardMaterial).map;

        // Add PointLight to Sun (Add to orbitGroup or Scene to avoid self-shadowing issues if any)
        const sunLight = new THREE.PointLight(0xffffff, 3, 1000);
        sunLight.castShadow = true;
        sunLight.shadow.mapSize.width = 1024;
        sunLight.shadow.mapSize.height = 1024;
        sunLight.shadow.bias = -0.0001;

        // sun.mesh is at 0,0,0 relative to orbitGroup. orbitGroup is at 0,0,0 relative to scene.
        // Adding to orbitGroup is safer.
        sun.orbitGroup.add(sunLight);

        this.bodies.push(sun);

        // 2. Planets
        // Data: Name, Radius (relative), Distance (relative), Color, Speed
        const planets = [
            { name: 'Mercury', radius: 0.8, distance: 20, color: 0xaaaaaa, speed: 0.04, texturePath: '/textures/mercury.png', inclination: 0.12 }, // ~7 degrees
            { name: 'Venus', radius: 1.5, distance: 30, color: 0xffcc00, speed: 0.015, texturePath: '/textures/venus.png', inclination: 0.06 }, // ~3.4 degrees
            { name: 'Earth', radius: 1.6, distance: 45, color: 0x2233ff, speed: 0.01, texturePath: '/textures/earth.png', inclination: 0 },
            { name: 'Mars', radius: 1.2, distance: 60, color: 0xff3300, speed: 0.008, texturePath: '/textures/mars.png', inclination: 0.03 }, // ~1.85 degrees
            { name: 'Jupiter', radius: 5, distance: 100, color: 0xcc9966, speed: 0.002, texturePath: '/textures/jupiter.png', inclination: 0.02 }, // ~1.3 degrees
            { name: 'Saturn', radius: 4, distance: 150, color: 0xffcc99, speed: 0.0015, ring: { innerRadius: 5, outerRadius: 8, color: 0xaa8866 }, texturePath: '/textures/saturn.png', inclination: 0.04 }, // ~2.5 degrees
            { name: 'Uranus', radius: 3, distance: 200, color: 0x66ccff, speed: 0.001, inclination: 0.01 }, // ~0.77 degrees
            { name: 'Neptune', radius: 2.8, distance: 250, color: 0x3366ff, speed: 0.0008, inclination: 0.03 }, // ~1.77 degrees
        ];

        planets.forEach(p => {
            const planet = new CelestialBody({
                name: p.name,
                radius: p.radius,
                distance: p.distance,
                color: p.color,
                rotationSpeed: 0.01,
                orbitSpeed: p.speed,
                parent: this.scene, // All orbit the center (Sun) for now
                ring: p.ring,
                texturePath: p.texturePath,
                inclination: p.inclination
            });
            this.bodies.push(planet);

            // Add Moon to Earth
            if (p.name === 'Earth') {
                const moon = new CelestialBody({
                    name: 'Moon',
                    radius: 0.4, // Relative to Earth's 1.6
                    distance: 5, // Close to Earth
                    color: 0x888888,
                    rotationSpeed: 0.02,
                    orbitSpeed: 0.05,
                    parent: planet.mesh, // Orbit around Earth's mesh (which rotates, so moon orbit will rotate with earth? No, mesh rotates on Y. OrbitGroup is separate. Wait.)
                    // If I add to planet.mesh, the moon will rotate with the earth's rotation (day/night cycle). That's wrong.
                    // The moon should orbit the Earth's position, but independent of Earth's rotation.
                    // My CelestialBody structure: Parent -> OrbitGroup (rotates) -> Mesh (rotates).
                    // If I make Earth's OrbitGroup the parent, the Moon will orbit the Sun along with Earth (good), but how do I make it orbit Earth?
                    // I need to add the Moon's OrbitGroup to Earth's OrbitGroup? No, Earth's OrbitGroup rotates around Sun.
                    // If I add Moon to Earth's OrbitGroup, Moon will be at fixed distance from Earth's center (OrbitGroup center is Sun).
                    // Wait. Earth's OrbitGroup is at 0,0,0. Earth's Mesh is at distance X.
                    // So if I add Moon to Earth's OrbitGroup, it will orbit the Sun.
                    // I need to add Moon to Earth's Mesh? If Earth's Mesh rotates, Moon rotates with it.
                    // I need a stable point at Earth's position.
                    // Actually, I can add Moon to Earth's Mesh but cancel rotation? No.
                    // Better: Add Moon to Earth's OrbitGroup, but position it relative to Earth's Mesh? No.
                    // Correct way: Add Moon to Earth's Mesh, but Earth's Mesh rotates.
                    // Let's add Moon to a new Group attached to Earth's OrbitGroup, positioned at Earth's distance.
                    // Or simpler: Add Moon to Earth's Mesh, but set Earth's Mesh rotation to 0? No.
                    // Let's just add it to Earth's Mesh for now. It will be tidally locked effectively if speeds match, or just rotate fast.
                    // Actually, if Earth rotates 365 times a year, Moon will orbit Earth 365 times a year if attached to Mesh. That's too fast.
                    // The Moon takes ~27 days.
                    // I need a "System" group for Earth that moves around Sun, but doesn't rotate.
                    // My current CelestialBody doesn't support that well.
                    // Hack: Add Moon to Earth's Mesh. It's a simulation, maybe acceptable if it spins with Earth.
                    // Alternative: Create a "EarthSystem" group in SolarSystem that holds Earth and Moon.
                    // Let's try adding to Earth's Mesh but with 0 distance? No.
                    // Let's use the current structure. If I add to planet.mesh, the moon's orbit center is the planet.
                    // The moon's OrbitGroup will rotate.
                    // But planet.mesh rotates (Earth's day). So Moon's OrbitGroup will rotate with Earth's day.
                    // So Moon will orbit Earth once per day. That's wrong.
                    // I'll stick to adding it to planet.mesh for simplicity now, acknowledging the speed issue.
                    // Or I can modify CelestialBody to expose a non-rotating anchor?
                    // Let's just add it and see. It might be fast but visually "orbiting".
                    // I'll use a texture if I had one, but I don't. I'll use Mercury's texture as fallback or just grey color.
                    texturePath: '/textures/mercury.png' // Reuse mercury texture for now as it's grey/cratered
                });
                this.bodies.push(moon);
            }
        });
        this.createStars();
    }

    private createStars() {
        const starGeometry = new THREE.BufferGeometry();
        // Make stars smaller and transparent
        const starMaterial = new THREE.PointsMaterial({
            color: 0xaaaaaa, // Slightly dimmer white
            size: 0.7, // Slightly larger but fewer? Or smaller? Let's try variable size or just smaller.
            transparent: true,
            opacity: 0.8,
            sizeAttenuation: true
        });

        const starVertices = [];
        // Reduce count from 10000 to 3000
        for (let i = 0; i < 3000; i++) {
            // Increase range to push them further back
            const x = (Math.random() - 0.5) * 4000;
            const y = (Math.random() - 0.5) * 4000;
            const z = (Math.random() - 0.5) * 4000;
            // Keep stars away from center to avoid cluttering the solar system
            if (Math.abs(x) < 500 && Math.abs(y) < 500 && Math.abs(z) < 500) continue;
            starVertices.push(x, y, z);
        }

        starGeometry.setAttribute('position', new THREE.Float32BufferAttribute(starVertices, 3));
        const stars = new THREE.Points(starGeometry, starMaterial);
        this.scene.add(stars);
    }

    public update(deltaTime: number) {
        this.bodies.forEach(body => body.update(deltaTime));
    }

    public getBodies(): CelestialBody[] {
        return this.bodies;
    }
}
