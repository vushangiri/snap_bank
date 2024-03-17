let uploadFiles = []

function CustomUpload(element) {
	let ref = this;
	this.imageFileArray = [];
	this.element = $(element);
	this.element.on('change', async function (e) {
		let arrayImage = e.target.files;
		let start = ref.imageFileArray.length;
		let validExt = ['image/jpg', 'image/jpeg', 'image/png'];
		$.each(arrayImage, (index, item) => {
			if ($.inArray(item.type,validExt) != -1) {
				item.index = start + index;
                uploadFiles = [...ref.imageFileArray]
				ref.imageFileArray.push(item);
				let fr = new FileReader();
				let imageItem = '';
				fr.onload = function (event) {
					imageItem += `
                            <div class="custom-file-preview-item"
                            style="background: url('${event.target.result}')">
                            <span data-key="${item.index}" class="custom-file-preview-del"><i
                            class="fa fa-times"></i></span>
                            </div>
                        `;
					$('.custom-file-preview').append(imageItem);
				}
				fr.readAsDataURL(item);
			}else{
				alert('This is not an image');
			}
			//Array images
			console.log(ref.imageFileArray);
		});
	});
	this.element.parent().on('click', '.custom-file-preview-del', function (e) {
		e.preventDefault();
		let del = $(this);
		let id = del.data('key');
		let index = ref.imageFileArray.findIndex(item => {
			return item.index == id;
		});
		ref.imageFileArray.splice(index, 1);
		del.parent().remove();
		//Array after deleted
		console.log(ref.imageFileArray);
        uploadFiles = [...ref.imageFileArray]
	});
    
    
}
const upload = new CustomUpload('#fileImage');


document.getElementById("uploadFiles").addEventListener('click', () => {
    console.log("uploadFiles", uploadFiles)
})

document.getElementById("clearAll").addEventListener('click', () => {
    location.reload();
})

