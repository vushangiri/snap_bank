// var socket = io.connect(
//   window.location.protocol + "//" + location.hostname + ":" + location.port
// )
var socket = io.connect("http://localhost:5000")
socket.on("connect", function() {
  console.log("Connected...!", socket.connected)
})

var canvas = document.getElementById("canvas")
var context = canvas.getContext("2d")
const video = document.querySelector("#videoElement")
var userData = document.getElementById('userName')

video.width = 400
video.height = 300

if (navigator.mediaDevices.getUserMedia) {
  navigator.mediaDevices
    .getUserMedia({
      video: true,
    })
    .then(function (stream) {
      video.srcObject = stream
      video.play
    })
    .catch(function (error) {})
}

const FPS = 10
setInterval(() => {
  width = video.width
  height = video.height
  context.drawImage(video, 0, 0, width, height)
  var data = canvas.toDataURL("image/jpeg", 0.5)
  context.clearRect(0, 0, width, height)
  socket.emit("image", data)
}, 1000/FPS)

socket.on("processed_image", function (response) {
  userData.innerText = response['details'] !== 'Unknown'? `Welcome ${response['details']}` : response['details'] 
  photo.setAttribute('src', response['data'])
})
