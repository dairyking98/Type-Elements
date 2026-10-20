// 3D STL viewer (three.js). Z-up like the build frame (+Z = away from the
// build plate), camera auto-fit to each new part, orbit/zoom/pan.
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { STLLoader } from "three/addons/loaders/STLLoader.js";

export class Viewer {
  constructor(el) {
    this.el = el;
    THREE.Object3D.DEFAULT_UP.set(0, 0, 1);
    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(35, 1, 0.1, 5000);
    this.camera.up.set(0, 0, 1);
    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    this.renderer.setPixelRatio(window.devicePixelRatio);
    el.appendChild(this.renderer.domElement);
    this.controls = new OrbitControls(this.camera, this.renderer.domElement);
    this.controls.enableDamping = true;

    this.scene.add(new THREE.HemisphereLight(0xffffff, 0x8a8f99, 1.6));
    const key = new THREE.DirectionalLight(0xffffff, 1.6);
    key.position.set(60, -80, 120);
    this.scene.add(key);
    const rim = new THREE.DirectionalLight(0xffffff, 0.6);
    rim.position.set(-80, 60, 40);
    this.scene.add(rim);

    this.grid = new THREE.GridHelper(120, 24, 0x9aa1ab, 0xc9ced6);
    this.grid.rotation.x = Math.PI / 2;
    this.scene.add(this.grid);
    this.material = new THREE.MeshStandardMaterial({ color: 0xd9dde3, roughness: 0.55, metalness: 0.05 });
    this.mesh = null;

    new ResizeObserver(() => this.resize()).observe(el);
    this.resize();
    this.camera.position.set(0, -60, 45);
    this.controls.target.set(0, 0, 10);
    const tick = () => { this.controls.update(); this.renderer.render(this.scene, this.camera); requestAnimationFrame(tick); };
    tick();
  }

  resize() {
    const w = this.el.clientWidth || 1, h = this.el.clientHeight || 1;
    this.renderer.setSize(w, h, false);
    this.camera.aspect = w / h;
    this.camera.updateProjectionMatrix();
  }

  setTheme(dark) {
    this.material.color.set(dark ? 0xc7ccd4 : 0xd9dde3);
    this.grid.material.color?.set?.(dark ? 0x3a4049 : 0xc9ced6);
  }

  async load(url, { top = false } = {}) {
    const geom = await new STLLoader().loadAsync(url);
    geom.computeVertexNormals();
    geom.computeBoundingBox();
    if (this.mesh) { this.scene.remove(this.mesh); this.mesh.geometry.dispose(); }
    this.mesh = new THREE.Mesh(geom, this.material);
    this.scene.add(this.mesh);
    const box = geom.boundingBox;
    const size = box.getSize(new THREE.Vector3());
    const center = box.getCenter(new THREE.Vector3());
    const r = Math.max(size.x, size.y, size.z) || 10;
    this.controls.target.copy(center);
    if (top) this.camera.position.set(center.x, center.y - r * 0.01, center.z + r * 2.2);   // flat type-test plate
    else this.camera.position.set(center.x + r * 0.9, center.y - r * 1.6, center.z + r * 1.1);
    this.camera.near = r / 100; this.camera.far = r * 100;
    this.camera.updateProjectionMatrix();
    this.grid.position.set(center.x, center.y, box.min.z);
    return { size, triangles: geom.attributes.position.count / 3 };
  }

  clear() {
    if (this.mesh) { this.scene.remove(this.mesh); this.mesh.geometry.dispose(); this.mesh = null; }
  }
}
