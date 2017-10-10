/* Return the trim of the received string
*/
function eaTrimString(inString) {
  if (inString == null || inString.length ==0) {
    return "";
  }
  inString = inString.replace( /^\s+/g, "" );// strip leading
  return inString.replace( /\s+$/g, "" );// strip trailing
}

/* Return true if the received radioCheckName element has a checked value, false otherwise
*/
function eaValidateMandatoryRadioCheck(theRadioCheck) {
	if (theRadioCheck.length > 0) {
  		for (i=0; i<theRadioCheck.length; i++)  {
			if (theRadioCheck[i].checked)  {
 	      	return true;
 	    	}
 		}
 	} else {
 		if (theRadioCheck.checked) {
 			return true;
 		}
 	}
 	return false;
}

/* Return true if the received selectName element has a selected value, false otherwise
*/
function eaValidateMandatorySelect(theSelect) {
  	//theOptions = theSelect.options;
  	//for (i=0; i<theOptions.length; i++)  {
	//	if (theOptions[i].selected)  {
 	//      return true;
 	//    }
 	//}
 	if (theSelect.selectedIndex >= 0 && eaTrimString(theSelect.options[theSelect.selectedIndex].value).length > 0 ){
 		return true;
 	}
 	return false;
}

/* Return true if the received text is not empty, false otherwise
*/
function eaValidateMandatoryText(theText) {
	if (eaTrimString(theText.value).length == 0) {
		return false;
    } 
    return true;
}