Fancybox.bind('[data-fancybox="gallery"]', {
    //
  }); 

var canvas = document.getElementById("canvas")
var context = canvas.getContext("2d")
const video = document.querySelector("#videoElement")

video.width = 110
video.height = 170

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


var img_count = 0
var data = []

var socket = io.connect(
  window.location.protocol + "//" + location.hostname + ":" + location.port
)
// var socket = io.connect("http://127.0.0.1:5000")
socket.on("connect", function() {
  console.log("Connected...!", socket.connected)
})


function wait() {
  return new Promise((resolve) => {
    setTimeout(resolve, 200);
  });
}


var submitBtn = document.getElementById("retrieveImages")
submitBtn.addEventListener('click', async () => {
  // var i = 0;                  //  set your counter to 1

  // function myLoop() {         //  create a loop function
  //   setTimeout(function() {   //  call a 3s setTimeout when the loop is called
  //     console.log('two')
  //     context.translate(800, 0);
  //     context.scale(-1, 1);
  //     context.drawImage(video, 0, 0, 800, 600);
  //     data.push(canvas.toDataURL("image/jpeg", 0.5))
  //     console.log('a')
  //     i++;                    //  increment the counter
  //     if (i < 20) {           //  if the counter < 10, call the loop function
  //       myLoop();             //  ..  again which will trigger another 
  //     }                       //  ..  setTimeout()
  //   }, 100)
  // }
  // myLoop();
  // console.log('one')
  for (let i = 0; i<=20; i++) {

      // console.log('two')
      context.translate(800, 0);
      context.scale(-1, 1);
      // context.drawImage(video, 0, 0, 800, 600);
      context.drawImage(video, 150, 0, 300, 600, 0, 0, 300, 600);
      // if ([0, 200, 400, 600, 800, 1000, 1200, 1400, 1600, 1800, 2000].includes(i)){
      await wait()
      data.push(canvas.toDataURL("image/jpeg", 0.5))
      // }
      // console.log('a')
      // console.log('col_data', data)
      // console.log(canvas.toDataURL("image/jpeg", 0.5))

  }
  console.log('data', data)
  if(data.length !== 0){
    socket.emit("image", {'data': data, 'img_count': img_count})
  }
})


socket.on("processed_image", function (response) {
  img_count = response['img_count']
  // console.log('res', response['data'])
  // console.log(response['details'])
  // console.log(response['result_image'])
  // console.log(response['result_image'].length)
  if (response['result_image'].length !== 0) {
    var divElement = document.getElementById('retrieve_images_server')
    var aTag = document.createElement('a')
    aTag.setAttribute("data-fancybox", "gallery")
    aTag.setAttribute("href", `static/images/${response["result_image"]}`)
    var imgTag = document.createElement('img')
    imgTag.setAttribute('class', 'image-card')
    imgTag.setAttribute('src', `static/images/${response["result_image"]}`)
    imgTag.setAttribute('alt', '')
    aTag.appendChild(imgTag)
    divElement.appendChild(aTag)

  }
  if (response['details'] !== 'Unknown') {
    socket.emit("image", {'data': response['data'], 'img_count': img_count})
  }
})

