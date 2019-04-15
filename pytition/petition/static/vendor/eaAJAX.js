/* AJAX stuff for AJAX enabled ea campaign */

/* create and return XMLHttpRequest or ActiveXObject, depending on browser
*/
function createXMLRequest() {
    var xmlobj = null;
    try {
      // instantiate request object for Mozilla, Nestcape, etc.
      xmlobj = new XMLHttpRequest();
    } catch(e) {
      try {
        // instantiate object for Internet Explorer
        xmlobj=new ActiveXObject('Microsoft.XMLHTTP');
      } catch(e) {
        return null;
      }
    }
    return xmlobj;
}

/* Submits ajax request based on the received form 
*  and puts the results of the request in the received target div
*/
function doAJAXForm(form, target, disableForm) {
    var serverProcess = form.action;
    var formElements=form.elements;
    var firstParameter=true;
    var theValue=null;
    for (var i=0;i<formElements.length;i++) {
    	var theValue=null;
    	var theElement=formElements[i];
//alert(theElement.name + " " + theElement.type);
    	if (theElement.type == 'button'
    	    || theElement.type == 'reset'
    	    || theElement.type == 'submit'
    	    || theElement.disabled == true) {
    		//skip
    	} else if (theElement.tagName == 'SELECT') {
				var options = theElement.options;
				for (var k=0;k<options.length;k++) {
					if (options[k].selected) {
						if(firstParameter == true) {
    	  					serverProcess=serverProcess + "?";
    	  					firstParameter=false;
    					} else {
    	  					serverProcess=serverProcess + "&";
    	  				}
//alert(theElement.name + ' = ' + options[k].value);
    	  				serverProcess += theElement.name + "=" + options[k].value;
					}	
				}
				theValue=null;
		}  else if (theElement.type == 'checkbox') {
			if (theElement.checked) {
				if(firstParameter == true) {
    	  			serverProcess=serverProcess + "?";
    	  			firstParameter=false;
    			} else {
    	  			serverProcess=serverProcess + "&";
    	  		}
//alert(theElement.name + ' = ' + theElement.value);
    	  		serverProcess += theElement.name + "=" + theElement.value;
			}	
		}  else if (theElement.type == 'radio') {
			if (theElement.checked) {
				if(firstParameter == true) {
    	  			serverProcess=serverProcess + "?";
    	  			firstParameter=false;
    			} else {
    	  			serverProcess=serverProcess + "&";
    	  		}
//alert(theElement.name + ' = ' + theElement.value);
    	  		serverProcess += theElement.name + "=" + theElement.value;
			}
		} else {
			theValue = theElement.value;
		}
//alert('the value ' + theValue);
		if (theValue != null) {
		  	if(firstParameter == true) {
    	  		serverProcess=serverProcess + "?";
    	  		firstParameter=false;
    		} else {
    	  		serverProcess=serverProcess + "&";
    	  	}
    		serverProcess=serverProcess + theElement.name + "=" + theValue;
    	}
    }
//alert(serverProcess);
    var result = doAJAX(serverProcess);
//alert('disableForm ' + disableForm);
    if (disableForm == true && result.indexOf("<EA_ERROR_MESSAGE>") < 0) {
    	handleExistingFormElements(form);
		var spans = document.getElementsByTagName("span");
		for (var l=0;l<spans.length;l++) {
	  	hideSubmitResetButtons(spans[l]);
		}
	}
	if (result.indexOf("<EA_ERROR_MESSAGE>") >= 0) {
		result = getErrorMessage(result);
		putResultInTarget(result, "eaAjaxErrorMessageContainer", true);
	} else {
		clearContainerNamedAndChildren("eaAjaxErrorMessageContainer");
		putResultInTarget(result, target, true);
	}
}

function doAJAXLink(url,target) {
  	var result = doAJAX(url);
  	if (result.indexOf("<EA_ERROR_MESSAGE>") >= 0) {
  		result = getErrorMessage(result);
		putResultInTarget(result, "eaAjaxErrorMessageContainer", true);
	} else {
		clearContainerNamedAndChildren("eaAjaxErrorMessageContainer");
  		putResultInTarget(result, target, true);
  	}
}

function getErrorMessage(result) {
	var idx = result.indexOf("<EA_ERROR_MESSAGE>");
	return result.substring(idx + 18);
}

function doAJAX(url) {
//alert('url\n ' + url);
  //append eaAJAXsubmit parameter
  url = url + "&ea.AJAX.submit=true";
  var result = "";
  var xmlobj = createXMLRequest();
  // open socket connection
  xmlobj.open('POST',url,false);
  // send request
  xmlobj.send(null);
  // if request is completed, grab the content
  if(xmlobj.readyState==4){
    if(xmlobj.status==200){
      result=xmlobj.responseText;
    }
  }
//alert('result \n' + result);
  return result;
}

function putResultInTarget(result, target, clearTarget) {
    var divs = document.getElementsByTagName("div");
    var theDiv;
    for (var i=0;i<divs.length;i++) {
      theDiv = divs[i];
      if (theDiv.className && theDiv.className.match(target)) {
 		if (clearTarget) {
 		  //clearContainer(theDiv);
 		}
 		theDiv.style.display="";
		var newdiv = document.createElement("div");
		newdiv.innerHTML = result;
		theDiv.appendChild(newdiv);
        return;
      }
    }
}

function putResultInTargetWithId(result, targetId, clearTarget) {
    var theDiv = document.getElementById(targetId);
    if (clearTarget) {
      clearContainer(theDiv);
    }
    theDiv.style.display="";
    var newdiv = document.createElement("div");
    newdiv.innerHTML = result;
    theDiv.appendChild(newdiv);
    return;
}

function clearContainerNamed(targetName) {
    var divs = document.getElementsByTagName("div");
    var theDiv;
    for (var i=0;i<divs.length;i++) {
      theDiv = divs[i];
      if (theDiv.className && theDiv.className.match(targetName)) {
 		  clearContainer(theDiv);
 	  }
 	}
}

function clearContainerNamedAndChildren(targetName) {
	var divs = document.getElementsByTagName("div");
    var theDiv;
    for (var i=0;i<divs.length;i++) {
      theDiv = divs[i];
      if (theDiv.className && theDiv.className.match(targetName)) {
 		  clearContainerAndChildren(theDiv);
 	  }
 	}
}

function clearContainer(theContainer) {
	theContainer.style.display = "none";
	theContainer.innerHTML="";
}

function clearContainerAndChildren(theContainer) {
	while(theContainer.firstChild) {
		theContainer.removeChild(theContainer.firstChild);
	}
}

/* hide any existing submit/reset buttons
*/
function hideSubmitResetButtons(theSpan) {
	if (theSpan.className && theSpan.className.match("eaSubmitResetButtonGroup")) {
	  theSpan.style.display = "none";
	}
}

/* deaden existing form elements since they can not be resubmitted anyway.
*/
function handleExistingFormElements(form) {
  var formElements = form.elements;
  for (var i=0;i<formElements.length;i++) {
    var theElement = formElements[i];
    theElement.disabled = true;
  }  
}

function clearContentWithBaseClass(baseClass) {
    var divs = document.getElementsByTagName("div");
    var theDiv;
    for (var i=0;i<divs.length;i++) {
      theDiv = divs[i];
      if (theDiv.className && theDiv.className.match(baseClass)) {
      	clearContainer(theDiv);
	  }
	}
}
