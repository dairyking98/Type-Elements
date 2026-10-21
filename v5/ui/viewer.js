// 3D STL viewer (three.js). Z-up like the build frame (+Z = away from the
// build plate), camera auto-fit to each new part, orbit/zoom/pan.
// A flat part (type-test plate, load(url, {top: true})) is shown as a 2D
// sheet instead: orthographic, looking straight down, pan and zoom only -
// read like a printed page, with no perspective to skew the spacing. The
// next element build switches back to the 3D orbit view.
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
    // real shadows: the key light casts them, the part shades itself (raised
    // characters, grooves and bores read in depth) and drops one on the floor
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    el.appendChild(this.renderer.domElement);
    this.ortho = new THREE.OrthographicCamera(-10, 10, 10, -10, 0.01, 5000);
    this.ortho.up.set(0, 1, 0);
    this.persp = this.camera;
    this.controls = new OrbitControls(this.camera, this.renderer.domElement);
    this.controls.enableDamping = true;
    this.flat = false;

    this.scene.add(new THREE.HemisphereLight(0xffffff, 0x8a8f99, 1.6));
    const key = new THREE.DirectionalLight(0xffffff, 2.2);
    key.position.set(60, -80, 120);
    key.castShadow = true;
    key.shadow.mapSize.set(2048, 2048);
    key.shadow.bias = -0.0004;
    key.shadow.normalBias = 0.02;
    this.scene.add(key.target);
    this.scene.add(key);
    const rim = new THREE.DirectionalLight(0xffffff, 0.6);
    rim.position.set(-80, 60, 40);
    this.scene.add(rim);
    this.key = key; this.rim = rim;
    // raking light for flat parts (type-test plates): skims the surface from
    // low angles so raised letters cast shadows instead of reading white-on-white
    this.rake = new THREE.DirectionalLight(0xffffff, 0);
    this.scene.add(this.rake);
    this.hemi = this.scene.children.find((c) => c.isHemisphereLight);

    this.grid = new THREE.GridHelper(120, 24, 0x9aa1ab, 0xc9ced6);
    this.grid.rotation.x = Math.PI / 2;
    this.scene.add(this.grid);
    this.material = new THREE.MeshStandardMaterial({ color: 0xd9dde3, roughness: 0.55, metalness: 0.05 });
    this.modelColor = null;      // user's part colour (null = the theme's)
    // the floor only shows the part's shadow
    this.floor = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), new THREE.ShadowMaterial({ opacity: 0.22 }));
    this.floor.receiveShadow = true;
    this.floor.visible = false;
    this.scene.add(this.floor);
    // type-test plates read like a printed page: near-black type on white,
    // whatever the theme or the chosen background
    this.inkMaterial = new THREE.MeshStandardMaterial({ color: 0x15171a, roughness: 0.9, metalness: 0 });
    this.mesh = null;
    this.background = null;      // user's backdrop for element views (null = the theme's)

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
    this.persp.aspect = w / h;
    this.persp.updateProjectionMatrix();
    if (this.flatSize) this.fitOrtho();
  }

  // the orthographic frustum that fits this.flatSize (mm) with a margin, at the view's aspect
  fitOrtho() {
    const aspect = (this.el.clientWidth || 1) / (this.el.clientHeight || 1);
    const { x, y } = this.flatSize;
    const halfH = Math.max(y, x / aspect) * 0.56;
    Object.assign(this.ortho, { left: -halfH * aspect, right: halfH * aspect, top: halfH, bottom: -halfH });
    this.ortho.updateProjectionMatrix();
  }

  setFlat(flat) {
    if (flat === this.flat) return;
    this.flat = flat;
    this.camera = flat ? this.ortho : this.persp;
    const c = this.controls;
    c.object = this.camera;
    c.enableRotate = !flat;
    c.screenSpacePanning = true;
    // flat: drag pans (either button), wheel/pinch zooms; 3D: the orbit defaults
    c.mouseButtons = flat ? { LEFT: THREE.MOUSE.PAN, MIDDLE: THREE.MOUSE.DOLLY, RIGHT: THREE.MOUSE.PAN }
      : { LEFT: THREE.MOUSE.ROTATE, MIDDLE: THREE.MOUSE.DOLLY, RIGHT: THREE.MOUSE.PAN };
    c.touches = flat ? { ONE: THREE.TOUCH.PAN, TWO: THREE.TOUCH.DOLLY_PAN } : { ONE: THREE.TOUCH.ROTATE, TWO: THREE.TOUCH.DOLLY_PAN };
    if (!flat) this.flatSize = null;
  }

  // the backdrop behind element builds (a CSS colour, or null for the
  // theme's own); type tests always sit on white
  setBackground(color) {
    this.background = color || null;
    this.applyBackground();
  }
  applyBackground() {
    this.el.style.background = this.flat ? "#ffffff" : (this.background || "");
  }

  setModelColor(color) {
    this.modelColor = color || null;
    this.material.color.set(this.modelColor || (this.dark ? 0xc7ccd4 : 0xd9dde3));
  }

  setTheme(dark) {
    this.dark = dark;
    this.material.color.set(this.modelColor || (dark ? 0xc7ccd4 : 0xd9dde3));
    this.grid.material.color?.set?.(dark ? 0x3a4049 : 0xc9ced6);
  }

  async load(url, { top = false } = {}) {
    const geom = await new STLLoader().loadAsync(url);
    geom.computeVertexNormals();
    geom.computeBoundingBox();
    if (this.mesh) { this.scene.remove(this.mesh); this.mesh.geometry.dispose(); }
    this.mesh = new THREE.Mesh(geom, top ? this.inkMaterial : this.material);
    this.mesh.castShadow = this.mesh.receiveShadow = !top;
    this.scene.add(this.mesh);
    const box = geom.boundingBox;
    const size = box.getSize(new THREE.Vector3());
    const center = box.getCenter(new THREE.Vector3());
    const r = Math.max(size.x, size.y, size.z) || 10;
    this.controls.target.copy(center);
    this.grid.visible = !top;
    this.rake.intensity = top ? 2.6 : 0;
    this.key.intensity = top ? 0.5 : 2.2;
    this.rim.intensity = top ? 0 : 0.6;
    if (this.hemi) this.hemi.intensity = top ? 0.9 : 1.2;
    this.setFlat(top);
    this.applyBackground();
    if (top) {
      // flat type-test plate: orthographic, straight down, the plate filling the view
      this.flatSize = { x: size.x, y: size.y };
      this.ortho.zoom = 1;
      this.fitOrtho();
      this.camera.position.set(center.x, center.y, box.max.z + r);
      this.camera.near = 0.01; this.camera.far = r * 4 + size.z;
      this.rake.position.set(center.x - size.x, center.y + size.y * 4, center.z + Math.max(size.x, size.y) * 0.35);
      this.rake.target.position.copy(center);
      this.rake.target.updateMatrixWorld();
    } else {
      this.camera.position.set(center.x + r * 0.9, center.y - r * 1.6, center.z + r * 1.1);
      this.camera.near = r / 100; this.camera.far = r * 100;
      // aim the shadow-casting key light at the part and fit its shadow box
      const k = this.key;
      k.position.set(center.x + r * 1.2, center.y - r * 1.6, center.z + r * 2.4);
      k.target.position.copy(center);
      k.target.updateMatrixWorld();
      const sc = k.shadow.camera;
      Object.assign(sc, { left: -r * 1.6, right: r * 1.6, top: r * 1.6, bottom: -r * 1.6, near: r * 0.5, far: r * 7 });
      sc.updateProjectionMatrix();
      this.floor.scale.set(r * 8, r * 8, 1);
      this.floor.position.set(center.x, center.y, box.min.z - 0.01);
    }
    this.floor.visible = !top;
    this.camera.updateProjectionMatrix();
    this.controls.update();
    this.grid.position.set(center.x, center.y, box.min.z);
    return { size, triangles: geom.attributes.position.count / 3 };
  }

  clear() {
    if (this.mesh) { this.scene.remove(this.mesh); this.mesh.geometry.dispose(); this.mesh = null; }
  }
}
