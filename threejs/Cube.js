import * as THREE from 'https://cdn.skypack.dev/three@0.130.0';

export default class Cube{
  static children = []
  static idCounter = 0

  constructor(scene, letter){
    let m, g, loader;
    const self = this;

    this.isTweening = false
    this.tween = false
    loader = new THREE.FontLoader()
    loader.load('https://storage.googleapis.com/feriapp/fonts/Origicide_Regular.json', function ( font ) {

      g = new THREE.TextGeometry( letter, {
        font: font,
        size: 2,
        height: 0.2,
        curveSegments: 1,
        bevelEnabled: false,
        bevelThickness: 1,
        bevelSize: 0,
        bevelOffset: 0,
        bevelSegments: 1
      });

      m = new THREE.MeshPhongMaterial({color:Cube.randomColor()})
      self.mesh = new THREE.Mesh(g, m);
      self.mesh.position.copy(Cube.randomPos('start'))
      self.mesh.castShadow = true
      self.mesh.receiveShadow = true
      self.mesh.name = ++Cube.idCounter

      scene.add(self.mesh)

      Cube.children.push(self)
    } );    
  }

  tweenRoutine(){
    if(!this.isTweening){
      const onStart = () => {
        this.isTweening = true
      }
      const onComplete = () => {
        this.isTweening = false
        TWEEN.remove(this.tween)
      }
      this.tween = new TWEEN.Tween(this.mesh.rotation)
      .to({y: ["+0.062", "-0.062"]}, Cube.randomTime())
      .easing(TWEEN.Easing.Quintic.InOut)
      .onStart(onStart)
      .onComplete(onComplete)
      .start()
    }
  }

  handleMouseHover(){
    const time = Cube.randomTime()
    this.tween.stop()
    TWEEN.remove(this.tween)

    const onComplete = () => {
      this.isTweening = false
    }
    const onStart = (time) => {
      const colorTween = new TWEEN.Tween(this.mesh.material.color)
      .to(Cube.randomColor(), time / 3)
      .easing(TWEEN.Easing.Exponential.In)
      .onComplete(()=>{TWEEN.remove(colorTween)})
      .start()
    }

    this.tween = new TWEEN.Tween(this.mesh.rotation)
    .to({y: "+31"}, time)
    .easing(TWEEN.Easing.Exponential.Out)
    .onStart(()=>{onStart(time)})
    .onComplete(onComplete)
    .start()

  }

  updateRoutine(){
    this.tweenRoutine()
  }

  static update(){
    Cube.children.forEach(child => child.updateRoutine())
  }

  static randomTime(){
    return (1000 + Math.random() * 2500)
  }
  static randomPos(){
    return Cube.children.length > 0 ?
    new THREE.Vector3(
      -5 + (Cube.children.length) * 1.5,
      1,
      - Math.random() * 2
    ) : 
    new THREE.Vector3(-5, 1, 0
    )
  }
  static randomColor(){
    const color = {
      r: .5 + Math.random() * .45,
      g: .5 + Math.random() * .45,
      b: .5 + Math.random() * .45,
    }
    return color
  }

  static find(mesh){
    return Cube.children.find(m => m.mesh.name == mesh.name)
  }
}