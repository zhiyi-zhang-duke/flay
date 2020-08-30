function clearRecipe() {
  document.getElementById("recipe").setAttribute('value','')
}

function clearIngredient() {
  document.getElementById("ingredient").setAttribute('value','')
}

function sanitizeSearches() {
	recipe = document.getElementById("recipe").getAttribute('value')
	if (recipe == "Recipe names i.e. chili"){
		document.getElementById("recipe").setAttribute('value','')
	}
	ingredient = document.getElementById("ingredient").getAttribute('value')
	if (ingredient == "Ingredients i.e. tomato"){
		document.getElementById("ingredient").setAttribute('value','')
	}	
}