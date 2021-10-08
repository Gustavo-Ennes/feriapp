import * as THREE from 'https://cdn.skypack.dev/three@0.130.0';
import Cube from './Cube.js';


let scene = null,
    camera = null,
    renderer = null,
    light = null



const rayEventListener = () => {
  const raycaster = new THREE.Raycaster();
  const mouse = new THREE.Vector2();

  const getObjects = () => {
    return scene.children.filter(c => c.name !== 'dome')
  }

  const onMouseMove = ( event ) =>{

    // calculate mouse position in normalized device coordinates
    // (-1 to +1) for both components

    mouse.x = ( event.clientX / window.innerWidth ) * 2 - 1;
    mouse.y = - ( event.clientY / window.innerHeight ) * 2 + 1;
    raycaster.setFromCamera( mouse, camera );

    // calculate objects intersecting the picking ray
    const intersects = raycaster.intersectObjects( getObjects() );
    let obj

    for ( let i = 0; i < intersects.length; i ++ ) {

      obj = Cube.find(intersects[i].object)

      if(obj){
        obj.handleMouseHover()
      }

    }
  }
  window.addEventListener( 'mousemove', onMouseMove, false );
}


const resizeListener = () => {
  window.addEventListener('resize', onWindowResize)
}

const onWindowResize = () => {
  camera.aspect = document.body.offsetWidth / document.body.offsetHeight;
  camera.updateProjectionMatrix();
  renderer.setSize( document.body.offsetWidth, document.body.offsetHeight);
}


const tweenCamera = () => {

  new TWEEN.Tween(camera.position)
  .to({x: [5, 0, -5, 0]}, 18000)
  .onUpdate(() => {
    camera.lookAt(new THREE.Vector3())
    camera.updateProjectionMatrix()
  })
  .repeat(Infinity)
  .start()
}

const addLight = () => {
  light = new THREE.SpotLight( 0xddddff, 0.8, 100, 1.4, 0.2, 2)
  light.position.set(0, 2, 10)
  light.target = new THREE.Object3D()
  light.target.position.set(0, 2, 0)
  light.castShadow = true
  light.shadow.mapSize.width = 2048 ;
  light.shadow.mapSize.height = 2048;

  light.shadow.camera.near = 1;
  light.shadow.camera.far = 100;
  light.shadow.camera.fov = 75;
  scene.add( light );
  scene.add( light.target)
  
}

export const init = (el) => {
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0xEDF6FF)
  camera = new THREE.PerspectiveCamera( 75, window.innerWidth / window.innerHeight, 1, 10000 );
  camera.lookAt(new THREE.Vector3(0, 0, 0))
  camera.position.set(0, 0, 10)

  renderer = new THREE.WebGL1Renderer({antialias: true});
  renderer.setSize( window.innerWidth, window.innerHeight );
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.shadowMap.enabled = true;

  el.appendChild( renderer.domElement );
  
  addLight()
  initEventListeners()
  tweenCamera()
  addPlane()
  createCubes()
  _animate()

}

const addPlane = () => {
  let g, m, mesh
  g = new THREE.PlaneGeometry(1000, 250)
  m = new THREE.MeshPhongMaterial({color: new THREE.Color(0xcdd8ff)})
  mesh = new THREE.Mesh(g, m)
  mesh.position.set(0, 0, -10)
  mesh.receiveShadow = true
  scene.add(mesh)
}


const initEventListeners = () => {  
  resizeListener()
  rayEventListener()
}

const createCubes = () => {
  let word = ['f','e','r','i','a','p','p',]
  for(let i = 0; i < word.length; i++){
    new Cube(scene, word[i])
  }
}


const _animate = () => {
  requestAnimationFrame( _animate );

  TWEEN.update()
  Cube.update()
  renderer.render( scene, camera );
}