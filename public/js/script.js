const text = "Selamat Datang....❤️";
let i = 0;
let n = 0;
let temp = [];
const speed = 100;
var defaultImg = 0;

var imgs = document.querySelectorAll(".album img");

imgs[defaultImg].style.display = "inline";

function textAnimate() {
  if (i < text.length) {
    document.getElementById("typings").innerHTML =
      temp.join("") + text.charAt(i) + "_";
    temp.push(text.charAt(i));
    i++;
    setTimeout(textAnimate, speed);
  } else {
    i = 0;
    temp = [];
    setTimeout(textAnimate, 1000);
  }
}
function addSlider(entitas) {  
  for (let ii = 0; ii < imgs.length; ii++) {
    imgs[ii].style.display = "none";
  }
  defaultImg += entitas;
  if (imgs.length-1 < defaultImg) {
    defaultImg = 0;
}
if (defaultImg === -1) defaultImg = 2;
  imgs[defaultImg].style.display = "inline";
}

textAnimate();
