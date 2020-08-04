document.addEventListener('DOMContentLoaded',function(){
	document.querySelector('#loginform').onsubmit = function(){
		localStorage.setItem('kunal',kuns);
		var bat = localStorage.getItem('kunal');
		console.log('hi');
		return true;
	};
});