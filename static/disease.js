const form = document.querySelector('#symptom-form');
const resultDiv = document.querySelector('#result');

const searchBar = document.getElementById('search-bar');
const checkboxes = document.querySelectorAll('#symptom-form input[type="checkbox"]');;//here we are selecting all the checboxes of the symptom-form element
//'#symptom-form input[type="checkbox"]' such a case is used when we want to retrive an element inside an another element

searchBar.addEventListener('input', () => {  //this eventlistner will be trigger whenever there will be input in the searchbar(whenever we will enter an element)
	//here we can use (event) or we can directly use () because (event) is just an object to refer that event and here we can find the searchbox value without event object 
  const searchValue = searchBar.value.toLowerCase();//converts searchbar value to lowercase

  checkboxes.forEach((checkbox) => {
    const label = checkbox.parentElement.textContent.toLowerCase();
	//parentElement property to access the parent element of the checkbox (which is the <label> element), and then use the textContent property to get its(<label>'s) text content:
	//<label>a<abel> teextcontent will give 'a' 

	if (searchValue === '') { 
		//this case is inserted because while deleting the letters from searchbox the eventlistner is also trigger and when it is empty it searches for an empty string
		//since a empty string s pesent in every string every box is colored
		//to eliminate this this case is covered 
		checkbox.parentElement.classList.remove('highlight');
		checkbox.parentElement.style.display = 'flex';
	  } else if (label.includes(searchValue)) {
		checkbox.parentElement.classList.add('highlight');//here .classList add a new class to <label> element.<label class="highlight"></label>
		checkbox.parentElement.style.display = 'flex';//Flexbox allows you to arrange elements in a row or a column, and it can help to align elements more precisely.However here whether it is flex or bock it will not create any change
	  } else {
		checkbox.parentElement.classList.remove('highlight');
	  }
  });
});

searchBar.addEventListener('keydown', (event) => { //this is triggered When a key is pressed down inside the search bar
	if (event.key === 'Enter') { // the listener checks if the pressed key is the Enter key.
	  const highlightedCheckbox = document.querySelector('.highlight input[type="checkbox"]'); //searches for the first checkbox that has the 'highlight' class applied to its parent element
	  highlightedCheckbox.scrollIntoView({ behavior: 'smooth' });//scrools to that checkbox smoothly
	}
  });

form.addEventListener('submit', (event) => {
	event.preventDefault();

	const checkboxes = Array.from(document.querySelectorAll('#symptom-form input[name="symptoms[]"]:checked'));
    const symptoms = checkboxes.map(input => parseInt(input.value));

	fetch('http://127.0.0.1:5000/predict1', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({symptoms: symptoms})
	})
	.then(response => response.json())
	.then(data => {
		// Getting the disease name from the response
		const disease = data.disease;
		console.log(disease);
		const additiona=data.message;
		const additional = additiona.replace(/\.\s*/g, ".\n\n");
		console.log(additional);
		
		// Calling the /wiki endpoint to get additional information
		
			resultDiv.innerHTML = `
			<div class="predicted-disease">Predicted disease: <b>${disease}</b></div>
			<div class="additional-info"><ul>${additional}</ul></div>`;
		})
		.catch(error => console.error(error));
	})
